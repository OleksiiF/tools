import asyncio
import time
from collections import OrderedDict


class Cache:
    class _Cache(OrderedDict):
        def __init__(self, ttl, maxsize=128, *args, **kwargs):
            self.maxsize = maxsize
            self.ttl = ttl
            super().__init__(*args, **kwargs)

        def __getitem__(self, key):
            value = super().__getitem__(key)

            if time.time() - value[1] < self.ttl:
                self.move_to_end(key)
                return value[0]

            else:
                raise KeyError(key)

        def __setitem__(self, key, value):
            super().__setitem__(key, (value, time.time()))

            if len(self) > self.maxsize:
                oldest = next(iter(self))
                del self[oldest]

    def __init__(self, maxsize=128, ttl=1.0):
        self.cache = self._Cache(ttl=ttl, maxsize=maxsize)
        self.lock = asyncio.Lock()

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            key = hash(f"{args}{kwargs}")
            try:
                result = self.cache[key]

            except KeyError:
                async with self.lock:
                    result = (
                        await func(*args, **kwargs)
                        if asyncio.iscoroutine(func)
                        else func(*args, **kwargs)
                    )
                    self.cache[key] = result

            return result

        return wrapper
