import functools
import hashlib
import json
import time
from typing import Optional
from collections import OrderedDict

from app.config import settings


class InMemoryCache:

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._store: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size

    def get(self, key: str):
        if key not in self._store:
            return None
        expires, value = self._store[key]
        if time.time() > expires:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: object, ttl: Optional[int] = None):
        expires = time.time() + (ttl or self.default_ttl)
        self._store[key] = (expires, value)
        self._store.move_to_end(key)
        if len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def clear(self):
        self._store.clear()


_cache = InMemoryCache()


def cache_result(ttl: int = 300):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not settings.cache_enabled:
                return await func(*args, **kwargs)

            key_data = {"func": func.__name__, "args": str(args), "kwargs": str(kwargs)}
            key = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

            cached = _cache.get(key)
            if cached is not None:
                return cached

            result = await func(*args, **kwargs)
            _cache.set(key, result, ttl=ttl)
            return result

        return wrapper
    return decorator
