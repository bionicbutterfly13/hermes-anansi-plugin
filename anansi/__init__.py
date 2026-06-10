"""anansi — metacognitive appraisal plugin for hermes-agent.

Observational per-turn appraisal with zero autonomy. Phase 1 skeleton:
register(ctx) plus three fail-open no-op lifecycle hooks. No LLM calls,
no injection, no state writes yet — those arrive in later phases.

Hard rules for this module (see .planning/research/ARCHITECTURE.md):
- Zero import-time side effects: no DB, no config reads, no host imports
  at module top level. Only stdlib functools/logging are imported here.
- Every hook accepts the documented kwargs PLUS **kwargs (the dispatcher
  injects extras such as telemetry_schema_version).
- Every hook is wrapped in the fail-open guard and returns None on any
  failure. A anansi hook must never raise into the dispatcher.
"""

import functools
import logging

logger = logging.getLogger("hermes.plugins.anansi")

# Host plugin context, stashed at register() time for later phases
# (ctx.llm appraisal calls land in Phase 2). None until register() runs.
_ctx = None


def _fail_open(fn):
    """Wrap a hook so any exception is logged and swallowed (returns None).

    This is the telemetry stub point — Phase 2 adds a telemetry row here.
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
            return None

    return wrapper


@_fail_open
def on_session_start(session_id="", platform="", **kwargs):
    """Phase 1: verify state-store availability, silent either way.

    Later: warm the state snapshot.
    """
    logger.debug("anansi on_session_start fired (session_id=%s)", session_id)
    from . import store  # lazy — preserves zero import-time side effects

    if not store.ensure_db():
        logger.debug("anansi state store unavailable — continuing without state")
    return None


@_fail_open
def pre_llm_call(session_id="", task_id="", turn_id="", user_message="",
                 conversation_history=None, is_first_turn=False, model="",
                 platform="", sender_id="", **kwargs):
    """No-op in Phase 1. Returns None = inject nothing.

    PLUG-04: the future return shape is {"context": block} or None.
    """
    logger.debug("anansi pre_llm_call fired (session_id=%s)", session_id)
    return None


@_fail_open
def on_session_end(session_id="", task_id="", turn_id="", completed=False,
                   interrupted=False, model="", platform="", **kwargs):
    """No-op in Phase 1. Return value is ignored by the host.

    Note: fires per run_conversation (per turn), not per session.
    """
    logger.debug("anansi on_session_end fired (session_id=%s)", session_id)
    return None


def register(ctx):
    """Host entry point. Stash ctx and register the three lifecycle hooks.

    Nothing else happens here — no DB, no config, no I/O.
    """
    global _ctx
    _ctx = ctx
    ctx.register_hook("on_session_start", on_session_start)
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("on_session_end", on_session_end)
