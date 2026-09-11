"""anansi config — kill switch + appraisal tuning (APPR-06/07).

Reads ``plugins.entries.anansi`` from the host config via a lazy
``hermes_cli.config.load_config`` import. On ANY failure (host absent,
config unreadable, malformed entry) every key falls back to its default —
get_cfg() never raises. The result is cached in a module global and reset
per session (on_session_start calls reset_cache(); long-lived gateway
processes serve many sessions — PITFALLS G6).

Plugin-own keys (read from the entry dict):
    enabled               bool, default True   — kill switch (APPR-07);
                          also gates reflection (checked in maybe_reflect)
    confidence_threshold  float, clamped [0,1], default 0.6 (APPR-03)
    deadline_seconds      float, clamped [0.5, 10.0], default 8.0 (R1)
    history_chars         int, default 4000
    max_tokens            int, default 700

Reflection keys (REFL-01, Phase 3):
    reflection_enabled        bool, default True — reflection-only switch
    reflect_every_n_turns     int, clamped [1, 50], default 5 — debounce
    reflect_max_tokens        int, default 700
    reflect_deadline_seconds  float, clamped [0.5, 10.0], default 8.0

Drive keys (DRIVE-06, Phase 7):
    drive_enabled             bool, default True — the SEPARATE drive kill
                              switch. Independent of `enabled`: when False the
                              appraisal still runs unchanged, but no goal-aware
                              fields are injected and no goal lines render
                              (drive off ⇒ goal fields vanish, appraisal
                              otherwise identical). Never gates the whole hook.
    drive_domains             list[str], default [] — the domain WHITELIST
                              (containment control 2 of 3). When NON-empty the
                              drive surfaces ONLY goals whose `domain` is in the
                              list; goals with an unlisted domain (or no domain)
                              are suppressed from goal-aware fields. The DEFAULT
                              [] means NO restriction — every goal surfaces, so
                              07-01..03 behaviour is unchanged out of the box.
                              Coerced via _coerce_str_list: a non-list value, or
                              junk members, fall back to clean stripped strings
                              (or []); never raises.
    drive_energy_budget       int, default 3, floor 0 — the per-turn energy /
                              attention budget (containment control 3 of 3): a
                              hard cap on how many NON-flagged drive lines
                              (`- drive want:` / `- drive note:`) surface per
                              turn. A FLAGGED-priority want is EXEMPT — it is
                              never dropped to satisfy the budget (DRIVE-05 takes
                              precedence over DRIVE-06; never-omit beats the
                              budget). Coerced via _coerce_int with a 0 floor; a
                              non-int value falls back to the default.
    drive_pressure            str, default "standard" — how firm the drive may
                              become; vocabulary is "quiet"|"standard"|"firm"
                              ONLY (code-red is EXCLUDED from Phase 7 — it remains
                              heartbeat/interruption planning). An invalid value
                              coerces to "standard"; never raises.

Requested model (host trust gate — we only read WHICH model to request;
allow_model_override / allowed_models are enforced by the host):
    plugins.entries.anansi.llm.model

Cheap-tier recommendations — documented only, NEVER auto-applied; the user
opts in by configuring the trust gate themselves:
    anthropic: claude-haiku-4-5
    openai:    gpt-4o-mini
    gemini:    gemini-2.5-flash
"""

import logging

logger = logging.getLogger("hermes.plugins.anansi.config")

DEFAULT_ENABLED = True
DEFAULT_CONFIDENCE_THRESHOLD = 0.6
DEFAULT_DEADLINE_SECONDS = 8.0
DEFAULT_HISTORY_CHARS = 4000
DEFAULT_MODEL = None  # no override requested by default
DEFAULT_MAX_TOKENS = 700
DEFAULT_REFLECTION_ENABLED = True
DEFAULT_REFLECT_EVERY_N_TURNS = 5
DEFAULT_REFLECT_MAX_TOKENS = 700
DEFAULT_REFLECT_DEADLINE_SECONDS = 8.0
DEFAULT_DRIVE_ENABLED = True
# DRIVE-06 containment controls 2 & 3 + pressure (Phase 7).
# Empty whitelist ⇒ NO domain restriction (07-01..03 behaviour unchanged).
DEFAULT_DRIVE_DOMAINS = []
# A generous per-turn cap that does not clip normal output (top-3 per category
# is the prior ceiling); tune lower via config to tighten the drive. Floor 0.
DEFAULT_DRIVE_ENERGY_BUDGET = 3
# quiet|standard|firm only — code-red is excluded from Phase 7.
DEFAULT_DRIVE_PRESSURE = "standard"
_DRIVE_PRESSURE_CHOICES = frozenset({"quiet", "standard", "firm"})

_cache = None
_last_degradations = []
_MISSING = object()
_BOOL_TOKENS = ("true", "yes", "on", "1", "false", "no", "off", "0")


def _load_host_entry():
    """Return the plugins.entries.anansi dict, or None.

    Lazy host import — keeps this module importable outside the host.
    Never raises.
    """
    try:
        from hermes_cli.config import load_config

        config = load_config() or {}
        plugins = config.get("plugins")
        if not isinstance(plugins, dict):
            return None
        entries = plugins.get("entries")
        if not isinstance(entries, dict):
            return None
        entry = entries.get("anansi")
        return entry if isinstance(entry, dict) else None
    except Exception as exc:
        logger.debug("anansi config unavailable, using defaults: %s", exc)
        return None


def _coerce_bool(value, default):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "yes", "on", "1"):
            return True
        if lowered in ("false", "no", "off", "0"):
            return False
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _coerce_float(value, default, lo, hi):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result:  # NaN
        return default
    return max(lo, min(hi, result))


def _coerce_int(value, default, lo, hi=None):
    try:
        result = int(value)
    except (TypeError, ValueError):
        return default
    result = max(lo, result)
    return min(hi, result) if hi is not None else result


def _coerce_str_list(value, default):
    """Coerce a config value to a list of clean domain strings (DRIVE-06).

    A non-list value (or None) falls back to ``default``. Otherwise each member
    is coerced to a stripped string; empty/whitespace-only members and any
    member that cannot be stringified are dropped. Never raises — a malformed
    whitelist degrades to the surviving clean strings (possibly []), so the
    drive stays contained, never crashes.
    """
    if not isinstance(value, list):
        return list(default)
    result = []
    for member in value:
        try:
            text = str(member).strip()
        except Exception:
            continue
        if text:
            result.append(text)
    return result


def _coerce_choice(value, default, choices):
    """Coerce a config value to one of an allowed vocabulary set (DRIVE-06).

    A non-string, or any value outside ``choices``, falls back to ``default``.
    Comparison is case-insensitive on a stripped string. Never raises.
    """
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in choices:
            return lowered
    return default


def _value_shape(raw):
    """Return a secret-safe shape for a rejected config value. Never raises."""
    try:
        if isinstance(raw, bool):
            return "<bool>"
        if isinstance(raw, str):
            return "<str len=%d>" % len(raw)
        if isinstance(raw, (int, float)):
            return "<%s>" % type(raw).__name__
        if isinstance(raw, (list, tuple, dict)):
            return "<%s len=%d>" % (type(raw).__name__, len(raw))
        if raw is None:
            return "<none>"
        return "<%s>" % type(raw).__name__
    except Exception:
        return "<unknown>"


def _bool_honored(raw):
    """Whether a provided value is accepted by _coerce_bool unchanged enough."""
    return (
        isinstance(raw, (bool, int, float))
        or (isinstance(raw, str) and raw.strip().lower() in _BOOL_TOKENS)
    )


def _number_degraded(raw, effective):
    """Whether numeric coercion rejected or clamped a provided value."""
    try:
        number = float(raw)
        return number != number or number != float(effective)
    except (TypeError, ValueError):
        return True


def _str_list_honored(raw):
    """Whether every list member survives _coerce_str_list."""
    if not isinstance(raw, list):
        return False
    try:
        return all(str(member).strip() for member in raw)
    except Exception:
        return False


def _applied_value(value):
    """Return a descriptor-safe representation of an effective config value."""
    if isinstance(value, (list, tuple, dict)):
        return _value_shape(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return _value_shape(value)


def _config_degradations(entry, effective):
    """Return secret-safe (key, rejected-shape, applied-effective) records.

    This works from a single load's local entry and effective values. Raw values
    never reach module state, telemetry, or callers.
    """
    out = []

    def add(key, raw):
        out.append((key, _value_shape(raw), _applied_value(effective.get(key))))

    try:
        for key in ("enabled", "reflection_enabled", "drive_enabled"):
            raw = entry.get(key, _MISSING)
            if raw is not _MISSING and not _bool_honored(raw):
                add(key, raw)

        for key in (
            "confidence_threshold", "deadline_seconds", "history_chars",
            "max_tokens", "reflect_every_n_turns", "reflect_max_tokens",
            "reflect_deadline_seconds", "drive_energy_budget",
        ):
            raw = entry.get(key, _MISSING)
            if raw is not _MISSING and _number_degraded(raw, effective.get(key)):
                add(key, raw)

        raw = entry.get("drive_domains", _MISSING)
        if raw is not _MISSING and not _str_list_honored(raw):
            add("drive_domains", raw)

        raw = entry.get("drive_pressure", _MISSING)
        if raw is not _MISSING and not (
            isinstance(raw, str) and raw.strip().lower() in _DRIVE_PRESSURE_CHOICES
        ):
            add("drive_pressure", raw)

        llm_cfg = entry.get("llm", _MISSING)
        if isinstance(llm_cfg, dict):
            raw = llm_cfg.get("model", _MISSING)
            if raw is not _MISSING and not (
                isinstance(raw, str) and bool(raw.strip())
            ):
                add("model", raw)
    except Exception:
        return out
    return out


def get_degradations():
    """Return secret-safe records from the most recent config load."""
    return list(_last_degradations)


def get_cfg(force_reload=False) -> dict:
    """Return the effective config dict (cached). Never raises."""
    global _cache, _last_degradations
    if _cache is not None and not force_reload:
        return _cache
    entry = _load_host_entry() or {}
    if not isinstance(entry, dict):
        entry = {}
    llm_cfg = entry.get("llm")
    if not isinstance(llm_cfg, dict):
        llm_cfg = {}
    model = llm_cfg.get("model")
    model = model.strip() if isinstance(model, str) and model.strip() else None
    _cache = {
        "enabled": _coerce_bool(entry.get("enabled"), DEFAULT_ENABLED),
        "confidence_threshold": _coerce_float(
            entry.get("confidence_threshold"),
            DEFAULT_CONFIDENCE_THRESHOLD, 0.0, 1.0,
        ),
        "deadline_seconds": _coerce_float(
            entry.get("deadline_seconds"), DEFAULT_DEADLINE_SECONDS, 0.5, 10.0
        ),
        "history_chars": _coerce_int(
            entry.get("history_chars"), DEFAULT_HISTORY_CHARS, 0
        ),
        "model": model,
        "max_tokens": _coerce_int(entry.get("max_tokens"), DEFAULT_MAX_TOKENS, 1),
        "reflection_enabled": _coerce_bool(
            entry.get("reflection_enabled"), DEFAULT_REFLECTION_ENABLED
        ),
        "reflect_every_n_turns": _coerce_int(
            entry.get("reflect_every_n_turns"),
            DEFAULT_REFLECT_EVERY_N_TURNS, 1, 50,
        ),
        "reflect_max_tokens": _coerce_int(
            entry.get("reflect_max_tokens"), DEFAULT_REFLECT_MAX_TOKENS, 1
        ),
        "reflect_deadline_seconds": _coerce_float(
            entry.get("reflect_deadline_seconds"),
            DEFAULT_REFLECT_DEADLINE_SECONDS, 0.5, 10.0,
        ),
        "drive_enabled": _coerce_bool(
            entry.get("drive_enabled"), DEFAULT_DRIVE_ENABLED
        ),
        "drive_domains": _coerce_str_list(
            entry.get("drive_domains"), DEFAULT_DRIVE_DOMAINS
        ),
        "drive_energy_budget": _coerce_int(
            entry.get("drive_energy_budget"), DEFAULT_DRIVE_ENERGY_BUDGET, 0
        ),
        "drive_pressure": _coerce_choice(
            entry.get("drive_pressure"), DEFAULT_DRIVE_PRESSURE,
            _DRIVE_PRESSURE_CHOICES,
        ),
    }
    _last_degradations = _config_degradations(entry, _cache)
    return _cache


def reset_cache() -> None:
    """Clear the cached config (called from on_session_start)."""
    global _cache, _last_degradations
    _cache = None
    _last_degradations = []
