import time
import logging
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import RATE_LIMIT_PER_MINUTE

# 请求日志
logger = logging.getLogger("chuling")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

# 限流存储: { ip: [timestamp, ...] }
_rate_window: dict[str, list[float]] = defaultdict(list)


def _clean_window(ip: str, now: float) -> None:
    cutoff = now - 60
    _rate_window[ip] = [t for t in _rate_window[ip] if t > cutoff]


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            ip = request.client.host if request.client else "unknown"
            now = time.time()
            _clean_window(ip, now)

            if len(_rate_window[ip]) >= RATE_LIMIT_PER_MINUTE:
                return JSONResponse(status_code=429, content={"detail": "请求太频繁，请稍后再试"})

            _rate_window[ip].append(now)

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            "%s %s %d %.2fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response
