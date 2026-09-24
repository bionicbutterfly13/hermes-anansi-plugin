"""Shared-worker regression contracts, with no provider or host installation."""

import sqlite3
import threading
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from types import SimpleNamespace

import pytest

import anansi
from anansi import appraisal, config, reflection, store


def _result():
    return SimpleNamespace(parsed={}, text="{}", model="fake", usage=None)


def _call(kind, llm, deadline=0.05):
    cfg = {"deadline_seconds": deadline, "reflect_deadline_seconds": deadline}
    if kind == "appraisal":
        return appraisal.run_appraisal(
            llm=llm, user_message="Review the database migration",
            conversation_history=[], snapshot=None, cfg=cfg,
        )
    return reflection.run_reflection(llm=llm, digest="Migration notes", cfg=cfg)


class BlockingLlm:
    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.calls = []

    def complete_structured(self, **kwargs):
        self.calls.append(kwargs["purpose"])
        self.started.set()
        if not self.release.wait(5):
            raise RuntimeError("test did not release its worker")
        return _result()


@pytest.fixture
def blocked():
    appraisal._reset_executor_for_tests()
    llm = BlockingLlm()
    yield llm
    # Cancel any pending work before release, including on a failing assertion.
    executor = appraisal._get_executor()
    executor.shutdown(wait=False, cancel_futures=True)
    llm.release.set()
    executor.shutdown(wait=True, cancel_futures=True)
    appraisal._reset_executor_for_tests()


@pytest.mark.parametrize("owner", ["appraisal", "reflection"])
@pytest.mark.parametrize("caller", ["appraisal", "reflection"])
def test_busy_worker_skips_without_queueing_and_recovers(blocked, owner, caller):
    first = _call(owner, blocked)
    assert first.outcome == ("timeout" if owner == "appraisal" else "reflect_timeout")
    assert blocked.started.is_set()
    expected = "skipped:worker_busy" if caller == "appraisal" else "reflect_skipped:worker_busy"
    # A normal 8-second budget must not cause another wait behind the owner.
    for _ in range(8):
        result = _call(caller, blocked, deadline=8)
        assert result.outcome == expected
        assert result.wall_ms < 500
        assert result.tokens_in == result.tokens_out == 0
    assert len(blocked.calls) == 1
    blocked.release.set()
    # Wait for the actual occupied future, without replacing the executor.
    executor = appraisal._get_executor()
    executor.submit(lambda: None).result(timeout=2)
    assert len(blocked.calls) == 1
    recovered = _call(caller, blocked, deadline=1)
    assert recovered.outcome == ("ok" if caller == "appraisal" else "reflect_ok")
    assert len(blocked.calls) == 2


def test_concurrent_appraisal_and_reflection_admission_is_atomic(blocked):
    barrier = threading.Barrier(12)
    results = []

    def attempt(index):
        barrier.wait(timeout=3)
        results.append(_call("appraisal" if index % 2 else "reflection", blocked, 0.2))

    threads = [threading.Thread(target=attempt, args=(i,)) for i in range(12)]
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=3)
        assert all(not thread.is_alive() for thread in threads)
        assert len(results) == 12
        assert sum(r.outcome in {"timeout", "reflect_timeout"} for r in results) == 1
        assert sum(r.outcome in {"skipped:worker_busy", "reflect_skipped:worker_busy"}
                   for r in results) == 11
        assert len(blocked.calls) == 1
    finally:
        blocked.release.set()
        for thread in threads:
            thread.join(timeout=3)


@pytest.mark.parametrize("kind", ["appraisal", "reflection"])
def test_expired_pending_future_is_cancelled_before_worker_frees(monkeypatch, kind):
    """Simulate an executor occupied before the admitted wrapper can start."""
    appraisal._reset_executor_for_tests()
    executor = ThreadPoolExecutor(max_workers=1)
    release = threading.Event()
    started = threading.Event()
    calls = []

    def occupy():
        started.set()
        release.wait(5)

    executor.submit(occupy)
    assert started.wait(2)
    submitted = []

    class RecordingExecutor:
        def submit(self, fn):
            future = executor.submit(fn)
            submitted.append(future)
            return future

    monkeypatch.setattr(appraisal, "_get_executor", lambda: RecordingExecutor())
    llm = SimpleNamespace(complete_structured=lambda **kw: calls.append(kw) or _result())
    try:
        result = _call(kind, llm)
        assert result.outcome == ("timeout" if kind == "appraisal" else "reflect_timeout")
        assert submitted[0].cancelled()
        release.set()
        executor.submit(lambda: None).result(timeout=2)
        assert calls == []
        assert _call(kind, llm, 1).outcome == ("ok" if kind == "appraisal" else "reflect_ok")
        assert len(calls) == 1
    finally:
        release.set()
        executor.shutdown(wait=True, cancel_futures=True)
        appraisal._reset_executor_for_tests()


@pytest.mark.parametrize("kind", ["appraisal", "reflection"])
def test_expired_wrapper_never_calls_model_when_cancel_loses_start_race(monkeypatch, kind):
    """Future is RUNNING, but its wrapper has not yet entered the model call."""
    appraisal._reset_executor_for_tests()
    calls = []

    class PausedExecutor:
        def submit(self, fn):
            self.fn = fn
            self.future = Future()
            assert self.future.set_running_or_notify_cancel()
            return self.future

    executor = PausedExecutor()
    monkeypatch.setattr(appraisal, "_get_executor", lambda: executor)
    llm = SimpleNamespace(complete_structured=lambda **kw: calls.append(kw) or _result())
    try:
        result = _call(kind, llm)
        assert result.outcome == ("timeout" if kind == "appraisal" else "reflect_timeout")
        assert not executor.future.cancelled()
        with pytest.raises(TimeoutError):
            executor.fn()
        assert calls == []
    finally:
        executor.future.set_result(None)
        appraisal._reset_executor_for_tests()


@pytest.mark.parametrize("kind", ["appraisal", "reflection"])
def test_submission_failure_does_not_poison_admission(monkeypatch, blocked, kind):
    executor = appraisal._get_executor()

    class FailOnce:
        failed = False

        def submit(self, fn):
            if not self.failed:
                self.failed = True
                raise RuntimeError("synthetic submission failure")
            return executor.submit(fn)

    replacement = FailOnce()
    with monkeypatch.context() as patch:
        patch.setattr(appraisal, "_get_executor", lambda: replacement)
        first = _call(kind, blocked)
        assert first.outcome == ("llm_error" if kind == "appraisal" else "reflect_llm_error")
        blocked.release.set()
        second = _call(kind, blocked, 1)
        assert second.outcome == ("ok" if kind == "appraisal" else "reflect_ok")


@pytest.mark.parametrize("kind", ["appraisal", "reflection"])
def test_model_exception_releases_worker_for_next_request(blocked, kind):
    attempts = []

    def fail_once(**kwargs):
        attempts.append(kwargs)
        if len(attempts) == 1:
            raise RuntimeError("synthetic model failure")
        return _result()

    llm = SimpleNamespace(complete_structured=fail_once)
    assert _call(kind, llm, 1).outcome == ("llm_error" if kind == "appraisal" else "reflect_llm_error")
    assert _call(kind, llm, 1).outcome == ("ok" if kind == "appraisal" else "reflect_ok")
    assert len(attempts) == 2


def test_busy_hook_and_reflection_record_skips_without_losing_turns(blocked, tmp_path, monkeypatch):
    db_path = tmp_path / "anansi" / "state.db"
    assert store.ensure_db(db_path)
    monkeypatch.setattr(store, "get_db_path", lambda: db_path)
    monkeypatch.setattr(config, "get_cfg", lambda: {"deadline_seconds": 8})
    monkeypatch.setattr(anansi, "_ctx", SimpleNamespace(llm=blocked))
    monkeypatch.setattr(anansi, "_session_state", {"session_id": None, "last_msg_norm": None})
    assert reflection.record_turn(
        session_id="before", turn_id="1", user_message="Migration notes",
        assistant_response="Database checks passed", db_path=db_path,
    )
    assert _call("appraisal", blocked).outcome == "timeout"
    assert anansi.pre_llm_call(
        session_id="busy", user_message="Review the database migration", conversation_history=[]
    ) is None
    snapshot = store.read_snapshot(db_path)
    assert reflection.maybe_reflect(llm=blocked, session_id="busy", cfg={}, db_path=db_path) == "reflect_skipped:worker_busy"
    assert store.read_snapshot(db_path) == snapshot
    assert store.get_meta("last_reflected_turn_log_id", db_path=db_path) is None
    assert len(store.read_turns_since(0, db_path=db_path)) == 1
    assert store.get_meta("last_seen_session_id", db_path=db_path) == "busy"
    with sqlite3.connect(db_path) as conn:
        outcomes = [row[0] for row in conn.execute("SELECT outcome FROM telemetry ORDER BY id")]
    assert outcomes == ["skipped:worker_busy", "reflect_skipped:worker_busy"]
    assert store.telemetry_summary(db_path)["failure_count"] == 0
    blocked.release.set()
    appraisal._get_executor().submit(lambda: None).result(timeout=2)
    assert len(blocked.calls) == 1
    # Preserve the existing consumed-session trigger: retry at the next session.
    assert reflection.maybe_reflect(llm=blocked, session_id="next", cfg={}, db_path=db_path) == "reflect_ok"
    assert int(store.get_meta("last_reflected_turn_log_id", db_path=db_path)) > 0
