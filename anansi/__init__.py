"""Anansi — metacognitive appraisal plugin for hermes-agent.

Observational per-turn appraisal with zero autonomy. Phase 2: pre_llm_call
runs one deadline-bounded JSON appraisal via ctx.llm and injects a compact
sanitized block. Phase 3: post_llm_call captures the completed turn and
on_session_end / on_session_start route through reflection.maybe_reflect —
the debounced, idempotent pass that carries appraisal context across the
one-turn lag (REFL-01..05; hooks stay thin, reflection.py does the work).

Hard rules for this module (see .planning/research/ARCHITECTURE.md):
- Zero import-time side effects: no DB, no config reads, no host imports
  at module top level. Only stdlib functools/logging/os are imported here;
  store/config/appraisal/render are imported lazily inside functions.
- Every hook accepts the documented kwargs PLUS **kwargs (the dispatcher
  injects extras such as telemetry_schema_version).
- Every hook is wrapped in the fail-open guard and returns None on any
  failure. Anansi hooks must never raise into the dispatcher.
"""

import functools
import logging
import os

logger = logging.getLogger("hermes.plugins.anansi")

# Host plugin context, stashed at register() time. None until register() runs.
_ctx = None

# Per-session throttle state (G6: long-lived gateway processes — reset on
# session rollover in on_session_start and in pre_llm_call's guard).
_session_state = {"session_id": None, "last_msg_norm": None}


def _filter_goals_by_domain(goals, drive_domains):
    """DRIVE-06 containment: keep only goals whose ``domain`` is in the
    whitelist when the whitelist is NON-empty; an empty whitelist means NO
    restriction (07-01..03 behaviour unchanged). Fail-open: any failure
    returns the UNFILTERED goals (a filter bug must never crash the hook or
    silently drop everything)."""
    try:
        if not goals or not drive_domains:
            return goals
        allowed = {str(d).strip() for d in drive_domains if str(d).strip()}
        if not allowed:
            return goals
        kept = [
            g for g in goals
            if isinstance(g, dict) and str(g.get("domain") or "").strip() in allowed
        ]
        return kept
    except Exception:
        return goals


def _filter_signals_by_goals(goal_signals, goals, drive_domains):
    """DRIVE-06 containment: when the domain whitelist is ACTIVE, drop any model
    ``goal_signals`` that do not relate to a surviving (whitelisted) persisted
    goal. This stops an off-domain goal the model echoed from leaking into the
    surfaced goal-aware fields even though it was filtered out of the appraisal
    context. An EMPTY whitelist leaves the signals untouched (07-01..03
    behaviour unchanged). Fail-open: any failure returns the unfiltered signals.
    """
    try:
        if not drive_domains or not goal_signals:
            return goal_signals
        texts = [
            str(g.get("text") or "").strip().lower()
            for g in (goals or [])
            if isinstance(g, dict) and str(g.get("text") or "").strip()
        ]
        if not texts:
            return []  # whitelist active but no whitelisted goal -> none surface
        kept = []
        for sig in goal_signals:
            if not isinstance(sig, dict):
                continue
            relates = str(sig.get("relates_to_goal") or "").strip().lower()
            if relates and any(relates in t or t in relates for t in texts):
                kept.append(sig)
        return kept
    except Exception:
        return goal_signals


def _fail_open(fn):
    """Wrap a hook so any exception is logged and swallowed (returns None).

    Telemetry stub fulfilled: raised paths record an llm_error row, inside
    a nested guard so a telemetry failure can never resurrect the exception.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            logger.warning(
                "anansi hook %s failed (fail-open): %s",
                fn.__name__,
                exc,
                exc_info=True,
            )
            try:
                from . import store

                store.record_telemetry(
                    "llm_error", error=(fn.__name__ + ": " + str(exc))[:300]
                )
            except Exception:
                pass
            return None

    return wrapper


@_fail_open
def on_session_start(session_id="", platform="", **kwargs):
    """Verify state-store availability, reset per-session caches, and run
    the session-change reflection trigger.

    maybe_reflect here runs BEFORE the new session's first appraisal — the
    ordering that lands cross-session surfacing on turn 1 of session B
    (ROADMAP criterion 3). Double-triggering with on_session_end is
    harmless BY DESIGN (the watermark makes the second fire a no-op).
    Latency: at most one reflect deadline once per session boundary —
    accepted (03-CONTEXT cost decision).
    """
    logger.debug("anansi on_session_start fired (session_id=%s)", session_id)
    from . import config, reflection, store  # lazy — zero import-time side effects

    _session_state["session_id"] = session_id or None
    _session_state["last_msg_norm"] = None
    config.reset_cache()

    if not store.ensure_db():
        logger.debug("anansi state store unavailable — continuing without state")

    llm = getattr(_ctx, "llm", None) if _ctx is not None else None
    reflection.maybe_reflect(llm=llm, session_id=session_id)
    return None


@_fail_open
def pre_llm_call(session_id="", task_id="", turn_id="", user_message="",
                 conversation_history=None, is_first_turn=False, model="",
                 platform="", sender_id="", **kwargs):
    """Run the appraisal pre-phase. Returns {"context": block} or None.

    Order is contractual (02-CONTEXT.md): kill switch -> session rollover ->
    throttle gates -> snapshot -> appraisal -> telemetry -> render/suppress.
    PLUG-04: user-message injection only.
    """
    logger.debug("anansi pre_llm_call fired (session_id=%s)", session_id)
    from . import appraisal, config, render, store  # lazy

    cfg = config.get_cfg()
    if not cfg.get("enabled", True):  # kill switch FIRST (APPR-07)
        store.record_telemetry("skipped:disabled", session_id=session_id)
        return None

    # The SEPARATE drive kill switch (DRIVE-06). Checked AFTER the appraisal
    # kill switch and does NOT early-return: appraisal still runs unchanged
    # when drive is off — only the goal-aware contribution is suppressed
    # (build_context omits the goals slice, render omits goal lines). The
    # skipped:drive_disabled telemetry row (a non-failure skipped:* prefix)
    # is recorded once per ELIGIBLE turn, below, where appraisal actually runs.
    drive_on = cfg.get("drive_enabled", True)

    if session_id != _session_state["session_id"]:  # session rollover guard
        _session_state["session_id"] = session_id
        _session_state["last_msg_norm"] = None

    reason = appraisal.should_skip(user_message, _session_state["last_msg_norm"])
    if reason:  # throttle gates (APPR-08)
        store.record_telemetry("skipped:" + reason, session_id=session_id)
        return None
    _session_state["last_msg_norm"] = appraisal.normalize_message(user_message)

    snapshot = store.read_snapshot()  # None is fine — message salience still applies

    if _ctx is None or getattr(_ctx, "llm", None) is None:
        store.record_telemetry("skipped:no_ctx", session_id=session_id)
        return None

    # DRIVE-06: once per ELIGIBLE turn, note the drive-off state as a
    # non-failure skipped:* row. goals stays None so build_context omits the
    # goals slice and render omits goal lines — appraisal otherwise unchanged.
    if drive_on:
        goals = (snapshot or {}).get("goals") or []
        # DRIVE-06 containment control 2: the domain WHITELIST. When
        # drive_domains is non-empty, only goals in a user-named domain reach
        # appraisal/render; an empty whitelist (the default) imposes no
        # restriction. Fail-open: a filter failure falls back to the unfiltered
        # goals rather than crashing or silently dropping a flagged priority.
        goals = _filter_goals_by_domain(goals, cfg.get("drive_domains") or [])
    else:
        goals = None
        store.record_telemetry("skipped:drive_disabled", session_id=session_id)

    result = appraisal.run_appraisal(
        llm=_ctx.llm,
        user_message=user_message,
        conversation_history=conversation_history or [],
        snapshot=snapshot,
        cfg=cfg,
        goals=goals,
    )

    store.record_telemetry(  # before returning; single quick INSERT, fail-open
        result.outcome,
        wall_ms=result.wall_ms,
        model=result.model,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        error=result.error,
        session_id=session_id,
    )

    if result.signals is None:
        return None
    # DRIVE-06: when the drive is off, suppress goal-aware fields at render
    # too — a faithful model returns no goal_signals (build_context omitted
    # the goals slice), but stripping here makes the drive-off block
    # byte-for-byte identical to a no-goals run regardless of model output.
    if not drive_on and result.signals.get("goal_signals"):
        result.signals["goal_signals"] = []
    # DRIVE-02: when drive is on, ground each goal_signal in the matching
    # persisted goal's READ-TIME momentum (stalled_days + any pressure
    # metadata) so the stalled signal is anchored to ground truth — render
    # then orders stalled goals first. Pure + fail-open; no-op when no goals.
    elif drive_on and result.signals.get("goal_signals"):
        # DRIVE-06: when the domain whitelist is active, drop any echoed
        # goal_signal that does not relate to a surviving (whitelisted)
        # persisted goal — an off-domain goal must not leak back through the
        # model's echo. No-op when the whitelist is empty (default).
        gsignals = _filter_signals_by_goals(
            result.signals["goal_signals"], goals, cfg.get("drive_domains") or []
        )
        result.signals["goal_signals"] = render.enrich_goal_signals(
            gsignals, goals
        )
    # snapshot rides along for REFL-05 trust hints (advisory only; empty-
    # signal suppression inside render_block still takes precedence).
    # DRIVE-05: the persisted goals (with flagged_priority) ride along too so a
    # user-flagged priority is NEVER silently omitted from the surfaced block
    # (it renders FIRST and outside the truncation pop range). goals is None
    # when drive is off, so the drive-off block stays byte-for-byte identical.
    # DRIVE-06 containment control 3: the per-turn ENERGY BUDGET caps how many
    # NON-flagged drive lines surface this turn. A flagged-priority want is
    # EXEMPT (never-omit, DRIVE-05 > DRIVE-06) — the cap is applied inside
    # render_block, after the protected flagged prefix is assembled, so a
    # flagged want is never dropped to satisfy the budget. None ⇒ no cap.
    energy_budget = cfg.get("drive_energy_budget") if drive_on else None
    pressure = cfg.get("drive_pressure") if drive_on else None
    block = render.render_block(
        result.signals, snapshot=snapshot, goals=goals,
        energy_budget=energy_budget, pressure=pressure,
    )
    if block is None:  # empty-signal suppression (APPR-05)
        return None

    dump_path = os.environ.get("ANANSI_DEBUG_DUMP")
    if dump_path:  # live-demo observability aid (Plan 02-02); off by default
        try:
            with open(dump_path, "a", encoding="utf-8") as fh:
                fh.write(block + "\n")
        except Exception:
            pass

    return {"context": block}


@_fail_open
def post_llm_call(session_id="", task_id="", turn_id="", user_message="",
                  assistant_response="", conversation_history=None, model="",
                  platform="", **kwargs):
    """Capture the completed turn for reflection (REFL-01 cheap bookkeeping).

    post_llm_call is the only hook carrying the assistant response (the
    host's on_session_end has no transcript — turn_finalizer.py:294/:415);
    it fires once per turn, only `if final_response and not interrupted`.
    Returns None always.
    """
    logger.debug("anansi post_llm_call fired (session_id=%s)", session_id)
    from . import reflection  # lazy

    reflection.record_turn(
        session_id=session_id,
        turn_id=turn_id,
        user_message=user_message,
        assistant_response=assistant_response,
    )
    return None


@_fail_open
def on_session_end(session_id="", task_id="", turn_id="", completed=False,
                   interrupted=False, model="", platform="", **kwargs):
    """Reflection trigger. Return value is ignored by the host.

    Fires per run_conversation (per turn), not per session — the debounce
    (session change OR every-N unreflected turns) lives in
    reflection.maybe_reflect, which never raises and records a reflect_*
    telemetry row per firing.
    """
    logger.debug("anansi on_session_end fired (session_id=%s)", session_id)
    from . import reflection  # lazy

    llm = getattr(_ctx, "llm", None) if _ctx is not None else None
    reflection.maybe_reflect(llm=llm, session_id=session_id)
    return None


def register(ctx):
    """Host entry point. Stash ctx and register the four lifecycle hooks.

    Nothing else happens here — no DB, no config, no I/O.
    """
    global _ctx
    _ctx = ctx
    ctx.register_hook("on_session_start", on_session_start)
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("post_llm_call", post_llm_call)
    ctx.register_hook("on_session_end", on_session_end)
