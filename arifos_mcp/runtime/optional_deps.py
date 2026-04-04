"""
Optional dependency shims for runtime protocol modules.

These fall back to in-process implementations when lightweight runtime extras
such as ``redis`` or ``aiofiles`` are unavailable in the current environment.
"""

from __future__ import annotations

import asyncio
import fnmatch
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import aiofiles as aiofiles  # type: ignore[no-redef]
except ImportError:

    class _AsyncFileWrapper:
        def __init__(self, path: str | Path, mode: str, *args: Any, **kwargs: Any) -> None:
            self._path = path
            self._mode = mode
            self._args = args
            self._kwargs = kwargs
            self._fp: Any = None

        async def __aenter__(self) -> "_AsyncFileWrapper":
            self._fp = await asyncio.to_thread(
                open, self._path, self._mode, *self._args, **self._kwargs
            )
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            if self._fp is not None:
                await asyncio.to_thread(self._fp.close)

        async def write(self, data: str) -> int:
            return await asyncio.to_thread(self._fp.write, data)

        async def read(self, *args: Any) -> str:
            return await asyncio.to_thread(self._fp.read, *args)

    class _AiofilesModule:
        @staticmethod
        def open(path: str | Path, mode: str = "r", *args: Any, **kwargs: Any) -> _AsyncFileWrapper:
            return _AsyncFileWrapper(path, mode, *args, **kwargs)

    aiofiles = _AiofilesModule()


try:
    import redis.asyncio as redis  # type: ignore[no-redef]
except ImportError:

    class InMemoryPubSub:
        def __init__(self, client: "InMemoryAsyncRedis") -> None:
            self._client = client
            self._patterns: set[str] = set()
            self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
            self._closed = False
            client._pubsubs.add(self)

        async def psubscribe(self, *patterns: str) -> None:
            self._patterns.update(patterns)

        async def unsubscribe(self) -> None:
            self._patterns.clear()
            self._closed = True
            self._client._pubsubs.discard(self)

        async def listen(self):
            while not self._closed:
                message = await self._queue.get()
                yield message

        def _accepts(self, channel: str) -> list[str]:
            return [pattern for pattern in self._patterns if fnmatch.fnmatch(channel, pattern)]

        async def _push(self, channel: str, data: Any) -> None:
            for pattern in self._accepts(channel):
                await self._queue.put(
                    {
                        "type": "pmessage",
                        "pattern": pattern,
                        "channel": channel,
                        "data": data,
                    }
                )

    class InMemoryPipeline:
        def __init__(self, client: "InMemoryAsyncRedis") -> None:
            self._client = client
            self._ops: list[tuple[str, tuple[Any, ...]]] = []

        def incr(self, key: str) -> "InMemoryPipeline":
            self._ops.append(("incr", (key,)))
            return self

        def expire(self, key: str, ttl: int) -> "InMemoryPipeline":
            self._ops.append(("expire", (key, ttl)))
            return self

        async def execute(self) -> list[Any]:
            results: list[Any] = []
            for name, args in self._ops:
                results.append(await getattr(self._client, name)(*args))
            self._ops.clear()
            return results

    class InMemoryAsyncRedis:
        def __init__(self, decode_responses: bool = True) -> None:
            self.decode_responses = decode_responses
            self._kv: dict[str, Any] = {}
            self._expiry: dict[str, float] = {}
            self._sets: defaultdict[str, set[Any]] = defaultdict(set)
            self._lists: defaultdict[str, list[Any]] = defaultdict(list)
            self._pubsubs: set[InMemoryPubSub] = set()

        def _purge_if_expired(self, key: str) -> None:
            expires_at = self._expiry.get(key)
            if expires_at is not None and expires_at <= time.time():
                self._kv.pop(key, None)
                self._expiry.pop(key, None)

        async def get(self, key: str) -> Any:
            self._purge_if_expired(key)
            return self._kv.get(key)

        async def setex(self, key: str, ttl: int, value: Any) -> bool:
            self._kv[key] = value
            self._expiry[key] = time.time() + ttl
            return True

        async def delete(self, key: str) -> int:
            existed = key in self._kv or key in self._sets or key in self._lists
            self._kv.pop(key, None)
            self._expiry.pop(key, None)
            self._sets.pop(key, None)
            self._lists.pop(key, None)
            return 1 if existed else 0

        async def keys(self, pattern: str) -> list[str]:
            keys = list(self._kv.keys()) + list(self._sets.keys()) + list(self._lists.keys())
            return [key for key in keys if fnmatch.fnmatch(key, pattern)]

        async def ttl(self, key: str) -> int:
            self._purge_if_expired(key)
            expires_at = self._expiry.get(key)
            if expires_at is None:
                return -1
            return max(0, int(expires_at - time.time()))

        def pipeline(self) -> InMemoryPipeline:
            return InMemoryPipeline(self)

        async def incr(self, key: str) -> int:
            self._purge_if_expired(key)
            current = int(self._kv.get(key, 0))
            current += 1
            self._kv[key] = current
            return current

        async def expire(self, key: str, ttl: int) -> bool:
            if key in self._kv:
                self._expiry[key] = time.time() + ttl
            return True

        async def publish(self, channel: str, data: Any) -> int:
            delivered = 0
            for pubsub in list(self._pubsubs):
                patterns = pubsub._accepts(channel)
                if patterns:
                    delivered += len(patterns)
                    await pubsub._push(channel, data)
            return delivered

        def pubsub(self) -> InMemoryPubSub:
            return InMemoryPubSub(self)

        async def sadd(self, key: str, value: Any) -> int:
            before = len(self._sets[key])
            self._sets[key].add(value)
            return 1 if len(self._sets[key]) > before else 0

        async def smembers(self, key: str) -> set[Any]:
            return set(self._sets.get(key, set()))

        async def rpush(self, key: str, value: Any) -> int:
            self._lists[key].append(value)
            return len(self._lists[key])

        async def lindex(self, key: str, index: int) -> Any:
            items = self._lists.get(key, [])
            try:
                return items[index]
            except IndexError:
                return None

        async def lrange(self, key: str, start: int, stop: int) -> list[Any]:
            items = self._lists.get(key, [])
            n = len(items)
            if start < 0:
                start = max(0, n + start)
            if stop < 0:
                stop = n + stop
            stop = min(stop, n - 1)
            if stop < start:
                return []
            return items[start : stop + 1]

        async def close(self) -> None:
            return None

    class _RedisClientNamespace:
        PubSub = InMemoryPubSub

    _REDIS_BY_URL: dict[str, InMemoryAsyncRedis] = {}

    class _RedisModule:
        Redis = InMemoryAsyncRedis
        client = _RedisClientNamespace

        @staticmethod
        def from_url(url: str, decode_responses: bool = True) -> InMemoryAsyncRedis:
            client = _REDIS_BY_URL.get(url)
            if client is None:
                client = InMemoryAsyncRedis(decode_responses=decode_responses)
                _REDIS_BY_URL[url] = client
            return client

    redis = _RedisModule()


__all__ = ["aiofiles", "redis", "InMemoryAsyncRedis", "InMemoryPubSub"]
