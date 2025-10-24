import time
from threading import RLock

from app.services.cache import get_cache

from .config import settings


_seen = {}
_lock = RLock()


def check_and_store(key: str) -> bool:
    """
    Returns True if new; False if duplicate.
    Uses Redis SETNX + EXPIRE when available; falls back to in-mem dict.
    """
    ttl_sec = getattr(settings, "IDMP_TTL_SECONDS", 600)

    # Try Redis first
    cache = get_cache()
    if cache.available:
        try:
            created = cache.set_if_not_exists(f"idemp:{key}", "1", ttl=ttl_sec)
            return bool(created)
        except Exception:
            pass  # fall through to in-memory

    # In-memory fallback
    now = time.time()
    with _lock:
        # TTL purge
        for k, (ts, _) in list(_seen.items()):
            if now - ts > ttl_sec:
                _seen.pop(k, None)

        if key in _seen:
            return False

        _seen[key] = (now, 1)
        return True
