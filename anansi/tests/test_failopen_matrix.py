"""THE consolidated SAFE-02 fail-open matrix (Phase 3, plans 03-01 + 03-02).

Every SAFE-02 case maps to exactly one row. Rows already proven elsewhere
(Phases 1-2 and test_reflection.py) are referenced by file::name (never
duplicated); the full-hook-path rows are implemented in this module. Every
implemented case asserts: no exception escapes the hook, the injection is
empty (hook returns None) or normal, a correct telemetry outcome row exists
when recordable, and module state is left sane. For reflection rows "no
state mutation" means the appraisal-state tables + the
last_reflected_turn_log_id watermark (last_seen_session_id is exempt —
written pre-call by design; see reflection.py's module docstring).

| case                                      | proven by                                                                                                    | status        |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------------|---------------|
| deadline timeout (LLM too slow)           | test_appraisal.py::test_timeout_binds_wall_clock                                                             | referenced    |
| llm raise (llm_error)                     | test_appraisal.py::test_llm_error_captured_without_raising; test_pre_llm_call.py::test_llm_raise_fails_open  | referenced    |
| trust rejection -> single fallback        | test_appraisal.py::test_trust_fallback_retries_once_without_override                                         | referenced    |
| parse_fail (run_appraisal level)          | test_appraisal.py::test_parse_fail_paths                                                                     | referenced    |
| unwritable telemetry DB                   | test_pre_llm_call.py::test_unwritable_telemetry_is_silent                                                    | referenced    |
| corrupt-DB quarantine                     | test_store.py::test_corrupt_db_quarantined; test_telemetry_store.py::test_v1_db_quarantined_and_recreated_at_current_schema | referenced |
| absent DB                                 | test_store.py::test_absent_db_read_returns_none; test_telemetry_store.py::test_record_telemetry_absent_or_corrupt_path_returns_false | referenced |
| kill switch                               | test_pre_llm_call.py::test_kill_switch_skips_llm                                                             | referenced    |
| empty / duplicate / social-closer gates   | test_pre_llm_call.py::test_empty_message_skipped, ::test_duplicate_gate_within_session, ::test_social_closer_skipped | referenced |
| injection sanitization                    | test_dryrun_demo.py::test_dryrun_demo                                                                        | referenced    |
| malformed JSON (full hook path)           | ::test_hook_parse_fail_trio[malformed_json]                                                                  | implemented   |
| truncated JSON (full hook path)           | ::test_hook_parse_fail_trio[truncated_json]                                                                  | implemented   |
| content: null (full hook path)            | ::test_hook_parse_fail_trio[content_null]                                                                    | implemented   |
| missing config: entry absent              | ::test_missing_config_entry_absent_defaults                                                                  | implemented   |
| missing config: host loader raises        | ::test_missing_config_host_loader_raises                                                                     | implemented   |
| missing config: malformed entry values    | ::test_missing_config_malformed_values_coerced                                                               | implemented   |
| gateway session-rollover state reuse      | ::test_gateway_rollover_reuses_module_state                                                                  | implemented   |
| locked DB: record_telemetry               | ::test_locked_db_record_telemetry_returns_false                                                              | implemented   |
| locked DB: read_snapshot                  | ::test_locked_db_read_snapshot_returns_none                                                                  | implemented   |
| locked DB: apply_deltas                   | ::test_locked_db_apply_deltas_returns_false                                                                  | implemented   |
| locked DB: full pre_llm_call              | ::test_locked_db_full_hook_still_injects                                                                     | implemented   |
| reflection idempotency + debounce double-fire | test_reflection.py::test_idempotence_reflect_twice_same_span, ::test_double_fire_back_to_back_second_is_noop, ::test_debounce_holds_until_five_unreflected_turns | referenced |
| reflection echo-exclusion                 | test_reflection.py::test_record_turn_strips_sentinel_lines, ::test_build_digest_strips_seeded_sentinel_rows, ::test_sentinel_never_reaches_the_reflection_llm | referenced |
| locked DB during reflection write         | test_reflection.py::test_locked_db_during_apply_no_partial_state                                            | referenced    |
| reflect timeout / parse_fail / llm_error  | test_reflection.py::test_timeout_leaves_state_untouched, ::test_parse_fail_leaves_state_untouched, ::test_llm_error_leaves_state_untouched | referenced |
| on_session_end: no DB + no ctx            | ::test_on_session_end_no_db_no_ctx_returns_none                                                              | implemented   |
| on_session_end: exploding reflection LLM  | ::test_on_session_end_exploding_llm_fails_open                                                               | implemented   |
| post_llm_call: locked DB                  | ::test_post_llm_call_locked_db_returns_none                                                                  | implemented   |

Lock-semantics note (verified 2026-06-10 against sqlite3 under the hermes
venv): in WAL mode — the production arrangement, set at DB creation — a held
``BEGIN EXCLUSIVE`` behaves like IMMEDIATE: it blocks WRITERS but never
READERS, so the hot-path snapshot read proceeds normally while telemetry
writes degrade to False. The read-degradation row therefore flips its tmp DB
to rollback journal mode, where EXCLUSIVE genuinely blocks readers.

Style: every test runs against tmp_path DBs (store.get_db_path monkeypatched
or explicit db_path=); the real $HERMES_HOME is never touched. Zero network.
"""

import json
import sqlite3
import time
import types

import pytest

plugin_llm = pytest.importorskip("agent.plugin_llm")

import anansi  # noqa: E402
from anansi import appraisal, config, store  # noqa: E402


def _response(text, prompt_tokens=120, completion_tokens=80):
    return types.SimpleNamespace(
        choices=[
            types.SimpleNamespace(
                message=types.SimpleNamespace(content=text, role="assistant"),
                finish_reason="stop",
            )
        ],
        usage=types.SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        model="fake-model",
    )


RICH_PAYLOAD = {
    "instincts": [
        {"kind": "caution", "intensity": 0.7, "reason": "deadline tension",
         "confidence": 0.8},
    ],
    "salient_observations": [
        {"text": "user switched projects mid-thread", "confidence": 0.9},
    ],
    "contradiction_flags": [],
    "suggested_memory_searches": ["prior deadline discussions"],
    "gut_reaction": "focused urgency",
}

MALFORMED_PROSE = "I cannot produce structured output for that request, sorry."

# A valid JSON document cut mid-string — simulating max-token truncation.
_FULL_JSON = json.dumps(RICH_PAYLOAD)
TRUNCATED_JSON = _FULL_JSON[: _FULL_JSON.index("deadline tension") + len("deadline ten")]


class _CountingCaller:
    """Fake sync_caller. payload: dict -> JSON content; str -> raw content;
    None -> content: null; Exception -> raised."""

    def __init__(self, payload):
        self.calls = 0
        self.payload = payload

    def __call__(self, *, messages, model_override=None, **kwargs):
        self.calls += 1
        if isinstance(self.payload, Exception):
            raise self.payload
        content = (
            json.dumps(self.payload) if isinstance(self.payload, dict)
            else self.payload
        )
        return ("openai", model_override or "fake-model", _response(content))


def _cfg(**overrides):
    cfg = {
        "enabled": True,
        "confidence_threshold": 0.6,
        "deadline_seconds": 8.0,
        "history_chars": 4000,
        "model": None,
        "max_tokens": 700,
        "drive_enabled": True,
    }
    cfg.update(overrides)
    return cfg


def _telemetry_rows(db_path):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return list(con.execute("SELECT outcome FROM telemetry ORDER BY id"))
    finally:
        con.close()


@pytest.fixture(autouse=True)
def _clean_config_cache():
    """Missing-config tests exercise the REAL get_cfg — keep its cache clean."""
    config.reset_cache()
    yield
    config.reset_cache()


@pytest.fixture
def matrix_env(tmp_path, monkeypatch):
    """Registered hook wired to tmp state + a swappable fake LLM.

    config.get_cfg is NOT patched here (the missing-config rows need the real
    one); tests that want a pinned cfg use the `pinned_env` fixture below.
    Mirrors test_pre_llm_call.py's arrangement.
    """
    db_path = tmp_path / "anansi" / "state.db"
    monkeypatch.setattr(store, "get_db_path", lambda: db_path)
    assert store.ensure_db()

    state = {"cfg": _cfg(), "caller": _CountingCaller(RICH_PAYLOAD)}

    def _delegating_caller(**kwargs):
        # late-bound so tests can swap state["caller"] after fixture setup
        return state["caller"](**kwargs)

    llm = plugin_llm.make_plugin_llm_for_test(
        plugin_id="anansi",
        policy=plugin_llm._TrustPolicy(plugin_id="anansi"),
        sync_caller=_delegating_caller,
    )
    anansi.register(
        types.SimpleNamespace(llm=llm, register_hook=lambda *a, **k: None)
    )
    anansi._session_state.update(
        {"session_id": None, "last_msg_norm": None}
    )
    yield types.SimpleNamespace(state=state, db_path=db_path)
    appraisal._reset_executor_for_tests()
    anansi._ctx = None


@pytest.fixture
def pinned_env(matrix_env, monkeypatch):
    """matrix_env with config.get_cfg pinned to the controllable cfg dict."""
    monkeypatch.setattr(
        config, "get_cfg", lambda force_reload=False: matrix_env.state["cfg"]
    )
    return matrix_env


# ---------------------------------------------------------------------------
# parse_fail trio — through the FULL registered pre_llm_call hook path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(MALFORMED_PROSE, id="malformed_json"),
        pytest.param(TRUNCATED_JSON, id="truncated_json"),
        pytest.param(None, id="content_null"),
    ],
)
def test_hook_parse_fail_trio(pinned_env, content):
    if content is not None:  # sanity: both string payloads are invalid JSON
        with pytest.raises(json.JSONDecodeError):
            json.loads(content)

    pinned_env.state["caller"] = _CountingCaller(content)
    message = "how is the migration going?"
    out = anansi.pre_llm_call(session_id="s1", user_message=message)

    assert out is None  # empty injection, no raise (else _fail_open -> llm_error)
    assert _telemetry_rows(pinned_env.db_path) == [("parse_fail",)]
    assert pinned_env.state["caller"].calls == 1

    # Module state left sane: session + duplicate-gate key recorded.
    assert anansi._session_state["session_id"] == "s1"
    assert anansi._session_state["last_msg_norm"] == (
        appraisal.normalize_message(message)
    )

    # Still fully functional after the failure: next turn injects normally.
    pinned_env.state["caller"] = _CountingCaller(RICH_PAYLOAD)
    out2 = anansi.pre_llm_call(
        session_id="s1", user_message="a different question entirely"
    )
    assert isinstance(out2, dict) and set(out2) == {"context"}
    assert _telemetry_rows(pinned_env.db_path) == [("parse_fail",), ("ok",)]


# ---------------------------------------------------------------------------
# missing-config path — the REAL get_cfg, host layer absent/raising/garbage
# ---------------------------------------------------------------------------


_DEFAULTS = {
    "enabled": True,
    "confidence_threshold": 0.6,
    "deadline_seconds": 8.0,
    "history_chars": 4000,
    "model": None,
    "max_tokens": 700,
    "reflection_enabled": True,
    "reflect_every_n_turns": 5,
    "reflect_max_tokens": 700,
    "reflect_deadline_seconds": 8.0,
    "drive_enabled": True,
}


def test_missing_config_entry_absent_defaults(matrix_env, monkeypatch):
    monkeypatch.setattr(config, "_load_host_entry", lambda: None)
    assert config.get_cfg(force_reload=True) == _DEFAULTS

    out = anansi.pre_llm_call(
        session_id="s1", user_message="how is the migration going?"
    )
    assert isinstance(out, dict) and out["context"].startswith("[anansi appraisal]")
    assert _telemetry_rows(matrix_env.db_path) == [("ok",)]


def test_missing_config_host_loader_raises(matrix_env, monkeypatch):
    def _boom():
        raise RuntimeError("host config unreadable")

    monkeypatch.setattr("hermes_cli.config.load_config", _boom)
    assert config.get_cfg(force_reload=True) == _DEFAULTS  # no raise

    out = anansi.pre_llm_call(
        session_id="s1", user_message="how is the migration going?"
    )
    assert isinstance(out, dict) and out["context"].startswith("[anansi appraisal]")
    assert _telemetry_rows(matrix_env.db_path) == [("ok",)]


def test_missing_config_malformed_values_coerced(matrix_env, monkeypatch):
    monkeypatch.setattr(
        config,
        "_load_host_entry",
        lambda: {
            "enabled": "definitely",         # unrecognized string -> True
            "confidence_threshold": "high",  # not a float -> 0.6
            "deadline_seconds": "soon",      # not a float -> 8.0
            "history_chars": "lots",         # not an int -> 4000
            "max_tokens": [],                # not an int -> 700
            "llm": "garbage-not-a-dict",     # not a dict -> model None
        },
    )
    assert config.get_cfg(force_reload=True) == _DEFAULTS  # coerced, no raise

    out = anansi.pre_llm_call(
        session_id="s1", user_message="how is the migration going?"
    )
    assert isinstance(out, dict) and out["context"].startswith("[anansi appraisal]")
    assert _telemetry_rows(matrix_env.db_path) == [("ok",)]


# ---------------------------------------------------------------------------
# gateway session-rollover state reuse (long-lived process, no
# on_session_start between sessions — the gateway-lane shape)
# ---------------------------------------------------------------------------


def test_gateway_rollover_reuses_module_state(pinned_env):
    message = "tell me about the deadline"
    first = anansi.pre_llm_call(session_id="A", user_message=message)
    assert isinstance(first, dict)

    # Session B, SAME message, no on_session_start in between: the rollover
    # guard resets last_msg_norm — NOT skipped as duplicate, runs normally.
    second = anansi.pre_llm_call(session_id="B", user_message=message)
    assert isinstance(second, dict)
    assert pinned_env.state["caller"].calls == 2
    assert _telemetry_rows(pinned_env.db_path) == [("ok",), ("ok",)]

    # No stale-state leakage: module state tracks the new session.
    assert anansi._session_state["session_id"] == "B"
    assert anansi._session_state["last_msg_norm"] == (
        appraisal.normalize_message(message)
    )

    # The duplicate gate still works WITHIN the new session.
    third = anansi.pre_llm_call(session_id="B", user_message=message)
    assert third is None
    assert _telemetry_rows(pinned_env.db_path)[-1] == ("skipped:duplicate",)
    assert pinned_env.state["caller"].calls == 2


# ---------------------------------------------------------------------------
# DRIVE-06: the SEPARATE drive kill switch (success criterion 4) — drive off
# ⇒ zero goal-aware fields, appraisal block byte-for-byte unchanged, and a
# non-failure skipped:drive_disabled telemetry row.
# ---------------------------------------------------------------------------


def _seed_goals(db_path):
    """Persist a flagged active goal + an INERT candidate into the tmp DB."""
    assert store.apply_deltas(
        {
            "goals_add": [
                {"text": "ship the drive layer", "status": "active",
                 "success_criteria": "phase 7 complete", "flagged_priority": 1},
                {"text": "maybe a dashboard", "status": "candidate"},
            ]
        },
        db_path,
    ) is True


def test_drive_disabled_appraisal_unchanged(pinned_env):
    """Drive off + a goals-bearing snapshot: the hook still returns a normal
    block; that block is byte-for-byte identical to the SAME inputs run with
    NO goals present (the appraisal-unchanged invariant). A non-failure
    skipped:drive_disabled telemetry row is recorded."""
    message = "how is the migration going?"

    # Run 1: drive OFF, goals present in the DB.
    pinned_env.state["cfg"] = _cfg(drive_enabled=False)
    _seed_goals(pinned_env.db_path)
    pinned_env.state["caller"] = _CountingCaller(RICH_PAYLOAD)
    out_off = anansi.pre_llm_call(session_id="s1", user_message=message)
    assert isinstance(out_off, dict) and set(out_off) == {"context"}
    assert out_off["context"].startswith("[anansi appraisal]")
    # The non-failure skipped row rode along this eligible turn.
    assert ("skipped:drive_disabled",) in _telemetry_rows(pinned_env.db_path)

    # Run 2: drive ON but NO goals in a fresh DB — the reference block.
    fresh_db = pinned_env.db_path.parent / "ref.db"
    assert store.ensure_db(fresh_db) is True
    real_get = store.get_db_path
    try:
        store.get_db_path = lambda: fresh_db
        pinned_env.state["cfg"] = _cfg(drive_enabled=True)
        anansi._session_state.update({"session_id": None, "last_msg_norm": None})
        pinned_env.state["caller"] = _CountingCaller(RICH_PAYLOAD)
        out_ref = anansi.pre_llm_call(session_id="s2", user_message=message)
    finally:
        store.get_db_path = real_get
    assert isinstance(out_ref, dict) and set(out_ref) == {"context"}

    # Byte-for-byte equal: drive-off-with-goals == drive-on-with-no-goals.
    assert out_off["context"] == out_ref["context"]


def test_drive_disabled_is_non_failure(pinned_env):
    """skipped:drive_disabled rides the skipped:* exclusion prefix: it does
    NOT count toward telemetry_summary.failure_count."""
    pinned_env.state["cfg"] = _cfg(drive_enabled=False)
    pinned_env.state["caller"] = _CountingCaller(RICH_PAYLOAD)
    out = anansi.pre_llm_call(
        session_id="s1", user_message="how is the migration going?"
    )
    assert isinstance(out, dict)
    rows = _telemetry_rows(pinned_env.db_path)
    assert ("skipped:drive_disabled",) in rows
    assert ("ok",) in rows  # appraisal still ran

    summary = store.telemetry_summary(pinned_env.db_path)
    assert summary is not None
    assert summary["failure_count"] == 0  # drive-disabled is a non-failure
    assert summary["by_outcome"].get("skipped:drive_disabled") == 1


# ---------------------------------------------------------------------------
# locked DB during write — a second connection holds BEGIN EXCLUSIVE
# ---------------------------------------------------------------------------


def test_locked_db_record_telemetry_returns_false(tmp_path, monkeypatch):
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    monkeypatch.setattr(store, "_DEFAULT_BUSY_TIMEOUT_MS", 100)  # keep it fast
    holder = sqlite3.connect(str(db))
    try:
        holder.execute("BEGIN EXCLUSIVE")
        assert store.record_telemetry("ok", wall_ms=1, db_path=db) is False
        # WAL design truth (STATE-02): the writer lock never blocks readers —
        # the hot-path snapshot read proceeds normally while writes degrade.
        assert store.read_snapshot(db) is not None
    finally:
        holder.rollback()
        holder.close()


def test_locked_db_read_snapshot_returns_none(tmp_path, monkeypatch):
    """Reader-blocking lock -> read_snapshot returns None, never raises.

    WAL readers are never blocked by BEGIN EXCLUSIVE (see the test above), so
    this row flips the tmp DB to rollback journal mode — where EXCLUSIVE
    genuinely blocks readers — to prove the read-degradation contract.
    Python's sqlite3.connect retries a busy DB for `timeout` seconds (default
    5.0); the wrapper shrinks it so the test stays fast (same idiom as the
    _DEFAULT_BUSY_TIMEOUT_MS monkeypatch on the write paths).
    """
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    conn = sqlite3.connect(str(db))
    try:
        conn.execute("PRAGMA journal_mode=DELETE")
    finally:
        conn.close()
    holder = sqlite3.connect(str(db))
    try:
        holder.execute("BEGIN EXCLUSIVE")
        real_connect = sqlite3.connect
        monkeypatch.setattr(
            store.sqlite3, "connect",
            lambda *args, **kwargs: real_connect(*args, timeout=0.1, **kwargs),
        )
        start = time.monotonic()
        assert store.read_snapshot(db) is None  # degrades, no raise
        assert time.monotonic() - start < 2.0
    finally:
        holder.rollback()
        holder.close()


def test_locked_db_apply_deltas_returns_false(tmp_path):
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    holder = sqlite3.connect(str(db))
    try:
        holder.execute("BEGIN EXCLUSIVE")
        start = time.monotonic()
        assert store.apply_deltas(
            {"concerns_add": [{"text": "blocked write"}]}, db, busy_timeout_ms=100
        ) is False
        assert time.monotonic() - start < 2.0  # busy timeout honored
    finally:
        holder.rollback()
        holder.close()


def test_locked_db_full_hook_still_injects(pinned_env, monkeypatch):
    """State DB locked for writes during the turn: the hook still returns its
    normal {"context": ...} result; the telemetry failure is silent."""
    monkeypatch.setattr(store, "_DEFAULT_BUSY_TIMEOUT_MS", 100)
    holder = sqlite3.connect(str(pinned_env.db_path))
    try:
        holder.execute("BEGIN EXCLUSIVE")
        out = anansi.pre_llm_call(
            session_id="s1", user_message="how is the migration going?"
        )
    finally:
        holder.rollback()
        holder.close()

    assert isinstance(out, dict) and out["context"].startswith("[anansi appraisal]")
    assert pinned_env.state["caller"].calls == 1
    # The ok-row INSERT hit the held lock and degraded silently: zero rows.
    assert _telemetry_rows(pinned_env.db_path) == []


# ---------------------------------------------------------------------------
# Reflection hooks — full registered-hook-path rows (plan 03-02; the
# engine-level reflection rows live in test_reflection.py, see the table)
# ---------------------------------------------------------------------------


def test_on_session_end_no_db_no_ctx_returns_none(tmp_path, monkeypatch):
    """on_session_end with NO ctx and NO database: returns None, never
    raises; nothing is created on disk (no telemetry recordable)."""
    absent = tmp_path / "absent" / "state.db"
    monkeypatch.setattr(store, "get_db_path", lambda: absent)
    monkeypatch.setattr(config, "get_cfg", lambda force_reload=False: dict(_DEFAULTS))
    monkeypatch.setattr(anansi, "_ctx", None)

    assert anansi.on_session_end(session_id="s1") is None
    assert not absent.parent.exists()  # nothing created either


def test_on_session_end_exploding_llm_fails_open(pinned_env):
    """on_session_end with a captured turn pending and a reflection LLM that
    raises: returns None, telemetry records reflect_llm_error."""
    from anansi import reflection

    assert reflection.record_turn(
        session_id="s1", turn_id="t1",
        user_message="topic under discussion",
        assistant_response="a completed reply",
    ) is True
    pinned_env.state["caller"] = _CountingCaller(
        RuntimeError("reflection provider down")
    )

    assert anansi.on_session_end(session_id="s1") is None
    assert pinned_env.state["caller"].calls == 1  # the attempt happened
    assert _telemetry_rows(pinned_env.db_path)[-1] == ("reflect_llm_error",)


def test_post_llm_call_locked_db_returns_none(pinned_env, monkeypatch):
    """post_llm_call capture against a write-locked DB: returns None, never
    raises; the blocked turn_log INSERT degrades silently."""
    monkeypatch.setattr(store, "_DEFAULT_BUSY_TIMEOUT_MS", 100)
    holder = sqlite3.connect(str(pinned_env.db_path))
    try:
        holder.execute("BEGIN EXCLUSIVE")
        out = anansi.post_llm_call(
            session_id="s1", turn_id="t1",
            user_message="msg", assistant_response="resp",
        )
    finally:
        holder.rollback()
        holder.close()

    assert out is None
    con = sqlite3.connect(f"file:{pinned_env.db_path}?mode=ro", uri=True)
    try:
        count = con.execute("SELECT COUNT(*) FROM turn_log").fetchone()[0]
    finally:
        con.close()
    assert count == 0  # no partial capture landed
