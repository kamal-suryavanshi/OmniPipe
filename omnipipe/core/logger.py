import os
import time
import logging

# ------------------------------------------------------------------
# Session-unique log file: ~/omnipipe/logs/YYMM/pipelog_DD_HHMMSS.log
# e.g.  ~/omnipipe/logs/2603/pipelog_26_194506.log
# A fresh file is created per-process, so logs are NEVER overwritten.
# ------------------------------------------------------------------

def _build_log_path() -> str:
    """Computes the unique log file path for the current process startup time."""
    now = time.localtime()
    folder   = time.strftime("%y%m", now)              # e.g. "2603"
    filename = time.strftime("pipelog_%d_%H%M%S.log", now)  # e.g. "pipelog_26_194506.log"
    log_dir  = os.path.join(os.path.expanduser("~"), "omnipipe", "logs", folder)
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, filename)


# Each process gets exactly one log file path, computed once at import time
_SESSION_LOG_PATH: str = _build_log_path()

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | [%(module)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_logger(name: str = "omnipipe", level: int = logging.DEBUG) -> logging.Logger:
    """
    Returns (or creates) a named Logger that writes to:
      - stdout  (INFO and above)
      - session log file  (DEBUG and above, never overwritten)
    """
    logger = logging.getLogger(name)

    # Guard against duplicate handlers when the module is re-imported in the same process
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # ── Console handler (INFO+) ──────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(_FORMATTER)
    logger.addHandler(ch)

    # ── File handler (DEBUG+, append so sub-loggers all share the file) ─
    fh = logging.FileHandler(_SESSION_LOG_PATH, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_FORMATTER)
    logger.addHandler(fh)

    logger.debug("Logger initialised → %s", _SESSION_LOG_PATH)
    return logger


# Global singleton for convenience import across the codebase
logger: logging.Logger = setup_logger()
