# Backend (FastAPI)
## `fastapi-backend/main.py`

**File:** `fastapi-backend/main.py`

**Summary:** Source file `fastapi-backend/main.py`.

### `startup_event`

- **File:** `fastapi-backend/main.py`
- **Lines:** `36-58`
- **Signature:** `async def startup_event():`
- **Purpose:** Ensure the RAG knowledge base and FAISS index are up-to-date on startup.

**Code:**
```python
async def startup_event():
    """Ensure the RAG knowledge base and FAISS index are up-to-date on startup.

    The build/load runs in a thread pool so heavy model imports do not block the
    Uvicorn event loop, and failures are logged as warnings instead of crashing
    the application.
    """
    from app.services.rag_pipeline import ensure_index_built
    logger = logging.getLogger(__name__)

    if not settings.enable_rag:
        logger.info("RAG is disabled via settings.")
        return

    if settings.rag_backend == "pgvector":
        logger.info("RAG_BACKEND=pgvector; FAISS index is not built at startup.")
        return

    try:
        await asyncio.to_thread(ensure_index_built)
        logger.info("RAG index ready on startup.")
    except Exception as exc:
        logger.warning("RAG index build failed on startup: %s", exc, exc_info=settings.debug)
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `getLogger()`, `info()`, `to_thread()`, `warning()`.

### `root`

- **File:** `fastapi-backend/main.py`
- **Lines:** `62-63`
- **Signature:** `async def root():`
- **Purpose:** Handles root.

**Code:**
```python
async def root():
    return {"status": "ok", "service": settings.app_name}
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation.


## `fastapi-backend/app/__init__.py`

**File:** `fastapi-backend/app/__init__.py`

**Summary:** Source file `fastapi-backend/app/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/auth/__init__.py`

**File:** `fastapi-backend/app/auth/__init__.py`

**Summary:** Source file `fastapi-backend/app/auth/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/auth/jwt.py`

**File:** `fastapi-backend/app/auth/jwt.py`

**Summary:** Source file `fastapi-backend/app/auth/jwt.py`.

### `verify_jwt`

- **File:** `fastapi-backend/app/auth/jwt.py`
- **Lines:** `6-17`
- **Signature:** `def verify_jwt(token: str) -> dict:`
- **Purpose:** Verifies jwt.

**Code:**
```python
def verify_jwt(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
```

**Explanation:** It accepts `token` and returns `dict`. See the code below for the full implementation. Key calls include `get_settings()`, `decode()`, `ValueError()`.


## `fastapi-backend/app/config/__init__.py`

**File:** `fastapi-backend/app/config/__init__.py`

**Summary:** Source file `fastapi-backend/app/config/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/config/settings.py`

**File:** `fastapi-backend/app/config/settings.py`

**Summary:** Source file `fastapi-backend/app/config/settings.py`.

### `Settings.parse_cors_origins`

- **File:** `fastapi-backend/app/config/settings.py`
- **Lines:** `108-113`
- **Signature:** `def parse_cors_origins(cls, value):`
- **Purpose:** Method of `Settings` that parses cors origins.

**Code:**
```python
def parse_cors_origins(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str) and value.strip():
            return json.loads(value)
        return ["http://localhost:5173"]
```

**Explanation:** It accepts `cls`, `value`. See the code below for the full implementation. Key calls include `isinstance()`, `strip()`, `loads()`.

### `Settings.parse_cors_origin_regex`

- **File:** `fastapi-backend/app/config/settings.py`
- **Lines:** `117-122`
- **Signature:** `def parse_cors_origin_regex(cls, value):`
- **Purpose:** Method of `Settings` that parses cors origin regex.

**Code:**
```python
def parse_cors_origin_regex(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value:
                return value
        return _DEFAULT_CORS_ORIGIN_REGEX
```

**Explanation:** It accepts `cls`, `value`. See the code below for the full implementation. Key calls include `isinstance()`, `strip()`.

### `get_settings`

- **File:** `fastapi-backend/app/config/settings.py`
- **Lines:** `126-128`
- **Signature:** `def get_settings() -> Settings:`
- **Purpose:** Retrieves settings.

**Code:**
```python
def get_settings() -> Settings:
    logger.info("Settings env file path: %s", ENV_FILE)
    return Settings()
```

**Explanation:** It accepts zero arguments and returns `Settings`. See the code below for the full implementation. Key calls include `info()`, `Settings()`.


## `fastapi-backend/app/dependencies/__init__.py`

**File:** `fastapi-backend/app/dependencies/__init__.py`

**Summary:** Source file `fastapi-backend/app/dependencies/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/dependencies/auth.py`

**File:** `fastapi-backend/app/dependencies/auth.py`

**Summary:** Source file `fastapi-backend/app/dependencies/auth.py`.

### `get_bearer_token`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `10-17`
- **Signature:** `def get_bearer_token(request: Request) -> str:`
- **Purpose:** Retrieves bearer token.

**Code:**
```python
def get_bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization")
    if not header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return parts[1]
```

**Explanation:** It accepts `request` and returns `str`. See the code below for the full implementation. Key calls include `get()`, `HTTPException()`, `split()`, `len()`, `lower()`.

### `_extract_user_data`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `20-27`
- **Signature:** `def _extract_user_data(user_response):`
- **Purpose:** Extract user dict from Supabase auth.get_user response.

**Code:**
```python
def _extract_user_data(user_response):
    """Extract user dict from Supabase auth.get_user response."""
    user_data = getattr(user_response, "user", None)
    if not user_data and hasattr(user_response, "data"):
        user_data = user_response.data
    if isinstance(user_data, dict) and "user" in user_data:
        user_data = user_data["user"]
    return user_data
```

**Explanation:** It accepts `user_response`. See the code below for the full implementation. Key calls include `getattr()`, `hasattr()`, `isinstance()`.

### `_build_user_claims`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `30-45`
- **Signature:** `def _build_user_claims(user_data) -> dict:`
- **Purpose:** Build a claims dict from Supabase User object or dict.

**Code:**
```python
def _build_user_claims(user_data) -> dict:
    """Build a claims dict from Supabase User object or dict."""
    if isinstance(user_data, dict):
        return {
            "sub": user_data.get("id"),
            "email": user_data.get("email"),
            "email_confirmed_at": user_data.get("email_confirmed_at") or user_data.get("confirmed_at"),
            "user_metadata": user_data.get("user_metadata", {}),
        }
    # Handle Supabase User object
    return {
        "sub": getattr(user_data, "id", None),
        "email": getattr(user_data, "email", None),
        "email_confirmed_at": getattr(user_data, "email_confirmed_at", None) or getattr(user_data, "confirmed_at", None),
        "user_metadata": getattr(user_data, "user_metadata", {}) or {},
    }
```

**Explanation:** It accepts `user_data` and returns `dict`. See the code below for the full implementation. Key calls include `isinstance()`, `get()`, `getattr()`.

### `get_current_user`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `48-57`
- **Signature:** `def get_current_user(token: str = Depends(get_bearer_token)) -> dict:`
- **Purpose:** Retrieves current user.

**Code:**
```python
def get_current_user(token: str = Depends(get_bearer_token)) -> dict:
    client = get_supabase_public_client()
    try:
        user_response = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_data = _extract_user_data(user_response)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return _build_user_claims(user_data)
```

**Explanation:** It accepts `token` and returns `dict`. See the code below for the full implementation. Key calls include `get_supabase_public_client()`, `get_user()`, `HTTPException()`, `_extract_user_data()`, `_build_user_claims()`.

### `get_verified_user`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `60-82`
- **Signature:** `def get_verified_user(token: str = Depends(get_bearer_token)) -> dict:`
- **Purpose:** Retrieves verified user.

**Code:**
```python
def get_verified_user(token: str = Depends(get_bearer_token)) -> dict:
    client = get_supabase_public_client()
    try:
        user_response = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_data = _extract_user_data(user_response)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    confirmed_at = (
        getattr(user_data, "email_confirmed_at", None)
        or getattr(user_data, "confirmed_at", None)
        or (isinstance(user_data, dict) and (user_data.get("email_confirmed_at") or user_data.get("confirmed_at")))
    )
    if not confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified"
        )

    return _build_user_claims(user_data)
```

**Explanation:** It accepts `token` and returns `dict`. See the code below for the full implementation. Key calls include `get_supabase_public_client()`, `get_user()`, `HTTPException()`, `_extract_user_data()`, `getattr()`.

### `_get_user_role`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `89-105`
- **Signature:** `def _get_user_role(user_id: str) -> str:`
- **Purpose:** Fetch the user's role from the user_roles table using service_role (bypasses RLS).

**Code:**
```python
def _get_user_role(user_id: str) -> str:
    """Fetch the user's role from the user_roles table using service_role (bypasses RLS)."""
    client = get_supabase_client()
    try:
        res = client.table("user_roles").select("role").eq("user_id", user_id).single().execute()
        data = getattr(res, "data", None)
        if isinstance(data, dict):
            role = data.get("role", "user")
            logger.debug("_get_user_role: user_id=%s role=%s", user_id, role)
            return role
        logger.warning("_get_user_role: no data returned for user_id=%s", user_id)
        return "user"
    except Exception as exc:
        # NOTE: Returning "user" on DB failure fails safely (no privilege escalation),
        # but legitimate admins will be denied access during outages.
        logger.error("_get_user_role DB failure for user_id=%s: %s", user_id, exc)
        return "user"
```

**Explanation:** It accepts `user_id` and returns `str`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `getattr()`, `isinstance()`, `warning()`.

### `get_current_user_with_role`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `108-111`
- **Signature:** `def get_current_user_with_role(user: dict = Depends(get_verified_user)) -> dict:`
- **Purpose:** Return the verified user dict enriched with their role.

**Code:**
```python
def get_current_user_with_role(user: dict = Depends(get_verified_user)) -> dict:
    """Return the verified user dict enriched with their role."""
    user["role"] = _get_user_role(user.get("sub"))
    return user
```

**Explanation:** It accepts `user` and returns `dict`. See the code below for the full implementation. Key calls include `_get_user_role()`, `get()`.

### `_get_effective_plan`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `114-129`
- **Signature:** `def _get_effective_plan(user_id: str) -> str:`
- **Purpose:** Return the user's effective plan. Admins/devs are always premium.

**Code:**
```python
def _get_effective_plan(user_id: str) -> str:
    """Return the user's effective plan. Admins/devs are always premium."""
    role = _get_user_role(user_id)
    if role in ("admin", "dev"):
        return "premium"
    # For normal users, fetch from profiles using service_role
    client = get_supabase_client()
    try:
        res = client.table("profiles").select("plan").eq("id", user_id).single().execute()
        data = getattr(res, "data", None)
        if isinstance(data, dict):
            return data.get("plan", "free")
        return "free"
    except Exception as exc:
        logger.error("_get_effective_plan failed for user_id=%s: %s", user_id, exc)
        return "free"
```

**Explanation:** It accepts `user_id` and returns `str`. See the code below for the full implementation. Key calls include `_get_user_role()`, `get_supabase_client()`, `execute()`, `getattr()`, `isinstance()`.

### `get_current_user_with_role_and_plan`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `132-136`
- **Signature:** `def get_current_user_with_role_and_plan(user: dict = Depends(get_verified_user)) -> dict:`
- **Purpose:** Return the verified user dict enriched with their role and effective plan.

**Code:**
```python
def get_current_user_with_role_and_plan(user: dict = Depends(get_verified_user)) -> dict:
    """Return the verified user dict enriched with their role and effective plan."""
    user["role"] = _get_user_role(user.get("sub"))
    user["plan"] = _get_effective_plan(user.get("sub"))
    return user
```

**Explanation:** It accepts `user` and returns `dict`. See the code below for the full implementation. Key calls include `_get_user_role()`, `get()`, `_get_effective_plan()`.

### `require_admin`

- **File:** `fastapi-backend/app/dependencies/auth.py`
- **Lines:** `139-146`
- **Signature:** `def require_admin(user: dict = Depends(get_verified_user)) -> dict:`
- **Purpose:** Require the authenticated user to have an admin or dev role.

**Code:**
```python
def require_admin(user: dict = Depends(get_verified_user)) -> dict:
    """Require the authenticated user to have an admin or dev role."""
    role = _get_user_role(user.get("sub"))
    if role not in ("admin", "dev"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    user["role"] = role
    user["plan"] = "premium"
    return user
```

**Explanation:** It accepts `user` and returns `dict`. See the code below for the full implementation. Key calls include `_get_user_role()`, `get()`, `HTTPException()`.


## `fastapi-backend/app/middleware/__init__.py`

**File:** `fastapi-backend/app/middleware/__init__.py`

**Summary:** Source file `fastapi-backend/app/middleware/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/middleware/rate_limit.py`

**File:** `fastapi-backend/app/middleware/rate_limit.py`

**Summary:** Distributed sliding-window rate limiting middleware for LUMI.

### `RateLimitMiddleware.__init__`

- **File:** `fastapi-backend/app/middleware/rate_limit.py`
- **Lines:** `25-29`
- **Signature:** `def __init__(self, app: Any, requests_per_minute: int = 60, window_seconds: int = 60) -> None:`
- **Purpose:** Method of `RateLimitMiddleware` that handles   init  .

**Code:**
```python
def __init__(self, app: Any, requests_per_minute: int = 60, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.rate_limit = requests_per_minute
        self._window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
```

**Explanation:** It accepts `app`, `requests_per_minute`, `window_seconds` and returns `None`. See the code below for the full implementation. Key calls include `__init__()`, `super()`, `defaultdict()`.

### `RateLimitMiddleware._client_ip`

- **File:** `fastapi-backend/app/middleware/rate_limit.py`
- **Lines:** `31-40`
- **Signature:** `def _client_ip(self, request: Request) -> str:`
- **Purpose:** Extract the real client IP, respecting reverse proxy headers.

**Code:**
```python
def _client_ip(self, request: Request) -> str:
        """Extract the real client IP, respecting reverse proxy headers."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # X-Forwarded-For can be a comma-separated list; the left-most is the original client.
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "unknown"
```

**Explanation:** It accepts `request` and returns `str`. See the code below for the full implementation. Key calls include `get()`, `strip()`, `split()`.

### `RateLimitMiddleware._is_allowed_memory`

- **File:** `fastapi-backend/app/middleware/rate_limit.py`
- **Lines:** `42-50`
- **Signature:** `async def _is_allowed_memory(self, client_ip: str) -> bool:`
- **Purpose:** In-memory sliding window fallback.

**Code:**
```python
async def _is_allowed_memory(self, client_ip: str) -> bool:
        """In-memory sliding window fallback."""
        now = time.time()
        cutoff = now - self._window
        self._hits[client_ip] = [t for t in self._hits[client_ip] if t > cutoff]
        if len(self._hits[client_ip]) >= self.rate_limit:
            return False
        self._hits[client_ip].append(now)
        return True
```

**Explanation:** It accepts `client_ip` and returns `bool`. See the code below for the full implementation. Key calls include `time()`, `len()`, `append()`.

### `RateLimitMiddleware._is_allowed_redis`

- **File:** `fastapi-backend/app/middleware/rate_limit.py`
- **Lines:** `52-73`
- **Signature:** `async def _is_allowed_redis(self, client_ip: str) -> bool:`
- **Purpose:** Redis sorted-set sliding window.

**Code:**
```python
async def _is_allowed_redis(self, client_ip: str) -> bool:
        """Redis sorted-set sliding window."""
        redis = get_redis()
        if isinstance(redis, NullRedis):
            return await self._is_allowed_memory(client_ip)

        now = time.time()
        key = f"lumi:rate_limit:{client_ip}"
        try:
            pipe = redis.pipeline()
            # Remove timestamps outside the current window
            pipe.zremrangebyscore(key, 0, now - self._window)
            # Count remaining entries in the window
            pipe.zcard(key)
            # Add the current timestamp and set key expiry
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self._window + 1)
            _, count, _, _ = await pipe.execute()
            return count < self.rate_limit
        except Exception as exc:
            logger.warning("Redis rate limit check failed for %s: %s", client_ip, exc)
            return await self._is_allowed_memory(client_ip)
```

**Explanation:** It accepts `client_ip` and returns `bool`. See the code below for the full implementation. Key calls include `get_redis()`, `isinstance()`, `_is_allowed_memory()`, `time()`, `pipeline()`.

### `RateLimitMiddleware.dispatch`

- **File:** `fastapi-backend/app/middleware/rate_limit.py`
- **Lines:** `75-94`
- **Signature:** `async def dispatch(self, request: Request, call_next: Any) -> Any:`
- **Purpose:** Method of `RateLimitMiddleware` that handles dispatch.

**Code:**
```python
async def dispatch(self, request: Request, call_next: Any) -> Any:
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        client_ip = self._client_ip(request)
        allowed = await self._is_allowed_redis(client_ip)

        if not allowed:
            retry_after = self._window
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Try again in a minute.",
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
```

**Explanation:** It accepts `request`, `call_next` and returns `Any`. See the code below for the full implementation. Key calls include `startswith()`, `call_next()`, `_client_ip()`, `_is_allowed_redis()`, `JSONResponse()`.


## `fastapi-backend/app/middleware/request_id.py`

**File:** `fastapi-backend/app/middleware/request_id.py`

**Summary:** Structured logging and request ID middleware for LUMI.

### `RequestIDMiddleware.dispatch`

- **File:** `fastapi-backend/app/middleware/request_id.py`
- **Lines:** `26-49`
- **Signature:** `async def dispatch(self, request: Request, call_next: Any) -> Response:`
- **Purpose:** Method of `RequestIDMiddleware` that handles dispatch.

**Code:**
```python
async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        # Structured log line
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
            },
        )

        return response
```

**Explanation:** It accepts `request`, `call_next` and returns `Response`. See the code below for the full implementation. Key calls include `get()`, `str()`, `uuid4()`, `time()`, `call_next()`.

### `DefaultRequestFilter.filter`

- **File:** `fastapi-backend/app/middleware/request_id.py`
- **Lines:** `69-73`
- **Signature:** `def filter(self, record: logging.LogRecord) -> bool:`
- **Purpose:** Method of `DefaultRequestFilter` that handles filter.

**Code:**
```python
def filter(self, record: logging.LogRecord) -> bool:
        for key, default in self._DEFAULTS.items():
            if not hasattr(record, key):
                setattr(record, key, default)
        return True
```

**Explanation:** It accepts `record` and returns `bool`. See the code below for the full implementation. Key calls include `items()`, `hasattr()`, `setattr()`.

### `SafeJSONFormatter.format`

- **File:** `fastapi-backend/app/middleware/request_id.py`
- **Lines:** `84-108`
- **Signature:** `def format(self, record: logging.LogRecord) -> str:`
- **Purpose:** Method of `SafeJSONFormatter` that handles format.

**Code:**
```python
def format(self, record: logging.LogRecord) -> str:
        try:
            message = record.getMessage()
        except (TypeError, ValueError, KeyError):
            message = str(record.msg)

        payload = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "request_id": getattr(record, "request_id", None),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "status_code": getattr(record, "status_code", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "client_ip": getattr(record, "client_ip", None),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(payload, default=str, ensure_ascii=False)
```

**Explanation:** It accepts `record` and returns `str`. See the code below for the full implementation. Key calls include `getMessage()`, `str()`, `formatTime()`, `getattr()`, `formatException()`.

### `setup_logging`

- **File:** `fastapi-backend/app/middleware/request_id.py`
- **Lines:** `111-150`
- **Signature:** `def setup_logging(level: int | str = logging.INFO) -> None:`
- **Purpose:** Configure structured logging for the application.

**Code:**
```python
def setup_logging(level: int | str = logging.INFO) -> None:
    """Configure structured logging for the application."""
    formatter = SafeJSONFormatter()
    default_filter = DefaultRequestFilter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(default_filter)

    # Reconfigure the root logger
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Reconfigure common library loggers that may carry their own handlers
    # (Uvicorn, FastAPI/Starlette, FAISS, HTTP clients).  Replace any handler
    # that has a non-safe formatter so it cannot raise on missing ``request_id``.
    for name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn.asgi",
        "fastapi",
        "starlette",
        "faiss",
        "httpx",
        "httpcore",
        "urllib3",
    ):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("faiss").setLevel(logging.WARNING)
```

**Explanation:** It accepts `level` and returns `None`. See the code below for the full implementation. Key calls include `SafeJSONFormatter()`, `DefaultRequestFilter()`, `StreamHandler()`, `setFormatter()`, `addFilter()`.


## `fastapi-backend/app/middleware/security.py`

**File:** `fastapi-backend/app/middleware/security.py`

**Summary:** Security headers and request body size limit middleware for LUMI.

### `SecurityHeadersMiddleware.dispatch`

- **File:** `fastapi-backend/app/middleware/security.py`
- **Lines:** `36-40`
- **Signature:** `async def dispatch(self, request: Request, call_next: Any) -> Response:`
- **Purpose:** Method of `SecurityHeadersMiddleware` that handles dispatch.

**Code:**
```python
async def dispatch(self, request: Request, call_next: Any) -> Response:
        response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response
```

**Explanation:** It accepts `request`, `call_next` and returns `Response`. See the code below for the full implementation. Key calls include `call_next()`, `items()`, `setdefault()`.

### `BodySizeLimitMiddleware.dispatch`

- **File:** `fastapi-backend/app/middleware/security.py`
- **Lines:** `46-53`
- **Signature:** `async def dispatch(self, request: Request, call_next: Any) -> Response:`
- **Purpose:** Method of `BodySizeLimitMiddleware` that handles dispatch.

**Code:**
```python
async def dispatch(self, request: Request, call_next: Any) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > _MAX_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large. Maximum size is 1 MB."},
            )
        return await call_next(request)
```

**Explanation:** It accepts `request`, `call_next` and returns `Response`. See the code below for the full implementation. Key calls include `get()`, `JSONResponse()`, `int()`, `call_next()`.


## `fastapi-backend/app/ml/__init__.py`

**File:** `fastapi-backend/app/ml/__init__.py`

**Summary:** Source file `fastapi-backend/app/ml/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/ml/predictor.py`

**File:** `fastapi-backend/app/ml/predictor.py`

**Summary:** Source file `fastapi-backend/app/ml/predictor.py`.

### `_sanitize_nan`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `17-25`
- **Signature:** `def _sanitize_nan(obj: Any) -> Any:`
- **Purpose:** Recursively replace NaN / Inf floats with None for JSON safety.

**Code:**
```python
def _sanitize_nan(obj: Any) -> Any:
    """Recursively replace NaN / Inf floats with None for JSON safety."""
    if isinstance(obj, dict):
        return {k: _sanitize_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_nan(v) for v in obj]
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj
```

**Explanation:** It accepts `obj` and returns `Any`. See the code below for the full implementation. Key calls include `isinstance()`, `_sanitize_nan()`, `items()`, `isnan()`, `isinf()`.

### `_load_csv_from_supabase`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `39-64`
- **Signature:** `def _load_csv_from_supabase(dataset_name: str) -> pd.DataFrame | None:`
- **Purpose:** Load a DOE CSV that has been migrated into public.doe_datasets.

**Code:**
```python
def _load_csv_from_supabase(dataset_name: str) -> pd.DataFrame | None:
    """Load a DOE CSV that has been migrated into public.doe_datasets."""
    cache_key = f"predictor:doe:{dataset_name}"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return pd.DataFrame(cached)

    try:
        client = get_supabase_client()
        resp = (
            client.table("doe_datasets")
            .select("data")
            .eq("dataset_name", dataset_name)
            .single()
            .execute()
        )
        if not resp.data:
            return None
        rows = resp.data.get("data")
        if not rows:
            return None
        cache_set_sync(cache_key, rows, ttl=3600)
        return pd.DataFrame(rows)
    except Exception as exc:
        logger.warning("Failed to load DOE dataset %s from Supabase: %s", dataset_name, exc)
        return None
```

**Explanation:** It accepts `dataset_name` and returns `pd.DataFrame | None`. See the code below for the full implementation. Key calls include `cache_get_sync()`, `DataFrame()`, `get_supabase_client()`, `execute()`, `get()`.

### `_load_csv`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `67-84`
- **Signature:** `def _load_csv(filename: str, subdir: str = "") -> pd.DataFrame | None:`
- **Purpose:** Handles  load csv.

**Code:**
```python
def _load_csv(filename: str, subdir: str = "") -> pd.DataFrame | None:
    dataset_name = f"{subdir}/{filename}" if subdir else filename
    path = _DATA_DIR / subdir / filename if subdir else _DATA_DIR / filename
    settings = get_settings()

    # Prefer bundled preprocessed CSVs on serverless/Vercel to avoid
    # repeated Supabase round-trips. Set USE_LOCAL_DATA_FALLBACK=false
    # to force loading from Supabase instead.
    if settings.use_local_data_fallback and path.exists():
        return pd.read_csv(path)

    df = _load_csv_from_supabase(dataset_name)
    if df is not None:
        return df

    if settings.use_local_data_fallback and path.exists():
        return pd.read_csv(path)
    return None
```

**Explanation:** It accepts `filename`, `subdir` and returns `pd.DataFrame | None`. See the code below for the full implementation. Key calls include `get_settings()`, `exists()`, `read_csv()`, `_load_csv_from_supabase()`.

### `EnergyHubML.__init__`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `95-108`
- **Signature:** `def __init__(self) -> None:`
- **Purpose:** Method of `EnergyHubML` that handles   init  .

**Code:**
```python
def __init__(self) -> None:
        self._historical: pd.DataFrame | None = None
        self._forecast_consumption: pd.DataFrame | None = None
        self._forecast_peak: pd.DataFrame | None = None
        self._model_comparison: pd.DataFrame | None = None
        self._tabula_raw: pd.DataFrame | None = None
        self._provincial_consumption: pd.DataFrame | None = None
        self._regional_sales: pd.DataFrame | None = None
        self._irena_capacity: pd.DataFrame | None = None
        self._irena_generation: pd.DataFrame | None = None
        self._irena_renewable_share: pd.DataFrame | None = None
        self._meralco_rates: pd.DataFrame | None = None
        self._solar_atlas: pd.DataFrame | None = None
        self._load_all()
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `_load_all()`.

### `EnergyHubML._load_all`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `110-127`
- **Signature:** `def _load_all(self) -> None:`
- **Purpose:** Method of `EnergyHubML` that handles  load all.

**Code:**
```python
def _load_all(self) -> None:
        # Prefer v2 preprocessed; fall back to v1 for backward compatibility
        def _prefer_v2(filename: str) -> pd.DataFrame | None:
            v2 = _load_csv(filename, "data_v2_preprocessed")
            return v2 if v2 is not None else _load_csv(filename, "data_v1")

        self._historical = _prefer_v2("master_preprocessed.csv")
        self._forecast_consumption = _prefer_v2("forecast_consumption_2025_2030.csv")
        self._forecast_peak = _prefer_v2("forecast_peak_demand_2025_2030.csv")
        self._model_comparison = _prefer_v2("model_comparison_results.csv")
        self._tabula_raw = _load_csv("Tabula_DOE_Data.csv", "data_v1")
        self._provincial_consumption = _load_csv("provincial_consumption_2003_2025.csv", "data_v2_preprocessed")
        self._regional_sales = _load_csv("regional_sales_2025.csv", "data_v2_preprocessed")
        self._irena_capacity = _load_csv("irena_ph_capacity_by_tech.csv", "data_v2_preprocessed")
        self._irena_generation = _load_csv("irena_ph_generation_by_tech.csv", "data_v2_preprocessed")
        self._irena_renewable_share = _load_csv("irena_renewable_share.csv", "data_v2_preprocessed")
        self._meralco_rates = _load_csv("meralco_rates_2011_2020.csv", "data_v2_preprocessed")
        self._solar_atlas = _load_csv("solar_atlas_ph.csv", "data_v2_preprocessed")
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `_load_csv()`, `_prefer_v2()`.

### `EnergyHubML.get_latest_statistics`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `131-163`
- **Signature:** `def get_latest_statistics(self) -> dict[str, Any]:`
- **Purpose:** Return the most recent year’s national energy snapshot.

**Code:**
```python
def get_latest_statistics(self) -> dict[str, Any]:
        """Return the most recent year’s national energy snapshot."""
        if self._historical is None or self._historical.empty:
            return {
                "year": 0,
                "total_consumption_gwh": 0.0,
                "total_peak_demand_mw": 0.0,
                "total_generation_gwh": 0.0,
                "renewable_generation_gwh": 0.0,
                "renewable_share_pct": 0.0,
                "capacity_margin_mw": None,
                "capacity_margin_pct": None,
            }
        df = self._historical
        latest = df.iloc[-1]
        latest_year = int(latest["year"])

        total_consumption = float(latest.get("total_consumption_gwh", 0))
        total_peak = float(latest.get("total_peak_demand_mw", 0))
        total_generation = float(latest.get("total_generation_gwh", 0))
        renewable_gen = float(latest.get("renewable_generation_gwh", 0))
        renewable_share = (renewable_gen / total_consumption * 100) if total_consumption else 0.0

        return _sanitize_nan({
            "year": latest_year,
            "total_consumption_gwh": round(total_consumption, 2),
            "total_peak_demand_mw": round(total_peak, 2),
            "total_generation_gwh": round(total_generation, 2),
            "renewable_generation_gwh": round(renewable_gen, 2),
            "renewable_share_pct": round(renewable_share, 2),
            "capacity_margin_mw": round(float(latest.get("capacity_margin_mw") or 0), 2),
            "capacity_margin_pct": round(float(latest.get("capacity_margin_pct") or 0), 2),
        })
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `int()`, `float()`, `get()`, `_sanitize_nan()`, `round()`.

### `EnergyHubML.get_historical_trends`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `165-186`
- **Signature:** `def get_historical_trends(self) -> dict[str, Any]:`
- **Purpose:** Return year-by-year national trends for charting.

**Code:**
```python
def get_historical_trends(self) -> dict[str, Any]:
        """Return year-by-year national trends for charting."""
        if self._historical is None or self._historical.empty:
            return {"years": [], "series": {}}
        df = self._historical.sort_values("year")
        years = df["year"].astype(int).tolist()

        series = {
            "total_consumption_gwh": df["total_consumption_gwh"].round(2).tolist(),
            "total_peak_demand_mw": df["total_peak_demand_mw"].round(2).tolist(),
            "total_generation_gwh": df.get("total_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
            "renewable_generation_gwh": df["renewable_generation_gwh"].round(2).tolist(),
            "renewable_share_pct": df.get("renewable_share_pct", pd.Series([], dtype=float)).round(2).tolist(),
            "coal_generation_gwh": df.get("coal_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
            "natural_gas_generation_gwh": df.get("natural_gas_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
            "oil_based_generation_gwh": df.get("oil_based_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
            "hydro_generation_gwh": df.get("hydro_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
            "geothermal_generation_gwh": df.get("geothermal_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
            "solar_generation_gwh": df.get("solar_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
            "wind_generation_gwh": df.get("wind_generation_gwh", pd.Series([], dtype=float)).round(2).tolist(),
        }
        return _sanitize_nan({"years": years, "series": series})
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `sort_values()`, `tolist()`, `astype()`, `round()`, `get()`.

### `EnergyHubML.get_forecast`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `188-221`
- **Signature:** `def get_forecast(self, metric: str = "consumption") -> dict[str, Any]:`
- **Purpose:** Return the 2025-2030 ML forecast with confidence intervals.

**Code:**
```python
def get_forecast(self, metric: str = "consumption") -> dict[str, Any]:
        """Return the 2025-2030 ML forecast with confidence intervals."""
        if metric == "peak_demand":
            df = self._forecast_peak
            target_col = "total_peak_demand_mw"
        else:
            df = self._forecast_consumption
            target_col = "total_consumption_gwh"

        if df is None or df.empty:
            return {
                "forecast_years": [],
                "forecast_values": [],
                "ci_lower": [],
                "ci_upper": [],
                "model": "ARIMA(1,1,1)",
                "training_period": "2003-2020",
                "test_period": "2021-2024",
            }

        years = df["year"].astype(int).tolist()
        values = df[target_col].round(2).tolist()
        ci_lower = df["ci_lower"].round(2).tolist() if "ci_lower" in df.columns else [None] * len(df)
        ci_upper = df["ci_upper"].round(2).tolist() if "ci_upper" in df.columns else [None] * len(df)

        return _sanitize_nan({
            "forecast_years": years,
            "forecast_values": values,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "model": "ARIMA(1,1,1)",
            "training_period": "2003-2020",
            "test_period": "2021-2024",
        })
```

**Explanation:** It accepts `metric` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `tolist()`, `astype()`, `round()`, `len()`, `_sanitize_nan()`.

### `EnergyHubML.get_model_comparison`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `223-231`
- **Signature:** `def get_model_comparison(self) -> list[dict[str, Any]]:`
- **Purpose:** Return test-set performance across all trained models.

**Code:**
```python
def get_model_comparison(self) -> list[dict[str, Any]]:
        """Return test-set performance across all trained models."""
        if self._model_comparison is None or self._model_comparison.empty:
            return []
        df = self._model_comparison.copy()
        df["mae"] = df["mae"].round(2)
        df["rmse"] = df["rmse"].round(2)
        df["mape"] = df["mape"].round(2)
        return _sanitize_nan(df.to_dict(orient="records"))
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `copy()`, `round()`, `_sanitize_nan()`, `to_dict()`.

### `EnergyHubML.get_source_breakdown`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `233-274`
- **Signature:** `def get_source_breakdown(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Return generation by plant type for a given year (latest if None).

**Code:**
```python
def get_source_breakdown(self, year: int | None = None) -> dict[str, Any]:
        """Return generation by plant type for a given year (latest if None)."""
        if self._historical is None or self._historical.empty:
            return {
                "year": 0,
                "total_generation_gwh": 0.0,
                "generation_gwh": {},
                "share_pct": {},
            }
        df = self._historical
        if year is None:
            row = df.iloc[-1]
            year = int(row["year"])
        else:
            match = df[df["year"] == year]
            if match.empty:
                return {
                    "year": year,
                    "total_generation_gwh": 0.0,
                    "generation_gwh": {},
                    "share_pct": {},
                }
            row = match.iloc[0]

        sources = {
            "coal": float(row.get("coal_generation_gwh", 0)),
            "natural_gas": float(row.get("natural_gas_generation_gwh", 0)),
            "oil_based": float(row.get("oil_based_generation_gwh", 0)),
            "geothermal": float(row.get("geothermal_generation_gwh", 0)),
            "hydro": float(row.get("hydro_generation_gwh", 0)),
            "solar": float(row.get("solar_generation_gwh", 0)),
            "wind": float(row.get("wind_generation_gwh", 0)),
            "biomass": float(row.get("biomass_generation_gwh", 0)),
        }
        total = sum(sources.values())
        shares = {k: round((v / total * 100), 2) if total else 0 for k, v in sources.items()}
        return _sanitize_nan({
            "year": year,
            "total_generation_gwh": round(total, 2),
            "generation_gwh": {k: round(v, 2) for k, v in sources.items()},
            "share_pct": shares,
        })
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `int()`, `float()`, `get()`, `sum()`, `values()`.

### `EnergyHubML.get_grid_breakdown`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `276-312`
- **Signature:** `def get_grid_breakdown(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Return generation by grid (Luzon, Visayas, Mindanao).

**Code:**
```python
def get_grid_breakdown(self, year: int | None = None) -> dict[str, Any]:
        """Return generation by grid (Luzon, Visayas, Mindanao)."""
        if self._historical is None or self._historical.empty:
            return {
                "year": 0,
                "total_generation_gwh": 0.0,
                "generation_gwh": {},
                "share_pct": {},
            }
        df = self._historical
        if year is None:
            row = df.iloc[-1]
            year = int(row["year"])
        else:
            match = df[df["year"] == year]
            if match.empty:
                return {
                    "year": year,
                    "total_generation_gwh": 0.0,
                    "generation_gwh": {},
                    "share_pct": {},
                }
            row = match.iloc[0]

        grids = {
            "luzon": float(row.get("luzon_generation_gwh", 0)),
            "visayas": float(row.get("visayas_generation_gwh", 0)),
            "mindanao": float(row.get("mindanao_generation_gwh", 0)),
        }
        total = sum(grids.values())
        shares = {k: round((v / total * 100), 2) if total else 0 for k, v in grids.items()}
        return _sanitize_nan({
            "year": year,
            "total_generation_gwh": round(total, 2),
            "generation_gwh": {k: round(v, 2) for k, v in grids.items()},
            "share_pct": shares,
        })
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `int()`, `float()`, `get()`, `sum()`, `values()`.

### `EnergyHubML.get_ai_insight`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `314-376`
- **Signature:** `def get_ai_insight(self) -> dict[str, str]:`
- **Purpose:** Generate a static AI-style insight based on the latest data.

**Code:**
```python
def get_ai_insight(self) -> dict[str, str]:
        """Generate a static AI-style insight based on the latest data.

        In a production system this would call an LLM; here we return
        pre-computed, data-backed observations to avoid latency and
        cost while still providing useful narrative context.
        """
        if self._historical is None or self._historical.empty:
            return {"insight": "No data available.", "recommendation": "", "data_year": 0}

        df = self._historical.sort_values("year")
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        latest_year = int(latest["year"])

        consumption = float(latest["total_consumption_gwh"])
        prev_consumption = float(prev["total_consumption_gwh"])
        growth = ((consumption / prev_consumption) - 1) * 100 if prev_consumption else 0

        renewable_share = float(latest.get("renewable_share_pct", 0))
        capacity_margin = float(latest.get("capacity_margin_pct", 0))

        insight = (
            f"In {latest_year}, Philippine total electricity consumption reached "
            f"{consumption:,.0f} GWh, marking a {growth:.1f}% year-over-year change. "
            f"Renewable energy accounted for {renewable_share:.1f}% of the national mix. "
        )

        if capacity_margin < 30:
            insight += (
                f"The capacity margin stands at {capacity_margin:.1f}%, indicating "
                f"elevated grid stress. Infrastructure expansion should be prioritized."
            )
            recommendation = (
                "Consider accelerating renewable projects and demand-side management "
                "programs to relieve peak-period strain."
            )
        else:
            insight += (
                f"The capacity margin of {capacity_margin:.1f}% provides adequate "
                f"headroom for demand growth in the near term."
            )
            recommendation = (
                "Continue diversifying the generation mix with cost-effective renewables "
                "to maintain long-term supply security."
            )

        # Add forecast-based insight if available
        forecast = self.get_forecast("consumption")
        if forecast.get("forecast_values"):
            f_2030 = forecast["forecast_values"][-1]
            f_growth = ((f_2030 / consumption) - 1) * 100
            insight += (
                f" The ARIMA(1,1,1) model projects consumption will reach "
                f"{f_2030:,.0f} GWh by 2030, a cumulative growth of {f_growth:.1f}% "
                f"from {latest_year}."
            )

        return _sanitize_nan({
            "insight": insight,
            "recommendation": recommendation,
            "data_year": latest_year,
        })
```

**Explanation:** It accepts zero arguments and returns `dict[str, str]`. See the code below for the full implementation. Key calls include `sort_values()`, `len()`, `int()`, `float()`, `get()`.

### `EnergyHubML.get_provincial_consumption`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `380-392`
- **Signature:** `def get_provincial_consumption(self, region: str | None = None) -> dict[str, Any]:`
- **Purpose:** Return provincial/regional consumption breakdown from DOE Annex 8.

**Code:**
```python
def get_provincial_consumption(self, region: str | None = None) -> dict[str, Any]:
        """Return provincial/regional consumption breakdown from DOE Annex 8.

        Values are in MWh as reported by DOE.  If region is None, all
        regions are returned.
        """
        if self._provincial_consumption is None or self._provincial_consumption.empty:
            return {"items": []}
        df = self._provincial_consumption.copy()
        if region:
            df = df[df["region"].str.upper() == region.upper()]
        items = df.to_dict(orient="records")
        return _sanitize_nan({"items": items})
```

**Explanation:** It accepts `region` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `upper()`, `to_dict()`, `_sanitize_nan()`.

### `EnergyHubML.get_regional_sales`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `394-402`
- **Signature:** `def get_regional_sales(self, region: str | None = None) -> dict[str, Any]:`
- **Purpose:** Return 2025 total sales per region.

**Code:**
```python
def get_regional_sales(self, region: str | None = None) -> dict[str, Any]:
        """Return 2025 total sales per region."""
        if self._regional_sales is None or self._regional_sales.empty:
            return {"items": []}
        df = self._regional_sales.copy()
        if region:
            df = df[df["region"].str.upper() == region.upper()]
        items = df.to_dict(orient="records")
        return _sanitize_nan({"items": items})
```

**Explanation:** It accepts `region` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `upper()`, `to_dict()`, `_sanitize_nan()`.

### `EnergyHubML.get_irena_capacity`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `406-415`
- **Signature:** `def get_irena_capacity(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Return IRENA Philippines capacity by technology.

**Code:**
```python
def get_irena_capacity(self, year: int | None = None) -> dict[str, Any]:
        """Return IRENA Philippines capacity by technology."""
        if self._irena_capacity is None or self._irena_capacity.empty:
            return {"items": []}
        df = self._irena_capacity.copy()
        if year:
            df = df[df["year"] == year]
        df["capacity_mw"] = df["capacity_mw"].round(2)
        items = df.to_dict(orient="records")
        return _sanitize_nan({"items": items})
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `round()`, `to_dict()`, `_sanitize_nan()`.

### `EnergyHubML.get_irena_generation`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `417-426`
- **Signature:** `def get_irena_generation(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Return IRENA Philippines generation by technology.

**Code:**
```python
def get_irena_generation(self, year: int | None = None) -> dict[str, Any]:
        """Return IRENA Philippines generation by technology."""
        if self._irena_generation is None or self._irena_generation.empty:
            return {"items": []}
        df = self._irena_generation.copy()
        if year:
            df = df[df["year"] == year]
        df["generation_gwh"] = df["generation_gwh"].round(2)
        items = df.to_dict(orient="records")
        return _sanitize_nan({"items": items})
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `round()`, `to_dict()`, `_sanitize_nan()`.

### `EnergyHubML.get_irena_renewable_share`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `428-435`
- **Signature:** `def get_irena_renewable_share(self) -> dict[str, Any]:`
- **Purpose:** Return year-by-year renewable share of electricity generation (%).

**Code:**
```python
def get_irena_renewable_share(self) -> dict[str, Any]:
        """Return year-by-year renewable share of electricity generation (%)."""
        if self._irena_renewable_share is None or self._irena_renewable_share.empty:
            return {"items": []}
        df = self._irena_renewable_share.copy()
        df["renewable_share_pct"] = df["renewable_share_pct"].round(2)
        items = df.to_dict(orient="records")
        return _sanitize_nan({"items": items})
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `round()`, `to_dict()`, `_sanitize_nan()`.

### `EnergyHubML.get_meralco_rate`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `437-459`
- **Signature:** `def get_meralco_rate(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Return Meralco residential generation charge rate for a given year.

**Code:**
```python
def get_meralco_rate(self, year: int | None = None) -> dict[str, Any]:
        """Return Meralco residential generation charge rate for a given year.

        If year is None, returns the most recent available year.
        """
        if self._meralco_rates is None or self._meralco_rates.empty:
            return {"rate_php_per_kwh": None, "year": None, "note": "Meralco data not available"}
        df = self._meralco_rates.copy()
        if year:
            match = df[df["year"] == year]
            if match.empty:
                return {"rate_php_per_kwh": None, "year": year, "note": "No data for requested year"}
            row = match.iloc[0]
        else:
            df = df.sort_values("year", ascending=True)
            row = df.iloc[-1]
        return _sanitize_nan({
            "rate_php_per_kwh": float(row["rate_php_per_kwh"]),
            "year": int(row["year"]),
            "customer_class": str(row.get("customer_class", "Residential")),
            "charge_component": str(row.get("charge_component", "Generation Energy Charge")),
            "note": "Meralco generation charge component only. Total bill includes transmission, distribution, and other charges.",
        })
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `sort_values()`, `_sanitize_nan()`, `float()`, `int()`.

### `EnergyHubML.get_solar_atlas`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `461-473`
- **Signature:** `def get_solar_atlas(self, location: str | None = None) -> dict[str, Any]:`
- **Purpose:** Return Global Solar Atlas data for Philippine locations.

**Code:**
```python
def get_solar_atlas(self, location: str | None = None) -> dict[str, Any]:
        """Return Global Solar Atlas data for Philippine locations.

        If location is provided, returns the closest match. Otherwise
        returns all sampled locations.
        """
        if self._solar_atlas is None or self._solar_atlas.empty:
            return {"items": [], "note": "Solar Atlas data not available"}
        df = self._solar_atlas.copy()
        if location:
            df = df[df["location"].str.lower().str.contains(location.lower(), regex=False)]
        items = df.to_dict(orient="records")
        return _sanitize_nan({"items": items, "note": "Data from Global Solar Atlas v2 (long-term annual averages)."})
```

**Explanation:** It accepts `location` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `contains()`, `lower()`, `to_dict()`, `_sanitize_nan()`.

### `get_energyhub_ml`

- **File:** `fastapi-backend/app/ml/predictor.py`
- **Lines:** `480-484`
- **Signature:** `def get_energyhub_ml() -> EnergyHubML:`
- **Purpose:** Retrieves energyhub ml.

**Code:**
```python
def get_energyhub_ml() -> EnergyHubML:
    global _energyhub_ml
    if _energyhub_ml is None:
        _energyhub_ml = EnergyHubML()
    return _energyhub_ml
```

**Explanation:** It accepts zero arguments and returns `EnergyHubML`. See the code below for the full implementation. Key calls include `EnergyHubML()`.


## `fastapi-backend/app/models/__init__.py`

**File:** `fastapi-backend/app/models/__init__.py`

**Summary:** Source file `fastapi-backend/app/models/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/routes/__init__.py`

**File:** `fastapi-backend/app/routes/__init__.py`

**Summary:** Source file `fastapi-backend/app/routes/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/routes/admin.py`

**File:** `fastapi-backend/app/routes/admin.py`

**Summary:** Admin portal backend routes for LUMI.

### `_log_admin_action`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `26-37`
- **Signature:** `def _log_admin_action(admin_id: str, action: str, target_user_id: str | None = None, details: dict | None = None) -> None:`
- **Purpose:** Handles  log admin action.

**Code:**
```python
def _log_admin_action(admin_id: str, action: str, target_user_id: str | None = None, details: dict | None = None) -> None:
    client = get_supabase_client()
    try:
        client.table("admin_audit_log").insert({
            "admin_id": admin_id,
            "action": action,
            "target_user_id": target_user_id,
            "details": details or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as exc:
        logger.warning("Admin audit log write failed: %s", exc)
```

**Explanation:** It accepts `admin_id`, `action`, `target_user_id`, `details` and returns `None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `warning()`, `insert()`, `table()`.

### `_has_auth_admin_api`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `40-42`
- **Signature:** `def _has_auth_admin_api(client: Any) -> bool:`
- **Purpose:** Return True if the client supports auth.admin methods.

**Code:**
```python
def _has_auth_admin_api(client: Any) -> bool:
    """Return True if the client supports auth.admin methods."""
    return hasattr(client, "auth") and hasattr(client.auth, "admin")
```

**Explanation:** It accepts `client` and returns `bool`. See the code below for the full implementation. Key calls include `hasattr()`.

### `_auth_user_to_dict`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `45-67`
- **Signature:** `def _auth_user_to_dict(u: Any) -> dict:`
- **Purpose:** Normalise a Supabase AuthUser (or dict fallback) to a plain dict.

**Code:**
```python
def _auth_user_to_dict(u: Any) -> dict:
    """Normalise a Supabase AuthUser (or dict fallback) to a plain dict."""
    if isinstance(u, dict):
        meta = u.get("user_metadata") or {}
        return {
            "id": u.get("id"),
            "email": u.get("email"),
            "created_at": u.get("created_at"),
            "email_confirmed_at": u.get("email_confirmed_at"),
            "last_sign_in_at": u.get("last_sign_in_at"),
            "full_name": meta.get("full_name") or meta.get("name"),
            "avatar_url": meta.get("avatar_url") or meta.get("picture"),
        }
    meta = (getattr(u, "user_metadata", None) or {}) if hasattr(u, "user_metadata") else {}
    return {
        "id": getattr(u, "id", None),
        "email": getattr(u, "email", None),
        "created_at": getattr(u, "created_at", None),
        "email_confirmed_at": getattr(u, "email_confirmed_at", None),
        "last_sign_in_at": getattr(u, "last_sign_in_at", None),
        "full_name": meta.get("full_name") or meta.get("name"),
        "avatar_url": meta.get("avatar_url") or meta.get("picture"),
    }
```

**Explanation:** It accepts `u` and returns `dict`. See the code below for the full implementation. Key calls include `isinstance()`, `get()`, `hasattr()`, `getattr()`.

### `list_users`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `75-126`
- **Signature:** `async def list_users(user: dict = Depends(require_admin)) -> dict[str, Any]:`
- **Purpose:** Return a paginated list of users with roles, profiles and real emails.

**Code:**
```python
async def list_users(user: dict = Depends(require_admin)) -> dict[str, Any]:
    """Return a paginated list of users with roles, profiles and real emails.

    Uses Supabase Auth as the primary source so every auth user is visible,
    even if they don't have a profile or role row yet.
    """
    client = get_supabase_client()

    profiles_resp = client.table("profiles").select("*").execute()
    profiles = {p["id"]: p for p in (profiles_resp.data or [])}

    roles_resp = client.table("user_roles").select("user_id, role").execute()
    roles = {r["user_id"]: r["role"] for r in (roles_resp.data or [])}

    users: list[dict] = []
    if _has_auth_admin_api(client):
        try:
            auth_resp = client.auth.admin.list_users()
            auth_users = auth_resp.users if hasattr(auth_resp, "users") else (auth_resp.data or {}).get("users", [])
            for u in auth_users:
                ud = _auth_user_to_dict(u)
                uid = ud["id"]
                prof = profiles.get(uid, {})
                users.append({
                    "id": uid,
                    "full_name": prof.get("full_name") or ud.get("full_name"),
                    "email": ud.get("email") or uid,
                    "avatar_url": prof.get("avatar_url") or ud.get("avatar_url"),
                    "role": roles.get(uid, "user"),
                    "plan": prof.get("plan", "free"),
                    "is_active": prof.get("is_active", True),
                    "created_at": ud.get("created_at") or prof.get("created_at"),
                })
        except Exception as exc:
            logger.warning("Admin user list enrichment failed for a user: %s", exc)

    # Fallback: if auth admin API is unavailable, return whatever profiles we have
    if not users:
        for uid, prof in profiles.items():
            users.append({
                "id": uid,
                "full_name": prof.get("full_name"),
                "email": prof.get("email") or uid,
                "avatar_url": prof.get("avatar_url"),
                "role": roles.get(uid, "user"),
                "plan": prof.get("plan", "free"),
                "is_active": prof.get("is_active", True),
                "created_at": prof.get("created_at"),
            })

    _log_admin_action(user.get("sub"), "list_users")
    return {"users": users}
```

**Explanation:** It accepts `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `select()`, `table()`, `_has_auth_admin_api()`.

### `create_user`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `134-208`
- **Signature:** `async def create_user(`
- **Purpose:** Admin creates a new user account.

**Code:**
```python
async def create_user(
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Admin creates a new user account.

    Payload:
        email: str (required)
        full_name: str (optional)
        role: "user" | "admin" | "dev" (default "user")
        plan: "free" | "premium" (default "free")
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")

    client = get_supabase_client()
    if not _has_auth_admin_api(client):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth Admin API not available. Check SUPABASE_SERVICE_ROLE_KEY.",
        )

    temp_password = secrets.token_urlsafe(12)
    role = payload.get("role", "user")
    # Admins and devs are always premium
    plan = "premium" if role in ("admin", "dev") else payload.get("plan", "free")
    full_name = payload.get("full_name", "")

    try:
        auth_resp = client.auth.admin.create_user({
            "email": email,
            "password": temp_password,
            "email_confirm": True,
            "user_metadata": {"full_name": full_name},
        })
        new_user = auth_resp.user if hasattr(auth_resp, "user") else (auth_resp.data or {}).get("user")
        user_id = new_user.id if hasattr(new_user, "id") else new_user.get("id")
    except Exception as exc:
        logger.error("Admin create_user failed for email=%s: %s", email, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user") from exc

    # Upsert profile + role (trigger may have already created them)
    try:
        client.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "plan": plan,
            "is_active": True,
        }).execute()
    except Exception as exc:
        logger.warning("Admin profile upsert failed: %s", exc)

    try:
        client.table("user_roles").upsert({
            "user_id": user_id,
            "role": role,
        }).execute()
    except Exception as exc:
        logger.warning("Admin role upsert failed: %s", exc)

    _log_admin_action(
        admin_user.get("sub"),
        "create_user",
        target_user_id=user_id,
        details={"email": email, "role": role, "plan": plan},
    )
    return {
        "id": user_id,
        "email": email,
        "role": role,
        "plan": plan,
        "temp_password": temp_password,
        "message": "User created. Share the temp password or have them use Forgot Password.",
    }
```

**Explanation:** It accepts `payload`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `HTTPException()`, `get_supabase_client()`, `_has_auth_admin_api()`, `token_urlsafe()`.

### `get_user_detail`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `216-248`
- **Signature:** `async def get_user_detail(`
- **Purpose:** Return full profile, role and auth metadata for a single user.

**Code:**
```python
async def get_user_detail(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return full profile, role and auth metadata for a single user."""
    client = get_supabase_client()

    profile_resp = client.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_resp.data or {}

    role_resp = client.table("user_roles").select("role").eq("user_id", user_id).single().execute()
    role = (role_resp.data or {}).get("role", "user") if role_resp.data else "user"

    # Try to get real email + auth metadata
    auth_info = {}
    if _has_auth_admin_api(client):
        try:
            auth_resp = client.auth.admin.get_user_by_id(user_id)
            u = auth_resp.user if hasattr(auth_resp, "user") else (auth_resp.data or {}).get("user")
            auth_info = _auth_user_to_dict(u)
        except Exception as exc:
            logger.warning("Admin auth metadata fetch failed: %s", exc)

    _log_admin_action(admin_user.get("sub"), "view_user", target_user_id=user_id)
    return {
        "id": user_id,
        "profile": profile,
        "role": role,
        "email": auth_info.get("email"),
        "created_at": auth_info.get("created_at") or profile.get("created_at"),
        "last_sign_in_at": auth_info.get("last_sign_in_at"),
        "email_confirmed": bool(auth_info.get("email_confirmed_at")),
    }
```

**Explanation:** It accepts `user_id`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `eq()`, `select()`.

### `toggle_user_ban`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `256-272`
- **Signature:** `async def toggle_user_ban(`
- **Purpose:** Toggle is_active on a user's profile (soft ban / unban).

**Code:**
```python
async def toggle_user_ban(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Toggle is_active on a user's profile (soft ban / unban)."""
    client = get_supabase_client()

    profile_resp = client.table("profiles").select("is_active").eq("id", user_id).single().execute()
    profile = profile_resp.data or {}
    current = profile.get("is_active", True)
    new_state = not current

    client.table("profiles").update({"is_active": new_state}).eq("id", user_id).execute()

    action = "unban_user" if new_state else "ban_user"
    _log_admin_action(admin_user.get("sub"), action, target_user_id=user_id, details={"is_active": new_state})
    return {"id": user_id, "is_active": new_state, "action": action}
```

**Explanation:** It accepts `user_id`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `eq()`, `select()`.

### `update_user_role`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `280-303`
- **Signature:** `async def update_user_role(`
- **Purpose:** Change a user's role (user / admin / dev). Admins/devs are always premium.

**Code:**
```python
async def update_user_role(
    user_id: str,
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Change a user's role (user / admin / dev). Admins/devs are always premium."""
    new_role = payload.get("role")
    if new_role not in ("user", "admin", "dev"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    client = get_supabase_client()
    client.table("user_roles").update({"role": new_role}).eq("user_id", user_id).execute()

    # Auto-sync plan: admin/dev → premium, user → free
    new_plan = "premium" if new_role in ("admin", "dev") else "free"
    client.table("profiles").update({"plan": new_plan}).eq("id", user_id).execute()

    _log_admin_action(
        admin_user.get("sub"),
        "change_role",
        target_user_id=user_id,
        details={"new_role": new_role, "auto_plan": new_plan},
    )
    return {"id": user_id, "role": new_role, "plan": new_plan}
```

**Explanation:** It accepts `user_id`, `payload`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `HTTPException()`, `get_supabase_client()`, `execute()`, `eq()`.

### `update_user_plan`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `311-330`
- **Signature:** `async def update_user_plan(`
- **Purpose:** Change a user's plan (free / premium).

**Code:**
```python
async def update_user_plan(
    user_id: str,
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Change a user's plan (free / premium)."""
    new_plan = payload.get("plan")
    if not new_plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan is required")

    client = get_supabase_client()
    client.table("profiles").update({"plan": new_plan}).eq("id", user_id).execute()

    _log_admin_action(
        admin_user.get("sub"),
        "change_plan",
        target_user_id=user_id,
        details={"new_plan": new_plan},
    )
    return {"id": user_id, "plan": new_plan}
```

**Explanation:** It accepts `user_id`, `payload`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `HTTPException()`, `get_supabase_client()`, `execute()`, `eq()`.

### `get_user_simulations`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `338-352`
- **Signature:** `async def get_user_simulations(`
- **Purpose:** Return all saved simulations for a user.

**Code:**
```python
async def get_user_simulations(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return all saved simulations for a user."""
    client = get_supabase_client()
    resp = (
        client.table("saved_simulations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    _log_admin_action(admin_user.get("sub"), "view_user_simulations", target_user_id=user_id)
    return {"simulations": resp.data or []}
```

**Explanation:** It accepts `user_id`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `order()`, `eq()`, `select()`.

### `get_user_report`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `360-406`
- **Signature:** `async def get_user_report(`
- **Purpose:** Return aggregated usage statistics for a single user.

**Code:**
```python
async def get_user_report(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return aggregated usage statistics for a single user."""
    client = get_supabase_client()

    sims_resp = (
        client.table("saved_simulations")
        .select("id, municipality_id, name, created_at", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    sims = sims_resp.data or []
    total_simulations = sims_resp.count or len(sims)

    chat_resp = (
        client.table("chat_sessions")
        .select("id, created_at", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    chats = chat_resp.data or []
    total_chat_sessions = chat_resp.count or len(chats)

    # Most-searched municipality
    municipality_counts: dict[str, int] = {}
    for s in sims:
        mid = s.get("municipality_id")
        if mid:
            municipality_counts[str(mid)] = municipality_counts.get(str(mid), 0) + 1
    peak_municipality_id = max(municipality_counts, key=municipality_counts.get) if municipality_counts else None

    # Last activity
    all_dates = [s.get("created_at") for s in sims] + [c.get("created_at") for c in chats]
    valid_dates = [d for d in all_dates if d]
    last_active = max(valid_dates) if valid_dates else None

    _log_admin_action(admin_user.get("sub"), "view_user_report", target_user_id=user_id)
    return {
        "user_id": user_id,
        "total_simulations": total_simulations,
        "total_chat_sessions": total_chat_sessions,
        "peak_municipality_id": peak_municipality_id,
        "last_active": last_active,
        "recent_simulations": sims[:5],
    }
```

**Explanation:** It accepts `user_id`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `eq()`, `select()`, `table()`.

### `soft_delete_user`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `414-434`
- **Signature:** `async def soft_delete_user(`
- **Purpose:** Soft-delete a user: ban + anonymise profile + log action.

**Code:**
```python
async def soft_delete_user(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Soft-delete a user: ban + anonymise profile + log action.
    Hard-delete from auth.users is optional and requires the Auth Admin API."""
    client = get_supabase_client()

    # 1. Ban
    client.table("profiles").update({"is_active": False}).eq("id", user_id).execute()

    # 2. Anonymise
    client.table("profiles").update({
        "full_name": "Deleted User",
        "avatar_url": None,
        "organization": None,
        "location": None,
    }).eq("id", user_id).execute()

    _log_admin_action(admin_user.get("sub"), "soft_delete_user", target_user_id=user_id)
    return {"id": user_id, "status": "soft_deleted", "message": "User banned and anonymised. Data retained for audit."}
```

**Explanation:** It accepts `user_id`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `eq()`, `update()`, `table()`.

### `get_analytics`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `442-470`
- **Signature:** `async def get_analytics(user: dict = Depends(require_admin)) -> dict[str, Any]:`
- **Purpose:** Return system-level analytics.

**Code:**
```python
async def get_analytics(user: dict = Depends(require_admin)) -> dict[str, Any]:
    """Return system-level analytics."""
    client = get_supabase_client()

    users_resp = client.table("profiles").select("id, plan, is_active", count="exact").execute()
    all_profiles = users_resp.data or []
    total_users = users_resp.count or len(all_profiles)
    active_users = sum(1 for u in all_profiles if u.get("is_active", True))
    banned_users = total_users - active_users

    sims_resp = client.table("saved_simulations").select("id", count="exact").execute()
    total_simulations = sims_resp.count or 0

    chat_resp = client.table("chat_sessions").select("id", count="exact").execute()
    total_chat_sessions = chat_resp.count or 0

    free_users = sum(1 for u in all_profiles if u.get("plan") == "free")
    premium_users = sum(1 for u in all_profiles if u.get("plan") != "free")

    _log_admin_action(user.get("sub"), "view_analytics")
    return {
        "total_users": total_users,
        "active_users": active_users,
        "banned_users": banned_users,
        "total_simulations": total_simulations,
        "total_chat_sessions": total_chat_sessions,
        "free_users": free_users,
        "premium_users": premium_users,
    }
```

**Explanation:** It accepts `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `select()`, `table()`, `len()`.

### `update_config`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `478-494`
- **Signature:** `async def update_config(`
- **Purpose:** Update system configuration toggles.

**Code:**
```python
async def update_config(
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Update system configuration toggles."""
    client = get_supabase_client()
    try:
        client.table("system_config").upsert({
            "key": "global",
            "value": payload,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as exc:
        logger.warning("Admin config upsert failed: %s", exc)

    _log_admin_action(admin_user.get("sub"), "update_config", details=payload)
    return {"status": "ok", "config": payload}
```

**Explanation:** It accepts `payload`, `admin_user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `warning()`, `upsert()`, `table()`.

### `get_config`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `498-510`
- **Signature:** `async def get_config(user: dict = Depends(require_admin)) -> dict[str, Any]:`
- **Purpose:** Return current system configuration.

**Code:**
```python
async def get_config(user: dict = Depends(require_admin)) -> dict[str, Any]:
    """Return current system configuration."""
    client = get_supabase_client()
    try:
        resp = client.table("system_config").select("value").eq("key", "global").single().execute()
        return resp.data.get("value", {}) if resp.data else {}
    except Exception:
        return {
            "chatbot_enabled": True,
            "maintenance_mode": False,
            "free_chat_limit": 5,
            "free_sim_limit": 3,
        }
```

**Explanation:** It accepts `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `get()`, `single()`, `eq()`.

### `list_chat_sessions`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `518-533`
- **Signature:** `async def list_chat_sessions(`
- **Purpose:** Return recent chat sessions for moderation review.

**Code:**
```python
async def list_chat_sessions(
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return recent chat sessions for moderation review."""
    client = get_supabase_client()
    resp = (
        client.table("chat_sessions")
        .select("*, chat_messages(*)")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    _log_admin_action(user.get("sub"), "view_chat_sessions")
    return {"sessions": resp.data or []}
```

**Explanation:** It accepts `limit`, `offset`, `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `limit()`, `order()`, `select()`.

### `flag_chat_session`

- **File:** `fastapi-backend/app/routes/admin.py`
- **Lines:** `537-547`
- **Signature:** `async def flag_chat_session(`
- **Purpose:** Flag or unflag a chat session.

**Code:**
```python
async def flag_chat_session(
    session_id: str,
    payload: dict,
    user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Flag or unflag a chat session."""
    is_flagged = payload.get("is_flagged", True)
    client = get_supabase_client()
    client.table("chat_sessions").update({"is_flagged": is_flagged}).eq("id", session_id).execute()
    _log_admin_action(user.get("sub"), "flag_chat_session", details={"session_id": session_id, "is_flagged": is_flagged})
    return {"session_id": session_id, "is_flagged": is_flagged}
```

**Explanation:** It accepts `session_id`, `payload`, `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `get_supabase_client()`, `execute()`, `eq()`, `update()`.


## `fastapi-backend/app/routes/api.py`

**File:** `fastapi-backend/app/routes/api.py`

**Summary:** Source file `fastapi-backend/app/routes/api.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/routes/chat.py`

**File:** `fastapi-backend/app/routes/chat.py`

**Summary:** RAG-powered chat backend for LUMI AI Assistant.

### `_build_chat_prompt`

- **File:** `fastapi-backend/app/routes/chat.py`
- **Lines:** `23-53`
- **Signature:** `def _build_chat_prompt(query: str, chunks: list[dict], user_context: dict | None = None) -> str:`
- **Purpose:** Assemble the user prompt with retrieved context and source metadata.

**Code:**
```python
def _build_chat_prompt(query: str, chunks: list[dict], user_context: dict | None = None) -> str:
    """Assemble the user prompt with retrieved context and source metadata."""
    def _source_label(i: int, chunk: dict) -> str:
        srcs = chunk.get("sources", [])
        if srcs and isinstance(srcs[0], dict):
            title = srcs[0].get("title") or srcs[0].get("name") or ""
            url = srcs[0].get("url") or ""
            if title:
                return f"[Source {i+1}: {title}]"
        return f"[Source {i+1}]"

    context_lines = []
    for i, c in enumerate(chunks):
        label = _source_label(i, c)
        text = c.get("text", "").strip()
        context_lines.append(f"{label}\n{text}")

    sections = [
        "Retrieved Context:",
        "\n\n".join(context_lines) or "(No relevant documents found.)",
    ]

    if user_context:
        sections.extend([
            "",
            "User Context:",
            json.dumps(user_context, indent=2, ensure_ascii=False),
        ])

    sections.extend(["", f"User Question: {query}"])
    return "\n".join(sections)
```

**Explanation:** It accepts `query`, `chunks`, `user_context` and returns `str`. See the code below for the full implementation. Key calls include `get()`, `isinstance()`, `enumerate()`, `_source_label()`, `strip()`.

### `_retrieve_context`

- **File:** `fastapi-backend/app/routes/chat.py`
- **Lines:** `56-70`
- **Signature:** `def _retrieve_context(query: str, top_k: int = 5) -> list[dict]:`
- **Purpose:** Hybrid retrieval: semantic + keyword search with reranking.

**Code:**
```python
def _retrieve_context(query: str, top_k: int = 5) -> list[dict]:
    """Hybrid retrieval: semantic + keyword search with reranking."""
    try:
        from app.services.rag_hybrid import hybrid_search, rerank_results
        results = hybrid_search(query, top_k=top_k * 2)
        results = rerank_results(query, results, top_k=top_k)
        return results
    except Exception as exc:
        logger.warning("Hybrid RAG retrieval failed, falling back to semantic: %s", exc)
        try:
            from app.services.rag_pipeline import retrieve_context
            return retrieve_context(query=query, top_k=top_k)
        except Exception as exc2:
            logger.warning("Semantic RAG retrieval also failed: %s", exc2)
            return []
```

**Explanation:** It accepts `query`, `top_k` and returns `list[dict]`. See the code below for the full implementation. Key calls include `hybrid_search()`, `rerank_results()`, `warning()`, `retrieve_context()`.

### `_generate_response`

- **File:** `fastapi-backend/app/routes/chat.py`
- **Lines:** `73-102`
- **Signature:** `def _generate_response(prompt: str) -> str:`
- **Purpose:** Call Groq directly (no Gemini, no JSON mode) for fast chat responses.

**Code:**
```python
def _generate_response(prompt: str) -> str:
    """Call Groq directly (no Gemini, no JSON mode) for fast chat responses."""
    try:
        from app.services.groq_client import _get_groq_client
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    "You are LUMI, a Renewable Energy Decision Support Assistant for the Philippines.\n\n"
                    "CRITICAL INSTRUCTION — FOLLOW THIS EXACT ORDER:\n"
                    "STEP 1: Check if the user's message is ONLY a greeting (hello, hi, good morning, how are you, etc.). If YES, respond warmly and normally.\n"
                    "STEP 2: If the message contains ANY question or topic completely unrelated to energy, climate, the Philippines, or sustainability (e.g., sports, celebrities, cooking, gaming), you MUST decline with ONLY this exact response — do NOT answer the question, do NOT use context:\n"
                    '\"I\'m LUMI, a Renewable Energy Decision Support Assistant for the Philippines. I\'m not able to help with that topic. Let me know if you have questions about solar, wind, geothermal, energy policy, or sustainability!\"\n'
                    "STEP 3: If the question IS about the Philippines — including its geography, climate, weather, temperature, or general environment — treat it as on-topic because climate knowledge is essential for renewable-energy decisions. Answer using the Retrieved Context and your general knowledge.\n"
                    "STEP 4: Only if the question IS about renewable energy, energy policy, solar, wind, geothermal, hydro, biomass, energy efficiency, power grids, electricity, climate change, sustainability, or the Philippines energy sector, then answer using ONLY the provided Retrieved Context below.\n"
                    "STEP 5: If the Retrieved Context does not contain the answer, say so clearly.\n"
                    "STEP 6: Cite sources using [Source N: Title] notation (e.g., [Source 1: DOE Renewable Energy Plan]).\n"
                    "STEP 7: Answer in plain text (not JSON)."
                )},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1024,
        )
        text = response.choices[0].message.content or ""
        return text.strip()
    except Exception as exc:
        logger.warning("Groq chat generation failed: %s", exc)
        return "I'm sorry, I couldn't generate a response at this time. Our AI service is temporarily unavailable — please try again later."
```

**Explanation:** It accepts `prompt` and returns `str`. See the code below for the full implementation. Key calls include `_get_groq_client()`, `create()`, `strip()`, `warning()`.

### `chat_message`

- **File:** `fastapi-backend/app/routes/chat.py`
- **Lines:** `106-179`
- **Signature:** `async def chat_message(`
- **Purpose:** Receive a chat message, run hybrid RAG retrieval, generate AI response.

**Code:**
```python
async def chat_message(
    payload: dict,
    user: dict = Depends(get_verified_user),
) -> dict[str, Any]:
    """Receive a chat message, run hybrid RAG retrieval, generate AI response.

    Includes input guardrails, hybrid search + reranking, citation verification,
    output sanitization, and chat history persistence.

    Payload:
        message: str (required)
        session_id: str | None (optional; creates new session if omitted)
    """
    from app.services.rag_hybrid import (
        validate_input,
        sanitize_output,
        verify_citations,
        save_chat_message,
        create_chat_session,
        get_chat_history,
    )

    message_text = payload.get("message", "").strip()

    if not message_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

    # Input guardrails
    is_valid, error_msg = validate_input(message_text)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Session management
    session_id = payload.get("session_id")
    if not session_id:
        session_id = create_chat_session()

    # Save user message
    if session_id:
        save_chat_message(session_id, "user", message_text)

    # Retrieve context with hybrid search + reranking
    chunks = _retrieve_context(message_text)

    # Build prompt with chat history for multi-turn context
    history = get_chat_history(session_id, limit=10) if session_id else []
    prompt = _build_chat_prompt(message_text, chunks)

    # Generate response
    response_text = _generate_response(prompt)

    # Output sanitization
    response_text = sanitize_output(response_text)

    # Citation verification
    citation_result = verify_citations(response_text, chunks) if chunks else None

    # Save assistant message
    if session_id:
        save_chat_message(
            session_id,
            "assistant",
            response_text,
            retrieved_chunks=chunks,
            citation_verification=citation_result,
        )

    return {
        "session_id": session_id,
        "role": "assistant",
        "message": response_text,
        "retrieved_chunks": chunks,
        "citations": citation_result,
    }
```

**Explanation:** It accepts `payload`, `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `strip()`, `get()`, `HTTPException()`, `validate_input()`, `create_chat_session()`.

### `list_sessions`

- **File:** `fastapi-backend/app/routes/chat.py`
- **Lines:** `183-199`
- **Signature:** `async def list_sessions(user: dict = Depends(get_verified_user)) -> dict[str, Any]:`
- **Purpose:** List recent chat sessions for the authenticated user.

**Code:**
```python
async def list_sessions(user: dict = Depends(get_verified_user)) -> dict[str, Any]:
    """List recent chat sessions for the authenticated user."""
    try:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()
        resp = (
            client.table("chat_sessions")
            .select("id,created_at")
            .eq("user_id", user.get("sub"))
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return {"sessions": resp.data or []}
    except Exception as exc:
        logger.warning("Failed to list chat sessions: %s", exc)
        return {"sessions": []}
```

**Explanation:** It accepts `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `warning()`, `limit()`, `order()`.

### `get_session_messages`

- **File:** `fastapi-backend/app/routes/chat.py`
- **Lines:** `203-230`
- **Signature:** `async def get_session_messages(`
- **Purpose:** Get all messages for a specific chat session (owner only).

**Code:**
```python
async def get_session_messages(
    session_id: str,
    user: dict = Depends(get_verified_user),
) -> dict[str, Any]:
    """Get all messages for a specific chat session (owner only)."""
    from app.services.supabase_service import get_supabase_client
    from app.services.rag_hybrid import get_chat_history

    # Verify session ownership
    client = get_supabase_client()
    try:
        resp = (
            client.table("chat_sessions")
            .select("user_id")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not resp.data or resp.data.get("user_id") != user.get("sub"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Failed to verify session ownership: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve session")

    messages = get_chat_history(session_id, limit=50)
    return {"messages": messages}
```

**Explanation:** It accepts `session_id`, `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `HTTPException()`, `warning()`, `single()`.


## `fastapi-backend/app/routes/ecosim.py`

**File:** `fastapi-backend/app/routes/ecosim.py`

**Summary:** Source file `fastapi-backend/app/routes/ecosim.py`.

### `get_ecosim_results`

- **File:** `fastapi-backend/app/routes/ecosim.py`
- **Lines:** `25-40`
- **Signature:** `async def get_ecosim_results(`
- **Purpose:** Retrieves ecosim results.

**Code:**
```python
async def get_ecosim_results(
    params: EcosimQueryParams = Depends(),
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
):
    return build_ecosim_dashboard_response(
        municipality_id=params.municipality_id,
        monthly_consumption=params.monthly_consumption,
        monthly_bill=params.monthly_bill,
        desired_savings=params.desired_savings,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
        mode=params.mode,
    )
```

**Explanation:** It accepts `params`, `include_ai`, `use_rag`, `rag_query`. See the code below for the full implementation. Key calls include `build_ecosim_dashboard_response()`.

### `get_municipalities`

- **File:** `fastapi-backend/app/routes/ecosim.py`
- **Lines:** `44-45`
- **Signature:** `async def get_municipalities():`
- **Purpose:** Retrieves municipalities.

**Code:**
```python
async def get_municipalities():
    return {"items": list_municipalities()}
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `list_municipalities()`.

### `get_provinces`

- **File:** `fastapi-backend/app/routes/ecosim.py`
- **Lines:** `49-50`
- **Signature:** `async def get_provinces():`
- **Purpose:** Retrieves provinces.

**Code:**
```python
async def get_provinces():
    return {"items": list_provinces()}
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `list_provinces()`.

### `get_barangays`

- **File:** `fastapi-backend/app/routes/ecosim.py`
- **Lines:** `54-57`
- **Signature:** `async def get_barangays(`
- **Purpose:** Retrieves barangays.

**Code:**
```python
async def get_barangays(
    municipality_id: int | None = Query(default=None, description="Filter by municipality ID"),
):
    return {"items": list_barangays(municipality_id)}
```

**Explanation:** It accepts `municipality_id`. See the code below for the full implementation. Key calls include `list_barangays()`.

### `post_item`

- **File:** `fastapi-backend/app/routes/ecosim.py`
- **Lines:** `61-79`
- **Signature:** `async def post_item(`
- **Purpose:** Posts item.

**Code:**
```python
async def post_item(
    body: PostHouse,
    user: dict = Depends(get_verified_user),
    include_ai: bool = True,
    use_rag: bool = True,
    rag_query: str | None = None,
):
    response_data = renewable_energy_calculator(
        body.house_name,
        body.municipality,
        body.current_electricity_bill,
        body.electricity_rate,
        body.desired_savings,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
        mode=body.mode,
    )
    return response_data
```

**Explanation:** It accepts `body`, `user`, `include_ai`, `use_rag`, `rag_query`. See the code below for the full implementation. Key calls include `renewable_energy_calculator()`.


## `fastapi-backend/app/routes/energyhub.py`

**File:** `fastapi-backend/app/routes/energyhub.py`

**Summary:** Source file `fastapi-backend/app/routes/energyhub.py`.

### `get_overview`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `27-31`
- **Signature:** `async def get_overview():`
- **Purpose:** Return the EnergyHub overview: latest statistics, forecast summary,

**Code:**
```python
async def get_overview():
    """Return the EnergyHub overview: latest statistics, forecast summary,
    and model comparison results."""
    svc = get_energyhub_service()
    return svc.build_overview()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `build_overview()`.

### `get_forecast`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `35-45`
- **Signature:** `async def get_forecast(`
- **Purpose:** Return the ML forecast (2025-2030) with confidence intervals.

**Code:**
```python
async def get_forecast(
    metric: str = Query(default="consumption", description="Metric to forecast: consumption or peak_demand"),
):
    """Return the ML forecast (2025-2030) with confidence intervals.

    The underlying model is ARIMA(1,1,1) trained on 2003-2020 data
    and evaluated on 2021-2024. Pre-computed forecasts are served
    directly without runtime retraining.
    """
    svc = get_energyhub_service()
    return svc.get_forecast(metric)
```

**Explanation:** It accepts `metric`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_forecast()`.

### `get_trends`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `49-53`
- **Signature:** `async def get_trends():`
- **Purpose:** Return historical trends, forecast overlay, source breakdown,

**Code:**
```python
async def get_trends():
    """Return historical trends, forecast overlay, source breakdown,
    and grid-level breakdown for charting."""
    svc = get_energyhub_service()
    return svc.build_trends()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `build_trends()`.

### `get_map_data`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `57-79`
- **Signature:** `async def get_map_data(`
- **Purpose:** Return geographic data points for the choropleth map.

**Code:**
```python
async def get_map_data(
    metric: str = Query(
        default="renewable_potential",
        description=(
            "Metric for choropleth coloring. "
            "Options: renewable_potential, solar_potential, wind_potential, "
            "hydro_potential, geothermal_potential"
        ),
    ),
    level: str = Query(
        default="province",
        description="Geographic level: province, municipality, or barangay. Municipality/barangay require pre-computed suitability scores.",
    ),
):
    """Return geographic data points for the choropleth map.

    All metrics use sub-national data:
    - Province-level: aggregated from municipality climate/terrain/suitability scores.
    - Municipality-level: pre-computed suitability scores from Supabase.
    - Barangay-level: inherits parent municipality suitability scores with barangay centroids.
    """
    svc = get_energyhub_service()
    return svc.build_map_data(metric, level)
```

**Explanation:** It accepts `metric`, `level`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `build_map_data()`.

### `get_source_breakdown`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `83-88`
- **Signature:** `async def get_source_breakdown(`
- **Purpose:** Return generation by plant type for a given year.

**Code:**
```python
async def get_source_breakdown(
    year: int | None = Query(default=None, description="Year (defaults to latest)"),
):
    """Return generation by plant type for a given year."""
    svc = get_energyhub_service()
    return svc._ml.get_source_breakdown(year)
```

**Explanation:** It accepts `year`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_source_breakdown()`.

### `get_grid_breakdown`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `92-97`
- **Signature:** `async def get_grid_breakdown(`
- **Purpose:** Return generation by grid (Luzon, Visayas, Mindanao) for a given year.

**Code:**
```python
async def get_grid_breakdown(
    year: int | None = Query(default=None, description="Year (defaults to latest)"),
):
    """Return generation by grid (Luzon, Visayas, Mindanao) for a given year."""
    svc = get_energyhub_service()
    return svc._ml.get_grid_breakdown(year)
```

**Explanation:** It accepts `year`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_grid_breakdown()`.

### `get_model_comparison`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `101-104`
- **Signature:** `async def get_model_comparison():`
- **Purpose:** Return test-set performance metrics for all trained models.

**Code:**
```python
async def get_model_comparison():
    """Return test-set performance metrics for all trained models."""
    svc = get_energyhub_service()
    return {"items": svc._ml.get_model_comparison()}
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_model_comparison()`.

### `get_ai_insight`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `108-118`
- **Signature:** `async def get_ai_insight(`
- **Purpose:** Return a data-backed narrative insight and recommendation.

**Code:**
```python
async def get_ai_insight(
    use_llm: bool = Query(default=False, description="Use LLM (Gemini/Groq) for dynamic analysis instead of static text"),
):
    """Return a data-backed narrative insight and recommendation.

    Set use_llm=true to get a dynamically generated analysis from
    the configured LLM (Gemini or Groq) based on the latest energy
    statistics, generation mix, and ARIMA forecast.
    """
    svc = get_energyhub_service()
    return svc.get_ai_insight(use_llm=use_llm)
```

**Explanation:** It accepts `use_llm`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_ai_insight()`.

### `analyze_chart`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `122-136`
- **Signature:** `async def analyze_chart(`
- **Purpose:** Send chart data to the LLM and receive a narrative explanation.

**Code:**
```python
async def analyze_chart(
    payload: AnalyzeChartRequest,
    user: dict = Depends(get_verified_user),
    force_refresh: bool = Query(default=False, description="Bypass cache and generate a fresh LLM response"),
):
    """Send chart data to the LLM and receive a narrative explanation.

    Use this endpoint to get AI-powered interpretations of specific
    visualizations (trends, source breakdown, or map).

    Set force_refresh=true to bypass the database cache and generate a
    brand-new explanation (useful for rotating responses).
    """
    svc = get_energyhub_service()
    return svc.analyze_chart(payload.chart_type, payload.chart_data, force_refresh=force_refresh)
```

**Explanation:** It accepts `payload`, `user`, `force_refresh`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `analyze_chart()`.

### `get_provincial_demand`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `140-145`
- **Signature:** `async def get_provincial_demand(`
- **Purpose:** Return DOE Annex 8 provincial/regional consumption breakdown.

**Code:**
```python
async def get_provincial_demand(
    region: str | None = Query(default=None, description="Filter by region code (e.g., IV-A, NCR)"),
):
    """Return DOE Annex 8 provincial/regional consumption breakdown."""
    svc = get_energyhub_service()
    return svc.get_provincial_consumption(region)
```

**Explanation:** It accepts `region`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_provincial_consumption()`.

### `get_municipal_demand`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `149-158`
- **Signature:** `async def get_municipal_demand(`
- **Purpose:** Return population-weighted municipal demand estimates for a province.

**Code:**
```python
async def get_municipal_demand(
    province_id: int,
):
    """Return population-weighted municipal demand estimates for a province.

    Requires PSA population data to be loaded in the municipal_population table.
    If population data is missing, returns an empty list with a data-gap note.
    """
    svc = get_energyhub_service()
    return svc.estimate_municipal_demand(province_id)
```

**Explanation:** It accepts `province_id`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `estimate_municipal_demand()`.

### `get_irena_overview`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `162-168`
- **Signature:** `async def get_irena_overview():`
- **Purpose:** Return IRENA capacity, generation, and renewable share statistics.

**Code:**
```python
async def get_irena_overview():
    """Return IRENA capacity, generation, and renewable share statistics.

    Displayed alongside DOE data for cross-validation and ASEAN benchmarking.
    """
    svc = get_energyhub_service()
    return svc.build_irena_overview()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `build_irena_overview()`.

### `get_irena_capacity`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `172-175`
- **Signature:** `async def get_irena_capacity(year: int | None = Query(default=None)):`
- **Purpose:** Return IRENA Philippines electricity capacity by technology.

**Code:**
```python
async def get_irena_capacity(year: int | None = Query(default=None)):
    """Return IRENA Philippines electricity capacity by technology."""
    svc = get_energyhub_service()
    return svc.get_irena_capacity(year)
```

**Explanation:** It accepts `year`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_irena_capacity()`.

### `get_irena_generation`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `179-182`
- **Signature:** `async def get_irena_generation(year: int | None = Query(default=None)):`
- **Purpose:** Return IRENA Philippines electricity generation by technology.

**Code:**
```python
async def get_irena_generation(year: int | None = Query(default=None)):
    """Return IRENA Philippines electricity generation by technology."""
    svc = get_energyhub_service()
    return svc.get_irena_generation(year)
```

**Explanation:** It accepts `year`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_irena_generation()`.

### `get_irena_renewable_share`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `186-189`
- **Signature:** `async def get_irena_renewable_share():`
- **Purpose:** Return year-by-year renewable share of electricity generation (%).

**Code:**
```python
async def get_irena_renewable_share():
    """Return year-by-year renewable share of electricity generation (%)."""
    svc = get_energyhub_service()
    return svc.get_irena_renewable_share()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_irena_renewable_share()`.

### `get_meralco_rate`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `193-200`
- **Signature:** `async def get_meralco_rate(year: int | None = Query(default=None)):`
- **Purpose:** Return Meralco residential generation charge rate for a given year.

**Code:**
```python
async def get_meralco_rate(year: int | None = Query(default=None)):
    """Return Meralco residential generation charge rate for a given year.

    Note: this is the generation charge component only. The total
    residential rate includes transmission, distribution, and other charges.
    """
    svc = get_energyhub_service()
    return svc.get_meralco_rate(year)
```

**Explanation:** It accepts `year`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_meralco_rate()`.

### `get_solar_atlas`

- **File:** `fastapi-backend/app/routes/energyhub.py`
- **Lines:** `204-211`
- **Signature:** `async def get_solar_atlas(location: str | None = Query(default=None)):`
- **Purpose:** Return Global Solar Atlas v2 data for Philippine locations.

**Code:**
```python
async def get_solar_atlas(location: str | None = Query(default=None)):
    """Return Global Solar Atlas v2 data for Philippine locations.

    High-resolution solar irradiance (GHI, DNI, DIF) and PV power
    output sampled at key cities. Supplements NASA POWER data in EcoSim.
    """
    svc = get_energyhub_service()
    return svc.get_solar_atlas(location)
```

**Explanation:** It accepts `location`. See the code below for the full implementation. Key calls include `get_energyhub_service()`, `get_solar_atlas()`.


## `fastapi-backend/app/routes/etl.py`

**File:** `fastapi-backend/app/routes/etl.py`

**Summary:** ETL and data engineering API routes for LUMI.

### `run_climate_etl`

- **File:** `fastapi-backend/app/routes/etl.py`
- **Lines:** `20-44`
- **Signature:** `async def run_climate_etl() -> dict[str, Any]:`
- **Purpose:** Run the climate data ETL pipeline.

**Code:**
```python
async def run_climate_etl() -> dict[str, Any]:
    """Run the climate data ETL pipeline."""
    from app.services.etl_orchestrator import build_climate_etl_pipeline

    orchestrator = build_climate_etl_pipeline()
    results = orchestrator.run()

    return {
        "pipeline": orchestrator.pipeline_name,
        "steps": [
            {
                "step": r.step_name,
                "status": r.status,
                "rows_affected": r.rows_affected,
                "duration_seconds": r.duration_seconds,
                "error": r.error,
            }
            for r in results
        ],
        "summary": {
            "success": sum(1 for r in results if r.status == "success"),
            "failed": sum(1 for r in results if r.status == "failed"),
            "skipped": sum(1 for r in results if r.status == "skipped"),
        },
    }
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `build_climate_etl_pipeline()`, `run()`, `sum()`.

### `get_lineage`

- **File:** `fastapi-backend/app/routes/etl.py`
- **Lines:** `48-57`
- **Signature:** `async def get_lineage(`
- **Purpose:** View data lineage history.

**Code:**
```python
async def get_lineage(
    source: str | None = Query(default=None, description="Filter by data source"),
    table: str | None = Query(default=None, description="Filter by target table"),
    limit: int = Query(default=50, le=200),
) -> dict[str, Any]:
    """View data lineage history."""
    from app.services.etl_orchestrator import get_lineage_history

    history = get_lineage_history(source=source, table=table, limit=limit)
    return {"items": history, "count": len(history)}
```

**Explanation:** It accepts `source`, `table`, `limit` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_lineage_history()`, `len()`.

### `validate_table`

- **File:** `fastapi-backend/app/routes/etl.py`
- **Lines:** `61-97`
- **Signature:** `async def validate_table(`
- **Purpose:** Run basic validation checks on a Supabase table.

**Code:**
```python
async def validate_table(
    table: str = Query(..., description="Table name to validate"),
) -> dict[str, Any]:
    """Run basic validation checks on a Supabase table.

    Checks row count, null rates, and basic column statistics.
    """
    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()
    try:
        resp = client.table(table).select("*").limit(1000).execute()
        rows = resp.data or []

        if not rows:
            return {"table": table, "valid": False, "error": "No rows returned"}

        # Basic stats
        columns = list(rows[0].keys()) if rows else []
        null_counts: dict[str, int] = {}
        for col in columns:
            null_counts[col] = sum(1 for r in rows if r.get(col) is None)

        return {
            "table": table,
            "valid": True,
            "row_count_sampled": len(rows),
            "columns": columns,
            "null_counts": null_counts,
            "null_rates": {
                col: round(null_counts[col] / len(rows), 4) if rows else 0
                for col in columns
            },
        }
    except Exception as exc:
        logger.warning("Table validation failed for %s: %s", table, exc)
        return {"table": table, "valid": False, "error": str(exc)}
```

**Explanation:** It accepts `table` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `list()`, `sum()`, `len()`.


## `fastapi-backend/app/routes/example.py`

**File:** `fastapi-backend/app/routes/example.py`

**Summary:** Source file `fastapi-backend/app/routes/example.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/routes/forecast.py`

**File:** `fastapi-backend/app/routes/forecast.py`

**Summary:** Forecasting API routes for LUMI EnergyHub.

### `run_forecast`

- **File:** `fastapi-backend/app/routes/forecast.py`
- **Lines:** `30-70`
- **Signature:** `async def run_forecast(`
- **Purpose:** Run a SARIMA forecast on demand.

**Code:**
```python
async def run_forecast(
    metric: str = Query(default="consumption", description="consumption or peak_demand"),
    order_p: int = Query(default=1, description="AR order"),
    order_d: int = Query(default=1, description="Differencing order"),
    order_q: int = Query(default=1, description="MA order"),
    forecast_to: int = Query(default=2030, description="Forecast end year"),
) -> dict[str, Any]:
    """Run a SARIMA forecast on demand.

    Uses DOE historical data loaded by EnergyHubML.
    """
    ml = get_energyhub_ml()
    if ml._historical is None or ml._historical.empty:
        return {"error": "Historical data not available"}

    target_col = "total_consumption_gwh" if metric == "consumption" else "total_peak_demand_mw"

    config = SARIMAConfig(order=(order_p, order_d, order_q))
    forecast_years = list(range(2025, forecast_to + 1))

    result = run_forecast_pipeline(
        df=ml._historical,
        target_col=target_col,
        forecast_years=forecast_years,
        config=config,
    )

    # Log to model registry
    log_model_run(
        model_name=result.model_name,
        target_variable=target_col,
        metrics=result.metrics or {},
        hyperparameters={"order": list(config.order), "seasonal_order": list(config.seasonal_order)},
        run_type="train",
    )

    # Reconcile with cached forecast
    cached = ml.get_forecast(metric)
    reconciled = reconcile_forecast_cache(result, cached)

    return reconciled
```

**Explanation:** It accepts `metric`, `order_p`, `order_d`, `order_q`, `forecast_to` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_energyhub_ml()`, `SARIMAConfig()`, `list()`, `range()`, `run_forecast_pipeline()`.

### `run_backtest`

- **File:** `fastapi-backend/app/routes/forecast.py`
- **Lines:** `74-114`
- **Signature:** `async def run_backtest(`
- **Purpose:** Run walk-forward backtesting on historical data.

**Code:**
```python
async def run_backtest(
    metric: str = Query(default="consumption"),
    train_end_year: int = Query(default=2020),
    order_p: int = Query(default=1),
    order_d: int = Query(default=1),
    order_q: int = Query(default=1),
) -> dict[str, Any]:
    """Run walk-forward backtesting on historical data."""
    ml = get_energyhub_ml()
    if ml._historical is None or ml._historical.empty:
        return {"error": "Historical data not available"}

    target_col = "total_consumption_gwh" if metric == "consumption" else "total_peak_demand_mw"
    df = ml._historical.sort_values("year").reset_index(drop=True)
    series = df.set_index("year")[target_col]

    config = SARIMAConfig(order=(order_p, order_d, order_q))
    train_end_idx = (df["year"] <= train_end_year).sum()

    if train_end_idx >= len(series):
        return {"error": f"train_end_year {train_end_year} is at or after the end of data"}

    bt = backtest_walk_forward(series, train_end_idx, config)

    log_model_run(
        model_name=bt.model_name,
        target_variable=target_col,
        metrics=bt.metrics,
        hyperparameters={"order": list(config.order)},
        run_type="backtest",
    )

    return {
        "model_name": bt.model_name,
        "train_period": bt.train_period,
        "test_period": bt.test_period,
        "actual_values": bt.actual_values,
        "predicted_values": bt.predicted_values,
        "metrics": bt.metrics,
        "residuals": bt.residuals,
    }
```

**Explanation:** It accepts `metric`, `train_end_year`, `order_p`, `order_d`, `order_q` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_energyhub_ml()`, `reset_index()`, `sort_values()`, `set_index()`, `SARIMAConfig()`.

### `list_model_runs`

- **File:** `fastapi-backend/app/routes/forecast.py`
- **Lines:** `118-135`
- **Signature:** `async def list_model_runs(`
- **Purpose:** List recent model runs from the forecast_model_runs registry.

**Code:**
```python
async def list_model_runs(
    limit: int = Query(default=20, le=100),
) -> dict[str, Any]:
    """List recent model runs from the forecast_model_runs registry."""
    try:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()
        resp = (
            client.table("forecast_model_runs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return {"items": resp.data or []}
    except Exception as exc:
        logger.warning("Failed to fetch model runs: %s", exc)
        return {"items": [], "error": str(exc)}
```

**Explanation:** It accepts `limit` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `warning()`, `limit()`, `str()`.


## `fastapi-backend/app/routes/geospatial.py`

**File:** `fastapi-backend/app/routes/geospatial.py`

**Summary:** Geospatial API routes for centroid and climate data.

### `get_centroids`

- **File:** `fastapi-backend/app/routes/geospatial.py`
- **Lines:** `92-103`
- **Signature:** `async def get_centroids(`
- **Purpose:** Return all centroids for a given administrative level.

**Code:**
```python
async def get_centroids(
    level: str = Query(
        default="province",
        description="Geographic level: region, province, municipality, or barangay",
    ),
):
    """Return all centroids for a given administrative level.

    Data is sourced from geospatial_metadata table with Redis caching.
    """
    items = get_all_centroids(level)
    return {"level": level, "items": items}
```

**Explanation:** It accepts `level`. See the code below for the full implementation. Key calls include `get_all_centroids()`.

### `get_single_centroid`

- **File:** `fastapi-backend/app/routes/geospatial.py`
- **Lines:** `107-149`
- **Signature:** `async def get_single_centroid(`
- **Purpose:** Return centroid metadata for a single administrative unit.

**Code:**
```python
async def get_single_centroid(
    level: str,
    geo_id: int,
):
    """Return centroid metadata for a single administrative unit.

    Falls back to lat/lon columns in the admin table if geospatial_metadata
    has no entry.
    """
    meta = get_geospatial_metadata(level, geo_id)
    if meta:
        return {
            "level": level,
            "geo_id": geo_id,
            "centroid_lat": meta.get("centroid_lat"),
            "centroid_lon": meta.get("centroid_lon"),
            "area_km2": meta.get("area_km2"),
            "elevation_m": meta.get("elevation_m"),
            "source": meta.get("source", "geospatial_metadata"),
        }

    # Fallback to admin table lat/lon
    centroid = get_centroid_with_fallback(level, geo_id)
    if centroid:
        return {
            "level": level,
            "geo_id": geo_id,
            "centroid_lat": centroid[0],
            "centroid_lon": centroid[1],
            "area_km2": None,
            "elevation_m": None,
            "source": "admin_table_fallback",
        }

    return {
        "level": level,
        "geo_id": geo_id,
        "centroid_lat": None,
        "centroid_lon": None,
        "area_km2": None,
        "elevation_m": None,
        "source": None,
    }
```

**Explanation:** It accepts `level`, `geo_id`. See the code below for the full implementation. Key calls include `get_geospatial_metadata()`, `get()`, `get_centroid_with_fallback()`.

### `get_climate`

- **File:** `fastapi-backend/app/routes/geospatial.py`
- **Lines:** `157-179`
- **Signature:** `async def get_climate(`
- **Purpose:** Return monthly climate data for a geographic unit at a specific level.

**Code:**
```python
async def get_climate(
    level: str = Query(
        default="municipality",
        description="Geographic level: province, municipality, or barangay",
    ),
    geo_id: int = Query(..., description="Geographic unit ID"),
    year: int | None = Query(default=None, description="Year filter (e.g., 2024). Returns all years if omitted."),
):
    """Return monthly climate data for a geographic unit at a specific level.

    Data is sourced from the level-specific climate table:
    - province → province_climate_monthly
    - municipality → municipality_climate_monthly
    - barangay → barangay_climate_monthly
    """
    records = get_climate_data(level, geo_id, year)
    return {
        "level": level,
        "geo_id": geo_id,
        "year": year,
        "source": f"{level}_climate_monthly",
        "records": records,
    }
```

**Explanation:** It accepts `level`, `geo_id`, `year`. See the code below for the full implementation. Key calls include `get_climate_data()`.

### `get_climate_hierarchy`

- **File:** `fastapi-backend/app/routes/geospatial.py`
- **Lines:** `183-207`
- **Signature:** `async def get_climate_hierarchy(`
- **Purpose:** Return climate data with automatic fallback through the geographic hierarchy.

**Code:**
```python
async def get_climate_hierarchy(
    barangay_id: int | None = Query(default=None, description="Barangay ID"),
    municipality_id: int | None = Query(default=None, description="Municipality ID"),
    province_id: int | None = Query(default=None, description="Province ID"),
    year: int | None = Query(default=None, description="Year filter"),
):
    """Return climate data with automatic fallback through the geographic hierarchy.

    Tries barangay → municipality → province resolution.
    Returns the actual level used and the climate records.
    """
    actual_level, actual_geo_id, records = get_climate_with_fallback(
        barangay_id=barangay_id,
        municipality_id=municipality_id,
        province_id=province_id,
        year=year,
    )
    requested = "barangay" if barangay_id else ("municipality" if municipality_id else "province")
    return {
        "requested_level": requested,
        "actual_level": actual_level,
        "geo_id": actual_geo_id,
        "year": year,
        "records": records,
    }
```

**Explanation:** It accepts `barangay_id`, `municipality_id`, `province_id`, `year`. See the code below for the full implementation. Key calls include `get_climate_with_fallback()`.

### `get_province_climate_aggregate`

- **File:** `fastapi-backend/app/routes/geospatial.py`
- **Lines:** `211-227`
- **Signature:** `async def get_province_climate_aggregate(`
- **Purpose:** Return province climate data, aggregating from municipalities if needed.

**Code:**
```python
async def get_province_climate_aggregate(
    province_id: int = Query(..., description="Province ID"),
    year: int = Query(..., description="Year"),
):
    """Return province climate data, aggregating from municipalities if needed.

    If province_climate_monthly has no data for the given province/year,
    this endpoint computes averages from all municipalities in the province.
    """
    records = get_or_compute_province_climate(province_id, year)
    return {
        "level": "province",
        "geo_id": province_id,
        "year": year,
        "source": "province_climate_monthly_or_aggregated",
        "records": records,
    }
```

**Explanation:** It accepts `province_id`, `year`. See the code below for the full implementation. Key calls include `get_or_compute_province_climate()`.


## `fastapi-backend/app/routes/geothermal.py`

**File:** `fastapi-backend/app/routes/geothermal.py`

**Summary:** Source file `fastapi-backend/app/routes/geothermal.py`.

### `get_geothermal_plants`

- **File:** `fastapi-backend/app/routes/geothermal.py`
- **Lines:** `19-22`
- **Signature:** `async def get_geothermal_plants():`
- **Purpose:** Return the full list of Philippines geothermal power plants

**Code:**
```python
async def get_geothermal_plants():
    """Return the full list of Philippines geothermal power plants
    from the Global Energy Monitor (GEM) dataset."""
    return get_all_ph_geothermal_plants()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_all_ph_geothermal_plants()`.

### `get_geothermal_analysis`

- **File:** `fastapi-backend/app/routes/geothermal.py`
- **Lines:** `26-122`
- **Signature:** `async def get_geothermal_analysis(municipality_id: int):`
- **Purpose:** Return combined geothermal suitability and output for a municipality.

**Code:**
```python
async def get_geothermal_analysis(municipality_id: int):
    """Return combined geothermal suitability and output for a municipality."""
    client = get_supabase_client()

    # Fetch municipality coordinates for fallback on-the-fly computation
    muni_resp = (
        client.table("municipalities")
        .select("municipality_id, name, lat, lon")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )
    if not muni_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipality not found",
        )
    muni = muni_resp.data

    # Try pre-computed tables first
    suit_resp = (
        client.table("geothermal_suitability")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )
    out_resp = (
        client.table("geothermal_output")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )

    suitability = suit_resp.data
    output = out_resp.data

    # Fallback to on-the-fly if pre-computed rows are missing
    if not suitability or not output:
        lat = muni.get("lat")
        lon = muni.get("lon")
        if lat is None or lon is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Municipality missing coordinates; cannot compute geothermal.",
            )

        # Get surface temperature from climate averages
        temp_resp = (
            client.table("municipality_climate_monthly")
            .select("t2m")
            .eq("municipality_id", municipality_id)
            .limit(1)
            .execute()
        )
        surface_temp = None
        if temp_resp.data:
            surface_temp = float(temp_resp.data[0].get("t2m", 0))

        suit_data = compute_geothermal_suitability(lat, lon, surface_temp, municipality_id=municipality_id)
        out_data = compute_geothermal_output(
            surface_temp,
            suit_data.get("_gradient_c_km"),
            suit_data.get("aquifer_score"),
            suit_data.get("_perm_log10"),
        )

        if not suitability:
            suitability = {
                "municipality_id": municipality_id,
                "heat_flow_score": suit_data.get("heat_flow_score"),
                "fault_density": suit_data.get("fault_density"),
                "fault_distance_km": suit_data.get("fault_distance_km"),
                "volcano_distance_km": suit_data.get("volcano_distance_km"),
                "aquifer_score": suit_data.get("aquifer_score"),
                "temperature_score": suit_data.get("temperature_score"),
                "geothermal_score": suit_data.get("geothermal_score"),
                "classification": suit_data.get("classification"),
            }
        if not output:
            output = {
                "municipality_id": municipality_id,
                "reservoir_temperature_c": out_data.get("reservoir_temperature_c"),
                "estimated_flow_rate_kg_s": out_data.get("estimated_flow_rate_kg_s"),
                "thermal_power_mw": out_data.get("thermal_power_mw"),
                "electric_power_mw": out_data.get("electric_power_mw"),
                "annual_energy_gwh": out_data.get("annual_energy_gwh"),
                "confidence_score": out_data.get("confidence_score"),
                "source": out_data.get("source"),
                "assumption": out_data.get("assumption"),
            }

    return {
        "suitability": suitability,
        "output": output,
    }
```

**Explanation:** It accepts `municipality_id`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `eq()`, `select()`.

### `get_geothermal_simulation_params`

- **File:** `fastapi-backend/app/routes/geothermal.py`
- **Lines:** `126-163`
- **Signature:** `async def get_geothermal_simulation_params(municipality_id: int):`
- **Purpose:** Return simulation-ready geothermal parameters for EcoSim.

**Code:**
```python
async def get_geothermal_simulation_params(municipality_id: int):
    """Return simulation-ready geothermal parameters for EcoSim."""
    client = get_supabase_client()

    suit_resp = (
        client.table("geothermal_suitability")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )
    out_resp = (
        client.table("geothermal_output")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )

    if not suit_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geothermal suitability not found for this municipality.",
        )

    suit = suit_resp.data
    out = out_resp.data or {}

    return {
        "municipality_id": municipality_id,
        "heat_flow_score": suit.get("heat_flow_score"),
        "fault_distance_km": suit.get("fault_distance_km"),
        "volcano_distance_km": suit.get("volcano_distance_km"),
        "aquifer_score": suit.get("aquifer_score"),
        "reservoir_temperature_c": out.get("reservoir_temperature_c"),
        "estimated_flow_rate_kg_s": out.get("estimated_flow_rate_kg_s"),
        "classification": suit.get("classification"),
    }
```

**Explanation:** It accepts `municipality_id`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `eq()`, `select()`.

### `get_geothermal_dashboard_summary`

- **File:** `fastapi-backend/app/routes/geothermal.py`
- **Lines:** `167-245`
- **Signature:** `async def get_geothermal_dashboard_summary():`
- **Purpose:** Return province-level geothermal summary for EcoHub dashboard.

**Code:**
```python
async def get_geothermal_dashboard_summary():
    """Return province-level geothermal summary for EcoHub dashboard."""
    client = get_supabase_client()

    # Fetch all geothermal suitability rows with municipality -> province mapping
    suit_resp = (
        client.table("geothermal_suitability")
        .select("municipality_id, geothermal_score, classification")
        .execute()
    )
    muni_resp = (
        client.table("municipalities")
        .select("municipality_id, province_id, name")
        .execute()
    )
    prov_resp = (
        client.table("provinces")
        .select("province_id, name")
        .execute()
    )
    out_resp = (
        client.table("geothermal_output")
        .select("municipality_id, electric_power_mw")
        .execute()
    )

    suit_rows = suit_resp.data or []
    muni_rows = muni_resp.data or []
    prov_rows = prov_resp.data or []
    out_rows = out_resp.data or []

    muni_to_prov = {m["municipality_id"]: m.get("province_id") for m in muni_rows}
    prov_names = {p["province_id"]: p.get("name", "") for p in prov_rows}
    out_by_muni = {o["municipality_id"]: o.get("electric_power_mw", 0) or 0 for o in out_rows}

    from collections import defaultdict

    prov_data = defaultdict(lambda: {
        "scores": [],
        "electric_mw": [],
        "classifications": defaultdict(int),
    })

    for row in suit_rows:
        mid = row.get("municipality_id")
        pid = muni_to_prov.get(mid)
        if pid is None:
            continue
        prov_name = prov_names.get(pid, "")
        if not prov_name:
            continue
        prov_data[prov_name]["scores"].append(float(row.get("geothermal_score") or 0))
        cls = row.get("classification") or "Unknown"
        prov_data[prov_name]["classifications"][cls] += 1

    for row in out_rows:
        mid = row.get("municipality_id")
        pid = muni_to_prov.get(mid)
        if pid is None:
            continue
        prov_name = prov_names.get(pid, "")
        if not prov_name:
            continue
        prov_data[prov_name]["electric_mw"].append(float(row.get("electric_power_mw") or 0))

    result = []
    for prov_name, data in prov_data.items():
        scores = data["scores"]
        e_mw = data["electric_mw"]
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0
        total_mw = round(sum(e_mw), 3) if e_mw else 0.0
        result.append({
            "province": prov_name,
            "avg_geothermal_score": avg_score,
            "total_electric_potential_mw": total_mw,
            "classification_counts": dict(data["classifications"]),
        })

    return sorted(result, key=lambda x: x["avg_geothermal_score"], reverse=True)
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `select()`, `table()`, `get()`.


## `fastapi-backend/app/routes/health.py`

**File:** `fastapi-backend/app/routes/health.py`

**Summary:** Source file `fastapi-backend/app/routes/health.py`.

### `health_check`

- **File:** `fastapi-backend/app/routes/health.py`
- **Lines:** `16-18`
- **Signature:** `async def health_check() -> dict[str, Any]:`
- **Purpose:** Basic liveness probe.

**Code:**
```python
async def health_check() -> dict[str, Any]:
    """Basic liveness probe."""
    return {"status": "ok"}
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation.

### `detailed_health_check`

- **File:** `fastapi-backend/app/routes/health.py`
- **Lines:** `22-57`
- **Signature:** `async def detailed_health_check() -> dict[str, Any]:`
- **Purpose:** Detailed health check with dependency status.

**Code:**
```python
async def detailed_health_check() -> dict[str, Any]:
    """Detailed health check with dependency status."""
    uptime_s = round(time.time() - _start_time, 2)

    checks: dict[str, str] = {}

    # Supabase check
    try:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()
        resp = client.table("regions").select("region_id").limit(1).execute()
        checks["supabase"] = "ok" if resp.data is not None else "degraded"
    except Exception:
        checks["supabase"] = "error"

    # Redis check (optional)
    try:
        checks["redis"] = "ok" if is_redis_available() else "not_configured"
    except Exception:
        checks["redis"] = "not_configured"

    # RAG index check
    try:
        from app.services.rag_pipeline import index_stats
        stats = index_stats()
        checks["rag_index"] = "ok" if stats.get("index_present") else "not_loaded"
    except Exception:
        checks["rag_index"] = "not_loaded"

    all_ok = all(v in ("ok", "not_configured", "not_loaded") for v in checks.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "uptime_seconds": uptime_s,
        "checks": checks,
    }
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `round()`, `time()`, `get_supabase_client()`, `execute()`, `limit()`.


## `fastapi-backend/app/routes/map.py`

**File:** `fastapi-backend/app/routes/map.py`

**Summary:** Map API routes for LUMI GIS/mapping.

### `_normalize_level`

- **File:** `fastapi-backend/app/routes/map.py`
- **Lines:** `23-26`
- **Signature:** `def _normalize_level(level: str | None) -> str:`
- **Purpose:** Strip trailing IDs (e.g. 'municipality:1') and validate the level.

**Code:**
```python
def _normalize_level(level: str | None) -> str:
    """Strip trailing IDs (e.g. 'municipality:1') and validate the level."""
    normalized = (level or "municipality").split(":")[0].lower().strip()
    return normalized if normalized in {"municipality", "province"} else "municipality"
```

**Explanation:** It accepts `level` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `lower()`, `split()`.

### `psgc_hierarchy`

- **File:** `fastapi-backend/app/routes/map.py`
- **Lines:** `30-48`
- **Signature:** `async def psgc_hierarchy(`
- **Purpose:** Fetch PSGC administrative hierarchy.

**Code:**
```python
async def psgc_hierarchy(
    municipality_id: int | None = Query(default=None),
    province_id: int | None = Query(default=None),
) -> dict[str, Any]:
    """Fetch PSGC administrative hierarchy.

    Provide either municipality_id or province_id to get the full
    administrative chain (region → province → municipality → barangays).
    """
    if not municipality_id and not province_id:
        return {
            "error": "Provide either municipality_id or province_id"
        }

    hierarchy = get_psgc_hierarchy(
        municipality_id=municipality_id,
        province_id=province_id,
    )
    return hierarchy
```

**Explanation:** It accepts `municipality_id`, `province_id` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_psgc_hierarchy()`.

### `coverage_summary`

- **File:** `fastapi-backend/app/routes/map.py`
- **Lines:** `52-62`
- **Signature:** `async def coverage_summary(`
- **Purpose:** Return data coverage summary for a given admin level.

**Code:**
```python
async def coverage_summary(
    level: str = Query(
        default="municipality",
        description="Geographic level: municipality or province",
    ),
) -> dict[str, Any]:
    """Return data coverage summary for a given admin level.

    Shows how many geographic units have climate data, suitability scores, etc.
    """
    return get_coverage_summary(level=_normalize_level(level))
```

**Explanation:** It accepts `level` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_coverage_summary()`, `_normalize_level()`.

### `get_suitability_map`

- **File:** `fastapi-backend/app/routes/map.py`
- **Lines:** `66-92`
- **Signature:** `async def get_suitability_map(`
- **Purpose:** Return suitability map data for a renewable type.

**Code:**
```python
async def get_suitability_map(
    renewable_type: str,
    level: str = Query(
        default="municipality",
        description="Geographic level: municipality or province",
    ),
    use_cache: bool = Query(default=True),
) -> dict[str, Any]:
    """Return suitability map data for a renewable type.

    Returns a list of geographic units with their suitability scores
    and centroid coordinates, suitable for choropleth map rendering.
    """
    valid_types = {"solar", "wind", "hydro", "geothermal"}
    if renewable_type not in valid_types:
        return {
            "error": f"Invalid renewable_type '{renewable_type}'. Must be one of: {', '.join(valid_types)}"
        }

    normalized_level = _normalize_level(level)
    data = get_map_data(renewable_type, level=normalized_level, use_cache=use_cache)
    return {
        "renewable_type": renewable_type,
        "level": normalized_level,
        "count": len(data),
        "items": data,
    }
```

**Explanation:** It accepts `renewable_type`, `level`, `use_cache` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `join()`, `_normalize_level()`, `get_map_data()`, `len()`.


## `fastapi-backend/app/routes/products.py`

**File:** `fastapi-backend/app/routes/products.py`

**Summary:** Source file `fastapi-backend/app/routes/products.py`.

### `recommend_products`

- **File:** `fastapi-backend/app/routes/products.py`
- **Lines:** `19-29`
- **Signature:** `async def recommend_products(`
- **Purpose:** Get context-aware product recommendations for a renewable energy type.

**Code:**
```python
async def recommend_products(
    energy_type: str = Query(..., description="Renewable type: solar, wind, hydro, geothermal"),
    budget_php: float | None = Query(default=None, description="Optional budget ceiling in PHP"),
    limit: int = Query(default=5, ge=1, le=20),
):
    """Get context-aware product recommendations for a renewable energy type.

    Returns actual scraped products from Alibaba, Amazon, Lazada, and Shopee.
    Links are not fabricated; products without URLs are excluded.
    """
    return get_product_recommendations(energy_type, budget_php=budget_php, limit=limit)
```

**Explanation:** It accepts `energy_type`, `budget_php`, `limit`. See the code below for the full implementation. Key calls include `get_product_recommendations()`.

### `browse_products_endpoint`

- **File:** `fastapi-backend/app/routes/products.py`
- **Lines:** `33-51`
- **Signature:** `async def browse_products_endpoint(`
- **Purpose:** Browse all scraped products with filters and pagination.

**Code:**
```python
async def browse_products_endpoint(
    category: str | None = Query(default=None),
    subcategory: str | None = Query(default=None),
    source_site: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """Browse all scraped products with filters and pagination."""
    return browse_products(
        category=category,
        subcategory=subcategory,
        source_site=source_site,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size,
    )
```

**Explanation:** It accepts `category`, `subcategory`, `source_site`, `min_price`, `max_price`, `page`, `page_size`. See the code below for the full implementation. Key calls include `browse_products()`.

### `product_audit`

- **File:** `fastapi-backend/app/routes/products.py`
- **Lines:** `55-61`
- **Signature:** `async def product_audit():`
- **Purpose:** Return a data quality audit of the scraped product dataset.

**Code:**
```python
async def product_audit():
    """Return a data quality audit of the scraped product dataset.

    Includes counts of missing URLs, misclassified categories, and
    recommendations for scraper improvements.
    """
    return get_product_data_audit()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `get_product_data_audit()`.


## `fastapi-backend/app/routes/protected.py`

**File:** `fastapi-backend/app/routes/protected.py`

**Summary:** Source file `fastapi-backend/app/routes/protected.py`.

### `read_me`

- **File:** `fastapi-backend/app/routes/protected.py`
- **Lines:** `19-20`
- **Signature:** `async def read_me(user=Depends(get_current_user_with_role_and_plan)):`
- **Purpose:** Reads me.

**Code:**
```python
async def read_me(user=Depends(get_current_user_with_role_and_plan)):
    return {"user": user}
```

**Explanation:** It accepts `user`. See the code below for the full implementation.

### `get_profile`

- **File:** `fastapi-backend/app/routes/protected.py`
- **Lines:** `24-36`
- **Signature:** `async def get_profile(user: dict = Depends(get_verified_user)) -> dict:`
- **Purpose:** Return the authenticated user's extended profile.

**Code:**
```python
async def get_profile(user: dict = Depends(get_verified_user)) -> dict:
    """Return the authenticated user's extended profile."""
    client = get_supabase_client()
    resp = (
        client.table("profiles")
        .select("*")
        .eq("id", user.get("sub"))
        .single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return {"profile": resp.data}
```

**Explanation:** It accepts `user` and returns `dict`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `eq()`, `get()`.

### `update_profile`

- **File:** `fastapi-backend/app/routes/protected.py`
- **Lines:** `40-54`
- **Signature:** `async def update_profile(payload: dict, user: dict = Depends(get_verified_user)) -> dict:`
- **Purpose:** Update the authenticated user's profile fields.

**Code:**
```python
async def update_profile(payload: dict, user: dict = Depends(get_verified_user)) -> dict:
    """Update the authenticated user's profile fields."""
    allowed_fields = {"full_name", "organization", "location", "preferred_municipality_id", "avatar_url"}
    updates = {k: v for k, v in payload.items() if k in allowed_fields}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update")

    client = get_supabase_client()
    resp = (
        client.table("profiles")
        .update(updates)
        .eq("id", user.get("sub"))
        .execute()
    )
    return {"profile": resp.data[0] if resp.data else None}
```

**Explanation:** It accepts `payload`, `user` and returns `dict`. See the code below for the full implementation. Key calls include `items()`, `HTTPException()`, `get_supabase_client()`, `execute()`, `eq()`.

### `sync_avatar`

- **File:** `fastapi-backend/app/routes/protected.py`
- **Lines:** `58-89`
- **Signature:** `async def sync_avatar(user: dict = Depends(get_verified_user)) -> dict:`
- **Purpose:** Sync avatar_url from auth.user_metadata into public.profiles.

**Code:**
```python
async def sync_avatar(user: dict = Depends(get_verified_user)) -> dict:
    """Sync avatar_url from auth.user_metadata into public.profiles.

    Creates a minimal profile row if one doesn't exist yet.
    """
    client = get_supabase_client()
    user_id = user.get("sub")
    metadata = user.get("user_metadata") or {}
    avatar_url = metadata.get("avatar_url") or metadata.get("picture")
    full_name = metadata.get("full_name") or metadata.get("name")

    # Check if profile exists
    existing = client.table("profiles").select("id").eq("id", user_id).single().execute()

    if existing.data:
        updates: dict[str, Any] = {}
        if avatar_url:
            updates["avatar_url"] = avatar_url
        if full_name:
            updates["full_name"] = full_name
        if updates:
            client.table("profiles").update(updates).eq("id", user_id).execute()
    else:
        client.table("profiles").insert({
            "id": user_id,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "plan": "free",
            "is_active": True,
        }).execute()

    return {"avatar_url": avatar_url, "full_name": full_name}
```

**Explanation:** It accepts `user` and returns `dict`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `get()`, `execute()`, `single()`, `eq()`.

### `store_session`

- **File:** `fastapi-backend/app/routes/protected.py`
- **Lines:** `93-101`
- **Signature:** `async def store_session(payload: SessionPayload, ttl_seconds: int = 3600, user=Depends(get_verified_user)):`
- **Purpose:** Handles store session.

**Code:**
```python
async def store_session(payload: SessionPayload, ttl_seconds: int = 3600, user=Depends(get_verified_user)):
    redis = get_redis()
    user_id = user.get("sub")
    key = f"user:{user_id}:session"
    serialized = json.dumps(payload.data)
    if len(serialized) > 10_000:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Session payload too large")
    await redis.set(key, serialized, ex=ttl_seconds)
    return {"stored": True, "key": key}
```

**Explanation:** It accepts `payload`, `ttl_seconds`, `user`. See the code below for the full implementation. Key calls include `get_redis()`, `get()`, `dumps()`, `len()`, `HTTPException()`.


## `fastapi-backend/app/routes/simulations.py`

**File:** `fastapi-backend/app/routes/simulations.py`

**Summary:** Source file `fastapi-backend/app/routes/simulations.py`.

### `_get_free_sim_limit`

- **File:** `fastapi-backend/app/routes/simulations.py`
- **Lines:** `26-37`
- **Signature:** `def _get_free_sim_limit() -> int | None:`
- **Purpose:** Fetch the current free simulation limit from system_config.

**Code:**
```python
def _get_free_sim_limit() -> int | None:
    """Fetch the current free simulation limit from system_config."""
    client = get_supabase_client()
    try:
        resp = client.table("system_config").select("value").eq("key", "global").single().execute()
        if resp.data:
            value = resp.data.get("value", {})
            limit = value.get("free_sim_limit")
            return int(limit) if limit is not None else None
    except Exception as exc:
        logger.warning("Free sim limit fetch failed, using default: %s", exc)
    return 3
```

**Explanation:** It accepts zero arguments and returns `int | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `get()`, `warning()`, `single()`.

### `_count_user_simulations`

- **File:** `fastapi-backend/app/routes/simulations.py`
- **Lines:** `40-52`
- **Signature:** `def _count_user_simulations(user_id: str) -> int:`
- **Purpose:** Count existing saved simulations for a user.

**Code:**
```python
def _count_user_simulations(user_id: str) -> int:
    """Count existing saved simulations for a user."""
    client = get_supabase_client()
    try:
        resp = (
            client.table("saved_simulations")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return resp.count or 0
    except Exception:
        return 0
```

**Explanation:** It accepts `user_id` and returns `int`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `eq()`, `select()`, `table()`.

### `create_simulation`

- **File:** `fastapi-backend/app/routes/simulations.py`
- **Lines:** `56-100`
- **Signature:** `async def create_simulation(`
- **Purpose:** Save a new simulation for the authenticated user.

**Code:**
```python
async def create_simulation(
    payload: SimulationCreate,
    user: dict = Depends(get_current_user_with_role_and_plan),
) -> dict[str, Any]:
    """Save a new simulation for the authenticated user."""
    user_id = user.get("sub")
    plan = user.get("plan", "free")

    # Usage limit check for free users
    if plan not in ("premium", "admin", "dev"):
        free_limit = _get_free_sim_limit()
        if free_limit is not None:
            current_count = _count_user_simulations(user_id)
            if current_count >= free_limit:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "Simulation save limit reached for your plan.",
                        "limit": free_limit,
                        "current": current_count,
                        "upgrade": True,
                    },
                )

    client = get_supabase_client()
    try:
        resp = (
            client.table("saved_simulations")
            .insert({
                "user_id": user_id,
                "label": payload.label,
                "municipality_id": payload.municipality_id,
                "inputs": payload.inputs,
                "results": payload.results,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
        return {"simulation": resp.data[0] if resp.data else None}
    except Exception as exc:
        logger.error("Failed to save simulation for user=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save simulation",
        )
```

**Explanation:** It accepts `payload`, `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `_get_free_sim_limit()`, `_count_user_simulations()`, `HTTPException()`, `get_supabase_client()`.

### `list_simulations`

- **File:** `fastapi-backend/app/routes/simulations.py`
- **Lines:** `104-128`
- **Signature:** `async def list_simulations(`
- **Purpose:** List saved simulations for the authenticated user.

**Code:**
```python
async def list_simulations(
    user: dict = Depends(get_verified_user),
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """List saved simulations for the authenticated user."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        resp = (
            client.table("saved_simulations")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .offset(offset)
            .execute()
        )
        return {"simulations": resp.data or [], "limit": limit, "offset": offset}
    except Exception as exc:
        logger.error("Failed to fetch simulations for user=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch simulations",
        )
```

**Explanation:** It accepts `user`, `limit`, `offset` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `get_supabase_client()`, `execute()`, `error()`, `HTTPException()`.

### `get_simulation`

- **File:** `fastapi-backend/app/routes/simulations.py`
- **Lines:** `132-161`
- **Signature:** `async def get_simulation(`
- **Purpose:** Get a single saved simulation by ID (owner only).

**Code:**
```python
async def get_simulation(
    simulation_id: str,
    user: dict = Depends(get_verified_user),
) -> dict[str, Any]:
    """Get a single saved simulation by ID (owner only)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        resp = (
            client.table("saved_simulations")
            .select("*")
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not resp.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or access denied",
            )
        return {"simulation": resp.data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch simulation %s for user=%s: %s", simulation_id, user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch simulation",
        )
```

**Explanation:** It accepts `simulation_id`, `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `get_supabase_client()`, `execute()`, `HTTPException()`, `error()`.

### `update_simulation`

- **File:** `fastapi-backend/app/routes/simulations.py`
- **Lines:** `165-204`
- **Signature:** `async def update_simulation(`
- **Purpose:** Update a saved simulation's label (owner only).

**Code:**
```python
async def update_simulation(
    simulation_id: str,
    payload: SimulationUpdate,
    user: dict = Depends(get_verified_user),
) -> dict[str, Any]:
    """Update a saved simulation's label (owner only)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        # Verify ownership
        existing = (
            client.table("saved_simulations")
            .select("id")
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or access denied",
            )

        resp = (
            client.table("saved_simulations")
            .update({"label": payload.label})
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .execute()
        )
        return {"simulation": resp.data[0] if resp.data else None}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to update simulation %s for user=%s: %s", simulation_id, user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update simulation",
        )
```

**Explanation:** It accepts `simulation_id`, `payload`, `user` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `get_supabase_client()`, `execute()`, `HTTPException()`, `error()`.

### `delete_simulation`

- **File:** `fastapi-backend/app/routes/simulations.py`
- **Lines:** `208-239`
- **Signature:** `async def delete_simulation(`
- **Purpose:** Delete a saved simulation (owner only).

**Code:**
```python
async def delete_simulation(
    simulation_id: str,
    user: dict = Depends(get_verified_user),
) -> None:
    """Delete a saved simulation (owner only)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        # Verify ownership
        existing = (
            client.table("saved_simulations")
            .select("id")
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or access denied",
            )

        client.table("saved_simulations").delete().eq("id", simulation_id).execute()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete simulation %s for user=%s: %s", simulation_id, user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete simulation",
        )
```

**Explanation:** It accepts `simulation_id`, `user` and returns `None`. See the code below for the full implementation. Key calls include `get()`, `get_supabase_client()`, `execute()`, `HTTPException()`, `error()`.


## `fastapi-backend/app/schemas/__init__.py`

**File:** `fastapi-backend/app/schemas/__init__.py`

**Summary:** Source file `fastapi-backend/app/schemas/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/schemas/ecosim.py`

**File:** `fastapi-backend/app/schemas/ecosim.py`

**Summary:** Source file `fastapi-backend/app/schemas/ecosim.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/schemas/energyhub.py`

**File:** `fastapi-backend/app/schemas/energyhub.py`

**Summary:** Source file `fastapi-backend/app/schemas/energyhub.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/schemas/example.py`

**File:** `fastapi-backend/app/schemas/example.py`

**Summary:** Source file `fastapi-backend/app/schemas/example.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/schemas/geothermal.py`

**File:** `fastapi-backend/app/schemas/geothermal.py`

**Summary:** Source file `fastapi-backend/app/schemas/geothermal.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/schemas/products.py`

**File:** `fastapi-backend/app/schemas/products.py`

**Summary:** Source file `fastapi-backend/app/schemas/products.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/__init__.py`

**File:** `fastapi-backend/app/services/__init__.py`

**Summary:** Source file `fastapi-backend/app/services/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/climate_service.py`

**File:** `fastapi-backend/app/services/climate_service.py`

**Summary:** Climate data service for multi-resolution geographic queries.

### `determine_resolution`

- **File:** `fastapi-backend/app/services/climate_service.py`
- **Lines:** `29-41`
- **Signature:** `def determine_resolution(`
- **Purpose:** Determine the finest available geographic resolution.

**Code:**
```python
def determine_resolution(
    province_id: int | None = None,
    municipality_id: int | None = None,
    barangay_id: int | None = None,
) -> str:
    """Determine the finest available geographic resolution."""
    if barangay_id is not None:
        return "barangay"
    if municipality_id is not None:
        return "municipality"
    if province_id is not None:
        return "province"
    return "national"
```

**Explanation:** It accepts `province_id`, `municipality_id`, `barangay_id` and returns `str`. See the code below for the full implementation.

### `get_climate_data`

- **File:** `fastapi-backend/app/services/climate_service.py`
- **Lines:** `66-114`
- **Signature:** `def get_climate_data(`
- **Purpose:** Fetch climate data for a geographic unit at a given level.

**Code:**
```python
def get_climate_data(
    level: str,
    geo_id: int,
    year: int | None = None,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    """Fetch climate data for a geographic unit at a given level.

    Args:
        level: 'province', 'municipality', or 'barangay'
        geo_id: The ID for the given level
        year: Optional year filter. If None, returns all years.
        use_cache: Whether to use Redis cache.

    Returns:
        List of monthly climate records.
    """
    if level not in _CLIMATE_TABLES:
        logger.warning("Unknown climate level: %s", level)
        return []

    # Try cache first
    cache_year = year if year else "all"
    if use_cache:
        cached = get_climate_cache_sync(level, geo_id, cache_year)
        if cached:
            logger.debug("Climate cache hit: %s/%s/%s", level, geo_id, cache_year)
            return cached

    # Query Supabase
    table = _CLIMATE_TABLES[level]
    fk_col = _CLIMATE_FK_COL[level]
    client = get_supabase_client()

    try:
        query = client.table(table).select("*").eq(fk_col, str(geo_id))
        if year is not None:
            query = query.eq("year", str(year))
        query = query.order("year", desc=False).order("month", desc=False)
        resp = query.execute()
        rows = resp.data or []
    except Exception as exc:
        logger.warning("Climate query failed for %s/%s: %s", level, geo_id, exc)
        return []

    if use_cache and rows:
        set_climate_cache_sync(level, geo_id, cache_year, rows)

    return rows
```

**Explanation:** It accepts `level`, `geo_id`, `year`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `warning()`, `get_climate_cache_sync()`, `debug()`, `get_supabase_client()`, `eq()`.

### `get_climate_with_fallback`

- **File:** `fastapi-backend/app/services/climate_service.py`
- **Lines:** `117-157`
- **Signature:** `def get_climate_with_fallback(`
- **Purpose:** Fetch climate data with automatic fallback.

**Code:**
```python
def get_climate_with_fallback(
    barangay_id: int | None = None,
    municipality_id: int | None = None,
    province_id: int | None = None,
    year: int | None = None,
) -> tuple[str, int, list[dict[str, Any]]]:
    """Fetch climate data with automatic fallback.

    Tries barangay → municipality → province resolution.
    Returns (actual_level, actual_geo_id, climate_records).

    Fallback strategy:
    1. Try the finest available level (barangay > municipality > province)
    2. If no data at that level, fall back to the next coarser level
    3. If no data at any level, return empty list
    """
    # Build resolution chain
    chain: list[tuple[str, int]] = []
    if barangay_id is not None:
        chain.append(("barangay", barangay_id))
    if municipality_id is not None:
        chain.append(("municipality", municipality_id))
    if province_id is not None:
        chain.append(("province", province_id))

    if not chain:
        logger.warning("No geographic IDs provided for climate lookup")
        return ("none", 0, [])

    for level, gid in chain:
        data = get_climate_data(level, gid, year)
        if data:
            logger.debug("Climate data found at %s level (id=%s): %s records", level, gid, len(data))
            return (level, gid, data)

    # All levels returned empty
    logger.info(
        "No climate data found at any level for barangay=%s, muni=%s, prov=%s",
        barangay_id, municipality_id, province_id,
    )
    return (chain[0][0], chain[0][1], [])
```

**Explanation:** It accepts `barangay_id`, `municipality_id`, `province_id`, `year` and returns `tuple[str, int, list[dict[str, Any]]]`. See the code below for the full implementation. Key calls include `append()`, `warning()`, `get_climate_data()`, `debug()`, `len()`.

### `get_or_compute_province_climate`

- **File:** `fastapi-backend/app/services/climate_service.py`
- **Lines:** `165-242`
- **Signature:** `def get_or_compute_province_climate(`
- **Purpose:** Get province climate from dedicated table, or compute from municipalities.

**Code:**
```python
def get_or_compute_province_climate(
    province_id: int,
    year: int,
    client=None,
) -> list[dict[str, Any]]:
    """Get province climate from dedicated table, or compute from municipalities.

    If province_climate_monthly has data for this province/year, return it.
    Otherwise, aggregate from municipality_climate_monthly for all
    municipalities in the province.
    """
    # Try province table first
    data = get_climate_data("province", province_id, year)
    if data:
        return data

    # Fall back to aggregating from municipalities
    if client is None:
        client = get_supabase_client()

    try:
        # Get all municipality IDs in this province
        muni_resp = (
            client.table("municipalities")
            .select("municipality_id")
            .eq("province_id", str(province_id))
            .execute()
        )
        muni_ids = [r["municipality_id"] for r in (muni_resp.data or [])]
        if not muni_ids:
            return []

        # Fetch all municipality climate data for the year
        all_rows = []
        for mid in muni_ids:
            rows = get_climate_data("municipality", mid, year)
            all_rows.extend(rows)

        if not all_rows:
            return []

        # Aggregate by month
        from collections import defaultdict
        import statistics

        monthly: dict[int, list[dict]] = defaultdict(list)
        for r in all_rows:
            month = r.get("month")
            if month is not None:
                monthly[month].append(r)

        aggregated = []
        climate_cols = [
            "t2m", "t2m_max", "t2m_min", "rh2m", "prectotcorr",
            "ws10m", "allsky_sfc_sw_dwn", "cloud_amt", "surface_pressure",
            "elevation", "rhoa",
        ]
        for month in sorted(monthly.keys()):
            records = monthly[month]
            agg = {
                "province_id": province_id,
                "year": year,
                "month": month,
                "source": "aggregated_from_municipalities",
            }
            for col in climate_cols:
                values = [r.get(col) for r in records if r.get(col) is not None]
                if values:
                    agg[col] = round(statistics.mean(values), 4)
                else:
                    agg[col] = None
            aggregated.append(agg)

        return aggregated

    except Exception as exc:
        logger.warning("Province climate aggregation failed for %s/%s: %s", province_id, year, exc)
        return []
```

**Explanation:** It accepts `province_id`, `year`, `client` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_climate_data()`, `get_supabase_client()`, `execute()`, `defaultdict()`, `sorted()`.

### `get_barangay_climate_or_fallback`

- **File:** `fastapi-backend/app/services/climate_service.py`
- **Lines:** `250-277`
- **Signature:** `def get_barangay_climate_or_fallback(`
- **Purpose:** Get barangay climate data, falling back to municipality then province.

**Code:**
```python
def get_barangay_climate_or_fallback(
    barangay_id: int,
    municipality_id: int,
    province_id: int,
    year: int | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Get barangay climate data, falling back to municipality then province.

    Returns (source_level, climate_records).
    """
    # 1. Try barangay table
    data = get_climate_data("barangay", barangay_id, year)
    if data:
        return ("barangay", data)

    # 2. Fall back to municipality
    data = get_climate_data("municipality", municipality_id, year)
    if data:
        logger.info("Barangay %s climate falling back to municipality %s", barangay_id, municipality_id)
        return ("municipality", data)

    # 3. Fall back to province
    data = get_or_compute_province_climate(province_id, year or 2024)
    if data:
        logger.info("Barangay %s climate falling back to province %s", barangay_id, province_id)
        return ("province", data)

    return ("none", [])
```

**Explanation:** It accepts `barangay_id`, `municipality_id`, `province_id`, `year` and returns `tuple[str, list[dict[str, Any]]]`. See the code below for the full implementation. Key calls include `get_climate_data()`, `info()`, `get_or_compute_province_climate()`.


## `fastapi-backend/app/services/confidence.py`

**File:** `fastapi-backend/app/services/confidence.py`

**Summary:** Confidence and uncertainty scoring for LUMI EcoSim.

### `_score_data_coverage`

- **File:** `fastapi-backend/app/services/confidence.py`
- **Lines:** `32-53`
- **Signature:** `def _score_data_coverage(f: ConfidenceFactors) -> float:`
- **Purpose:** Score 0-1 based on how much data is available.

**Code:**
```python
def _score_data_coverage(f: ConfidenceFactors) -> float:
    """Score 0-1 based on how much data is available."""
    score = 0.0
    max_vars = 10  # T2M, T2M_MAX, T2M_MIN, RH2M, PRECTOTCORR, WS10M, ALLSKY_SFC_SW_DWN, CLOUD_AMT, PS, RHOA

    if f.has_climate_data:
        score += 0.3
        score += 0.3 * min(f.climate_variables_count / max_vars, 1.0)

    if f.has_terrain_data:
        score += 0.15

    if f.has_population_data:
        score += 0.1

    if f.has_tariff_data:
        score += 0.1

    if f.user_provided_inputs:
        score += 0.05

    return min(score, 1.0)
```

**Explanation:** It accepts `f` and returns `float`. See the code below for the full implementation. Key calls include `min()`.

### `_score_data_recency`

- **File:** `fastapi-backend/app/services/confidence.py`
- **Lines:** `56-69`
- **Signature:** `def _score_data_recency(f: ConfidenceFactors) -> float:`
- **Purpose:** Score 0-1 based on how recent the climate data is.

**Code:**
```python
def _score_data_recency(f: ConfidenceFactors) -> float:
    """Score 0-1 based on how recent the climate data is."""
    if f.climate_data_year is None:
        return 0.3  # Unknown recency — low confidence

    current_year = 2025
    age = current_year - f.climate_data_year
    if age <= 2:
        return 1.0
    if age <= 5:
        return 0.8
    if age <= 10:
        return 0.6
    return 0.4
```

**Explanation:** It accepts `f` and returns `float`. See the code below for the full implementation.

### `_score_model_maturity`

- **File:** `fastapi-backend/app/services/confidence.py`
- **Lines:** `72-80`
- **Signature:** `def _score_model_maturity(energy_type: str) -> float:`
- **Purpose:** Score 0-1 based on model sophistication.

**Code:**
```python
def _score_model_maturity(energy_type: str) -> float:
    """Score 0-1 based on model sophistication."""
    maturity = {
        "solar": 0.85,      # Well-established irradiance → output models
        "wind": 0.70,       # Good but wind is inherently more variable
        "hydro": 0.50,      # Rational method is a simplification
        "geothermal": 0.40, # Sparse data, IDW interpolation
    }
    return maturity.get(energy_type, 0.5)
```

**Explanation:** It accepts `energy_type` and returns `float`. See the code below for the full implementation. Key calls include `get()`.

### `_score_spatial_resolution`

- **File:** `fastapi-backend/app/services/confidence.py`
- **Lines:** `83-87`
- **Signature:** `def _score_spatial_resolution(energy_type: str) -> float:`
- **Purpose:** Score 0-1 based on spatial resolution of source data.

**Code:**
```python
def _score_spatial_resolution(energy_type: str) -> float:
    """Score 0-1 based on spatial resolution of source data."""
    # NASA POWER is ~0.5° (~50km) — coarse for municipal-level assessment
    # This is the same for all types currently
    return 0.55
```

**Explanation:** It accepts `energy_type` and returns `float`. See the code below for the full implementation.

### `calculate_confidence`

- **File:** `fastapi-backend/app/services/confidence.py`
- **Lines:** `90-141`
- **Signature:** `def calculate_confidence(f: ConfidenceFactors) -> dict[str, Any]:`
- **Purpose:** Calculate overall confidence score and contributing factors.

**Code:**
```python
def calculate_confidence(f: ConfidenceFactors) -> dict[str, Any]:
    """Calculate overall confidence score and contributing factors.

    Args:
        f: ConfidenceFactors describing data availability

    Returns:
        Dict with overall_score (0-100), factor breakdown, and confidence label
    """
    coverage = _score_data_coverage(f)
    recency = _score_data_recency(f)
    maturity = _score_model_maturity(f.energy_type)
    resolution = _score_spatial_resolution(f.energy_type)

    # Weighted average
    weights = {
        "coverage": 0.35,
        "recency": 0.15,
        "model_maturity": 0.30,
        "spatial_resolution": 0.20,
    }

    overall = (
        coverage * weights["coverage"]
        + recency * weights["recency"]
        + maturity * weights["model_maturity"]
        + resolution * weights["spatial_resolution"]
    )

    score = round(overall * 100, 1)

    if score >= 75:
        label = "High"
    elif score >= 55:
        label = "Moderate"
    elif score >= 35:
        label = "Low"
    else:
        label = "Very Low"

    return {
        "confidence_score": score,
        "confidence_label": label,
        "factors": {
            "data_coverage": round(coverage * 100, 1),
            "data_recency": round(recency * 100, 1),
            "model_maturity": round(maturity * 100, 1),
            "spatial_resolution": round(resolution * 100, 1),
        },
        "weights": weights,
        "recommendations": _generate_recommendations(f, coverage, recency, maturity, resolution),
    }
```

**Explanation:** It accepts `f` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_score_data_coverage()`, `_score_data_recency()`, `_score_model_maturity()`, `_score_spatial_resolution()`, `round()`.

### `_generate_recommendations`

- **File:** `fastapi-backend/app/services/confidence.py`
- **Lines:** `144-177`
- **Signature:** `def _generate_recommendations(`
- **Purpose:** Generate actionable recommendations to improve confidence.

**Code:**
```python
def _generate_recommendations(
    f: ConfidenceFactors,
    coverage: float,
    recency: float,
    maturity: float,
    resolution: float,
) -> list[str]:
    """Generate actionable recommendations to improve confidence."""
    recs: list[str] = []

    if not f.has_climate_data:
        recs.append("Fetch NASA POWER climate data for this municipality to enable energy calculations.")
    elif f.climate_variables_count < 8:
        recs.append(f"Only {f.climate_variables_count}/10 climate variables available. Fetch complete NASA POWER data.")

    if recency < 0.6:
        recs.append("Climate data is outdated. Re-fetch from NASA POWER for the latest period.")

    if not f.has_terrain_data and f.energy_type in ("hydro", "wind"):
        recs.append("Add DEM-derived terrain data (slope, elevation) for more accurate site assessment.")

    if not f.has_tariff_data:
        recs.append("Add DU tariff data for accurate financial savings calculations.")

    if resolution < 0.7:
        recs.append("Consider higher-resolution data sources (Global Solar Atlas, Global Wind Atlas) for improved accuracy.")

    if f.energy_type == "hydro" and maturity < 0.6:
        recs.append("Rational method provides rough estimates only. Consider streamflow data for reliable hydro assessment.")

    if f.energy_type == "geothermal" and maturity < 0.5:
        recs.append("Geothermal assessment is limited by sparse heat-flow data. Consult PHIVOLCS/DOE prospectivity maps.")

    return recs
```

**Explanation:** It accepts `f`, `coverage`, `recency`, `maturity`, `resolution` and returns `list[str]`. See the code below for the full implementation. Key calls include `append()`.


## `fastapi-backend/app/services/data_cache.py`

**File:** `fastapi-backend/app/services/data_cache.py`

**Summary:** Thin Redis cache layer with optional gzip + base64 compression.

### `_serialize`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `24-31`
- **Signature:** `def _serialize(value: Any) -> str:`
- **Purpose:** Serialize a value for Redis; compress large payloads.

**Code:**
```python
def _serialize(value: Any) -> str:
    """Serialize a value for Redis; compress large payloads."""
    payload = json.dumps(value, default=str).encode("utf-8")
    if len(payload) > _COMPRESS_THRESHOLD:
        compressed = gzip.compress(payload, compresslevel=6)
        encoded = base64.b64encode(compressed).decode("ascii")
        return f"{_GZIP_PREFIX}{encoded}"
    return payload.decode("utf-8")
```

**Explanation:** It accepts `value` and returns `str`. See the code below for the full implementation. Key calls include `encode()`, `dumps()`, `len()`, `compress()`, `decode()`.

### `_deserialize`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `34-48`
- **Signature:** `def _deserialize(raw: Any) -> Any | None:`
- **Purpose:** Deserialize a Redis value; decompress if it was compressed.

**Code:**
```python
def _deserialize(raw: Any) -> Any | None:
    """Deserialize a Redis value; decompress if it was compressed."""
    if raw is None:
        return None
    if not isinstance(raw, str):
        raw = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
    try:
        if raw.startswith(_GZIP_PREFIX):
            compressed = base64.b64decode(raw[len(_GZIP_PREFIX):].encode("ascii"))
            payload = gzip.decompress(compressed)
            return json.loads(payload)
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Cache decode failed: %s", exc)
        return None
```

**Explanation:** It accepts `raw` and returns `Any | None`. See the code below for the full implementation. Key calls include `isinstance()`, `decode()`, `str()`, `startswith()`, `loads()`.

### `cache_get`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `56-64`
- **Signature:** `async def cache_get(key: str) -> Any | None:`
- **Purpose:** Fetch a cached value by key, returning None on miss/error.

**Code:**
```python
async def cache_get(key: str) -> Any | None:
    """Fetch a cached value by key, returning None on miss/error."""
    try:
        redis = get_redis()
        raw = await redis.get(key)
        return _deserialize(raw)
    except Exception as exc:
        logger.debug("Redis async cache read failed for %s: %s", key, exc)
        return None
```

**Explanation:** It accepts `key` and returns `Any | None`. See the code below for the full implementation. Key calls include `get_redis()`, `_deserialize()`, `get()`, `debug()`.

### `cache_set`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `67-74`
- **Signature:** `async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:`
- **Purpose:** Store a JSON-serializable value with TTL.

**Code:**
```python
async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a JSON-serializable value with TTL."""
    try:
        redis = get_redis()
        payload = _serialize(value)
        await redis.setex(key, ttl, payload)
    except Exception as exc:
        logger.debug("Redis async cache write failed for %s: %s", key, exc)
```

**Explanation:** It accepts `key`, `value`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `_serialize()`, `setex()`, `debug()`.

### `cache_delete`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `77-82`
- **Signature:** `async def cache_delete(key: str) -> None:`
- **Purpose:** Handles cache delete.

**Code:**
```python
async def cache_delete(key: str) -> None:
    try:
        redis = get_redis()
        await redis.delete(key)
    except Exception as exc:
        logger.debug("Redis async cache delete failed for %s: %s", key, exc)
```

**Explanation:** It accepts `key` and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `delete()`, `debug()`.

### `cache_delete_pattern`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `85-92`
- **Signature:** `async def cache_delete_pattern(pattern: str) -> None:`
- **Purpose:** Handles cache delete pattern.

**Code:**
```python
async def cache_delete_pattern(pattern: str) -> None:
    try:
        redis = get_redis()
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    except Exception as exc:
        logger.debug("Redis async cache delete pattern failed for %s: %s", pattern, exc)
```

**Explanation:** It accepts `pattern` and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `keys()`, `debug()`, `delete()`.

### `cache_get_sync`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `100-108`
- **Signature:** `def cache_get_sync(key: str) -> Any | None:`
- **Purpose:** Fetch a cached value synchronously.

**Code:**
```python
def cache_get_sync(key: str) -> Any | None:
    """Fetch a cached value synchronously."""
    try:
        redis = get_redis_sync()
        raw = redis.get(key)
        return _deserialize(raw)
    except Exception as exc:
        logger.debug("Redis sync cache read failed for %s: %s", key, exc)
        return None
```

**Explanation:** It accepts `key` and returns `Any | None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `get()`, `_deserialize()`, `debug()`.

### `cache_set_sync`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `111-118`
- **Signature:** `def cache_set_sync(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:`
- **Purpose:** Store a JSON-serializable value with TTL synchronously.

**Code:**
```python
def cache_set_sync(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a JSON-serializable value with TTL synchronously."""
    try:
        redis = get_redis_sync()
        payload = _serialize(value)
        redis.setex(key, ttl, payload)
    except Exception as exc:
        logger.debug("Redis sync cache write failed for %s: %s", key, exc)
```

**Explanation:** It accepts `key`, `value`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `_serialize()`, `setex()`, `debug()`.

### `cache_delete_sync`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `121-126`
- **Signature:** `def cache_delete_sync(key: str) -> None:`
- **Purpose:** Handles cache delete sync.

**Code:**
```python
def cache_delete_sync(key: str) -> None:
    try:
        redis = get_redis_sync()
        redis.delete(key)
    except Exception as exc:
        logger.debug("Redis sync cache delete failed for %s: %s", key, exc)
```

**Explanation:** It accepts `key` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `delete()`, `debug()`.

### `cache_delete_pattern_sync`

- **File:** `fastapi-backend/app/services/data_cache.py`
- **Lines:** `129-136`
- **Signature:** `def cache_delete_pattern_sync(pattern: str) -> None:`
- **Purpose:** Handles cache delete pattern sync.

**Code:**
```python
def cache_delete_pattern_sync(pattern: str) -> None:
    try:
        redis = get_redis_sync()
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
    except Exception as exc:
        logger.debug("Redis sync cache delete pattern failed for %s: %s", pattern, exc)
```

**Explanation:** It accepts `pattern` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `keys()`, `delete()`, `debug()`.


## `fastapi-backend/app/services/ecosim.py`

**File:** `fastapi-backend/app/services/ecosim.py`

**Summary:** Source file `fastapi-backend/app/services/ecosim.py`.

### `_get_climate_df`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `39-66`
- **Signature:** `def _get_climate_df() -> pd.DataFrame:`
- **Purpose:** Load municipality climate averages from Supabase/cache or local CSV fallback.

**Code:**
```python
def _get_climate_df() -> pd.DataFrame:
    """Load municipality climate averages from Supabase/cache or local CSV fallback."""
    global _climate_df
    if _climate_df is not None:
        return _climate_df

    cache_key = "climate:all_averages"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        _climate_df = pd.DataFrame(cached)
        return _climate_df

    try:
        client = get_supabase_client()
        resp = client.table("municipality_climate_averages").select("*").execute()
        rows = resp.data or []
        if rows:
            cache_set_sync(cache_key, rows, ttl=86400)
            _climate_df = pd.DataFrame(rows)
            return _climate_df
    except Exception as exc:
        logger.warning("Failed to load climate averages from Supabase: %s", exc)

    if os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true" and _CLIMATE_CSV.exists():
        _climate_df = pd.read_csv(str(_CLIMATE_CSV))
        return _climate_df

    raise RuntimeError("Climate data unavailable from Supabase and local fallback disabled")
```

**Explanation:** It accepts zero arguments and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `cache_get_sync()`, `DataFrame()`, `get_supabase_client()`, `execute()`, `cache_set_sync()`.

### `get_municipality_terrain_data`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `88-111`
- **Signature:** `def get_municipality_terrain_data(municipality: str) -> dict | None:`
- **Purpose:** Fetches pre-computed terrain metrics for a municipality.

**Code:**
```python
def get_municipality_terrain_data(municipality: str) -> dict | None:
    """
    Fetches pre-computed terrain metrics for a municipality.
    Returns None if unavailable so callers can degrade gracefully.

    Expected table: municipality_terrain_metrics
    Columns used:
    hydraulic_head_m, runoff_potential, gravity_flow_potential,
    watershed_gradient, terrain_ruggedness, hydro_suitability_score,
    estimated_hydropower_potential_kw, mean_slope_deg, elevation_range_m
    """
    client = get_supabase_client()
    try:
        result = (
            client
            .table("hydropower_suitability")
            .select()
            .eq("municipality_name", municipality.upper())
            .single()
            .execute()
        )
        return result.data or None
    except APIError:
        return None
```

**Explanation:** It accepts `municipality` and returns `dict | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `eq()`, `upper()`.

### `get_municipality_data`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `113-156`
- **Signature:** `def get_municipality_data(municipality: str):`
- **Purpose:** Retrieves municipality data.

**Code:**
```python
def get_municipality_data(municipality: str):
    client = get_supabase_client()
    try:
        municipality_result = (
            client
            .table("municipalities")
            .select()
            .eq("name", municipality.upper())
            .limit(1)
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Municipality not found",
            )
        raise

    if not municipality_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipality not found",
        )

    municipality_id = (
        municipality_result.data["municipality_id"]
    )

    climate_df = _get_climate_df()
    municipality_data = (
        climate_df[climate_df["municipality_id"] == municipality_id]
        .to_dict(orient="records")
    )

    if not municipality_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No climate average data found for this municipality.",
        )
        
    return municipality_data
```

**Explanation:** It accepts `municipality`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `getattr()`, `isinstance()`.

### `list_municipalities`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `159-192`
- **Signature:** `def list_municipalities() -> list[dict]:`
- **Purpose:** Handles list municipalities.

**Code:**
```python
def list_municipalities() -> list[dict]:
    client = get_supabase_client()
    try:
        result = (
            client
            .table("municipalities")
            .select("municipality_id,name")
            .order("name")
            .limit(20000)
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict):
            message = error.get("message") or "Failed to load municipalities"
        else:
            message = "Failed to load municipalities"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )

    items = result.data or []
    return sorted(
        (
            {
                "municipality_id": item.get("municipality_id"),
                "name": item.get("name"),
            }
            for item in items
            if item.get("municipality_id") and item.get("name")
        ),
        key=lambda item: item["name"].upper(),
    )
```

**Explanation:** It accepts zero arguments and returns `list[dict]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `isinstance()`, `HTTPException()`, `limit()`.

### `list_provinces`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `195-228`
- **Signature:** `def list_provinces() -> list[dict]:`
- **Purpose:** Handles list provinces.

**Code:**
```python
def list_provinces() -> list[dict]:
    client = get_supabase_client()
    try:
        result = (
            client
            .table("provinces")
            .select("province_id,name")
            .order("name")
            .limit(1000)
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict):
            message = error.get("message") or "Failed to load provinces"
        else:
            message = "Failed to load provinces"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )

    items = result.data or []
    return sorted(
        (
            {
                "province_id": item.get("province_id"),
                "name": item.get("name"),
            }
            for item in items
            if item.get("province_id") and item.get("name")
        ),
        key=lambda item: item["name"].upper(),
    )
```

**Explanation:** It accepts zero arguments and returns `list[dict]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `isinstance()`, `HTTPException()`, `limit()`.

### `list_barangays`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `231-267`
- **Signature:** `def list_barangays(municipality_id: int | None = None) -> list[dict]:`
- **Purpose:** List barangays, optionally filtered by municipality_id.

**Code:**
```python
def list_barangays(municipality_id: int | None = None) -> list[dict]:
    """List barangays, optionally filtered by municipality_id."""
    client = get_supabase_client()
    try:
        query = (
            client.table("barangays")
            .select("barangay_id,name,municipality_id")
            .order("name")
            .limit(50000)
        )
        if municipality_id is not None:
            query = query.eq("municipality_id", str(municipality_id))
        result = query.execute()
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict):
            message = error.get("message") or "Failed to load barangays"
        else:
            message = "Failed to load barangays"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )

    items = result.data or []
    return sorted(
        (
            {
                "barangay_id": item.get("barangay_id"),
                "name": item.get("name"),
                "municipality_id": item.get("municipality_id"),
            }
            for item in items
            if item.get("barangay_id") and item.get("name")
        ),
        key=lambda item: item["name"].upper(),
    )
```

**Explanation:** It accepts `municipality_id` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `limit()`, `execute()`, `eq()`, `isinstance()`.

### `get_province_data`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `270-361`
- **Signature:** `def get_province_data(province_name: str) -> dict:`
- **Purpose:** Aggregate municipality climate data for a province.

**Code:**
```python
def get_province_data(province_name: str) -> dict:
    """Aggregate municipality climate data for a province.

    Returns a dict with the same structure as a single municipality record
    so it can be used interchangeably in renewable_energy_calculator.
    """
    client = get_supabase_client()
    try:
        prov_resp = (
            client.table("provinces")
            .select("province_id,name,lat,lon")
            .ilike("name", province_name.upper())
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Province not found",
            )
        raise

    if not prov_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )

    province_id = prov_resp.data["province_id"]
    province_lat = prov_resp.data.get("lat")
    province_lon = prov_resp.data.get("lon")

    # Fetch all municipalities in this province
    muni_resp = (
        client.table("municipalities")
        .select("municipality_id,name,lat,lon")
        .eq("province_id", province_id)
        .limit(20000)
        .execute()
    )
    muni_rows = muni_resp.data or []
    municipality_ids = [m["municipality_id"] for m in muni_rows if m.get("municipality_id")]

    if not municipality_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No municipalities found for this province.",
        )

    # Aggregate climate data
    climate_df = _get_climate_df()
    province_df = climate_df[climate_df["municipality_id"].isin(municipality_ids)]
    if province_df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No climate average data found for this province.",
        )

    numeric_cols = [
        "avg_t2m", "avg_t2m_max", "avg_t2m_min", "avg_rh2m",
        "avg_prectotcorr", "avg_ws10m", "avg_allsky_sfc_sw_dwn",
        "avg_cloud_amt", "avg_surface_pressure", "avg_rhoa", "avg_elevation",
    ]

    aggregated = {"municipality_id": province_id, "name": province_name.upper()}
    for col in numeric_cols:
        if col in province_df.columns:
            aggregated[col] = round(float(province_df[col].mean()), 2)
        else:
            aggregated[col] = None

    # Terrain aggregation (optional, from hydropower_suitability)
    try:
        terrain_resp = (
            client.table("hydropower_suitability")
            .select("hydraulic_head_m,runoff_potential,watershed_gradient,mean_slope_deg,gravity_flow_potential")
            .in_("municipality_id", municipality_ids)
            .execute()
        )
        terrain_rows = terrain_resp.data or []
        if terrain_rows:
            terrain = {}
            for key in ["hydraulic_head_m", "runoff_potential", "watershed_gradient", "mean_slope_deg", "gravity_flow_potential"]:
                vals = [r[key] for r in terrain_rows if r.get(key) is not None]
                terrain[key] = round(sum(vals) / len(vals), 2) if vals else 0.0
            aggregated["terrain"] = terrain
    except Exception:
        aggregated["terrain"] = None

    return aggregated
```

**Explanation:** It accepts `province_name` and returns `dict`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `getattr()`, `isinstance()`.

### `get_geothermal_data`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `364-450`
- **Signature:** `def get_geothermal_data(municipality_name: str, municipality_data: dict) -> dict:`
- **Purpose:** Fetch pre-computed geothermal output from Supabase.

**Code:**
```python
def get_geothermal_data(municipality_name: str, municipality_data: dict) -> dict:
    """
    Fetch pre-computed geothermal output from Supabase.
    Falls back to on-the-fly estimation if pre-computed row is missing.
    """
    client = get_supabase_client()
    mid = municipality_data.get("municipality_id")
    try:
        output_result = (
            client
            .table("geothermal_output")
            .select("*")
            .eq("municipality_id", mid)
            .single()
            .execute()
        )
        if output_result.data:
            data = output_result.data
            # Fetch true geothermal suitability score and classification
            geo_score = 0.0
            classification = "Unknown"
            try:
                suit_result = (
                    client
                    .table("geothermal_suitability")
                    .select("geothermal_score,classification")
                    .eq("municipality_id", mid)
                    .single()
                    .execute()
                )
                if suit_result.data:
                    geo_score = suit_result.data.get("geothermal_score") or 0.0
                    classification = suit_result.data.get("classification", "Unknown")
            except APIError:
                pass
            return {
                "energy_type": "geothermal",
                "suitability_score": round(geo_score * 100, 2),
                "classification": classification,
                "reservoir_temperature_c": data.get("reservoir_temperature_c"),
                "thermal_power_mw": data.get("thermal_power_mw"),
                "electric_power_mw": data.get("electric_power_mw"),
                "annual_energy_gwh": data.get("annual_energy_gwh"),
                "confidence": data.get("confidence_score"),
                "source": data.get("source", "Supabase pre-computed"),
                "assumption": data.get("assumption", ""),
            }
    except APIError:
        pass

    # Fallback: compute on-the-fly using NASA POWER surface temp
    surface_temp = municipality_data.get("avg_t2m")
    lat = municipality_data.get("lat")
    lon = municipality_data.get("lon")

    if lat is None or lon is None:
        return {
            "energy_type": "geothermal",
            "suitability_score": 0.0,
            "thermal_power_mw": None,
            "electric_power_mw": None,
            "annual_energy_gwh": None,
            "confidence": 0.0,
            "source": "Fallback on-the-fly estimation",
            "assumption": "Pre-computed data unavailable; using measured NASA POWER temperature and inferred aquifer/heatflow.",
        }

    suitability = compute_geothermal_suitability(lat, lon, surface_temp, municipality_id=mid)
    output = compute_geothermal_output(
        surface_temp,
        suitability.get("_gradient_c_km"),
        suitability.get("aquifer_score"),
        suitability.get("_perm_log10"),
    )

    return {
        "energy_type": "geothermal",
        "suitability_score": round(suitability.get("geothermal_score", 0) * 100, 2),
        "classification": suitability.get("classification", "Unknown"),
        "reservoir_temperature_c": output.get("reservoir_temperature_c"),
        "thermal_power_mw": output.get("thermal_power_mw"),
        "electric_power_mw": output.get("electric_power_mw"),
        "annual_energy_gwh": output.get("annual_energy_gwh"),
        "confidence": output.get("confidence_score"),
        "source": output.get("source"),
        "assumption": output.get("assumption"),
    }
```

**Explanation:** It accepts `municipality_name`, `municipality_data` and returns `dict`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `get()`, `execute()`, `single()`, `round()`.

### `get_municipality_name_by_id`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `453-479`
- **Signature:** `def get_municipality_name_by_id(municipality_id: int) -> str:`
- **Purpose:** Retrieves municipality name by id.

**Code:**
```python
def get_municipality_name_by_id(municipality_id: int) -> str:
    client = get_supabase_client()
    try:
        municipality_result = (
            client
            .table("municipalities")
            .select("name")
            .eq("municipality_id", municipality_id)
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Municipality not found",
            )
        raise

    if not municipality_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipality not found",
        )

    return municipality_result.data["name"]
```

**Explanation:** It accepts `municipality_id` and returns `str`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `getattr()`, `isinstance()`.

### `get_province_name_by_id`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `482-508`
- **Signature:** `def get_province_name_by_id(province_id: int) -> str:`
- **Purpose:** Retrieves province name by id.

**Code:**
```python
def get_province_name_by_id(province_id: int) -> str:
    client = get_supabase_client()
    try:
        result = (
            client
            .table("provinces")
            .select("name")
            .eq("province_id", province_id)
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Province not found",
            )
        raise

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )

    return result.data["name"]
```

**Explanation:** It accepts `province_id` and returns `str`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `getattr()`, `isinstance()`.

### `consumption_calculator`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `511-521`
- **Signature:** `def consumption_calculator(current_electricity_bill: float, electricity_rate: float, desired_savings: float):`
- **Purpose:** Handles consumption calculator.

**Code:**
```python
def consumption_calculator(current_electricity_bill: float, electricity_rate: float, desired_savings: float):
    monthly_consumption_kwh = current_electricity_bill / electricity_rate
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    daily_consumption_kwh = monthly_consumption_kwh / days_in_month
    target_monthly_consumption_kwh = monthly_consumption_kwh * (1 - desired_savings)
    return {
        "monthly_consumption_kwh": monthly_consumption_kwh,
        "daily_consumption_kwh": daily_consumption_kwh,
        "target_monthly_consumption_kwh": target_monthly_consumption_kwh
    }
```

**Explanation:** It accepts `current_electricity_bill`, `electricity_rate`, `desired_savings`. See the code below for the full implementation. Key calls include `now()`, `monthrange()`.

### `renewable_energy_calculator`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `536-749`
- **Signature:** `def renewable_energy_calculator(`
- **Purpose:** Handles renewable energy calculator.

**Code:**
```python
def renewable_energy_calculator(
    house: str,
    municipality: str,
    current_electricity_bill: float,
    electricity_rate: float,
    desired_savings: float,
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
    nearby_geo_plants: list[dict[str, Any]] | None = None,
    mode: str = "municipality",
) -> dict:
    # NOTE: Data fetching
    if mode == "province":
        municipality_data = get_province_data(municipality)
        municipality_results = [municipality_data]
        terrain_data = municipality_data.get("terrain")
    else:
        municipality_results = get_municipality_data(municipality)
        municipality_data = municipality_results[0]
        terrain_data = get_municipality_terrain_data(municipality)

    # Try Redis cache for the full EcoSim result
    geo_id = municipality_data.get("municipality_id")
    params_hash: str | None = None
    if geo_id:
        cache_payload = {
            "house": house,
            "municipality": municipality,
            "mode": mode,
            "current_electricity_bill": current_electricity_bill,
            "electricity_rate": electricity_rate,
            "desired_savings": desired_savings,
            "include_ai": include_ai,
            "use_rag": use_rag,
            "rag_query": rag_query,
        }
        params_hash = hashlib.md5(
            json.dumps(cache_payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:24]
        cached = get_ecosim_cache_sync("municipality", geo_id, params_hash)
        if cached:
            logger.info("EcoSim cache hit for %s (geo_id=%s)", municipality, geo_id)
            return cached

    consumption_results = consumption_calculator(
        current_electricity_bill,
        electricity_rate,
        desired_savings,
    )
    solar_irradiance = municipality_data.get("avg_allsky_sfc_sw_dwn") or 0.0
    avg_temp = municipality_data.get("avg_t2m")
    cloud_amt = municipality_data.get("avg_cloud_amt")
    rainfall = municipality_data.get("avg_prectotcorr")
    wind_speed = municipality_data.get("avg_ws10m")
    humidity = municipality_data.get("avg_rh2m")
    surface_pressure = municipality_data.get("avg_surface_pressure")
    air_density = municipality_data.get("avg_rhoa")
    elevation = municipality_data.get("avg_elevation")
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    # NOTE: SOLAR CALCULATIONS:
    # NOTE: this default config is estimated based on typical residential solar panel setups and can be adjusted in the future for more customization or to reflect different market conditions. It is currently hardcoded for simplicity and to provide a baseline for calculations.   
    solar_panel_default_config = {
        "panel_wattage": 400,
        "number_of_panels": 2,
        "system_efficiency": 0.80,
        "temp_coeff_per_c": -0.004,
        "dust_loss": 0.97,
        "inverter_efficiency": 0.96,
        "mismatch_loss": 0.98,
        "wiring_loss": 0.98,
        "degradation_loss": 0.99,
    }
    temperature_factor = calculate_temperature_factor(
        avg_temp_c=avg_temp,
        temp_coeff_per_c=solar_panel_default_config["temp_coeff_per_c"],
    )
    performance_ratio = calculate_performance_ratio(
        system_efficiency=solar_panel_default_config["system_efficiency"],
        temperature_factor=temperature_factor,
        dust_loss=calculate_dust_loss_from_wind(ws10m=wind_speed, base_dust_loss=solar_panel_default_config["dust_loss"]),
        inverter_efficiency=solar_panel_default_config["inverter_efficiency"],
        mismatch_loss=solar_panel_default_config["mismatch_loss"],
        wiring_loss=solar_panel_default_config["wiring_loss"],
        degradation_loss=calculate_degradation_from_humidity(rh2m=humidity, base_degradation=solar_panel_default_config["degradation_loss"]),
    )
    solar_output = solar_calc(
        panel_wattage=solar_panel_default_config["panel_wattage"],
        number_of_panels=solar_panel_default_config["number_of_panels"],
        solar_irradiance=solar_irradiance,
        performance_ratio=performance_ratio,
        days_in_month=days_in_month,
    )
    solar_output["annual_solar_output"] = (solar_output.get("monthly_solar_output") or 0.0) * 12.0

    # NOTE: HYDRO CALCULATIONS
    hydraulic_head_m = terrain_data.get("hydraulic_head_m") if terrain_data else 0.0
    flow_rate_cms = estimated_flow_rate(
        rainfall_mm_monthly=rainfall,
        runoff_potential=terrain_data.get("runoff_potential") if terrain_data else 0.0,
        watershed_gradient=terrain_data.get("watershed_gradient") if terrain_data else 0.0,
        mean_slope_deg=terrain_data.get("mean_slope_deg") if terrain_data else 0.0,
        gravity_flow_potential=terrain_data.get("gravity_flow_potential") if terrain_data else 0.0,
    )
    hydro_output_raw = calculate_hydropower(
        flow_rate_cms=flow_rate_cms,
        head_m=hydraulic_head_m,
        days_in_month=days_in_month
    )
    hydro_output = {
        "system_kwp": hydro_output_raw.get("available_power_kw", 0.0),
        "daily_hydro_output": hydro_output_raw.get("daily_energy_kwh", 0.0),
        "monthly_hydro_output": hydro_output_raw.get("monthly_energy_kwh", 0.0),
        "annual_hydro_output": (hydro_output_raw.get("monthly_energy_kwh") or 0.0) * 12.0,
        "hydro_score": hydro_output_raw.get("hydro_score", 0.0),
    }

    # NOTE: GEOTHERMAL CALCULATIONS
    geothermal_output = get_geothermal_data(municipality, municipality_data)
    # Add daily/monthly/annual kWh for card standardization
    geo_annual_gwh = geothermal_output.get("annual_energy_gwh") or 0.0
    geo_annual_kwh = geo_annual_gwh * 1_000_000.0
    geothermal_output["annual_energy_kwh"] = round(geo_annual_kwh, 2) if geo_annual_kwh > 0 else None
    geothermal_output["monthly_energy_kwh"] = round(geo_annual_kwh / 12.0, 2) if geo_annual_kwh > 0 else None
    geothermal_output["daily_energy_kwh"] = round(geo_annual_kwh / 365.0, 2) if geo_annual_kwh > 0 else None

    #NOTE: WIND CALCULATIONS
    wind_output = calculate_wind_output(wind_speed_mps=wind_speed, days_in_month=days_in_month, air_density=air_density)
    wind_output["annual_wind_output_kwh"] = (wind_output.get("monthly_energy_kwh") or 0.0) * 12.0

    renewable_energy_results = {
        "municipality": municipality.upper(),
        "municipality_id": municipality_data.get("municipality_id"),
        #json climate data coming from the NASA Power
        "climate": {
            "avg_t2m": avg_temp,
            "avg_t2m_max": municipality_data.get("avg_t2m_max"),
            "avg_t2m_min": municipality_data.get("avg_t2m_min"),
            "avg_rh2m": humidity,
            "avg_rhoa": air_density,
            "avg_prectotcorr": rainfall,
            "avg_ws10m": wind_speed,
            "avg_allsky_sfc_sw_dwn": solar_irradiance,
            "avg_cloud_amt": cloud_amt,
            "avg_surface_pressure": surface_pressure,
            "elevation": elevation,
        },
        #json estimates and assumptions for the renewable energy calculations, which can be used for transparency and future adjustments
        "assumptions": {
            "temperature_factor": temperature_factor,
            "performance_ratio": performance_ratio,
            "days_in_month": days_in_month,
            "panel_wattage": solar_panel_default_config["panel_wattage"],
            "number_of_panels": solar_panel_default_config["number_of_panels"],
        },
        # json for the solar outputs
        "solar_output": solar_output,
        "hydro_output": hydro_output,
        "wind_output": wind_output,
        "geothermal_output": geothermal_output,
        # json for the consumption calculations
        "consumption_results": consumption_results,
    }
    
    ai_analysis = None
    if include_ai:
        try:
            analysis_payload = {
                "municipality_data": municipality_results,
                "consumption_results": consumption_results,
                "renewable_energy_results": renewable_energy_results,
                "nearby_geothermal_plants": nearby_geo_plants or [],
            }

            if use_rag and rag_query:
                from app.services.rag_gemini_funcs import analyze_with_rag

                ai_analysis = analyze_with_rag(analysis_payload, rag_query)
            else:
                from app.services.gemini_funcs import analyze_renewable_results

                ai_analysis = analyze_renewable_results(analysis_payload)
        except Exception:
            logger.exception("Gemini analysis failed in Ecosim")
            ai_analysis = {
                "summary": "Gemini analysis failed.",
                "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
                "recommendation": {"best_option": "", "reason": ""},
                "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
                "environmental_impact": "",
            }

    # Merge static fallback explanations so every renewable type always has text
    if ai_analysis:
        static_explanations = _build_static_renewable_explanations(renewable_energy_results)
        ra = ai_analysis.get("renewable_analysis") or {}
        for key, text in static_explanations.items():
            if not ra.get(key):
                ra[key] = text
        ai_analysis["renewable_analysis"] = ra

    result = {
        "municipality_data": municipality_results,
        "consumption_results": consumption_results,
        "renewable_energy_results": renewable_energy_results,
        "ai_analysis": ai_analysis,
    }

    if geo_id and params_hash:
        set_ecosim_cache_sync("municipality", geo_id, params_hash, result)

    return result
```

**Explanation:** It accepts `house`, `municipality`, `current_electricity_bill`, `electricity_rate`, `desired_savings`, `include_ai`, `use_rag`, `rag_query`, `nearby_geo_plants`, `mode` and returns `dict`. See the code below for the full implementation. Key calls include `get_province_data()`, `get()`, `get_municipality_data()`, `get_municipality_terrain_data()`, `get_ecosim_cache_sync()`.

### `_build_static_renewable_explanations`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `752-899`
- **Signature:** `def _build_static_renewable_explanations(results: dict) -> dict[str, str]:`
- **Purpose:** Create deterministic fallback explanations with causal reasoning.

**Code:**
```python
def _build_static_renewable_explanations(results: dict) -> dict[str, str]:
    """Create deterministic fallback explanations with causal reasoning.
    Every renewable type MUST produce a multi-sentence explanation even when
    specific output numbers are zero or unavailable."""
    climate = results.get("climate") or {}
    solar = results.get("solar_output") or {}
    wind = results.get("wind_output") or {}
    hydro = results.get("hydro_output") or {}
    geo = results.get("geothermal_output") or {}

    explanations: dict[str, str] = {}

    # Solar — always explain irradiance, cloud, temperature physics
    if solar:
        irradiance = climate.get("avg_allsky_sfc_sw_dwn")
        cloud = climate.get("avg_cloud_amt")
        temp = climate.get("avg_t2m")
        parts: list[str] = []
        parts.append(
            "Solar panels convert photons into electricity: higher irradiance means more photons strike the silicon cells, freeing more electrons and raising current."
        )
        if irradiance is not None:
            parts.append(
                f"This location receives {float(irradiance):.2f} kWh/m²/day on average."
            )
        if cloud is not None:
            parts.append(
                f"Cloud coverage at {float(cloud):.1f}% reduces effective irradiance because water droplets scatter and absorb incoming sunlight before it reaches the panels, directly lowering generation."
            )
        if temp is not None:
            parts.append(
                f"High surface temperatures ({float(temp):.1f}°C) also reduce efficiency: silicon cells lose about 0.4% output per degree above 25°C, so tropical heat partially offsets the benefit of strong sun."
            )
        monthly = solar.get("monthly_solar_output")
        if monthly:
            parts.append(f"The simulated system produces {float(monthly):.1f} kWh/month under these combined conditions.")
        else:
            parts.append("Simulated output is negligible given these atmospheric conditions.")
        explanations["solar"] = " ".join(parts)

    # Wind — always explain V³ physics and capacity factor
    if wind:
        ws = climate.get("avg_ws10m")
        parts: list[str] = []
        parts.append(
            "Wind turbines extract kinetic energy from moving air. Because kinetic energy scales with the cube of velocity (P ∝ V³), even a small increase in wind speed produces a disproportionately large jump in power output."
        )
        if ws is not None:
            parts.append(
                f"This location averages {float(ws):.2f} m/s."
            )
        cf = wind.get("capacity_factor")
        if cf is not None:
            parts.append(
                f"The capacity factor ({float(cf):.2f}) matters because turbines rarely run at full rated power in practice: variable winds, maintenance downtime, and cut-in/cut-out speeds mean actual output is a fraction of the theoretical maximum."
            )
        monthly = wind.get("monthly_energy_kwh")
        if monthly:
            parts.append(f"Realistically, the simulated turbine generates {float(monthly):.1f} kWh/month after accounting for these operational constraints.")
        else:
            parts.append("Simulated wind output is minimal at this average wind speed.")
        explanations["wind"] = " ".join(parts)

    # Hydro — always explain rainfall + head physics
    if hydro:
        rainfall = climate.get("avg_prectotcorr")
        elevation = climate.get("elevation")
        parts: list[str] = []
        parts.append(
            "Micro-hydro depends on two things: water flow and hydraulic head. Rainfall feeds the watershed and increases stream flow rate, which directly raises the kinetic energy available to spin the turbine."
        )
        if rainfall is not None:
            parts.append(
                f"This location averages {float(rainfall):.2f} mm/day of precipitation."
            )
        if elevation is not None:
            parts.append(
                f"Elevation at {float(elevation):.0f} m creates hydraulic head: water falling from a greater height carries more gravitational potential energy (mgh), which converts to higher pressure and more power at the turbine."
            )
        monthly = hydro.get("monthly_hydro_output")
        if monthly:
            parts.append(f"The simulated micro-hydro system is estimated to produce {float(monthly):.1f} kWh monthly given these water and head conditions.")
        else:
            parts.append("Simulated hydro output is minimal because the combination of rainfall and elevation at this site does not produce sufficient flow or head for meaningful generation.")
        explanations["hydro"] = " ".join(parts)

    # Geothermal — ALWAYS explain the four key subsurface drivers, even with zero data
    if geo:
        reservoir_temp = geo.get("reservoir_temperature_c")
        thermal = geo.get("thermal_power_mw")
        electric = geo.get("electric_power_mw")
        annual = geo.get("annual_energy_gwh")
        confidence = geo.get("confidence")
        classification = geo.get("classification")
        surface_temp = climate.get("avg_t2m")
        parts: list[str] = []

        # Always start with the fundamental physics
        parts.append(
            "Geothermal energy depends on four subsurface factors: surface heat flow (how much heat escapes the crust), proximity to faults or volcanoes (which channel hot fluids upward), aquifer permeability (whether water can circulate through hot rock), and the geothermal gradient (how fast temperature rises with depth)."
        )

        if surface_temp is not None:
            parts.append(
                f"The average surface temperature here is {float(surface_temp):.1f}°C."
            )

        if reservoir_temp is not None:
            parts.append(
                f"The estimated reservoir temperature is {float(reservoir_temp):.1f}°C. This is critical because extractable thermal energy equals mass flow × specific heat × temperature drop (Q = m·Cp·ΔT). A hotter reservoir means a larger ΔT and therefore more usable heat per kilogram of fluid circulated."
            )
        else:
            parts.append(
                "Without measured heat-flow data, the reservoir temperature cannot be reliably estimated. Low or absent heat-flow measurements usually indicate either low crustal heat production or insufficient survey coverage for this area."
            )

        if classification and classification != "Unknown":
            parts.append(
                f"Site classification is {classification}, reflecting the combined subsurface heat and permeability conditions."
            )
        else:
            parts.append(
                "Without subsurface data the site cannot be classified, but Philippine locations far from active volcanic arcs or major fault systems typically have lower geothermal potential."
            )

        if thermal is not None and electric is not None and (thermal > 0 or electric > 0):
            parts.append(
                f"Estimated thermal power is {float(thermal):.3f} MW and convertible electric power is {float(electric):.3f} MW, limited by the efficiency of the binary or flash cycle (typically 10–15%)."
            )
        else:
            parts.append(
                "No meaningful thermal or electric power is estimated for this site because the subsurface temperature or permeability is too low to sustain a viable geothermal plant."
            )

        if annual is not None and annual > 0:
            parts.append(f"This yields {float(annual):.3f} GWh annually.")
        else:
            parts.append(
                "Annual energy yield is effectively zero under current assumptions, meaning geothermal is not a practical option at this location."
            )

        if confidence is not None:
            parts.append(
                f"Data confidence is {float(confidence):.2f}, indicating how complete the measured heat-flow and aquifer datasets are for this municipality."
            )
        explanations["geothermal"] = " ".join(parts)

    return explanations
```

**Explanation:** It accepts `results` and returns `dict[str, str]`. See the code below for the full implementation. Key calls include `get()`, `append()`, `join()`, `float()`.

### `_calculate_option_summary`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `902-1045`
- **Signature:** `def _calculate_option_summary(`
- **Purpose:** Compute economic and environmental indicators for a single renewable option.

**Code:**
```python
def _calculate_option_summary(
    source: str,
    estimated_generation_kwh: float,
    source_score: float,
    monthly_consumption_kwh: float,
    electricity_rate: float,
    installation_cost_per_kw: float,
) -> dict:
    """
    Compute economic and environmental indicators for a single renewable option.

    Formulas and their academic support (APA 7th):
    ------------------------------------------------------------------------
    1. Simple Payback Period (SPP)
       SPP = installation_cost / (monthly_savings × 12)
       Source: Ngwakwe (2025) — quasi-systematic review confirming SPP as the
       dominant first-screening metric in residential PV techno-economic studies.
       Also applied by Huda et al. (2024) for Indonesian PV systems.

    2. CO₂ displacement
       carbon_reduction = usable_kwh × CO2_KG_PER_KWH
       Uses the Philippines DOE 2019–2021 National Grid Emission Factor
       (Luzon–Visayas OMEF = 0.6835 kg CO₂/kWh) (DOE, 2022).

    3. System-size proxy (for cost estimation)
       system_kw = monthly_generation / 30 days / 4.0 equivalent peak-sun hrs
       The 4 hr/day figure is a conservative Philippines national estimate;
       Taduran & Piao (2025) measured 3.01 kWh/kWp/day (Final Yield) in
       Tarlac City, while NREL data show 4.0–6.0 kWh/m²/day nationwide.

    4. Weighted suitability score (0–100 scale)
       score = source_score × (0.4 + 0.6 × energy_ratio) × 100
       Multiplicative scoring ensures source quality (climate/resource conditions)
       is the primary driver. A source with poor climate conditions cannot win
       simply because its energy output is high. This prevents misleading
       recommendations where, for example, wind is chosen over solar despite
       clearly inferior wind speeds.

    References
    ----------
    Asadi, M., Pourhossein, K., Noorollahi, Y., Marzband, M., & Iglesias, G. (2023).
        A new decision framework for hybrid solar and wind power plant site selection
        using linear regression modeling based on GIS-AHP. Sustainability, 15(10), 8359.
        https://doi.org/10.3390/su15108359

    Department of Energy (Philippines). (2022). 2019–2021 National Grid Emission Factor.
        Energy Regulatory Commission. https://www.foi.gov.ph/requests/national-grid-emission-factor/

    Huda, A., Kurniawan, I., Purba, K. F., Ichwani, R., Aryansyah, & Fionasari, R. (2024).
        Techno-economic assessment of residential and farm-based photovoltaic systems in Indonesia.
        Renewable Energy, 219, Article 119886. https://doi.org/10.1016/j.renene.2023.119886

    Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy
        investment: A quasi-systematic review. Oblik i finansi, (1), 59–66.
        https://ideas.repec.org/a/iaf/journl/y2025i1p59-66.html

    Taduran, A. J. R., & Piao, L. P. (2025). Analyzing the performance of a 2.72 kWp rooftop
        grid-tied photovoltaic system in Tarlac City, Philippines. International Journal of
        Engineering Trends and Technology, 73(9), 318–327.
        https://doi.org/10.14445/22315381/IJETT-V73I9P127
    """
    generation_kwh = max(float(estimated_generation_kwh or 0.0), 0.0)
    consumption_kwh = max(float(monthly_consumption_kwh or 0.0), 0.0)
    usable_kwh = min(generation_kwh, consumption_kwh)
    monthly_savings = usable_kwh * electricity_rate

    # Source-specific system sizing so costs reflect real-world installs
    source_lower = (source or "").lower()
    if "geothermal" in source_lower:
        # Utility-scale plant: cost based on plant MW capacity, not household kW
        # Approximate PHP per kW for utility geothermal in the Philippines
        system_kw = generation_kwh / 30.0 / 24.0 if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = None
        scale = "utility"
    elif "wind" in source_lower:
        # Residential wind CF ~25 % (PH small-turbine range 15–35 %)
        system_kw = generation_kwh / (30.0 * 24.0 * 0.25) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = (
            installation_cost / (monthly_savings * 12.0)
            if monthly_savings > 0
            else None
        )
        scale = "residential"
    elif "hydro" in source_lower:
        # Micro-hydro CF ~50 % (run-of-river / micro range 40–60 %)
        system_kw = generation_kwh / (30.0 * 24.0 * 0.50) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = (
            installation_cost / (monthly_savings * 12.0)
            if monthly_savings > 0
            else None
        )
        scale = "residential"
    else:
        # Solar: 4.5 peak-sun hrs/day ≈ 135 kWh/kWp/month (PH conservative)
        system_kw = generation_kwh / (30.0 * 4.5) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = (
            installation_cost / (monthly_savings * 12.0)
            if monthly_savings > 0
            else None
        )
        scale = "residential"

    energy_ratio = min(generation_kwh / consumption_kwh, 1.0) if consumption_kwh > 0 else 0.0
    # Multiplicative scoring: source quality is primary, energy coverage is secondary.
    # This prevents poor-quality sources from winning just because they generate more energy.
    source_score = float(source_score or 0.0)
    suitability_score = round(source_score * (0.4 + 0.6 * energy_ratio) * 100, 1)
    carbon_reduction = usable_kwh * CO2_KG_PER_KWH

    # Financial analysis (NPV, IRR, LCOE, discounted payback)
    annual_energy = generation_kwh * 12.0
    fin_inputs = FinancialInputs(
        system_capacity_kw=round(system_kw, 3),
        annual_energy_kwh=annual_energy,
        capital_cost_php=installation_cost,
        annual_om_cost_php=installation_cost * 0.01,  # 1% of CapEx annually
        electricity_tariff_php_kwh=electricity_rate,
        discount_rate=0.10,
        system_lifetime_years=25 if scale == "residential" else 30,
        degradation_rate=0.005,
    )
    fin_results = analyze_financials(fin_inputs)
    financials = financials_to_dict(fin_results)

    return {
        "source": source,
        "suitability_score": suitability_score,
        "estimated_generation_kwh": generation_kwh,
        "monthly_savings": monthly_savings,
        "installation_cost": installation_cost,
        "payback_years": payback_years,
        "discounted_payback_years": financials["discounted_payback_years"],
        "npv_php": financials["npv_php"],
        "irr": financials["irr"],
        "lcoe_php_kwh": financials["lcoe_php_kwh"],
        "benefit_cost_ratio": financials["benefit_cost_ratio"],
        "carbon_reduction": carbon_reduction,
        "system_kw": round(system_kw, 3),
        "scale": scale,
    }
```

**Explanation:** It accepts `source`, `estimated_generation_kwh`, `source_score`, `monthly_consumption_kwh`, `electricity_rate`, `installation_cost_per_kw` and returns `dict`. See the code below for the full implementation. Key calls include `max()`, `float()`, `min()`, `lower()`, `round()`.

### `build_ecosim_dashboard_response`

- **File:** `fastapi-backend/app/services/ecosim.py`
- **Lines:** `1048-1320`
- **Signature:** `def build_ecosim_dashboard_response(`
- **Purpose:** Builds ecosim dashboard response.

**Code:**
```python
def build_ecosim_dashboard_response(
    municipality_id: int,
    monthly_consumption: float,
    monthly_bill: float,
    desired_savings: float = 0.5,
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
    mode: str = "municipality",
) -> dict:
    if monthly_consumption <= 0 or monthly_bill <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="monthly_consumption and monthly_bill must be greater than zero",
        )

    electricity_rate = monthly_bill / monthly_consumption
    if mode == "province":
        municipality_name = get_province_name_by_id(municipality_id)
    else:
        municipality_name = get_municipality_name_by_id(municipality_id)

    # Fetch municipality lat/lon for proximity boost
    muni_lat: float | None = None
    muni_lon: float | None = None
    try:
        client = get_supabase_client()
        if mode == "province":
            # For province mode, lat/lon come from the provinces table
            prov_resp = (
                client.table("provinces")
                .select("lat,lon")
                .eq("province_id", municipality_id)
                .single()
                .execute()
            )
            if prov_resp.data:
                muni_lat = prov_resp.data.get("lat")
                muni_lon = prov_resp.data.get("lon")
        else:
            muni_resp = (
                client.table("municipalities")
                .select("lat,lon")
                .eq("municipality_id", municipality_id)
                .single()
                .execute()
            )
            if muni_resp.data:
                muni_lat = muni_resp.data.get("lat")
                muni_lon = muni_resp.data.get("lon")
    except Exception as exc:
        logger.warning("Municipality lat/lon fetch failed: %s", exc)

    nearby_geo_plants: list[dict[str, Any]] = []
    base_results = renewable_energy_calculator(
        house="Ecosim",
        municipality=municipality_name,
        current_electricity_bill=monthly_bill,
        electricity_rate=electricity_rate,
        desired_savings=desired_savings,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
        nearby_geo_plants=nearby_geo_plants,
        mode=mode,
    )

    renewable_results = base_results["renewable_energy_results"]
    solar_output = renewable_results.get("solar_output", {})
    wind_output = renewable_results.get("wind_output", {})
    hydro_output = renewable_results.get("hydro_output", {})
    geothermal_output = renewable_results.get("geothermal_output", {})

    solar_score = float(solar_output.get("solar_score", 0.0)) / 100.0
    hydro_score = float(hydro_output.get("hydro_score", 0.0)) / 100.0
    # Derive wind source quality from actual wind speed, not fixed capacity factor
    wind_speed_mps = float(base_results.get("climate", {}).get("avg_ws10m", 0.0))
    if wind_speed_mps >= 6.0:
        wind_score = 0.85
    elif wind_speed_mps >= 4.5:
        wind_score = 0.60
    elif wind_speed_mps >= 3.0:
        wind_score = 0.35
    elif wind_speed_mps > 0:
        wind_score = 0.15
    else:
        wind_score = 0.0

    # Apply proximity boost to geothermal score if municipality is near an operating plant
    raw_geo_score = float(geothermal_output.get("suitability_score", 0.0))
    if muni_lat is not None and muni_lon is not None:
        boosted_score, nearby_geo_plants = calculate_proximity_boost(
            float(muni_lat), float(muni_lon), raw_geo_score
        )
        geo_score = boosted_score / 100.0
    else:
        geo_score = raw_geo_score / 100.0

    # Geothermal is utility-scale; convert annual GWh to monthly kWh for comparison
    geo_annual_gwh = geothermal_output.get("annual_energy_gwh") or 0.0
    geo_monthly_kwh = (geo_annual_gwh * 1_000_000) / 12.0

    options = [
        _calculate_option_summary(
            source="Solar",
            estimated_generation_kwh=solar_output.get("monthly_solar_output", 0.0),
            source_score=solar_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_SOLAR,
        ),
        _calculate_option_summary(
            source="Wind",
            estimated_generation_kwh=wind_output.get("monthly_energy_kwh", 0.0),
            source_score=wind_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_WIND,
        ),
        _calculate_option_summary(
            source="Hydropower",
            estimated_generation_kwh=hydro_output.get("monthly_hydro_output", 0.0),
            source_score=hydro_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_HYDRO,
        ),
        _calculate_option_summary(
            source="Geothermal",
            estimated_generation_kwh=geo_monthly_kwh,
            source_score=geo_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_GEOTHERMAL,
        ),
    ]

    for option in options:
        score = option["suitability_score"]
        gen = option["estimated_generation_kwh"]
        pct = (gen / monthly_consumption * 100) if monthly_consumption > 0 else 0
        if score >= 80:
            rating = "Excellent"
            why = "This location has ideal conditions for this type of energy."
        elif score >= 60:
            rating = "Good"
            why = "This location has favorable conditions, but may need some planning."
        elif score >= 40:
            rating = "Moderate"
            why = "This location can work, but it may not be the most cost-effective option."
        else:
            rating = "Fair"
            why = "Conditions at this location are not ideal for this type of energy."
        option["explanation"] = (
            f"{rating} match — {why} With your current usage, this system could generate about "
            f"{gen:.0f} kWh per month, covering roughly {pct:.0f}% of your electricity needs."
        )

    # Confidence scoring per energy type
    climate_data = renewable_results.get("climate", {})
    climate_vars_available = sum(1 for v in climate_data.values() if v is not None)
    for option in options:
        src_lower = (option["source"] or "").lower()
        energy_type = "solar" if "solar" in src_lower else "wind" if "wind" in src_lower else "hydro" if "hydro" in src_lower else "geothermal"
        conf_factors = ConfidenceFactors(
            has_climate_data=climate_vars_available > 0,
            climate_variables_count=climate_vars_available,
            climate_data_year=2024,
            has_terrain_data=terrain_data is not None if mode != "province" else True,
            has_population_data=False,
            has_tariff_data=electricity_rate > 0,
            user_provided_inputs=monthly_consumption > 0,
            energy_type=energy_type,
        )
        option["confidence"] = calculate_confidence(conf_factors)

    # Recommend only household-scale sources (exclude utility-scale geothermal)
    household_options = [o for o in options if o.get("scale") != "utility"]
    recommended = max(
        household_options,
        key=lambda item: (item["suitability_score"], item["estimated_generation_kwh"]),
    )

    net_consumption = max(monthly_consumption - recommended["estimated_generation_kwh"], 0.0)
    net_bill = net_consumption * electricity_rate

    rec_gen = recommended["estimated_generation_kwh"]
    rec_savings = recommended["monthly_savings"]
    rec_payback = recommended.get("payback_years")
    rec_pct = (rec_gen / monthly_consumption * 100) if monthly_consumption > 0 else 0

    payback_text = (
        f" The system would pay for itself in about {rec_payback:.1f} years through savings on your bill."
        if rec_payback is not None and rec_payback > 0 and rec_payback < 100
        else ""
    )

    explanation = (
        f"Based on your location's climate and your monthly electricity use, {recommended['source']} energy is the best match for your home. "
        f"A typical {recommended['source'].lower()} system here could generate about {rec_gen:.0f} kWh per month, "
        f"covering roughly {rec_pct:.0f}% of your electricity needs and saving you about PHP {rec_savings:,.0f} per month.{payback_text}"
    )

    # Meralco franchise area check
    meralco_franchise_provinces = {
        "metro manila", "ncr", "bulacan", "cavite", "laguna", "rizal"
    }
    # Known Meralco-served municipalities (subset; extend as needed)
    meralco_franchise_municipalities: set[str] = {
        "calamba", "cabuyao", "santa rosa", "biñan", "san pedro",
        "general trias", "imus", "dasmariñas", "bacoor", "kawit",
        "norzagaray", "malolos", "meycauayan", "marilao", "bocaue",
        "cainta", "taytay", "angono", "binangonan", "antipolo",
    }
    meralco_info = None
    try:
        client = get_supabase_client()
        if mode == "province":
            prov_name = municipality_name.lower()
            muni_name = ""
        else:
            # Fetch municipality and province name
            muni_resp = (
                client.table("municipalities")
                .select("name,provinces(name)")
                .eq("municipality_id", municipality_id)
                .single()
                .execute()
            )
            muni_data = muni_resp.data or {}
            muni_name = str(muni_data.get("name", "")).lower().strip()
            prov_name = (
                str(muni_data.get("provinces", {}).get("name", "")).lower().strip()
                if isinstance(muni_data.get("provinces"), dict) else ""
            )
        # Municipality-level whitelist first, then province fallback
        if muni_name in meralco_franchise_municipalities or any(
            p in prov_name for p in meralco_franchise_provinces
        ):
            from app.ml.predictor import get_energyhub_ml
            ml = get_energyhub_ml()
            meralco_info = ml.get_meralco_rate()
    except Exception as exc:
        logger.warning("Meralco franchise lookup failed: %s", exc)

    return {
        "municipality": municipality_name.upper(),
        "municipality_id": municipality_id,
        "monthly_consumption_kwh": monthly_consumption,
        "monthly_bill": monthly_bill,
        "recommended_source": recommended["source"],
        "suitability_score": recommended["suitability_score"],
        "estimated_generation_kwh": recommended["estimated_generation_kwh"],
        "monthly_savings": recommended["monthly_savings"],
        "installation_cost": recommended["installation_cost"],
        "payback_years": recommended["payback_years"],
        "carbon_reduction": recommended["carbon_reduction"],
        "explanation": explanation,
        "options": options,
        "comparison": {
            "current_monthly_consumption_kwh": monthly_consumption,
            "current_monthly_bill": monthly_bill,
            "renewable_monthly_consumption_kwh": net_consumption,
            "renewable_monthly_bill": net_bill,
        },
        "climate": renewable_results.get("climate"),
        "renewable_energy_results": renewable_results,
        "consumption_results": base_results.get("consumption_results"),
        "municipality_data": base_results.get("municipality_data"),
        "ai_analysis": base_results.get("ai_analysis"),
        "nearby_geothermal_plants": nearby_geo_plants,
        "meralco_rate": meralco_info,
    }
```

**Explanation:** It accepts `municipality_id`, `monthly_consumption`, `monthly_bill`, `desired_savings`, `include_ai`, `use_rag`, `rag_query`, `mode` and returns `dict`. See the code below for the full implementation. Key calls include `HTTPException()`, `get_province_name_by_id()`, `get_municipality_name_by_id()`, `get_supabase_client()`, `execute()`.


## `fastapi-backend/app/services/energyhub.py`

**File:** `fastapi-backend/app/services/energyhub.py`

**Summary:** Source file `fastapi-backend/app/services/energyhub.py`.

### `_get_geojson_province_names`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `52-87`
- **Signature:** `def _get_geojson_province_names() -> list[dict[str, str]]:`
- **Purpose:** Return the list of GeoJSON province names used to align map data.

**Code:**
```python
def _get_geojson_province_names() -> list[dict[str, str]]:
    """Return the list of GeoJSON province names used to align map data.

    The names come from the provinces table (geojson_name column) with a
    short-lived Redis cache.  If the DB is unavailable and local fallback is
    enabled, the original GeoJSON file is parsed.
    """
    cache_key = "energyhub:province_names"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

    names: list[dict[str, str]] = []
    try:
        client = get_supabase_client()
        resp = client.table("provinces").select("name,geojson_name").execute()
        for row in resp.data or []:
            name = row.get("geojson_name") or row.get("name")
            if name:
                name = str(name).strip()
                names.append({"name": name, "name_lower": name.lower()})
    except Exception as exc:
        logger.warning("Supabase province geojson name query failed: %s", exc)

    if not names and os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true":
        geojson_path = _GEOJSON_DIR / "philippine_geojson_file_per_region.json"
        if geojson_path.exists():
            with open(geojson_path, "r", encoding="utf-8") as f:
                geo_data = json.load(f)
            for feat in geo_data.get("features", []):
                adm2 = (feat.get("properties", {}).get("adm2_en") or "").strip()
                if adm2:
                    names.append({"name": adm2, "name_lower": adm2.lower()})

    cache_set_sync(cache_key, names, ttl=86400)
    return names
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, str]]`. See the code below for the full implementation. Key calls include `cache_get_sync()`, `get_supabase_client()`, `execute()`, `warning()`, `select()`.

### `EnergyHubService.__init__`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `97-98`
- **Signature:** `def __init__(self) -> None:`
- **Purpose:** Method of `EnergyHubService` that handles   init  .

**Code:**
```python
def __init__(self) -> None:
        self._ml = get_energyhub_ml()
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_energyhub_ml()`.

### `EnergyHubService.build_overview`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `102-126`
- **Signature:** `def build_overview(self) -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that builds overview.

**Code:**
```python
def build_overview(self) -> dict[str, Any]:
        latest = self._ml.get_latest_statistics()
        forecast = self._ml.get_forecast("consumption")
        comparison = self._ml.get_model_comparison()

        # Derive a simple forecast growth metric for the overview card
        forecast_summary = {}
        if forecast.get("forecast_values"):
            current = latest.get("total_consumption_gwh", 0)
            f_2030 = forecast["forecast_values"][-1]
            forecast_summary = {
                "forecast_2030_gwh": f_2030,
                "forecast_growth_pct": round(((f_2030 / current) - 1) * 100, 2) if current else 0,
                "best_model": forecast.get("model", "ARIMA(1,1,1)"),
                "best_mape_pct": next(
                    (m["mape"] for m in comparison if m["model"] == "Linear Trend Regression"),
                    None,
                ),
            }

        return _sanitize_nan({
            "latest": latest,
            "forecast_summary": forecast_summary,
            "model_comparison": comparison,
        })
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_latest_statistics()`, `get_forecast()`, `get_model_comparison()`, `get()`, `next()`.

### `EnergyHubService.get_forecast`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `130-131`
- **Signature:** `def get_forecast(self, metric: str = "consumption") -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that retrieves forecast.

**Code:**
```python
def get_forecast(self, metric: str = "consumption") -> dict[str, Any]:
        return self._ml.get_forecast(metric)
```

**Explanation:** It accepts `metric` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_forecast()`.

### `EnergyHubService.build_trends`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `135-146`
- **Signature:** `def build_trends(self) -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that builds trends.

**Code:**
```python
def build_trends(self) -> dict[str, Any]:
        historical = self._ml.get_historical_trends()
        forecast = self._ml.get_forecast("consumption")
        source_breakdown = self._ml.get_source_breakdown()
        grid_breakdown = self._ml.get_grid_breakdown()
        return _sanitize_nan({
            "years": historical["years"],
            "series": historical["series"],
            "forecast": forecast,
            "source_breakdown": source_breakdown,
            "grid_breakdown": grid_breakdown,
        })
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_historical_trends()`, `get_forecast()`, `get_source_breakdown()`, `get_grid_breakdown()`, `_sanitize_nan()`.

### `EnergyHubService.build_map_data`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `150-162`
- **Signature:** `def build_map_data(`
- **Purpose:** Return cached map data or build it on demand.

**Code:**
```python
def build_map_data(
        self,
        metric: str = "renewable_potential",
        level: str = "province",
    ) -> dict[str, Any]:
        """Return cached map data or build it on demand."""
        cache_key = f"energyhub:map:{metric}:{level}"
        cached = cache_get_sync(cache_key)
        if cached is not None:
            return cached
        result = self._build_map_data(metric, level)
        cache_set_sync(cache_key, result, ttl=3600)
        return result
```

**Explanation:** It accepts `metric`, `level` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `cache_get_sync()`, `_build_map_data()`, `cache_set_sync()`.

### `EnergyHubService._build_map_data`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `164-209`
- **Signature:** `def _build_map_data(`
- **Purpose:** Build choropleth-ready data.

**Code:**
```python
def _build_map_data(
        self,
        metric: str = "renewable_potential",
        level: str = "province",
    ) -> dict[str, Any]:
        """Build choropleth-ready data.

        All metrics use sub-national data:
        - Province-level: aggregated from municipality climate/terrain/suitability scores.
        - Municipality-level: pre-computed suitability scores from Supabase.
        - Barangay-level: inherits parent municipality suitability scores
          with centroid coordinates from geospatial_metadata.

        Args:
            metric: Metric to visualise. One of: renewable_potential,
                solar_potential, wind_potential, hydro_potential, geothermal_potential.
            level: "province", "municipality", or "barangay".
        """
        items: list[dict[str, Any]] = []

        # Municipality-level suitability metrics
        municipality_metrics = {
            "renewable_potential": "composite",
            "solar_potential": "solar",
            "wind_potential": "wind",
            "hydro_potential": "hydro",
            "geothermal_potential": "geothermal",
        }

        if metric in municipality_metrics and level == "municipality":
            column_prefix = municipality_metrics[metric]
            items = self._build_municipality_potential_map(column_prefix)
            return {"items": items, "metric": metric, "level": level}

        if metric in municipality_metrics and level == "barangay":
            items = self._build_barangay_potential_map(municipality_metrics[metric])
            return {"items": items, "metric": metric, "level": level}

        if metric == "renewable_potential":
            # Province-level aggregation (backward compatible)
            items = self._build_renewable_potential_map()

        elif metric == "geothermal_potential":
            items = self._build_geothermal_potential_map()

        return {"items": items, "metric": metric, "level": level}
```

**Explanation:** It accepts `metric`, `level` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_build_municipality_potential_map()`, `_build_barangay_potential_map()`, `_build_renewable_potential_map()`, `_build_geothermal_potential_map()`.

### `EnergyHubService._build_geothermal_potential_map`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `211-342`
- **Signature:** `def _build_geothermal_potential_map(self) -> list[dict[str, Any]]:`
- **Purpose:** Aggregate municipality-level geothermal scores to province level.

**Code:**
```python
def _build_geothermal_potential_map(self) -> list[dict[str, Any]]:
        """Aggregate municipality-level geothermal scores to province level.

        Proximity boost is applied per-municipality (within 25 km of an
        operating plant) before averaging to province level.
        """
        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        try:
            prov_resp = client.table("provinces").select(
                "province_id,name,lat,lon"
            ).limit(10000).execute()
            prov_rows = prov_resp.data or []

            # Fetch municipalities with lat/lon for proximity boost
            muni_resp = client.table("municipalities").select(
                "municipality_id,province_id,name,lat,lon"
            ).limit(10000).execute()
            muni_rows = muni_resp.data or []

            geo_resp = client.table("geothermal_suitability").select(
                "municipality_id,geothermal_score"
            ).limit(10000).execute()
            geo_rows = geo_resp.data or []

            muni_to_prov = {m["municipality_id"]: m["province_id"] for m in muni_rows}
            muni_latlon = {
                m["municipality_id"]: (m.get("lat"), m.get("lon"))
                for m in muni_rows
            }
            muni_name = {
                m["municipality_id"]: m.get("name", "")
                for m in muni_rows
            }

            # Build per-province list of municipality scores (with boost)
            prov_scores: dict[int, list[float]] = {}
            prov_nearby: dict[int, list[dict]] = {}
            for row in geo_rows:
                mid = row.get("municipality_id")
                pid = muni_to_prov.get(mid)
                if pid is None:
                    continue
                base_score = float(row.get("geothermal_score") or 0) * 100.0
                lat, lon = muni_latlon.get(mid, (None, None))
                if lat is not None and lon is not None:
                    boosted, nearby = calculate_proximity_boost(
                        float(lat), float(lon), base_score
                    )
                else:
                    boosted = base_score
                    nearby = []
                prov_scores.setdefault(pid, []).append(boosted)
                if nearby:
                    existing = prov_nearby.setdefault(pid, [])
                    for p in nearby:
                        if not any(
                            e.get("project_name") == p["project_name"]
                            for e in existing
                        ):
                            existing.append(p)

            province_data: dict[str, dict[str, Any]] = {}
            for p in prov_rows:
                pid = p.get("province_id")
                pname = p.get("name", "").strip()
                if not pid or not pname:
                    continue
                scores = prov_scores.get(pid, [0])
                avg = (sum(scores) / len(scores)) if scores else 0.0
                nearby = prov_nearby.get(pid, [])
                province_data[pname.lower()] = {
                    "region": "",
                    "province": pname,
                    "value": round(avg, 2),
                    "lat": p.get("lat"),
                    "lon": p.get("lon"),
                    "nearby_plants": nearby,
                }

            geojson_provinces: list[dict[str, Any]] = _get_geojson_province_names()

            seen = set()
            for gp in geojson_provinces:
                gname = gp["name_lower"]
                if gname in seen:
                    continue
                seen.add(gname)
                data = province_data.get(gname)
                if not data:
                    for api_name, geo_name in _PROVINCE_NAME_MAP.items():
                        if geo_name.lower() == gname and api_name in province_data:
                            data = province_data[api_name]
                            break
                if data:
                    items.append({
                        "region": data["region"],
                        "province": gp["name"],
                        "municipality": None,
                        "value": data["value"],
                        "metric": "geothermal_potential",
                        "lat": data["lat"],
                        "lon": data["lon"],
                        "nearby_plants": data.get("nearby_plants", []),
                    })
                else:
                    items.append({
                        "region": "",
                        "province": gp["name"],
                        "municipality": None,
                        "value": None,
                        "metric": "geothermal_potential",
                        "lat": None,
                        "lon": None,
                        "nearby_plants": [],
                    })

        except Exception as exc:
            logger.warning("Supabase query failed for geothermal map data: %s", exc)
            items.append({
                "region": "Philippines",
                "province": None,
                "municipality": None,
                "value": 50.0,
                "metric": "geothermal_potential",
                "lat": 12.8797,
                "lon": 121.7740,
                "nearby_plants": [],
            })

        return items
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `_get_geojson_province_names()`, `set()`, `get()`.

### `EnergyHubService._build_renewable_potential_map`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `344-506`
- **Signature:** `def _build_renewable_potential_map(self) -> list[dict[str, Any]]:`
- **Purpose:** Aggregate municipality-level climate/terrain into

**Code:**
```python
def _build_renewable_potential_map(self) -> list[dict[str, Any]]:
        """Aggregate municipality-level climate/terrain into
        province-level renewable potential scores."""
        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        try:
            # 1. Fetch provinces directly
            prov_resp = client.table("provinces").select(
                "province_id,name,lat,lon"
            ).limit(10000).execute()
            prov_rows = prov_resp.data or []

            # 2. Fetch hydropower suitability scores
            hydro_resp = client.table("hydropower_suitability").select(
                "province,municipality_name,hydro_suitability_score"
            ).limit(10000).execute()
            hydro_rows = hydro_resp.data or []

            # 2b. Fetch geothermal suitability scores
            geo_resp = client.table("geothermal_suitability").select(
                "municipality_id,geothermal_score"
            ).limit(10000).execute()
            geo_rows = geo_resp.data or []

            # 3. Fetch municipality → province mapping
            muni_resp = client.table("municipalities").select(
                "municipality_id,province_id"
            ).limit(10000).execute()
            muni_rows = muni_resp.data or []

            # 4. Fetch raw climate data (dataset is for 2010)
            climate_resp = client.table("municipality_climate_monthly").select(
                "municipality_id,allsky_sfc_sw_dwn,ws10m"
            ).eq("year", 2010).limit(10000).execute()
            climate_rows = climate_resp.data or []

            # Build mappings
            muni_to_prov = {m["municipality_id"]: m["province_id"] for m in muni_rows}

            # Aggregate climate by province_id
            prov_climate = defaultdict(lambda: {"solar": [], "wind": []})
            for row in climate_rows:
                mid = row.get("municipality_id")
                pid = muni_to_prov.get(mid)
                if pid is not None:
                    prov_climate[pid]["solar"].append(float(row.get("allsky_sfc_sw_dwn") or 0))
                    prov_climate[pid]["wind"].append(float(row.get("ws10m") or 0))

            # Aggregate hydro by province name
            hydro_by_prov: dict[str, list[float]] = {}
            for row in hydro_rows:
                prov = row.get("province", "").strip().lower()
                if prov:
                    score = float(row.get("hydro_suitability_score") or 0)
                    hydro_by_prov.setdefault(prov, []).append(score)

            # Aggregate geothermal by province_id
            geo_by_prov: dict[int, list[float]] = {}
            for row in geo_rows:
                mid = row.get("municipality_id")
                pid = muni_to_prov.get(mid)
                if pid is not None:
                    score = float(row.get("geothermal_score") or 0)
                    geo_by_prov.setdefault(pid, []).append(score)

            # Build province data dict keyed by normalized name
            province_data: dict[str, dict[str, Any]] = {}
            for p in prov_rows:
                pid = p.get("province_id")
                pname = p.get("name", "").strip()
                if not pid or not pname:
                    continue

                solar_vals = prov_climate.get(pid, {}).get("solar", [])
                wind_vals = prov_climate.get(pid, {}).get("wind", [])

                # Convert raw climate values to 0-100 suitability scores
                # Solar: 5.0 kWh/m²/day = excellent → 100
                solar_score = round(min((sum(solar_vals) / len(solar_vals)) / 5.0 * 100, 100), 2) if solar_vals else None
                # Wind: 7.0 m/s = good onshore wind → 100
                wind_score = round(min((sum(wind_vals) / len(wind_vals)) / 7.0 * 100, 100), 2) if wind_vals else None

                prov_lower = pname.lower()
                hydro_scores = hydro_by_prov.get(prov_lower, [])
                # hydro_suitability_score is stored 0-1 → convert to 0-100
                hydro_score = round((sum(hydro_scores) / len(hydro_scores)) * 100, 2) if hydro_scores else None

                geo_scores = geo_by_prov.get(pid, [])
                # geothermal_score is stored 0-1 → convert to 0-100
                geo_score = round((sum(geo_scores) / len(geo_scores)) * 100, 2) if geo_scores else None

                # Average only the renewable scores that have actual data
                available_scores = [
                    s for s in (solar_score, wind_score, hydro_score, geo_score)
                    if s is not None
                ]
                composite = round(sum(available_scores) / len(available_scores), 2) if available_scores else None

                province_data[pname.lower()] = {
                    "region": "",
                    "province": pname,
                    "value": composite,
                    "lat": p.get("lat"),
                    "lon": p.get("lon"),
                }

            # 5. Load GeoJSON to ensure every rendered province has data
            geojson_provinces: list[dict[str, Any]] = _get_geojson_province_names()

            # Build final items: for each GeoJSON province, find matching API data
            seen = set()
            for gp in geojson_provinces:
                gname = gp["name_lower"]
                if gname in seen:
                    continue
                seen.add(gname)

                # Direct match
                data = province_data.get(gname)

                # Try mapped names
                if not data:
                    for api_name, geo_name in _PROVINCE_NAME_MAP.items():
                        if geo_name.lower() == gname and api_name in province_data:
                            data = province_data[api_name]
                            break

                if data:
                    items.append({
                        "region": data["region"],
                        "province": gp["name"],  # Use GeoJSON name for frontend matching
                        "municipality": None,
                        "value": data["value"],
                        "metric": "renewable_potential",
                        "lat": data["lat"],
                        "lon": data["lon"],
                    })
                else:
                    # Missing from database — mark as no data
                    items.append({
                        "region": "",
                        "province": gp["name"],
                        "municipality": None,
                        "value": None,
                        "metric": "renewable_potential",
                        "lat": None,
                        "lon": None,
                    })

        except Exception as exc:
            logger.warning("Supabase query failed for map data: %s", exc)
            items.append({
                "region": "Philippines",
                "province": None,
                "municipality": None,
                "value": 50.0,
                "metric": "renewable_potential",
                "lat": 12.8797,
                "lon": 121.7740,
            })

        return items
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `defaultdict()`, `_get_geojson_province_names()`, `set()`.

### `EnergyHubService._apply_geothermal_boost`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `508-535`
- **Signature:** `def _apply_geothermal_boost(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:`
- **Purpose:** Apply proximity boost and nearby_plants to municipality items.

**Code:**
```python
def _apply_geothermal_boost(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply proximity boost and nearby_plants to municipality items."""
        for item in items:
            lat = item.get("lat")
            lon = item.get("lon")
            value = item.get("value", 0)
            factors = item.get("factors")
            if lat is None or lon is None:
                continue
            boosted, nearby = calculate_proximity_boost(
                float(lat), float(lon), float(value)
            )
            item["value"] = boosted
            item["nearby_plants"] = nearby
            if nearby and factors is not None:
                plant_names = ", ".join(
                    f"{p.get('project_name', 'Plant')} ({p.get('capacity_mw', '?')} MW)"
                    for p in nearby[:3]
                )
                note = f"Near operating geothermal plant(s): {plant_names}."
                try:
                    parsed = json.loads(factors)
                    if isinstance(parsed, dict):
                        parsed["nearby_plants"] = note
                        item["factors"] = json.dumps(parsed)
                except Exception:
                    item["factors"] = f"{factors}\n{note}" if factors else note
        return items
```

**Explanation:** It accepts `items` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get()`, `calculate_proximity_boost()`, `float()`, `join()`, `loads()`.

### `EnergyHubService._build_municipality_potential_map`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `537-597`
- **Signature:** `def _build_municipality_potential_map(self, column_prefix: str) -> list[dict[str, Any]]:`
- **Purpose:** Return pre-computed municipality suitability scores from Supabase.

**Code:**
```python
def _build_municipality_potential_map(self, column_prefix: str) -> list[dict[str, Any]]:
        """Return pre-computed municipality suitability scores from Supabase.

        Uses Redis cache first, then falls back to the municipalities table.
        """
        metric_name = f"{column_prefix}_potential" if column_prefix != "composite" else "renewable_potential"
        cached = get_suitability_cache_sync(metric_name, "municipality")
        if cached and column_prefix != "geothermal":
            logger.info("Cache hit for municipality %s suitability", metric_name)
            return cached  # type: ignore[return-value]

        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        score_col = f"{column_prefix}_suitability_score"
        class_col = f"{column_prefix}_classification"
        factors_col = f"{column_prefix}_factors"
        # composite_factors may not exist yet; omit from select if composite
        has_factors_col = column_prefix != "composite"
        select_cols = (
            f"municipality_id, name, province_id, lat, lon, "
            f"provinces(name), {score_col}, {class_col}"
        )
        if has_factors_col:
            select_cols += f", {factors_col}"

        try:
            resp = (
                client.table("municipalities")
                .select(select_cols)
                .not_.is_(score_col, "null")
                .execute()
            )
            rows = resp.data or []
            for r in rows:
                province_obj = r.get("provinces")
                province_name = province_obj.get("name", "") if province_obj else ""
                items.append({
                    "region": "",
                    "province": province_name,
                    "municipality": r.get("name"),
                    "municipality_id": r.get("municipality_id"),
                    "value": float(r.get(score_col) or 0),
                    "classification": r.get(class_col),
                    "factors": r.get(factors_col) if has_factors_col else None,
                    "metric": metric_name,
                    "lat": r.get("lat"),
                    "lon": r.get("lon"),
                    "nearby_plants": [],
                })

            # Apply geothermal proximity boost after building items
            if column_prefix == "geothermal":
                items = self._apply_geothermal_boost(items)
                # Don't cache boosted geothermal data so boosts are always fresh
            else:
                set_suitability_cache_sync(metric_name, "municipality", items)
        except Exception as exc:
            logger.warning("Supabase query failed for municipality map data: %s", exc)

        return items
```

**Explanation:** It accepts `column_prefix` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_suitability_cache_sync()`, `info()`, `get_supabase_client()`, `execute()`, `get()`.

### `EnergyHubService._build_barangay_potential_map`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `599-663`
- **Signature:** `def _build_barangay_potential_map(self, column_prefix: str) -> list[dict[str, Any]]:`
- **Purpose:** Build barangay-level suitability map by inheriting parent municipality scores.

**Code:**
```python
def _build_barangay_potential_map(self, column_prefix: str) -> list[dict[str, Any]]:
        """Build barangay-level suitability map by inheriting parent municipality scores.

        Barangays don't have their own suitability scores — they inherit
        from their parent municipality. Centroids come from geospatial_metadata
        or barangays.lat/lon as fallback.
        """
        metric_name = f"{column_prefix}_potential" if column_prefix != "composite" else "renewable_potential"
        cached = get_suitability_cache_sync(metric_name, "barangay")
        if cached and column_prefix != "geothermal":
            logger.info("Cache hit for barangay %s suitability", metric_name)
            return cached  # type: ignore[return-value]

        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        score_col = f"{column_prefix}_suitability_score"
        class_col = f"{column_prefix}_classification"

        try:
            # Fetch barangays with parent municipality info
            select_cols = (
                f"barangay_id, name, municipality_id, lat, lon, "
                f"municipalities(name, province_id, {score_col}, {class_col}, provinces(name))"
            )
            resp = (
                client.table("barangays")
                .select(select_cols)
                .limit(50000)
                .execute()
            )
            rows = resp.data or []

            for r in rows:
                muni = r.get("municipalities")
                if not muni:
                    continue
                score = muni.get(score_col)
                if score is None:
                    continue

                prov_obj = muni.get("provinces")
                province_name = prov_obj.get("name", "") if prov_obj else ""

                items.append({
                    "region": "",
                    "province": province_name,
                    "municipality": muni.get("name"),
                    "barangay": r.get("name"),
                    "barangay_id": r.get("barangay_id"),
                    "value": float(score),
                    "classification": muni.get(class_col),
                    "metric": metric_name,
                    "lat": r.get("lat"),
                    "lon": r.get("lon"),
                    "nearby_plants": [],
                })

            if column_prefix != "geothermal" and items:
                set_suitability_cache_sync(metric_name, "barangay", items)

        except Exception as exc:
            logger.warning("Supabase query failed for barangay map data: %s", exc)

        return items
```

**Explanation:** It accepts `column_prefix` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_suitability_cache_sync()`, `info()`, `get_supabase_client()`, `execute()`, `get()`.

### `EnergyHubService.get_ai_insight`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `667-670`
- **Signature:** `def get_ai_insight(self, use_llm: bool = False) -> dict[str, str]:`
- **Purpose:** Method of `EnergyHubService` that retrieves ai insight.

**Code:**
```python
def get_ai_insight(self, use_llm: bool = False) -> dict[str, str]:
        if use_llm:
            return self._generate_llm_insight()
        return self._ml.get_ai_insight()
```

**Explanation:** It accepts `use_llm` and returns `dict[str, str]`. See the code below for the full implementation. Key calls include `_generate_llm_insight()`, `get_ai_insight()`.

### `EnergyHubService.analyze_chart`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `672-712`
- **Signature:** `def analyze_chart(self, chart_type: str, chart_data: dict[str, Any], force_refresh: bool = False) -> dict[str, str]:`
- **Purpose:** Generate an LLM-powered explanation for a specific chart with DB caching and rotation.

**Code:**
```python
def analyze_chart(self, chart_type: str, chart_data: dict[str, Any], force_refresh: bool = False) -> dict[str, str]:
        """Generate an LLM-powered explanation for a specific chart with DB caching and rotation."""
        chart_hash = self._hash_chart_data(chart_data)

        # 1. Check cache (unless force refresh)
        if not force_refresh:
            cached = self._get_cached_insight(chart_type, chart_hash)
            if cached:
                logger.info("Cache hit for chart %s (hash=%s)", chart_type, chart_hash[:8])
                return {
                    "insight": cached,
                    "recommendation": "",
                    "data_year": chart_data.get("latest_year", 2024),
                    "chart_type": chart_type,
                }

        # 2. Call LLM
        try:
            from app.services.llm_client import generate_response
        except Exception:
            logger.warning("LLM client not available; falling back to static insight.")
            return self._ml.get_ai_insight()

        prompt = self._build_chart_prompt(chart_type, chart_data)
        try:
            text = generate_response(prompt, temperature=0.5, max_output_tokens=2500)
        except Exception as exc:
            logger.warning("LLM call failed for chart analysis: %s", exc)
            return self._ml.get_ai_insight()

        cleaned = self._clean_llm_text(text)

        # 3. Store in cache
        self._cache_insight(chart_type, chart_hash, cleaned)

        return {
            "insight": cleaned,
            "recommendation": "",
            "data_year": chart_data.get("latest_year", 2024),
            "chart_type": chart_type,
        }
```

**Explanation:** It accepts `chart_type`, `chart_data`, `force_refresh` and returns `dict[str, str]`. See the code below for the full implementation. Key calls include `_hash_chart_data()`, `_get_cached_insight()`, `info()`, `get()`, `warning()`.

### `EnergyHubService._hash_chart_data`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `715-719`
- **Signature:** `def _hash_chart_data(chart_data: dict[str, Any]) -> str:`
- **Purpose:** Stable hash for chart data so identical inputs share cache.

**Code:**
```python
def _hash_chart_data(chart_data: dict[str, Any]) -> str:
        """Stable hash for chart data so identical inputs share cache."""
        import hashlib, json
        canonical = json.dumps(chart_data, sort_keys=True, default=str)
        return hashlib.md5(canonical.encode()).hexdigest()
```

**Explanation:** It accepts `chart_data` and returns `str`. See the code below for the full implementation. Key calls include `dumps()`, `hexdigest()`, `md5()`, `encode()`.

### `EnergyHubService._get_cached_insight`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `721-740`
- **Signature:** `def _get_cached_insight(self, chart_type: str, chart_hash: str) -> str | None:`
- **Purpose:** Fetch a cached insight; if multiple exist, rotate randomly.

**Code:**
```python
def _get_cached_insight(self, chart_type: str, chart_hash: str) -> str | None:
        """Fetch a cached insight; if multiple exist, rotate randomly."""
        client = get_supabase_client()
        try:
            resp = (
                client.table("chart_ai_insights")
                .select("insight")
                .eq("chart_type", chart_type)
                .eq("chart_data_hash", chart_hash)
                .execute()
            )
            rows = resp.data or []
            if not rows:
                return None
            # Rotate: pick one at random from cached variants
            import random
            return random.choice(rows)["insight"]
        except Exception as exc:
            logger.debug("Cache read failed (table may not exist yet): %s", exc)
            return None
```

**Explanation:** It accepts `chart_type`, `chart_hash` and returns `str | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `choice()`, `debug()`, `eq()`.

### `EnergyHubService._cache_insight`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `742-775`
- **Signature:** `def _cache_insight(self, chart_type: str, chart_hash: str, insight: str) -> None:`
- **Purpose:** Store a new LLM insight in the cache. Keeps up to 3 variants per chart+hash.

**Code:**
```python
def _cache_insight(self, chart_type: str, chart_hash: str, insight: str) -> None:
        """Store a new LLM insight in the cache. Keeps up to 3 variants per chart+hash."""
        client = get_supabase_client()
        try:
            # Count existing variants
            count_resp = (
                client.table("chart_ai_insights")
                .select("id", count="exact")
                .eq("chart_type", chart_type)
                .eq("chart_data_hash", chart_hash)
                .execute()
            )
            existing = count_resp.count or 0
            if existing >= 3:
                # Evict oldest to keep cache bounded
                oldest = (
                    client.table("chart_ai_insights")
                    .select("id")
                    .eq("chart_type", chart_type)
                    .eq("chart_data_hash", chart_hash)
                    .order("created_at")
                    .limit(1)
                    .execute()
                )
                if oldest.data:
                    old_id = oldest.data[0]["id"]
                    client.table("chart_ai_insights").delete().eq("id", old_id).execute()
            client.table("chart_ai_insights").insert({
                "chart_type": chart_type,
                "chart_data_hash": chart_hash,
                "insight": insight,
            }).execute()
        except Exception as exc:
            logger.debug("Cache write failed (table may not exist yet): %s", exc)
```

**Explanation:** It accepts `chart_type`, `chart_hash`, `insight` and returns `None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `debug()`, `eq()`, `insert()`.

### `EnergyHubService._generate_llm_insight`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `777-831`
- **Signature:** `def _generate_llm_insight(self) -> dict[str, str]:`
- **Purpose:** Generate a comprehensive LLM insight from all energy data.

**Code:**
```python
def _generate_llm_insight(self) -> dict[str, str]:
        """Generate a comprehensive LLM insight from all energy data."""
        try:
            from app.services.llm_client import generate_response
        except Exception:
            logger.warning("LLM client not available; falling back to static insight.")
            return self._ml.get_ai_insight()

        latest = self._ml.get_latest_statistics()
        forecast = self._ml.get_forecast("consumption")
        source = self._ml.get_source_breakdown()

        forecast_values = forecast.get("forecast_values") or []
        f_2030 = forecast_values[-1] if forecast_values else 0
        consumption = latest.get("total_consumption_gwh", 0) or 0
        forecast_growth = ((f_2030 / consumption) - 1) * 100 if consumption else 0.0

        prompt = (
            "You are LUMI, an Environmental Intelligence assistant for Philippine energy data.\n"
            "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
            f"Latest Year: {latest.get('year', 2024)}\n"
            f"Total Consumption: {latest.get('total_consumption_gwh', 0):,.0f} GWh\n"
            f"Total Peak Demand: {latest.get('total_peak_demand_mw', 0):,.0f} MW\n"
            f"Renewable Share: {latest.get('renewable_share_pct', 0)}%\n"
            f"Capacity Margin: {latest.get('capacity_margin_pct', 0)}%\n\n"
            f"ARIMA Forecast 2030: {f_2030:,.0f} GWh\n"
            f"Forecast Growth: {forecast_growth:.1f}%\n\n"
            "Generation Mix (2024):\n"
        )
        for src, pct in source.get("share_pct", {}).items():
            prompt += f"  - {src}: {pct}%\n"

        prompt += (
            "\nProvide a comprehensive 5-paragraph response that is PRESCRIPTIVE and ACTION-ORIENTED, not just descriptive.\n"
            "Each paragraph must end with concrete, specific recommendations (what should be done, by whom, and by when).\n\n"
            "1. Diagnose the current energy situation (consumption, peak demand, capacity margin) and prescribe immediate actions for the DOE and NGCP.\n"
            "2. Evaluate the renewable energy share and generation mix, then recommend specific policy changes, feed-in tariffs, or regulatory reforms to accelerate RE adoption.\n"
            "3. Interpret the ARIMA 2030 forecast and prescribe infrastructure investments, transmission upgrades, and capacity additions with timelines.\n"
            "4. Identify barriers to decarbonization and prescribe risk-mitigation strategies for stranded assets, baseload transitions, and grid integration.\n"
            "5. Give a forward-looking action plan with specific, measurable steps for the DOE, NGCP, local government units, and private investors.\n"
            "Aim for 400–600 words. Use plain language suitable for students and communities, but include specific data points and actionable steps."
        )

        try:
            text = generate_response(prompt, temperature=0.3, max_output_tokens=2500)
        except Exception as exc:
            logger.warning("LLM call failed: %s", exc)
            return self._ml.get_ai_insight()

        cleaned = self._clean_llm_text(text)
        return {
            "insight": cleaned,
            "recommendation": "",
            "data_year": latest.get("year", 2024),
        }
```

**Explanation:** It accepts zero arguments and returns `dict[str, str]`. See the code below for the full implementation. Key calls include `warning()`, `get_ai_insight()`, `get_latest_statistics()`, `get_forecast()`, `get_source_breakdown()`.

### `EnergyHubService._clean_llm_text`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `834-840`
- **Signature:** `def _clean_llm_text(text: str) -> str:`
- **Purpose:** Strip JSON wrappers, markdown fences, and clean LLM output for display.

**Code:**
```python
def _clean_llm_text(text: str) -> str:
        """Strip JSON wrappers, markdown fences, and clean LLM output for display.

        Delegates to the unified llm_sanitizer module.
        """
        from app.services.llm_sanitizer import sanitize_llm_output
        return sanitize_llm_output(text)
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `sanitize_llm_output()`.

### `EnergyHubService._build_chart_prompt`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `842-955`
- **Signature:** `def _build_chart_prompt(self, chart_type: str, chart_data: dict[str, Any]) -> str:`
- **Purpose:** Method of `EnergyHubService` that handles  build chart prompt.

**Code:**
```python
def _build_chart_prompt(self, chart_type: str, chart_data: dict[str, Any]) -> str:
        if chart_type == "trends":
            years = chart_data.get("years", [])
            consumption = chart_data.get("consumption", [])
            forecast = chart_data.get("forecast", [])
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine energy consumption trend in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                f"Historical years: {years[:5]}...{years[-3:]}\n"
                f"Consumption (GWh): {consumption[:5]}...{consumption[-3:]}\n"
                f"Forecast: {forecast}\n\n"
                "Cover:\n"
                "1) Identify key consumption patterns and prescribe immediate demand-side management or efficiency programs.\n"
                "2) Flag inflection points and prescribe policy responses or infrastructure investments needed.\n"
                "3) Translate the forecast into concrete grid planning actions with timelines for the DOE and NGCP."
            )
        if chart_type == "consumption_trend":
            years = chart_data.get("years", [])
            consumption = chart_data.get("consumption", [])
            forecast_years = chart_data.get("forecast_years", [])
            forecast_values = chart_data.get("forecast_values", [])
            latest = consumption[-1] if consumption else 0
            first = consumption[0] if consumption else 0
            growth = ((latest / first) - 1) * 100 if first else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine total energy consumption chart in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                f"Historical consumption (GWh): {consumption[:3]} ... {consumption[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Forecast: {forecast_values[0] if forecast_values else 'N/A'} GWh in {forecast_years[0] if forecast_years else 'N/A'} "
                f"to {forecast_values[-1] if forecast_values else 'N/A'} GWh in {forecast_years[-1] if forecast_years else 'N/A'}\n"
                f"Overall growth from {first:.0f} to {latest:.0f} GWh = {growth:.1f}%\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Diagnose the growth trajectory and prescribe what the DOE and ERC should do now (policy, pricing, enforcement).\n"
                "2) Identify acceleration/deceleration phases and prescribe demand-side management or industrial efficiency programs.\n"
                "3) Compare to ASEAN benchmarks and prescribe specific capacity targets or import strategies.\n"
                "4) Translate the forecast into concrete grid planning and transmission investment priorities with timelines.\n"
                "5) Prescribe emergency and long-term actions to diversify the generation mix and improve energy security."
            )
        if chart_type == "peak_demand":
            years = chart_data.get("years", [])
            peak_demand = chart_data.get("peak_demand", [])
            latest = peak_demand[-1] if peak_demand else 0
            first = peak_demand[0] if peak_demand else 0
            growth = ((latest / first) - 1) * 100 if first else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine peak electricity demand chart in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                f"Peak demand (MW): {peak_demand[:3]} ... {peak_demand[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Overall growth from {first:.0f} to {latest:.0f} MW = {growth:.1f}%\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Compare peak demand growth to installed capacity and prescribe immediate capacity additions or reserve contracts.\n"
                "2) Assess grid reliability risks and prescribe concrete brownout prevention measures for NGCP.\n"
                "3) Prescribe demand-side management programs and time-of-use pricing reforms with implementation steps.\n"
                "4) Recommend specific renewable + battery storage projects to displace peaker plants and reduce peak stress.\n"
                "5) Give a 5-year infrastructure roadmap with policy actions for the DOE and NGCP."
            )
        if chart_type == "renewable_generation":
            years = chart_data.get("years", [])
            renewable = chart_data.get("renewable_generation", [])
            total = chart_data.get("total_generation", [])
            latest_re = renewable[-1] if renewable else 0
            latest_total = total[-1] if total else 1
            share = (latest_re / latest_total) * 100 if latest_total else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine renewable energy generation chart in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                f"Renewable generation (GWh): {renewable[:3]} ... {renewable[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Total generation (GWh): {total[:3]} ... {total[-3:]}\n"
                f"Latest renewable share: {share:.1f}%\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Assess renewable growth pace and prescribe specific capacity targets and auction schedules to meet the 35% RE Act goal.\n"
                "2) Compare current share to the 35% target and prescribe regulatory reforms (permitting, grid access, FIT adjustments).\n"
                "3) Break down each renewable source and prescribe resource-specific investment priorities and locations.\n"
                "4) Identify financing gaps and prescribe blended finance instruments, green bonds, or development bank partnerships.\n"
                "5) Prescribe grid integration solutions, storage mandates, and transmission upgrades to handle intermittency."
            )
        if chart_type == "sources":
            shares = chart_data.get("shares", {})
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of the Philippine energy generation mix in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                + "\n".join([f"  - {k}: {v}%" for k, v in shares.items()])
                + "\n\nCover these points with actionable recommendations:\n"
                "1) Diagnose fossil fuel dominance and prescribe concrete coal phase-out milestones, natural gas transition plans, and replacement targets.\n"
                "2) Evaluate each renewable source and prescribe resource-specific procurement targets, auction volumes, and pipeline projects.\n"
                "3) Assess climate commitment gaps and prescribe NDC updates, carbon pricing, and just transition fund mechanisms.\n"
                "4) Identify decarbonization barriers and prescribe stranded asset mitigation strategies, flexible baseload contracts, and smart grid investments.\n"
                "5) Provide a decade-by-decade action roadmap with specific 2030, 2035, and 2040 milestones for reaching 50% renewables."
            )
        if chart_type == "map":
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine province-level renewable potential map in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                "Scores are based on solar irradiance (40%), wind speed (30%), and hydropower suitability (30%).\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Explain regional score variations and prescribe priority zones for solar parks, wind farms, and micro-hydro installations.\n"
                "2) Prescribe how the DOE and NREB should use this map for competitive RE auctions, zoning, and transmission planning.\n"
                "3) Recommend specific actions for LGUs (local government units), investors, and host communities to develop high-potential sites.\n"
                "4) Identify data limitations and prescribe additional surveys (LiDAR wind, streamflow gauging, grid capacity mapping).\n"
                "5) Prescribe how to integrate these scores into the Philippine Energy Plan with concrete capacity targets per region."
            )
        return "Provide a brief energy insight based on the available data."
```

**Explanation:** It accepts `chart_type`, `chart_data` and returns `str`. See the code below for the full implementation. Key calls include `get()`, `join()`, `items()`.

### `EnergyHubService.get_provincial_consumption`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `959-966`
- **Signature:** `def get_provincial_consumption(self, region: str | None = None) -> dict[str, Any]:`
- **Purpose:** Return DOE Annex 8 provincial/regional consumption.

**Code:**
```python
def get_provincial_consumption(self, region: str | None = None) -> dict[str, Any]:
        """Return DOE Annex 8 provincial/regional consumption."""
        data = self._ml.get_provincial_consumption(region)
        return {
            "items": data.get("items", []),
            "region": region,
            "note": "Values in MWh from DOE Annex 8 (2025).",
        }
```

**Explanation:** It accepts `region` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_provincial_consumption()`, `get()`.

### `EnergyHubService.estimate_municipal_demand`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `968-1056`
- **Signature:** `def estimate_municipal_demand(self, province_id: int) -> dict[str, Any]:`
- **Purpose:** Estimate municipal demand via population-weighted disaggregation.

**Code:**
```python
def estimate_municipal_demand(self, province_id: int) -> dict[str, Any]:
        """Estimate municipal demand via population-weighted disaggregation.

        Formula: D_muni = D_prov * (P_muni / P_prov)
        Requires PSA population data in the municipal_population table.
        """
        client = get_supabase_client()

        # 1. Fetch province total consumption from DOE v2
        prov_name_resp = (
            client.table("provinces")
            .select("name")
            .eq("province_id", province_id)
            .single()
            .execute()
        )
        if not prov_name_resp.data:
            return {"items": [], "province": None, "note": "Province not found."}
        province_name = prov_name_resp.data["name"]

        # Map province name to DOE region code (best-effort mapping)
        region_code = self._province_to_region_code(province_name)
        prov_data = self._ml.get_provincial_consumption(region_code)
        total_consumption_items = [
            item for item in prov_data.get("items", [])
            if item.get("sector") == "Total Consumption"
        ]
        if not total_consumption_items:
            return {
                "items": [],
                "province": province_name,
                "note": f"No DOE consumption data found for region {region_code}.",
            }
        total_consumption_mwh = float(total_consumption_items[0].get("value_mwh", 0))

        # 2. Fetch municipality populations
        try:
            pop_resp = (
                client.table("municipal_population")
                .select("municipality_id,population,municipalities(name)")
                .eq("province_id", province_id)
                .execute()
            )
            pop_rows = pop_resp.data or []
        except Exception:
            pop_rows = []

        if not pop_rows:
            return {
                "items": [],
                "province": province_name,
                "note": (
                    "PSA population data not yet loaded. "
                    "Municipal demand estimation requires municipal_population table."
                ),
            }

        total_pop = sum(r.get("population", 0) or 0 for r in pop_rows)
        if total_pop <= 0:
            return {
                "items": [],
                "province": province_name,
                "note": "Population data sums to zero.",
            }

        items = []
        for row in pop_rows:
            muni_pop = row.get("population", 0) or 0
            ratio = muni_pop / total_pop if total_pop > 0 else 0
            est_demand = total_consumption_mwh * ratio
            muni_name = (
                row.get("municipalities", {}).get("name")
                if isinstance(row.get("municipalities"), dict)
                else row.get("municipality_name", "Unknown")
            )
            items.append({
                "municipality_id": row.get("municipality_id"),
                "municipality_name": muni_name,
                "province_name": province_name,
                "estimated_demand_mwh": round(est_demand, 2),
                "method": "population_weighted_disaggregation",
                "note": "Estimated from provincial DOE data using PSA population ratios. Actual demand may vary.",
            })

        return {
            "items": items,
            "province": province_name,
            "note": f"Estimated for {len(items)} municipalities in {province_name}.",
        }
```

**Explanation:** It accepts `province_id` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `single()`, `eq()`, `select()`.

### `EnergyHubService._province_to_region_code`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1059-1152`
- **Signature:** `def _province_to_region_code(province_name: str) -> str:`
- **Purpose:** Best-effort mapping of province name to DOE region code.

**Code:**
```python
def _province_to_region_code(province_name: str) -> str:
        """Best-effort mapping of province name to DOE region code.

        DOE Annex 8 uses region codes (I, II, III, IV-A, IV-B, V, VI,
        VII, VIII, IX, X, XI, XII, XIII, NCR, CAR, ARMM, NIR).
        """
        mapping = {
            "metro manila": "NCR",
            "ncr": "NCR",
            "abra": "CAR",
            "apayao": "CAR",
            "benguet": "CAR",
            "ifugao": "CAR",
            "kalinga": "CAR",
            "mountain province": "CAR",
            "ilocos norte": "I",
            "ilocos sur": "I",
            "la union": "I",
            "pangasinan": "I",
            "batanes": "II",
            "cagayan": "II",
            "isabela": "II",
            "nueva vizcaya": "II",
            "quirino": "II",
            "aurora": "III",
            "bataan": "III",
            "bulacan": "III",
            "nueva ecija": "III",
            "pampanga": "III",
            "tarlac": "III",
            "zambales": "III",
            "batangas": "IV-A",
            "cavite": "IV-A",
            "laguna": "IV-A",
            "quezon": "IV-A",
            "rizal": "IV-A",
            "marinduque": "IV-B",
            "occidental mindoro": "IV-B",
            "oriental mindoro": "IV-B",
            "palawan": "IV-B",
            "romblon": "IV-B",
            "albay": "V",
            "camarines norte": "V",
            "camarines sur": "V",
            "catanduanes": "V",
            "masbate": "V",
            "sorsogon": "V",
            "aklan": "VI",
            "antique": "VI",
            "capiz": "VI",
            "guimaras": "VI",
            "iloilo": "VI",
            "negros occidental": "VI",
            "bohol": "VII",
            "cebu": "VII",
            "negros oriental": "VII",
            "siargao": "XIII",
            "siquijor": "VII",
            "biliran": "VIII",
            "eastern samar": "VIII",
            "leyte": "VIII",
            "northern samar": "VIII",
            "samar": "VIII",
            "southern leyte": "VIII",
            "zamboanga del norte": "IX",
            "zamboanga del sur": "IX",
            "zamboanga sibugay": "IX",
            "bukidnon": "X",
            "camiguin": "X",
            "lanao del norte": "X",
            "misamis occidental": "X",
            "misamis oriental": "X",
            "compostela valley": "XI",
            "davao de oro": "XI",
            "davao del norte": "XI",
            "davao del sur": "XI",
            "davao occidental": "XI",
            "davao oriental": "XI",
            "cotabato": "XII",
            "sarangani": "XII",
            "south cotabato": "XII",
            "sultan kudarat": "XII",
            "agusan del norte": "XIII",
            "agusan del sur": "XIII",
            "dinagat islands": "XIII",
            "surigao del norte": "XIII",
            "surigao del sur": "XIII",
            "basilan": "ARMM",
            "lanao del sur": "ARMM",
            "maguindanao": "ARMM",
            "sulu": "ARMM",
            "tawi-tawi": "ARMM",
        }
        return mapping.get(province_name.lower().strip(), province_name)
```

**Explanation:** It accepts `province_name` and returns `str`. See the code below for the full implementation. Key calls include `get()`, `strip()`, `lower()`.

### `EnergyHubService.get_irena_capacity`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1156-1157`
- **Signature:** `def get_irena_capacity(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that retrieves irena capacity.

**Code:**
```python
def get_irena_capacity(self, year: int | None = None) -> dict[str, Any]:
        return self._ml.get_irena_capacity(year)
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_irena_capacity()`.

### `EnergyHubService.get_irena_generation`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1159-1160`
- **Signature:** `def get_irena_generation(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that retrieves irena generation.

**Code:**
```python
def get_irena_generation(self, year: int | None = None) -> dict[str, Any]:
        return self._ml.get_irena_generation(year)
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_irena_generation()`.

### `EnergyHubService.get_irena_renewable_share`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1162-1163`
- **Signature:** `def get_irena_renewable_share(self) -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that retrieves irena renewable share.

**Code:**
```python
def get_irena_renewable_share(self) -> dict[str, Any]:
        return self._ml.get_irena_renewable_share()
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_irena_renewable_share()`.

### `EnergyHubService.get_meralco_rate`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1165-1166`
- **Signature:** `def get_meralco_rate(self, year: int | None = None) -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that retrieves meralco rate.

**Code:**
```python
def get_meralco_rate(self, year: int | None = None) -> dict[str, Any]:
        return self._ml.get_meralco_rate(year)
```

**Explanation:** It accepts `year` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_meralco_rate()`.

### `EnergyHubService.get_solar_atlas`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1168-1169`
- **Signature:** `def get_solar_atlas(self, location: str | None = None) -> dict[str, Any]:`
- **Purpose:** Method of `EnergyHubService` that retrieves solar atlas.

**Code:**
```python
def get_solar_atlas(self, location: str | None = None) -> dict[str, Any]:
        return self._ml.get_solar_atlas(location)
```

**Explanation:** It accepts `location` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_solar_atlas()`.

### `EnergyHubService.build_irena_overview`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1171-1181`
- **Signature:** `def build_irena_overview(self) -> dict[str, Any]:`
- **Purpose:** Combine capacity, generation, and renewable share for frontend benchmarking.

**Code:**
```python
def build_irena_overview(self) -> dict[str, Any]:
        """Combine capacity, generation, and renewable share for frontend benchmarking."""
        cap = self._ml.get_irena_capacity()
        gen = self._ml.get_irena_generation()
        share = self._ml.get_irena_renewable_share()
        return {
            "capacity": cap.get("items", []),
            "generation": gen.get("items", []),
            "renewable_share": share.get("items", []),
            "note": "Data from IRENA. Displayed alongside DOE for benchmarking purposes.",
        }
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_irena_capacity()`, `get_irena_generation()`, `get_irena_renewable_share()`, `get()`.

### `get_energyhub_service`

- **File:** `fastapi-backend/app/services/energyhub.py`
- **Lines:** `1188-1192`
- **Signature:** `def get_energyhub_service() -> EnergyHubService:`
- **Purpose:** Retrieves energyhub service.

**Code:**
```python
def get_energyhub_service() -> EnergyHubService:
    global _energyhub_service
    if _energyhub_service is None:
        _energyhub_service = EnergyHubService()
    return _energyhub_service
```

**Explanation:** It accepts zero arguments and returns `EnergyHubService`. See the code below for the full implementation. Key calls include `EnergyHubService()`.


## `fastapi-backend/app/services/etl_orchestrator.py`

**File:** `fastapi-backend/app/services/etl_orchestrator.py`

**Summary:** ETL orchestrator, data lineage tracking, and validation for LUMI.

### `log_lineage`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `25-71`
- **Signature:** `def log_lineage(`
- **Purpose:** Log a data lineage entry to the data_lineage table.

**Code:**
```python
def log_lineage(
    source: str,
    table: str,
    operation: str,
    rows_affected: int = 0,
    status: str = "success",
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str | None:
    """Log a data lineage entry to the data_lineage table.

    Args:
        source: Data source name (e.g., 'NASA_POWER', 'PSGC', 'DOE')
        table: Target table name
        operation: 'insert', 'update', 'upsert', 'delete', 'scrape'
        rows_affected: Number of rows affected
        status: 'success', 'failed', 'partial'
        error_message: Error details if failed
        metadata: Additional context (URLs, parameters, etc.)

    Returns:
        Lineage record ID if logged, None on failure
    """
    try:
        import json as _json
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table("data_lineage")
            .insert({
                "source": source,
                "target_table": table,
                "operation": operation,
                "rows_affected": rows_affected,
                "status": status,
                "error_message": error_message,
                "metadata": _json.dumps(metadata) if metadata else None,
                "run_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
        if resp.data:
            return resp.data[0].get("id")
    except Exception as exc:
        logger.warning("Failed to log data lineage: %s", exc)
    return None
```

**Explanation:** It accepts `source`, `table`, `operation`, `rows_affected`, `status`, `error_message`, `metadata` and returns `str | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `get()`, `warning()`, `insert()`.

### `get_lineage_history`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `74-93`
- **Signature:** `def get_lineage_history(`
- **Purpose:** Fetch data lineage history with optional filters.

**Code:**
```python
def get_lineage_history(
    source: str | None = None,
    table: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Fetch data lineage history with optional filters."""
    try:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()

        query = client.table("data_lineage").select("*")
        if source:
            query = query.eq("source", source)
        if table:
            query = query.eq("target_table", table)
        resp = query.order("run_at", desc=True).limit(limit).execute()
        return resp.data or []
    except Exception as exc:
        logger.warning("Failed to fetch lineage history: %s", exc)
        return []
```

**Explanation:** It accepts `source`, `table`, `limit` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `select()`, `execute()`, `eq()`, `warning()`.

### `validate_dataframe`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `110-212`
- **Signature:** `def validate_dataframe(`
- **Purpose:** Validate a pandas DataFrame against schema constraints.

**Code:**
```python
def validate_dataframe(
    df: Any,
    required_columns: list[str],
    column_ranges: dict[str, tuple[float, float]] | None = None,
    unique_columns: list[str] | None = None,
    non_null_columns: list[str] | None = None,
) -> ValidationResult:
    """Validate a pandas DataFrame against schema constraints.

    Args:
        df: pandas DataFrame to validate
        required_columns: Columns that must exist
        column_ranges: Dict of column → (min, max) for range checks
        unique_columns: Columns that must have unique values
        non_null_columns: Columns that must not have null values

    Returns:
        ValidationResult with errors, warnings, and column statistics
    """
    import pandas as pd

    errors: list[str] = []
    warnings: list[str] = []
    column_stats: dict[str, dict[str, Any]] = {}

    if df is None or df.empty:
        return ValidationResult(
            is_valid=False,
            total_rows=0,
            errors=["DataFrame is empty or None"],
        )

    total_rows = len(df)

    # Check required columns
    missing_cols = [c for c in required_columns if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")

    # Check non-null constraints
    if non_null_columns:
        for col in non_null_columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    errors.append(f"Column '{col}' has {null_count} null values (must be non-null)")

    # Check range constraints
    if column_ranges:
        for col, (min_val, max_val) in column_ranges.items():
            if col not in df.columns:
                continue
            col_data = df[col].dropna()
            if col_data.empty:
                continue
            out_of_range = ((col_data < min_val) | (col_data > max_val)).sum()
            if out_of_range > 0:
                errors.append(
                    f"Column '{col}' has {out_of_range} values outside range [{min_val}, {max_val}]"
                )

    # Check uniqueness constraints
    if unique_columns:
        for col in unique_columns:
            if col in df.columns:
                dup_count = df[col].duplicated().sum()
                if dup_count > 0:
                    errors.append(f"Column '{col}' has {dup_count} duplicate values (must be unique)")

    # Compute column statistics
    for col in df.columns:
        if df[col].dtype in ["float64", "int64", "float32", "int32"]:
            col_data = df[col].dropna()
            column_stats[col] = {
                "count": int(col_data.count()),
                "null_count": int(df[col].isnull().sum()),
                "min": float(col_data.min()) if not col_data.empty else None,
                "max": float(col_data.max()) if not col_data.empty else None,
                "mean": float(col_data.mean()) if not col_data.empty else None,
                "std": float(col_data.std()) if not col_data.empty else None,
            }
        else:
            column_stats[col] = {
                "count": int(df[col].count()),
                "null_count": int(df[col].isnull().sum()),
                "unique_values": int(df[col].nunique()),
            }

    # Warnings for high null rates
    for col in df.columns:
        null_rate = df[col].isnull().sum() / total_rows if total_rows else 0
        if 0.1 < null_rate <= 0.5:
            warnings.append(f"Column '{col}' has {null_rate:.1%} null values")
        elif null_rate > 0.5:
            warnings.append(f"Column '{col}' has {null_rate:.1%} null values (high null rate)")

    return ValidationResult(
        is_valid=len(errors) == 0,
        total_rows=total_rows,
        errors=errors,
        warnings=warnings,
        column_stats=column_stats,
    )
```

**Explanation:** It accepts `df`, `required_columns`, `column_ranges`, `unique_columns`, `non_null_columns` and returns `ValidationResult`. See the code below for the full implementation. Key calls include `ValidationResult()`, `len()`, `append()`, `join()`, `sum()`.

### `get_random_user_agent`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `227-230`
- **Signature:** `def get_random_user_agent() -> str:`
- **Purpose:** Return a random user-agent string for scraper rotation.

**Code:**
```python
def get_random_user_agent() -> str:
    """Return a random user-agent string for scraper rotation."""
    import random
    return random.choice(_USER_AGENTS)
```

**Explanation:** It accepts zero arguments and returns `str`. See the code below for the full implementation. Key calls include `choice()`.

### `fetch_with_retry`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `233-292`
- **Signature:** `def fetch_with_retry(`
- **Purpose:** Fetch a URL with retry, timeout, and backoff.

**Code:**
```python
def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    timeout: int = 30,
    backoff_base: float = 2.0,
) -> dict[str, Any] | None:
    """Fetch a URL with retry, timeout, and backoff.

    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        backoff_base: Base for exponential backoff (2.0 = 2s, 4s, 8s)

    Returns:
        Dict with status_code, content, and headers, or None on failure
    """
    import httpx

    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": get_random_user_agent(),
                "Accept": "text/html,application/json,*/*",
                "Accept-Language": "en-US,en;q=0.9",
            }
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)

            if resp.status_code == 200:
                return {
                    "status_code": resp.status_code,
                    "content": resp.text,
                    "headers": dict(resp.headers),
                }

            if resp.status_code == 429:
                # Rate limited — wait longer
                wait = backoff_base ** (attempt + 2)
                logger.warning("Rate limited (429), waiting %.1fs before retry", wait)
                time.sleep(wait)
                continue

            if 400 <= resp.status_code < 500:
                logger.warning("Client error %d for %s — not retrying", resp.status_code, url)
                return None

            # 5xx — retry with backoff
            logger.warning("Server error %d for %s (attempt %d/%d)", resp.status_code, url, attempt + 1, max_retries)

        except httpx.TimeoutException:
            logger.warning("Timeout for %s (attempt %d/%d)", url, attempt + 1, max_retries)
        except Exception as exc:
            logger.warning("Fetch error for %s: %s (attempt %d/%d)", url, exc, attempt + 1, max_retries)

        if attempt < max_retries - 1:
            wait = backoff_base ** attempt
            time.sleep(wait)

    return None
```

**Explanation:** It accepts `url`, `max_retries`, `timeout`, `backoff_base` and returns `dict[str, Any] | None`. See the code below for the full implementation. Key calls include `range()`, `warning()`, `sleep()`, `get_random_user_agent()`, `Client()`.

### `ETLOrchestrator.__init__`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `325-329`
- **Signature:** `def __init__(self, pipeline_name: str) -> None:`
- **Purpose:** Method of `ETLOrchestrator` that handles   init  .

**Code:**
```python
def __init__(self, pipeline_name: str) -> None:
        self.pipeline_name = pipeline_name
        self.steps: list[ETLStep] = []
        self.results: list[ETLStepResult] = []
        self._step_map: dict[str, ETLStep] = {}
```

**Explanation:** It accepts `pipeline_name` and returns `None`. See the code below for the full implementation.

### `ETLOrchestrator.add_step`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `331-334`
- **Signature:** `def add_step(self, step: ETLStep) -> None:`
- **Purpose:** Add a step to the pipeline.

**Code:**
```python
def add_step(self, step: ETLStep) -> None:
        """Add a step to the pipeline."""
        self.steps.append(step)
        self._step_map[step.name] = step
```

**Explanation:** It accepts `step` and returns `None`. See the code below for the full implementation. Key calls include `append()`.

### `ETLOrchestrator.run`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `336-376`
- **Signature:** `def run(self) -> list[ETLStepResult]:`
- **Purpose:** Execute all steps in dependency order.

**Code:**
```python
def run(self) -> list[ETLStepResult]:
        """Execute all steps in dependency order.

        Returns:
            List of ETLStepResult for each step
        """
        logger.info("Starting ETL pipeline: %s (%d steps)", self.pipeline_name, len(self.steps))
        self.results = []
        completed: set[str] = set()

        for step in self.steps:
            # Check dependencies
            missing_deps = [d for d in step.depends_on if d not in completed]
            if missing_deps:
                logger.warning("Skipping step '%s' — missing dependencies: %s", step.name, missing_deps)
                result = ETLStepResult(
                    step_name=step.name,
                    status="skipped",
                    error=f"Missing dependencies: {', '.join(missing_deps)}",
                )
                self.results.append(result)
                continue

            result = self._run_step(step)
            self.results.append(result)

            if result.status == "success":
                completed.add(step.name)
            else:
                logger.error("Step '%s' failed, downstream steps may be affected", step.name)

        # Log pipeline summary
        success_count = sum(1 for r in self.results if r.status == "success")
        failed_count = sum(1 for r in self.results if r.status == "failed")
        skipped_count = sum(1 for r in self.results if r.status == "skipped")
        logger.info(
            "ETL pipeline '%s' complete: %d success, %d failed, %d skipped",
            self.pipeline_name, success_count, failed_count, skipped_count,
        )

        return self.results
```

**Explanation:** It accepts zero arguments and returns `list[ETLStepResult]`. See the code below for the full implementation. Key calls include `info()`, `len()`, `set()`, `_run_step()`, `append()`.

### `ETLOrchestrator._run_step`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `378-438`
- **Signature:** `def _run_step(self, step: ETLStep) -> ETLStepResult:`
- **Purpose:** Execute a single ETL step with retry logic.

**Code:**
```python
def _run_step(self, step: ETLStep) -> ETLStepResult:
        """Execute a single ETL step with retry logic."""
        start_time = time.time()

        for attempt in range(step.max_retries + 1):
            try:
                logger.info("Running ETL step '%s' (attempt %d)", step.name, attempt + 1)
                step_result = step.func()

                rows = step_result.get("rows_affected", 0)
                metadata = step_result.get("metadata", {})

                # Log lineage
                if step.source and step.target_table:
                    log_lineage(
                        source=step.source,
                        table=step.target_table,
                        operation=step_result.get("operation", "upsert"),
                        rows_affected=rows,
                        status="success",
                        metadata=metadata,
                    )

                duration = round(time.time() - start_time, 2)
                return ETLStepResult(
                    step_name=step.name,
                    status="success",
                    rows_affected=rows,
                    duration_seconds=duration,
                    metadata=metadata,
                )

            except Exception as exc:
                logger.warning("ETL step '%s' failed (attempt %d): %s", step.name, attempt + 1, exc)
                if attempt < step.max_retries:
                    wait = 2.0 ** attempt
                    time.sleep(wait)
                else:
                    duration = round(time.time() - start_time, 2)
                    # Log failed lineage
                    if step.source and step.target_table:
                        log_lineage(
                            source=step.source,
                            table=step.target_table,
                            operation="upsert",
                            status="failed",
                            error_message=str(exc),
                        )
                    return ETLStepResult(
                        step_name=step.name,
                        status="failed",
                        duration_seconds=duration,
                        error=str(exc),
                    )

        # Should not reach here, but just in case
        return ETLStepResult(
            step_name=step.name,
            status="failed",
            error="Max retries exceeded",
        )
```

**Explanation:** It accepts `step` and returns `ETLStepResult`. See the code below for the full implementation. Key calls include `time()`, `range()`, `info()`, `func()`, `get()`.

### `build_climate_etl_pipeline`

- **File:** `fastapi-backend/app/services/etl_orchestrator.py`
- **Lines:** `445-505`
- **Signature:** `def build_climate_etl_pipeline() -> ETLOrchestrator:`
- **Purpose:** Build the climate data ETL pipeline.

**Code:**
```python
def build_climate_etl_pipeline() -> ETLOrchestrator:
    """Build the climate data ETL pipeline.

    Steps:
    1. Fetch gaps from Supabase (municipalities without climate data)
    2. Fetch from NASA POWER API
    3. Validate data
    4. Upsert to Supabase
    """
    orchestrator = ETLOrchestrator("climate_data_sync")

    def _fetch_gaps() -> dict[str, Any]:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .not_.is_("lat", "null")
            .limit(100)
            .execute()
        )
        gaps = resp.data or []
        return {"rows_affected": len(gaps), "metadata": {"gap_count": len(gaps)}}

    def _fetch_nasa() -> dict[str, Any]:
        # Placeholder — actual NASA POWER fetch logic is in scripts/run_nasa_for_gaps.py
        return {"rows_affected": 0, "metadata": {"note": "NASA POWER fetch handled by external script"}}

    def _validate() -> dict[str, Any]:
        return {"rows_affected": 0, "metadata": {"validation": "passed"}}

    def _upsert() -> dict[str, Any]:
        return {"rows_affected": 0, "metadata": {"note": "Upsert handled by external script"}}

    orchestrator.add_step(ETLStep(
        name="fetch_gaps",
        func=_fetch_gaps,
        source="Supabase",
        target_table="municipalities",
    ))
    orchestrator.add_step(ETLStep(
        name="fetch_nasa",
        func=_fetch_nasa,
        source="NASA_POWER",
        target_table="municipality_climate_monthly",
        depends_on=["fetch_gaps"],
    ))
    orchestrator.add_step(ETLStep(
        name="validate",
        func=_validate,
        depends_on=["fetch_nasa"],
    ))
    orchestrator.add_step(ETLStep(
        name="upsert",
        func=_upsert,
        source="NASA_POWER",
        target_table="municipality_climate_monthly",
        depends_on=["validate"],
    ))

    return orchestrator
```

**Explanation:** It accepts zero arguments and returns `ETLOrchestrator`. See the code below for the full implementation. Key calls include `ETLOrchestrator()`, `get_supabase_client()`, `execute()`, `len()`, `limit()`.


## `fastapi-backend/app/services/example_service.py`

**File:** `fastapi-backend/app/services/example_service.py`

**Summary:** Source file `fastapi-backend/app/services/example_service.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/financials.py`

**File:** `fastapi-backend/app/services/financials.py`

**Summary:** Financial analysis module for LUMI EcoSim.

### `calculate_npv`

- **File:** `fastapi-backend/app/services/financials.py`
- **Lines:** `45-61`
- **Signature:** `def calculate_npv(`
- **Purpose:** Calculate Net Present Value of a series of cash flows.

**Code:**
```python
def calculate_npv(
    cash_flows: list[float],
    discount_rate: float,
) -> float:
    """Calculate Net Present Value of a series of cash flows.

    Args:
        cash_flows: List of annual cash flows (index 0 = initial investment, negative)
        discount_rate: Annual discount rate (e.g., 0.10 for 10%)

    Returns:
        NPV in PHP
    """
    npv = 0.0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** t)
    return npv
```

**Explanation:** It accepts `cash_flows`, `discount_rate` and returns `float`. See the code below for the full implementation. Key calls include `enumerate()`.

### `calculate_irr`

- **File:** `fastapi-backend/app/services/financials.py`
- **Lines:** `64-97`
- **Signature:** `def calculate_irr(`
- **Purpose:** Calculate Internal Rate of Return using Newton-Raphson.

**Code:**
```python
def calculate_irr(
    cash_flows: list[float],
    guess: float = 0.1,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> float | None:
    """Calculate Internal Rate of Return using Newton-Raphson.

    Args:
        cash_flows: List of annual cash flows (index 0 = initial investment)
        guess: Initial IRR guess
        max_iter: Maximum iterations
        tol: Convergence tolerance

    Returns:
        IRR as decimal (e.g., 0.12 for 12%) or None if no convergence
    """
    rate = guess
    for _ in range(max_iter):
        npv = 0.0
        dnpv = 0.0
        for t, cf in enumerate(cash_flows):
            factor = (1 + rate) ** t
            npv += cf / factor
            if t > 0:
                dnpv -= t * cf / (factor * (1 + rate))
        if abs(npv) < tol:
            return rate
        if abs(dnpv) < 1e-12:
            break
        rate -= npv / dnpv
        if rate <= -1.0:
            return None
    return None
```

**Explanation:** It accepts `cash_flows`, `guess`, `max_iter`, `tol` and returns `float | None`. See the code below for the full implementation. Key calls include `range()`, `enumerate()`, `abs()`.

### `calculate_lcoe`

- **File:** `fastapi-backend/app/services/financials.py`
- **Lines:** `100-134`
- **Signature:** `def calculate_lcoe(`
- **Purpose:** Calculate Levelized Cost of Energy (LCOE).

**Code:**
```python
def calculate_lcoe(
    capital_cost_php: float,
    annual_om_cost_php: float,
    annual_energy_kwh: float,
    discount_rate: float,
    lifetime_years: int,
    degradation_rate: float = 0.005,
) -> float:
    """Calculate Levelized Cost of Energy (LCOE).

    LCOE = (PV of costs) / (PV of energy production)

    Args:
        capital_cost_php: Total upfront capital cost
        annual_om_cost_php: Annual O&M cost (assumed constant in real terms)
        annual_energy_kwh: Year 1 energy production
        discount_rate: Annual discount rate
        lifetime_years: System lifetime
        degradation_rate: Annual energy degradation rate

    Returns:
        LCOE in PHP/kWh
    """
    pv_costs = capital_cost_php
    pv_energy = 0.0

    for t in range(1, lifetime_years + 1):
        discount_factor = 1 / ((1 + discount_rate) ** t)
        pv_costs += annual_om_cost_php * discount_factor
        annual_energy = annual_energy_kwh * ((1 - degradation_rate) ** (t - 1))
        pv_energy += annual_energy * discount_factor

    if pv_energy <= 0:
        return float("inf")
    return pv_costs / pv_energy
```

**Explanation:** It accepts `capital_cost_php`, `annual_om_cost_php`, `annual_energy_kwh`, `discount_rate`, `lifetime_years`, `degradation_rate` and returns `float`. See the code below for the full implementation. Key calls include `range()`, `float()`.

### `calculate_payback`

- **File:** `fastapi-backend/app/services/financials.py`
- **Lines:** `137-176`
- **Signature:** `def calculate_payback(`
- **Purpose:** Calculate simple and discounted payback periods.

**Code:**
```python
def calculate_payback(
    capital_cost_php: float,
    annual_savings_php: float,
    discount_rate: float,
    degradation_rate: float = 0.005,
    max_years: int = 50,
) -> tuple[float | None, float | None]:
    """Calculate simple and discounted payback periods.

    Args:
        capital_cost_php: Total upfront cost
        annual_savings_php: Year 1 net savings
        discount_rate: Annual discount rate
        degradation_rate: Annual degradation of savings
        max_years: Maximum years to consider

    Returns:
        Tuple of (simple_payback_years, discounted_payback_years)
    """
    if annual_savings_php <= 0:
        return None, None

    # Simple payback
    simple = capital_cost_php / annual_savings_php

    # Discounted payback
    cumulative = -capital_cost_php
    discounted = None
    for t in range(1, max_years + 1):
        savings = annual_savings_php * ((1 - degradation_rate) ** (t - 1))
        discounted_savings = savings / ((1 + discount_rate) ** t)
        prev_cumulative = cumulative
        cumulative += discounted_savings
        if cumulative >= 0 and prev_cumulative < 0:
            # Interpolate within the year
            fraction = abs(prev_cumulative) / discounted_savings
            discounted = t - 1 + fraction
            break

    return round(simple, 2), discounted
```

**Explanation:** It accepts `capital_cost_php`, `annual_savings_php`, `discount_rate`, `degradation_rate`, `max_years` and returns `tuple[float | None, float | None]`. See the code below for the full implementation. Key calls include `range()`, `abs()`, `round()`.

### `analyze_financials`

- **File:** `fastapi-backend/app/services/financials.py`
- **Lines:** `179-257`
- **Signature:** `def analyze_financials(inputs: FinancialInputs) -> FinancialResults:`
- **Purpose:** Full financial analysis of a renewable energy system.

**Code:**
```python
def analyze_financials(inputs: FinancialInputs) -> FinancialResults:
    """Full financial analysis of a renewable energy system.

    Args:
        inputs: FinancialInputs dataclass with system parameters

    Returns:
        FinancialResults dataclass with all metrics
    """
    # Build cash flow series: Year 0 = -capital_cost, Years 1..N = net savings
    cash_flows: list[float] = [-inputs.capital_cost_php]

    annual_savings_y1 = inputs.annual_energy_kwh * inputs.electricity_tariff_php_kwh
    net_cash_y1 = annual_savings_y1 - inputs.annual_om_cost_php

    total_revenue = 0.0
    total_om = 0.0

    for t in range(1, inputs.system_lifetime_years + 1):
        energy = inputs.annual_energy_kwh * ((1 - inputs.degradation_rate) ** (t - 1))
        revenue = energy * inputs.electricity_tariff_php_kwh
        om = inputs.annual_om_cost_php
        net = revenue - om
        cash_flows.append(net)
        total_revenue += revenue
        total_om += om

    # Add residual value in final year
    if inputs.residual_value_php > 0:
        cash_flows[-1] += inputs.residual_value_php

    # NPV
    npv = calculate_npv(cash_flows, inputs.discount_rate)

    # IRR
    irr = calculate_irr(cash_flows)

    # LCOE
    lcoe = calculate_lcoe(
        capital_cost_php=inputs.capital_cost_php,
        annual_om_cost_php=inputs.annual_om_cost_php,
        annual_energy_kwh=inputs.annual_energy_kwh,
        discount_rate=inputs.discount_rate,
        lifetime_years=inputs.system_lifetime_years,
        degradation_rate=inputs.degradation_rate,
    )

    # Payback
    simple_pb, discounted_pb = calculate_payback(
        capital_cost_php=inputs.capital_cost_php,
        annual_savings_php=net_cash_y1,
        discount_rate=inputs.discount_rate,
        degradation_rate=inputs.degradation_rate,
    )

    # Benefit-cost ratio
    pv_benefits = sum(
        inputs.annual_energy_kwh * ((1 - inputs.degradation_rate) ** (t - 1))
        * inputs.electricity_tariff_php_kwh / ((1 + inputs.discount_rate) ** t)
        for t in range(1, inputs.system_lifetime_years + 1)
    )
    pv_costs = inputs.capital_cost_php + sum(
        inputs.annual_om_cost_php / ((1 + inputs.discount_rate) ** t)
        for t in range(1, inputs.system_lifetime_years + 1)
    )
    bcr = pv_benefits / pv_costs if pv_costs > 0 else 0.0

    return FinancialResults(
        npv_php=round(npv, 2),
        irr=round(irr, 4) if irr is not None else None,
        lcoe_php_kwh=round(lcoe, 4),
        simple_payback_years=simple_pb,
        discounted_payback_years=discounted_pb,
        total_revenue_php=round(total_revenue, 2),
        total_cost_php=round(inputs.capital_cost_php + total_om, 2),
        net_cash_flow_year_1_php=round(net_cash_y1, 2),
        benefit_cost_ratio=round(bcr, 4),
        annual_savings_year_1_php=round(annual_savings_y1, 2),
    )
```

**Explanation:** It accepts `inputs` and returns `FinancialResults`. See the code below for the full implementation. Key calls include `range()`, `append()`, `calculate_npv()`, `calculate_irr()`, `calculate_lcoe()`.

### `to_dict`

- **File:** `fastapi-backend/app/services/financials.py`
- **Lines:** `260-273`
- **Signature:** `def to_dict(results: FinancialResults) -> dict[str, Any]:`
- **Purpose:** Convert FinancialResults to a dict for API responses.

**Code:**
```python
def to_dict(results: FinancialResults) -> dict[str, Any]:
    """Convert FinancialResults to a dict for API responses."""
    return {
        "npv_php": results.npv_php,
        "irr": results.irr,
        "lcoe_php_kwh": results.lcoe_php_kwh,
        "simple_payback_years": results.simple_payback_years,
        "discounted_payback_years": results.discounted_payback_years,
        "total_revenue_php": results.total_revenue_php,
        "total_cost_php": results.total_cost_php,
        "net_cash_flow_year_1_php": results.net_cash_flow_year_1_php,
        "benefit_cost_ratio": results.benefit_cost_ratio,
        "annual_savings_year_1_php": results.annual_savings_year_1_php,
    }
```

**Explanation:** It accepts `results` and returns `dict[str, Any]`. See the code below for the full implementation.


## `fastapi-backend/app/services/forecasting.py`

**File:** `fastapi-backend/app/services/forecasting.py`

**Summary:** SARIMA/ARIMAX forecasting module for LUMI EnergyHub.

### `_forecast_cache_key`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `34-41`
- **Signature:** `def _forecast_cache_key(`
- **Purpose:** Handles  forecast cache key.

**Code:**
```python
def _forecast_cache_key(
    target_col: str,
    exog_cols: tuple[str, ...] | None,
    forecast_years: tuple[int, ...],
) -> str:
    payload = f"{target_col}:{sorted(exog_cols or ())}:{forecast_years}"
    digest = hashlib.md5(payload.encode("utf-8")).hexdigest()[:24]
    return f"lumi:forecast:{digest}"
```

**Explanation:** It accepts `target_col`, `exog_cols`, `forecast_years` and returns `str`. See the code below for the full implementation. Key calls include `sorted()`, `hexdigest()`, `md5()`, `encode()`.

### `_safe_float`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `77-85`
- **Signature:** `def _safe_float(val: Any) -> float | None:`
- **Purpose:** Convert to float, returning None for NaN/Inf.

**Code:**
```python
def _safe_float(val: Any) -> float | None:
    """Convert to float, returning None for NaN/Inf."""
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None
```

**Explanation:** It accepts `val` and returns `float | None`. See the code below for the full implementation. Key calls include `float()`, `isnan()`, `isinf()`.

### `fit_sarima`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `88-114`
- **Signature:** `def fit_sarima(`
- **Purpose:** Fit a SARIMA model to a time series.

**Code:**
```python
def fit_sarima(
    series: pd.Series,
    config: SARIMAConfig | None = None,
) -> Any:
    """Fit a SARIMA model to a time series.

    Args:
        series: Pandas Series with datetime index or integer year index
        config: SARIMA configuration

    Returns:
        Fitted SARIMAXResults object
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    if config is None:
        config = SARIMAConfig()

    model = SARIMAX(
        series,
        order=config.order,
        seasonal_order=config.seasonal_order,
        trend=config.trend,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)
```

**Explanation:** It accepts `series`, `config` and returns `Any`. See the code below for the full implementation. Key calls include `SARIMAConfig()`, `SARIMAX()`, `fit()`.

### `fit_arimax`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `117-141`
- **Signature:** `def fit_arimax(`
- **Purpose:** Fit an ARIMAX model with exogenous variables.

**Code:**
```python
def fit_arimax(
    series: pd.Series,
    exog: pd.DataFrame | None = None,
    order: tuple[int, int, int] = (1, 1, 1),
) -> Any:
    """Fit an ARIMAX model with exogenous variables.

    Args:
        series: Target time series
        exog: Exogenous variables DataFrame (must align with series index)
        order: ARIMA order (p, d, q)

    Returns:
        Fitted SARIMAXResults object
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    model = SARIMAX(
        series,
        exog=exog,
        order=order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)
```

**Explanation:** It accepts `series`, `exog`, `order` and returns `Any`. See the code below for the full implementation. Key calls include `SARIMAX()`, `fit()`.

### `forecast_sarima`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `144-173`
- **Signature:** `def forecast_sarima(`
- **Purpose:** Generate forecast with confidence intervals from a fitted SARIMA model.

**Code:**
```python
def forecast_sarima(
    fitted_model: Any,
    steps: int = 6,
    exog: pd.DataFrame | None = None,
    ci_alpha: float = 0.05,
) -> dict[str, list[float | None]]:
    """Generate forecast with confidence intervals from a fitted SARIMA model.

    Args:
        fitted_model: Fitted SARIMAXResults
        steps: Number of periods to forecast
        exog: Exogenous variables for forecast period
        ci_alpha: Confidence interval alpha (0.05 = 95% CI)

    Returns:
        Dict with forecast_values, ci_lower, ci_upper
    """
    forecast = fitted_model.get_forecast(steps=steps, exog=exog)
    pred_mean = forecast.predicted_mean
    ci = forecast.conf_int(alpha=ci_alpha)

    values = [_safe_float(v) for v in pred_mean.values]
    lower = [_safe_float(v) for v in ci.iloc[:, 0].values]
    upper = [_safe_float(v) for v in ci.iloc[:, 1].values]

    return {
        "forecast_values": values,
        "ci_lower": lower,
        "ci_upper": upper,
    }
```

**Explanation:** It accepts `fitted_model`, `steps`, `exog`, `ci_alpha` and returns `dict[str, list[float | None]]`. See the code below for the full implementation. Key calls include `get_forecast()`, `conf_int()`, `_safe_float()`.

### `backtest_walk_forward`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `176-247`
- **Signature:** `def backtest_walk_forward(`
- **Purpose:** Walk-forward backtesting: train on [0:train_end], predict one step,

**Code:**
```python
def backtest_walk_forward(
    series: pd.Series,
    train_end_idx: int,
    config: SARIMAConfig | None = None,
    exog: pd.DataFrame | None = None,
) -> BacktestResult:
    """Walk-forward backtesting: train on [0:train_end], predict one step,
    add actual to training set, retrain, repeat.

    Args:
        series: Full time series
        train_end_idx: Index where training ends (test starts at train_end_idx)
        config: SARIMA config
        exog: Optional exogenous variables

    Returns:
        BacktestResult with actuals, predictions, and metrics
    """
    if config is None:
        config = SARIMAConfig()

    train = series.iloc[:train_end_idx]
    test = series.iloc[train_end_idx:]

    actuals: list[float] = []
    predictions: list[float] = []

    history = train.copy()

    for i in range(len(test)):
        try:
            exog_train = exog.iloc[:train_end_idx + i] if exog is not None else None
            exog_forecast = exog.iloc[[train_end_idx + i]] if exog is not None else None

            if exog is not None:
                model = fit_arimax(history, exog=exog_train, order=config.order)
                fc = forecast_sarima(model, steps=1, exog=exog_forecast)
            else:
                model = fit_sarima(history, config)
                fc = forecast_sarima(model, steps=1)

            pred = fc["forecast_values"][0] if fc["forecast_values"] else None
            if pred is None:
                pred = float(history.iloc[-1])  # naive fallback

            predictions.append(pred)
            actuals.append(float(test.iloc[i]))

            # Add actual to history for next iteration
            history = pd.concat([history, test.iloc[[i]]])

        except Exception as exc:
            logger.warning("Backtest step %d failed: %s", i, exc)
            predictions.append(float(history.iloc[-1]))
            actuals.append(float(test.iloc[i]))
            history = pd.concat([history, test.iloc[[i]]])

    metrics = calculate_metrics(actuals, predictions)
    residuals = [a - p for a, p in zip(actuals, predictions)]

    train_years = f"{int(series.index[0])}-{int(series.index[train_end_idx - 1])}"
    test_years = f"{int(series.index[train_end_idx])}-{int(series.index[-1])}"

    return BacktestResult(
        model_name=f"SARIMA{config.order}{config.seasonal_order}",
        train_period=train_years,
        test_period=test_years,
        actual_values=actuals,
        predicted_values=predictions,
        metrics=metrics,
        residuals=residuals,
    )
```

**Explanation:** It accepts `series`, `train_end_idx`, `config`, `exog` and returns `BacktestResult`. See the code below for the full implementation. Key calls include `SARIMAConfig()`, `copy()`, `range()`, `len()`, `append()`.

### `calculate_metrics`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `250-272`
- **Signature:** `def calculate_metrics(actuals: list[float], predictions: list[float]) -> dict[str, float]:`
- **Purpose:** Calculate standard forecast accuracy metrics.

**Code:**
```python
def calculate_metrics(actuals: list[float], predictions: list[float]) -> dict[str, float]:
    """Calculate standard forecast accuracy metrics."""
    if not actuals or not predictions:
        return {"mae": 0, "rmse": 0, "mape": 0, "smape": 0}

    errors = [a - p for a, p in zip(actuals, predictions)]
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(np.square(errors))))

    # MAPE with zero-guard
    mape_values = [abs(e / a) * 100 for a, e in zip(actuals, errors) if abs(a) > 1e-8]
    mape = float(np.mean(mape_values)) if mape_values else 0.0

    # sMAPE (symmetric MAPE)
    smape_values = [abs(e) / ((abs(a) + abs(p)) / 2) * 100 for a, p, e in zip(actuals, predictions, errors) if (abs(a) + abs(p)) > 1e-8]
    smape = float(np.mean(smape_values)) if smape_values else 0.0

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "smape": round(smape, 2),
    }
```

**Explanation:** It accepts `actuals`, `predictions` and returns `dict[str, float]`. See the code below for the full implementation. Key calls include `zip()`, `float()`, `mean()`, `abs()`, `sqrt()`.

### `run_forecast_pipeline`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `275-345`
- **Signature:** `def run_forecast_pipeline(`
- **Purpose:** Full forecasting pipeline: train, backtest, forecast future.

**Code:**
```python
def run_forecast_pipeline(
    df: pd.DataFrame,
    target_col: str = "total_consumption_gwh",
    year_col: str = "year",
    forecast_years: list[int] | None = None,
    train_end_year: int = 2020,
    config: SARIMAConfig | None = None,
    exog_cols: list[str] | None = None,
) -> ForecastResult:
    """Full forecasting pipeline: train, backtest, forecast future.

    Args:
        df: DataFrame with historical data
        target_col: Column to forecast
        year_col: Column with year values
        forecast_years: Years to forecast (default: 2025-2030)
        train_end_year: Last year in training set for backtesting
        config: SARIMA configuration
        exog_cols: Optional exogenous variable column names

    Returns:
        ForecastResult with forecast values, CIs, and backtest metrics
    """
    if forecast_years is None:
        forecast_years = list(range(2025, 2031))

    if config is None:
        config = SARIMAConfig()

    # Prepare series
    df = df.sort_values(year_col).reset_index(drop=True)
    series = df.set_index(year_col)[target_col]

    # Exogenous variables
    exog = df.set_index(year_col)[exog_cols] if exog_cols else None

    # Backtest
    train_end_idx = (df[year_col] <= train_end_year).sum()
    if train_end_idx < len(series):
        bt = backtest_walk_forward(series, train_end_idx, config, exog)
        metrics = bt.metrics
        train_period = bt.train_period
        test_period = bt.test_period
    else:
        metrics = {}
        train_period = f"{int(series.index[0])}-{train_end_year}"
        test_period = f"{train_end_year + 1}-{int(series.index[-1])}"

    # Full model fit
    if exog is not None:
        fitted = fit_arimax(series, exog=exog, order=config.order)
        # Forecast future exog (naive: use last values)
        future_exog = pd.DataFrame(
            {col: [exog[col].iloc[-1]] * len(forecast_years) for col in exog.columns},
            index=forecast_years,
        )
        fc = forecast_sarima(fitted, steps=len(forecast_years), exog=future_exog)
    else:
        fitted = fit_sarima(series, config)
        fc = forecast_sarima(fitted, steps=len(forecast_years))

    return ForecastResult(
        model_name=f"SARIMA{config.order}{config.seasonal_order}",
        forecast_years=forecast_years,
        forecast_values=fc["forecast_values"],
        ci_lower=fc["ci_lower"],
        ci_upper=fc["ci_upper"],
        training_period=f"{int(series.index[0])}-{int(series.index[-1])}",
        test_period=test_period,
        metrics=metrics,
    )
```

**Explanation:** It accepts `df`, `target_col`, `year_col`, `forecast_years`, `train_end_year`, `config`, `exog_cols` and returns `ForecastResult`. See the code below for the full implementation. Key calls include `list()`, `range()`, `SARIMAConfig()`, `reset_index()`, `sort_values()`.

### `reconcile_forecast_cache`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `348-428`
- **Signature:** `def reconcile_forecast_cache(`
- **Purpose:** Reconcile a new forecast with cached forecast data.

**Code:**
```python
def reconcile_forecast_cache(
    forecast_result: ForecastResult,
    cached_forecast: dict[str, Any] | None,
) -> dict[str, Any]:
    """Reconcile a new forecast with cached forecast data.

    If cached data exists and covers the same years, merge by taking
    the newer forecast. If years differ, extend with new years.

    Args:
        forecast_result: New ForecastResult
        cached_forecast: Dict from cache or None

    Returns:
        Reconciled forecast dict ready for API response
    """
    new_data = {
        "forecast_years": forecast_result.forecast_years,
        "forecast_values": forecast_result.forecast_values,
        "ci_lower": forecast_result.ci_lower,
        "ci_upper": forecast_result.ci_upper,
        "model": forecast_result.model_name,
        "training_period": forecast_result.training_period,
        "test_period": forecast_result.test_period,
        "metrics": forecast_result.metrics,
    }

    if not cached_forecast or not cached_forecast.get("forecast_years"):
        return new_data

    cached_years = set(cached_forecast.get("forecast_years", []))
    new_years = set(forecast_result.forecast_years)

    # If new forecast covers all cached years, replace entirely
    if new_years >= cached_years:
        return new_data

    # Otherwise merge: use cached for overlapping, new for new years
    merged_years = sorted(cached_years | new_years)
    merged_values: list[float | None] = []
    merged_lower: list[float | None] = []
    merged_upper: list[float | None] = []

    new_map = {
        y: (v, l, u)
        for y, v, l, u in zip(
            forecast_result.forecast_years,
            forecast_result.forecast_values,
            forecast_result.ci_lower,
            forecast_result.ci_upper,
        )
    }
    cached_map = {
        y: (v, l, u)
        for y, v, l, u in zip(
            cached_forecast.get("forecast_years", []),
            cached_forecast.get("forecast_values", []),
            cached_forecast.get("ci_lower", []),
            cached_forecast.get("ci_upper", []),
        )
    }

    for y in merged_years:
        if y in new_map:
            v, l, u = new_map[y]
        else:
            v, l, u = cached_map.get(y, (None, None, None))
        merged_values.append(v)
        merged_lower.append(l)
        merged_upper.append(u)

    return {
        "forecast_years": merged_years,
        "forecast_values": merged_values,
        "ci_lower": merged_lower,
        "ci_upper": merged_upper,
        "model": forecast_result.model_name,
        "training_period": forecast_result.training_period,
        "test_period": forecast_result.test_period,
        "metrics": forecast_result.metrics,
    }
```

**Explanation:** It accepts `forecast_result`, `cached_forecast` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `set()`, `sorted()`, `zip()`, `append()`.

### `_classify_model_type`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `431-442`
- **Signature:** `def _classify_model_type(model_name: str) -> str:`
- **Purpose:** Map a model name to the constrained ml_model_registry.model_type.

**Code:**
```python
def _classify_model_type(model_name: str) -> str:
    """Map a model name to the constrained ml_model_registry.model_type."""
    name = model_name.strip().upper()
    if name.startswith(("SARIMA", "ARIMA")):
        return "SARIMA"
    if "LIGHTGBM" in name:
        return "LightGBM"
    if "XGBOOST" in name:
        return "XGBoost"
    if "PROPHET" in name:
        return "Prophet"
    return "SARIMA"
```

**Explanation:** It accepts `model_name` and returns `str`. See the code below for the full implementation. Key calls include `upper()`, `strip()`, `startswith()`.

### `log_model_run`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `445-507`
- **Signature:** `def log_model_run(`
- **Purpose:** Log a model run and register the model in ml_model_registry.

**Code:**
```python
def log_model_run(
    model_name: str,
    target_variable: str,
    metrics: dict[str, float],
    hyperparameters: dict[str, Any] | None = None,
    run_type: str = "train",
    status: str = "success",
) -> str | None:
    """Log a model run and register the model in ml_model_registry.

    Creates a row in ml_model_registry and links it to the new
    forecast_model_runs row via model_id.

    Args:
        model_name: Name of the model
        target_variable: What was forecasted
        metrics: Performance metrics dict
        hyperparameters: Model hyperparameters
        run_type: 'train', 'backtest', 'retrain', or 'evaluate'
        status: 'success', 'failed', 'running'

    Returns:
        Run ID if logged successfully, None otherwise
    """
    try:
        from app.services.supabase_service import get_supabase_client
        import json as _json
        from datetime import datetime, timezone

        client = get_supabase_client()
        now = datetime.now(timezone.utc)

        # Register this trained/backtested model version
        registry_payload = {
            "model_name": model_name,
            "model_version": now.strftime("%Y.%m.%d-%H%M%S"),
            "model_type": _classify_model_type(model_name),
            "target_variable": target_variable,
            "train_date": now.date().isoformat(),
            "metrics": metrics,
            "is_active": False,
        }
        reg_resp = client.table("ml_model_registry").insert(registry_payload).execute()
        if not reg_resp.data:
            raise RuntimeError("ml_model_registry insert returned no data")
        model_id = reg_resp.data[0].get("model_id")

        run_payload = {
            "model_id": model_id,
            "run_type": run_type,
            "target_variable": target_variable,
            "hyperparameters": _json.dumps(hyperparameters or {}),
            "metrics": _json.dumps(metrics),
            "started_at": now.isoformat(),
            "finished_at": now.isoformat(),
            "status": status,
        }
        run_resp = client.table("forecast_model_runs").insert(run_payload).execute()
        if run_resp.data:
            return run_resp.data[0].get("id")
    except Exception as exc:
        logger.warning("Failed to log model run: %s", exc)
    return None
```

**Explanation:** It accepts `model_name`, `target_variable`, `metrics`, `hyperparameters`, `run_type`, `status` and returns `str | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `now()`, `execute()`, `get()`, `strftime()`.

### `select_best_sarima_config`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `510-545`
- **Signature:** `def select_best_sarima_config(`
- **Purpose:** Try multiple SARIMA configs and return the one with the lowest AIC/BIC.

**Code:**
```python
def select_best_sarima_config(
    series: pd.Series,
    candidates: list[SARIMAConfig] | None = None,
    criterion: str = "aic",
) -> SARIMAConfig:
    """Try multiple SARIMA configs and return the one with the lowest AIC/BIC.

    This is a lightweight auto-arima that avoids the heavy ``pmdarima``
    dependency.  It silently skips configs that fail to converge.
    """
    if candidates is None:
        candidates = [
            SARIMAConfig(order=(0, 1, 0)),
            SARIMAConfig(order=(1, 1, 0)),
            SARIMAConfig(order=(0, 1, 1)),
            SARIMAConfig(order=(1, 1, 1)),
            SARIMAConfig(order=(2, 1, 2)),
            SARIMAConfig(order=(1, 1, 2)),
            SARIMAConfig(order=(2, 1, 1)),
        ]

    best_config = candidates[0]
    best_score = float("inf")

    for config in candidates:
        try:
            fitted = fit_sarima(series, config)
            score = float(getattr(fitted, criterion, float("inf")))
            if score < best_score:
                best_score = score
                best_config = config
        except Exception as exc:
            logger.debug("SARIMA config %s failed: %s", config, exc)

    logger.info("Selected SARIMA config %s with %s=%.2f", best_config, criterion, best_score)
    return best_config
```

**Explanation:** It accepts `series`, `candidates`, `criterion` and returns `SARIMAConfig`. See the code below for the full implementation. Key calls include `SARIMAConfig()`, `float()`, `fit_sarima()`, `getattr()`, `debug()`.

### `run_forecast_pipeline_cached`

- **File:** `fastapi-backend/app/services/forecasting.py`
- **Lines:** `548-602`
- **Signature:** `def run_forecast_pipeline_cached(`
- **Purpose:** Forecast pipeline with Redis result caching and optional auto order selection.

**Code:**
```python
def run_forecast_pipeline_cached(
    df: pd.DataFrame,
    target_col: str = "total_consumption_gwh",
    year_col: str = "year",
    forecast_years: list[int] | None = None,
    train_end_year: int = 2020,
    config: SARIMAConfig | None = None,
    exog_cols: list[str] | None = None,
    auto_select: bool = True,
) -> ForecastResult:
    """Forecast pipeline with Redis result caching and optional auto order selection."""
    if forecast_years is None:
        forecast_years = list(range(2025, 2031))

    cache_key = _forecast_cache_key(
        target_col,
        tuple(exog_cols) if exog_cols else None,
        tuple(forecast_years),
    )

    try:
        redis = get_redis_sync()
        cached = redis.get(cache_key)
        if cached:
            parsed = json.loads(cached)
            return ForecastResult(**parsed)
    except Exception as exc:
        logger.debug("Forecast cache read failed: %s", exc)

    if auto_select and config is None:
        df_sorted = df.sort_values(year_col).reset_index(drop=True)
        series = df_sorted.set_index(year_col)[target_col]
        config = select_best_sarima_config(series)

    result = run_forecast_pipeline(
        df,
        target_col=target_col,
        year_col=year_col,
        forecast_years=forecast_years,
        train_end_year=train_end_year,
        config=config,
        exog_cols=exog_cols,
    )

    try:
        redis = get_redis_sync()
        redis.setex(
            cache_key,
            FORECAST_CACHE_TTL_SECONDS,
            json.dumps(result.__dict__, default=str),
        )
    except Exception as exc:
        logger.debug("Forecast cache write failed: %s", exc)

    return result
```

**Explanation:** It accepts `df`, `target_col`, `year_col`, `forecast_years`, `train_end_year`, `config`, `exog_cols`, `auto_select` and returns `ForecastResult`. See the code below for the full implementation. Key calls include `list()`, `range()`, `_forecast_cache_key()`, `tuple()`, `get_redis_sync()`.


## `fastapi-backend/app/services/gemini_funcs.py`

**File:** `fastapi-backend/app/services/gemini_funcs.py`

**Summary:** Source file `fastapi-backend/app/services/gemini_funcs.py`.

### `_get_gemini_client`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `33-41`
- **Signature:** `def _get_gemini_client() -> genai.Client:`
- **Purpose:** Handles  get gemini client.

**Code:**
```python
def _get_gemini_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY is not set")
            raise ValueError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client
```

**Explanation:** It accepts zero arguments and returns `genai.Client`. See the code below for the full implementation. Key calls include `getenv()`, `Client()`, `error()`, `ValueError()`.

### `_generate_once`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `44-89`
- **Signature:** `def _generate_once(`
- **Purpose:** Single Gemini call — no retry logic here.

**Code:**
```python
def _generate_once(
    client: genai.Client,
    model_name: str,
    content: str,
    config: Any,
) -> str:
    """Single Gemini call — no retry logic here."""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=content,
            config=config,
        )
    except TypeError:
        response = client.models.generate_content(
            model=model_name,
            contents=content,
        )

    if GEMINI_DEBUG:
        finish_reasons = []
        for candidate in getattr(response, "candidates", None) or []:
            finish_reasons.append(getattr(candidate, "finish_reason", None))
        logger.info("Gemini finish_reasons=%s", finish_reasons)

    text = getattr(response, "text", "") or ""
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content_obj = getattr(candidate, "content", None)
        parts = getattr(content_obj, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", "")
            if part_text:
                return part_text

    if GEMINI_DEBUG:
        finish_reasons = []
        for candidate in candidates:
            finish_reasons.append(getattr(candidate, "finish_reason", None))
        logger.warning("Gemini returned an empty response; finish_reasons=%s", finish_reasons)
    else:
        logger.warning("Gemini returned an empty response")
    return ""
```

**Explanation:** It accepts `client`, `model_name`, `content`, `config` and returns `str`. See the code below for the full implementation. Key calls include `generate_content()`, `info()`, `getattr()`, `append()`, `warning()`.

### `generate_gemini_response`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `108-213`
- **Signature:** `def generate_gemini_response(`
- **Purpose:** Generate a response from Gemini with retry + model fallback.

**Code:**
```python
def generate_gemini_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    max_retries: int = 3,
) -> str:
    """
    Generate a response from Gemini with retry + model fallback.

    If the primary model returns 503 UNAVAILABLE, we retry with exponential
    backoff and then fall back to less-loaded free models.
    """
    client = _get_gemini_client()
    model_name = model or DEFAULT_GEMINI_MODEL
    temp_value = DEFAULT_TEMPERATURE if temperature is None else temperature
    token_limit = DEFAULT_MAX_OUTPUT_TOKENS if max_output_tokens is None else max_output_tokens

    # Prepend simple-vocabulary instruction to all content
    full_content = SIMPLE_VOCABULARY_INSTRUCTION + content

    try:
        config = genai.types.GenerateContentConfig(
            temperature=temp_value,
            max_output_tokens=token_limit,
            response_mime_type="text/plain",
        )
    except AttributeError:
        config = {
            "temperature": temp_value,
            "max_output_tokens": token_limit,
            "response_mime_type": "text/plain",
        }

    # Build the full fallback chain: primary -> fallback models
    models_to_try = [model_name]
    for fallback in FALLBACK_GEMINI_MODELS:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error: Exception | None = None

    for attempt_model in models_to_try:
        for attempt in range(1, max_retries + 1):
            try:
                if GEMINI_DEBUG:
                    logger.info(
                        "Gemini attempt %s/%s on model=%s",
                        attempt,
                        max_retries,
                        attempt_model,
                    )
                return _generate_once(client, attempt_model, full_content, config)
            except genai_errors.ServerError as exc:
                last_error = exc
                # 503 / 529 — back off and retry
                if attempt < max_retries:
                    wait = 2 ** attempt  # 2, 4, 8 seconds
                    logger.warning(
                        "Gemini model=%s attempt=%s failed (%s). "
                        "Retrying in %ss...",
                        attempt_model,
                        attempt,
                        exc,
                        wait,
                    )
                    time.sleep(wait)
                else:
                    logger.warning(
                        "Gemini model=%s exhausted all %s retries.",
                        attempt_model,
                        max_retries,
                    )
            except genai_errors.ClientError as exc:
                last_error = exc
                code = getattr(exc, "code", None)
                # 429 RESOURCE_EXHAUSTED is transient — retry it
                if code == 429 and attempt < max_retries:
                    wait = 2 ** attempt
                    logger.warning(
                        "Gemini model=%s rate-limited (429). "
                        "Retrying in %ss...",
                        attempt_model,
                        wait,
                    )
                    time.sleep(wait)
                else:
                    logger.error(
                        "Gemini model=%s client error: %s",
                        attempt_model,
                        exc,
                    )
                    break
            except Exception as exc:
                # Non-retryable error (auth, bad request, etc.)
                last_error = exc
                logger.error(
                    "Gemini model=%s non-retryable error: %s",
                    attempt_model,
                    exc,
                )
                break

    # All models exhausted
    raise last_error or RuntimeError("All Gemini models failed")
```

**Explanation:** It accepts `content` and returns `str`. See the code below for the full implementation. Key calls include `_get_gemini_client()`, `GenerateContentConfig()`, `append()`, `range()`, `_generate_once()`.

### `_extract_json_block`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `216-220`
- **Signature:** `def _extract_json_block(text: str) -> str | None:`
- **Purpose:** Handles  extract json block.

**Code:**
```python
def _extract_json_block(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0) if match else None
```

**Explanation:** It accepts `text` and returns `str | None`. See the code below for the full implementation. Key calls include `search()`, `group()`.

### `parse_gemini_json_response`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `223-235`
- **Signature:** `def parse_gemini_json_response(text: str) -> dict[str, Any]:`
- **Purpose:** Parses gemini json response.

**Code:**
```python
def parse_gemini_json_response(text: str) -> dict[str, Any]:
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        json_block = _extract_json_block(text)
        if json_block:
            try:
                return json.loads(json_block)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Gemini JSON block")
        return {}
```

**Explanation:** It accepts `text` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `loads()`, `_extract_json_block()`, `warning()`.

### `_extract_summary`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `238-242`
- **Signature:** `def _extract_summary(text: str) -> str:`
- **Purpose:** Handles  extract summary.

**Code:**
```python
def _extract_summary(text: str) -> str:
    match = re.search(r"\"summary\"\s*:\s*\"([\s\S]*?)\"", text)
    if match:
        return match.group(1).strip()
    return text.strip()
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `search()`, `strip()`, `group()`.

### `_normalize_analysis_output`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `245-281`
- **Signature:** `def _normalize_analysis_output(data: dict[str, Any]) -> dict[str, Any]:`
- **Purpose:** Handles  normalize analysis output.

**Code:**
```python
def _normalize_analysis_output(data: dict[str, Any]) -> dict[str, Any]:
    output = {
        "summary": "",
        "renewable_analysis": {
            "solar": "",
            "wind": "",
            "hydro": "",
            "geothermal": "",
        },
        "recommendation": {
            "best_option": "",
            "reason": "",
        },
        "cost_estimation": {
            "solar": {},
            "wind": {},
            "hydro": {},
            "geothermal": {},
        },
        "environmental_impact": "",
    }

    if not isinstance(data, dict):
        return output

    output.update({k: v for k, v in data.items() if k in output})

    if isinstance(data.get("renewable_analysis"), dict):
        output["renewable_analysis"].update(data["renewable_analysis"])

    if isinstance(data.get("recommendation"), dict):
        output["recommendation"].update(data["recommendation"])

    if isinstance(data.get("cost_estimation"), dict):
        output["cost_estimation"].update(data["cost_estimation"])

    return output
```

**Explanation:** It accepts `data` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `isinstance()`, `update()`, `items()`, `get()`.

### `_build_renewable_analysis_prompt`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `284-334`
- **Signature:** `def _build_renewable_analysis_prompt(analysis_payload: dict[str, Any]) -> str:`
- **Purpose:** Handles  build renewable analysis prompt.

**Code:**
```python
def _build_renewable_analysis_prompt(analysis_payload: dict[str, Any]) -> str:
    # Extract nearby plants so they appear at the top of the prompt
    nearby_plants = analysis_payload.pop("nearby_geothermal_plants", None)
    payload = json.dumps(analysis_payload, ensure_ascii=True, indent=2)

    plant_context = ""
    if nearby_plants:
        lines = []
        for p in nearby_plants[:5]:
            lines.append(
                f"- {p.get('project_name', 'Unknown')} ({p.get('capacity_mw', '?')} MW, "
                f"{p.get('technology', 'unknown')}, {p.get('status', 'unknown')}) — "
                f"{p.get('distance_km', '?')} km away"
            )
        plant_context = (
            "IMPORTANT CONTEXT: This municipality is near the following operating geothermal power plant(s):\n"
            + "\n".join(lines)
            + "\n\n"
        )

    return (
        "You are LUMI, an environmental intelligence assistant helping Filipino households choose renewable energy. "
        "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
        + plant_context
        + "CRITICAL RULES:\n"
        "- Use ONLY markdown headers (## Section Name) to separate sections.\n"
        "- Write in short, clear paragraphs suitable for non-technical users.\n"
        "- Use bullet points (dash + space) for lists, not long walls of text.\n"
        "- NEVER skip any renewable type (solar, wind, hydro, geothermal).\n"
        "- Do NOT use JSON, code blocks, or raw data dumps.\n\n"
        "STRUCTURE YOUR RESPONSE IN THESE EXACT SECTIONS (use ## headers):\n\n"
        "## Observation\n"
        "2-3 sentences describing the municipality's climate: temperature, humidity, solar irradiance, wind speed, rainfall, elevation.\n\n"
        "## Interpretation\n"
        "For EACH renewable source, write ONE short paragraph (2-3 sentences max):\n"
        "- **Solar**: Explain if the irradiance and cloud cover make solar viable.\n"
        "- **Wind**: Explain if the wind speed is strong enough for turbines.\n"
        "- **Hydro**: Explain if rainfall and elevation support micro-hydro.\n"
        "- **Geothermal**: Explain if subsurface heat indicators are present.\n\n"
        "## Recommendation\n"
        "State the BEST renewable option for this household. Then give 3-4 BULLET POINTS of SPECIFIC, ACTIONABLE advice:\n"
        "- What size or type of system to install (e.g., '4-panel 400W rooftop solar')\n"
        "- Estimated monthly generation and what % of their bill it covers\n"
        "- Rough installation cost range in PHP\n"
        "- First step they should take (e.g., 'Contact a DOE-accredited solar installer for site assessment')\n"
        "- Any permit or net-metering application they should file\n\n"
        "## Reason\n"
        "Briefly compare the top 2-3 options. Explain why the recommended one wins and why the others are less suitable, using the actual numbers.\n\n"
        "SIMULATION DATA:\n"
        f"{payload}\n"
    )
```

**Explanation:** It accepts `analysis_payload` and returns `str`. See the code below for the full implementation. Key calls include `pop()`, `dumps()`, `append()`, `join()`, `get()`.

### `analyze_renewable_results`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `337-377`
- **Signature:** `def analyze_renewable_results(analysis_payload: dict[str, Any]) -> dict[str, Any]:`
- **Purpose:** Handles analyze renewable results.

**Code:**
```python
def analyze_renewable_results(analysis_payload: dict[str, Any]) -> dict[str, Any]:
    try:
        prompt = _build_renewable_analysis_prompt(analysis_payload)
        # Use unified client so Groq fallback works when Gemini is rate-limited
        from app.services.llm_client import generate_response
        from app.services.llm_sanitizer import sanitize_llm_output, extract_prescriptive_recommendation

        response_text = generate_response(prompt)
        if GEMINI_DEBUG:
            snippet = response_text[:500] if response_text else ""
            logger.info("Gemini prompt chars=%s response chars=%s", len(prompt), len(response_text))
            logger.info("Gemini response snippet=%s", snippet)

        cleaned = sanitize_llm_output(response_text)
        if not cleaned:
            logger.warning("LLM returned empty response after sanitization")
            return _normalize_analysis_output({})

        prescriptive = extract_prescriptive_recommendation(cleaned)

        return {
            "summary": cleaned,
            "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
            "recommendation": {
                "best_option": prescriptive.get("recommendation", ""),
                "reason": prescriptive.get("reason", ""),
            },
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
            "environmental_impact": "",
            "prescriptive_recommendation": prescriptive,
        }
    except Exception as exc:
        logger.exception("LLM analysis failed")
        return {
            "summary": "LLM analysis failed.",
            "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
            "recommendation": {"best_option": "", "reason": ""},
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
            "environmental_impact": "",
            "error": str(exc),
        }
```

**Explanation:** It accepts `analysis_payload` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_build_renewable_analysis_prompt()`, `generate_response()`, `sanitize_llm_output()`, `extract_prescriptive_recommendation()`, `info()`.

### `analyze_renewable_results_async`

- **File:** `fastapi-backend/app/services/gemini_funcs.py`
- **Lines:** `380-383`
- **Signature:** `async def analyze_renewable_results_async(`
- **Purpose:** Handles analyze renewable results async.

**Code:**
```python
async def analyze_renewable_results_async(
    analysis_payload: dict[str, Any],
) -> dict[str, Any]:
    return await asyncio.to_thread(analyze_renewable_results, analysis_payload)
```

**Explanation:** It accepts `analysis_payload` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `to_thread()`.


## `fastapi-backend/app/services/geospatial_service.py`

**File:** `fastapi-backend/app/services/geospatial_service.py`

**Summary:** Geospatial metadata service for centroid and area queries.

### `get_geospatial_metadata`

- **File:** `fastapi-backend/app/services/geospatial_service.py`
- **Lines:** `33-62`
- **Signature:** `def get_geospatial_metadata(`
- **Purpose:** Fetch geospatial metadata for a single admin unit.

**Code:**
```python
def get_geospatial_metadata(
    level: str,
    geo_id: int,
) -> dict[str, Any] | None:
    """Fetch geospatial metadata for a single admin unit.

    Returns dict with centroid_lat, centroid_lon, area_km2, elevation_m, etc.
    or None if not found.
    """
    if level not in _GEO_COL_MAP:
        logger.warning("Unknown geospatial level: %s", level)
        return None

    fk_col = _GEO_COL_MAP[level]
    client = get_supabase_client()

    try:
        resp = (
            client.table("geospatial_metadata")
            .select("*")
            .eq(fk_col, str(geo_id))
            .limit(1)
            .execute()
        )
        if resp.data:
            return resp.data[0]
    except Exception as exc:
        logger.warning("Geospatial metadata query failed for %s/%s: %s", level, geo_id, exc)

    return None
```

**Explanation:** It accepts `level`, `geo_id` and returns `dict[str, Any] | None`. See the code below for the full implementation. Key calls include `warning()`, `get_supabase_client()`, `execute()`, `limit()`, `eq()`.

### `get_centroid`

- **File:** `fastapi-backend/app/services/geospatial_service.py`
- **Lines:** `65-70`
- **Signature:** `def get_centroid(level: str, geo_id: int) -> tuple[float, float] | None:`
- **Purpose:** Get (lat, lon) centroid for an admin unit. Returns None if not found.

**Code:**
```python
def get_centroid(level: str, geo_id: int) -> tuple[float, float] | None:
    """Get (lat, lon) centroid for an admin unit. Returns None if not found."""
    meta = get_geospatial_metadata(level, geo_id)
    if meta and meta.get("centroid_lat") and meta.get("centroid_lon"):
        return (float(meta["centroid_lat"]), float(meta["centroid_lon"]))
    return None
```

**Explanation:** It accepts `level`, `geo_id` and returns `tuple[float, float] | None`. See the code below for the full implementation. Key calls include `get_geospatial_metadata()`, `get()`, `float()`.

### `get_all_centroids`

- **File:** `fastapi-backend/app/services/geospatial_service.py`
- **Lines:** `78-130`
- **Signature:** `def get_all_centroids(level: str, use_cache: bool = True) -> list[dict[str, Any]]:`
- **Purpose:** Fetch all centroids for a given level.

**Code:**
```python
def get_all_centroids(level: str, use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch all centroids for a given level.

    Returns list of dicts with geo_id, name, centroid_lat, centroid_lon, area_km2.
    """
    if level not in _GEO_COL_MAP:
        logger.warning("Unknown geospatial level: %s", level)
        return []

    if use_cache:
        cached = get_centroid_cache_sync(level)
        if cached:
            return cached

    fk_col = _GEO_COL_MAP[level]
    admin_table = f"{level}s"  # regions, provinces, municipalities, barangays
    admin_pk = f"{level}_id"

    client = get_supabase_client()

    try:
        # Join admin table with geospatial_metadata
        select_cols = f"{admin_pk},name,geospatial_metadata(centroid_lat,centroid_lon,area_km2,elevation_m)"
        resp = (
            client.table(admin_table)
            .select(select_cols)
            .execute()
        )
        rows = resp.data or []

        result = []
        for r in rows:
            geo = r.get("geospatial_metadata")
            if isinstance(geo, list):
                geo = geo[0] if geo else None
            if geo and geo.get("centroid_lat"):
                result.append({
                    "geo_id": r.get(admin_pk),
                    "name": r.get("name"),
                    "centroid_lat": float(geo["centroid_lat"]),
                    "centroid_lon": float(geo["centroid_lon"]),
                    "area_km2": geo.get("area_km2"),
                    "elevation_m": geo.get("elevation_m"),
                })

        if use_cache and result:
            set_centroid_cache_sync(level, result)

        return result

    except Exception as exc:
        logger.warning("Bulk centroid query failed for %s: %s", level, exc)
        return []
```

**Explanation:** It accepts `level`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `warning()`, `get_centroid_cache_sync()`, `get_supabase_client()`, `execute()`, `get()`.

### `get_centroid_fallback`

- **File:** `fastapi-backend/app/services/geospatial_service.py`
- **Lines:** `138-167`
- **Signature:** `def get_centroid_fallback(level: str, geo_id: int) -> tuple[float, float] | None:`
- **Purpose:** Fallback: get lat/lon directly from admin table if geospatial_metadata is empty.

**Code:**
```python
def get_centroid_fallback(level: str, geo_id: int) -> tuple[float, float] | None:
    """Fallback: get lat/lon directly from admin table if geospatial_metadata is empty.

    The admin tables (regions, provinces, municipalities, barangays) still
    have lat/lon columns from the original schema. Use these as a fallback
    when geospatial_metadata has no entry.
    """
    admin_table = f"{level}s"
    admin_pk = f"{level}_id"

    client = get_supabase_client()

    try:
        resp = (
            client.table(admin_table)
            .select(f"{admin_pk},lat,lon")
            .eq(admin_pk, str(geo_id))
            .limit(1)
            .execute()
        )
        if resp.data:
            row = resp.data[0]
            lat = row.get("lat")
            lon = row.get("lon")
            if lat is not None and lon is not None:
                return (float(lat), float(lon))
    except Exception as exc:
        logger.debug("Centroid fallback query failed for %s/%s: %s", level, geo_id, exc)

    return None
```

**Explanation:** It accepts `level`, `geo_id` and returns `tuple[float, float] | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `get()`, `debug()`, `limit()`.

### `get_centroid_with_fallback`

- **File:** `fastapi-backend/app/services/geospatial_service.py`
- **Lines:** `170-175`
- **Signature:** `def get_centroid_with_fallback(level: str, geo_id: int) -> tuple[float, float] | None:`
- **Purpose:** Get centroid from geospatial_metadata, falling back to admin table lat/lon.

**Code:**
```python
def get_centroid_with_fallback(level: str, geo_id: int) -> tuple[float, float] | None:
    """Get centroid from geospatial_metadata, falling back to admin table lat/lon."""
    centroid = get_centroid(level, geo_id)
    if centroid:
        return centroid
    return get_centroid_fallback(level, geo_id)
```

**Explanation:** It accepts `level`, `geo_id` and returns `tuple[float, float] | None`. See the code below for the full implementation. Key calls include `get_centroid()`, `get_centroid_fallback()`.


## `fastapi-backend/app/services/geothermal/__init__.py`

**File:** `fastapi-backend/app/services/geothermal/__init__.py`

**Summary:** Source file `fastapi-backend/app/services/geothermal/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/geothermal/batch_compute.py`

**File:** `fastapi-backend/app/services/geothermal/batch_compute.py`

**Summary:** Batch pre-computation script for geothermal suitability and output.

### `fetch_municipalities`

- **File:** `fastapi-backend/app/services/geothermal/batch_compute.py`
- **Lines:** `36-55`
- **Signature:** `def fetch_municipalities() -> list[dict]:`
- **Purpose:** Fetches municipalities.

**Code:**
```python
def fetch_municipalities() -> list[dict]:
    client = get_supabase_client()
    all_rows: list[dict] = []
    offset = 0
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .limit(1000)
            .offset(offset)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < 1000:
            break
        offset += 1000
    return all_rows
```

**Explanation:** It accepts zero arguments and returns `list[dict]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `extend()`, `len()`, `offset()`.

### `fetch_all_climate`

- **File:** `fastapi-backend/app/services/geothermal/batch_compute.py`
- **Lines:** `58-82`
- **Signature:** `def fetch_all_climate() -> dict[int, float]:`
- **Purpose:** Fetch climate temperatures (2010 annual data) and map by municipality_id.

**Code:**
```python
def fetch_all_climate() -> dict[int, float]:
    """Fetch climate temperatures (2010 annual data) and map by municipality_id."""
    client = get_supabase_client()
    mapping: dict[int, float] = {}
    offset = 0
    while True:
        resp = (
            client.table("municipality_climate_monthly")
            .select("municipality_id,t2m")
            .eq("year", 2010)
            .limit(1000)
            .offset(offset)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        for row in rows:
            mid = row.get("municipality_id")
            if mid is not None:
                mapping[mid] = float(row.get("t2m", 0))
        if len(rows) < 1000:
            break
        offset += 1000
    return mapping
```

**Explanation:** It accepts zero arguments and returns `dict[int, float]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `get()`, `len()`, `offset()`.

### `batch_upsert`

- **File:** `fastapi-backend/app/services/geothermal/batch_compute.py`
- **Lines:** `85-96`
- **Signature:** `def batch_upsert(table: str, rows: list[dict], chunk_size: int = 100) -> None:`
- **Purpose:** Upsert rows in batches to minimize API round-trips.

**Code:**
```python
def batch_upsert(table: str, rows: list[dict], chunk_size: int = 100) -> None:
    """Upsert rows in batches to minimize API round-trips."""
    client = get_supabase_client()
    total = len(rows)
    for i in range(0, total, chunk_size):
        chunk = rows[i : i + chunk_size]
        try:
            client.table(table).upsert(chunk).execute()
        except Exception as exc:
            logger.warning("Batch upsert to %s failed for chunk %d-%d: %s", table, i, i + len(chunk), exc)
        if (i + chunk_size) % 500 == 0 or (i + chunk_size) >= total:
            logger.info("Upserted %d/%d rows to %s", min(i + chunk_size, total), total, table)
```

**Explanation:** It accepts `table`, `rows`, `chunk_size` and returns `None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `len()`, `range()`, `execute()`, `info()`.

### `main`

- **File:** `fastapi-backend/app/services/geothermal/batch_compute.py`
- **Lines:** `99-169`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    logger.info("Loading geothermal datasets...")
    datasets = load_geothermal_datasets()
    logger.info("Datasets loaded.")

    municipalities = fetch_municipalities()
    total = len(municipalities)
    logger.info("Found %d municipalities to process.", total)

    logger.info("Fetching all climate data in one query...")
    climate_map = fetch_all_climate()
    logger.info("Loaded climate for %d municipalities.", len(climate_map))

    suit_rows: list[dict] = []
    output_rows: list[dict] = []

    for idx, muni in enumerate(municipalities, start=1):
        mid = muni.get("municipality_id")
        name = muni.get("name", "")
        lat = muni.get("lat")
        lon = muni.get("lon")

        if lat is None or lon is None:
            logger.warning("Skipping %s (%s) — missing coordinates", name, mid)
            continue

        surface_temp = climate_map.get(mid)

        suit = compute_geothermal_suitability(lat, lon, surface_temp, datasets, municipality_id=mid)
        output = compute_geothermal_output(
            surface_temp,
            suit.get("_gradient_c_km"),
            suit.get("aquifer_score"),
            suit.get("_perm_log10"),
        )

        suit_rows.append({
            "municipality_id": mid,
            "heat_flow_score": suit.get("heat_flow_score"),
            "fault_density": suit.get("fault_density"),
            "fault_distance_km": suit.get("fault_distance_km"),
            "volcano_distance_km": suit.get("volcano_distance_km"),
            "aquifer_score": suit.get("aquifer_score"),
            "temperature_score": suit.get("temperature_score"),
            "geothermal_score": suit.get("geothermal_score"),
            "geothermal_score_mcda": suit.get("geothermal_score"),
            "classification": suit.get("classification"),
        })

        output_rows.append({
            "municipality_id": mid,
            "reservoir_temperature_c": output.get("reservoir_temperature_c"),
            "estimated_flow_rate_kg_s": output.get("estimated_flow_rate_kg_s"),
            "thermal_power_mw": output.get("thermal_power_mw"),
            "electric_power_mw": output.get("electric_power_mw"),
            "annual_energy_gwh": output.get("annual_energy_gwh"),
            "confidence_score": output.get("confidence_score"),
            "source": output.get("source"),
            "assumption": output.get("assumption"),
        })

        if idx % 100 == 0 or idx == total:
            logger.info("Computed %d/%d municipalities", idx, total)

    logger.info("Batch upserting %d suitability rows...", len(suit_rows))
    batch_upsert("geothermal_suitability", suit_rows, chunk_size=100)

    logger.info("Batch upserting %d output rows...", len(output_rows))
    batch_upsert("geothermal_output", output_rows, chunk_size=100)

    logger.info("Batch pre-computation complete.")
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `info()`, `load_geothermal_datasets()`, `fetch_municipalities()`, `len()`, `fetch_all_climate()`.


## `fastapi-backend/app/services/geothermal/extract_kmz.py`

**File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`

**Summary:** One-time batch script to extract coordinates from KMZ files.

### `_parse_kmz_coords`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `40-109`
- **Signature:** `def _parse_kmz_coords(kmz_path: Path) -> list[dict]:`
- **Purpose:** Extract point coordinates from a KMZ file.

**Code:**
```python
def _parse_kmz_coords(kmz_path: Path) -> list[dict]:
    """Extract point coordinates from a KMZ file.

    Returns list of dicts with keys: lat, lon, name (optional), length_km (optional).
    """
    items: list[dict] = []
    with zipfile.ZipFile(kmz_path, "r") as zf:
        # Find the KML inside the KMZ
        kml_names = [n for n in zf.namelist() if n.endswith(".kml")]
        if not kml_names:
            logger.error("No .kml found inside %s", kmz_path)
            return items

        with zf.open(kml_names[0]) as kml_file:
            tree = ET.parse(kml_file)
            root = tree.getroot()

        # KML namespace
        ns = {"kml": "http://www.opengis.net/kml/2.2"}

        # Parse Placemark points
        for placemark in root.findall(".//kml:Placemark", ns):
            name_elem = placemark.find("kml:name", ns)
            name = name_elem.text if name_elem is not None else ""

            point = placemark.find(".//kml:Point/kml:coordinates", ns)
            if point is not None and point.text:
                coords = point.text.strip()
                # Format: lon,lat,alt or lon,lat
                parts = coords.split(",")
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        if PH_MIN_LAT <= lat <= PH_MAX_LAT and PH_MIN_LON <= lon <= PH_MAX_LON:
                            items.append({"lat": lat, "lon": lon, "name": name})
                    except ValueError:
                        continue
                continue

            # LineString (faults)
            line = placemark.find(".//kml:LineString/kml:coordinates", ns)
            if line is not None and line.text:
                coords_text = line.text.strip()
                coord_pairs = [c.strip() for c in coords_text.split() if c.strip()]
                lats, lons = [], []
                for pair in coord_pairs:
                    parts = pair.split(",")
                    if len(parts) >= 2:
                        try:
                            lons.append(float(parts[0]))
                            lats.append(float(parts[1]))
                        except ValueError:
                            continue
                if lats and lons:
                    # Calculate approximate length via Haversine sum
                    total_km = 0.0
                    for i in range(1, len(lats)):
                        total_km += _haversine(lats[i - 1], lons[i - 1], lats[i], lons[i])
                    # Use midpoint for representative point
                    mid_lat = sum(lats) / len(lats)
                    mid_lon = sum(lons) / len(lons)
                    if PH_MIN_LAT <= mid_lat <= PH_MAX_LAT and PH_MIN_LON <= mid_lon <= PH_MAX_LON:
                        items.append({
                            "lat": round(mid_lat, 6),
                            "lon": round(mid_lon, 6),
                            "name": name,
                            "length_km": round(total_km, 3),
                        })
    return items
```

**Explanation:** It accepts `kmz_path` and returns `list[dict]`. See the code below for the full implementation. Key calls include `ZipFile()`, `findall()`, `error()`, `open()`, `parse()`.

### `_haversine`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `112-123`
- **Signature:** `def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:`
- **Purpose:** Return distance in km.

**Code:**
```python
def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
```

**Explanation:** It accepts `lat1`, `lon1`, `lat2`, `lon2` and returns `float`. See the code below for the full implementation. Key calls include `radians()`, `sin()`, `cos()`, `atan2()`, `sqrt()`.

### `extract_faults`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `126-135`
- **Signature:** `def extract_faults() -> None:`
- **Purpose:** Extracts faults.

**Code:**
```python
def extract_faults() -> None:
    kmz = _DATASET_DIR / "aft_2025_000000000_02.kmz"
    out = _LOCAL_DATA_DIR / "geothermal_faults.json"
    if not kmz.exists():
        logger.error("Fault KMZ not found: %s", kmz)
        return
    faults = _parse_kmz_coords(kmz)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(faults, f, indent=2)
    logger.info("Extracted %d faults to %s", len(faults), out)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `_parse_kmz_coords()`, `open()`, `dump()`.

### `extract_volcanoes`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `138-147`
- **Signature:** `def extract_volcanoes() -> None:`
- **Purpose:** Extracts volcanoes.

**Code:**
```python
def extract_volcanoes() -> None:
    kmz = _DATASET_DIR / "VOL_2016_000000000_02.kmz"
    out = _LOCAL_DATA_DIR / "geothermal_volcanoes.json"
    if not kmz.exists():
        logger.error("Volcano KMZ not found: %s", kmz)
        return
    volcanoes = _parse_kmz_coords(kmz)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(volcanoes, f, indent=2)
    logger.info("Extracted %d volcanoes to %s", len(volcanoes), out)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `_parse_kmz_coords()`, `open()`, `dump()`.

### `extract_heatflow`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `150-186`
- **Signature:** `def extract_heatflow() -> None:`
- **Purpose:** Parse the IHFC txt file and write a filtered CSV for Philippines.

**Code:**
```python
def extract_heatflow() -> None:
    """Parse the IHFC txt file and write a filtered CSV for Philippines."""
    txt_path = _DATASET_DIR / "IHFC_2024_GHFDB_v.2026.03.txt"
    out = _LOCAL_DATA_DIR / "geothermal_heatflow.csv"
    if not txt_path.exists():
        logger.error("Heatflow txt not found: %s", txt_path)
        return

    rows: list[dict] = []
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            parts = stripped.split("\t")
            if len(parts) < 20:
                continue
            try:
                # GHFDB 2024 column mapping (0-indexed):
                #   0 = q (heat flow mW/m2)
                #   3 = lat_NS
                #   4 = long_EW
                q = float(parts[0].strip()) if parts[0].strip() else None
                lat = float(parts[3].strip()) if parts[3].strip() else None
                lon = float(parts[4].strip()) if parts[4].strip() else None
                if q is not None and lat is not None and lon is not None:
                    if PH_MIN_LAT <= lat <= PH_MAX_LAT and PH_MIN_LON <= lon <= PH_MAX_LON:
                        rows.append({"lat": lat, "lon": lon, "heat_flow_mw_m2": q})
            except (ValueError, IndexError):
                continue

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(out, index=False)
        logger.info("Extracted %d heat-flow points to %s", len(df), out)
    else:
        logger.warning("No heat-flow rows extracted.")
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `open()`, `strip()`, `split()`.

### `_write_philippine_volcanoes`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `189-212`
- **Signature:** `def _write_philippine_volcanoes() -> None:`
- **Purpose:** Generate hardcoded volcano coordinates for the Philippines.

**Code:**
```python
def _write_philippine_volcanoes() -> None:
    """Generate hardcoded volcano coordinates for the Philippines.
    The source KMZ is a raster overlay; we use known volcano locations."""
    out = _LOCAL_DATA_DIR / "geothermal_volcanoes.json"
    volcanoes = [
        {"lat": 13.2548, "lon": 123.6850, "name": "Mayon"},
        {"lat": 14.0027, "lon": 120.9935, "name": "Taal"},
        {"lat": 15.1429, "lon": 120.3496, "name": "Pinatubo"},
        {"lat": 12.7697, "lon": 124.0561, "name": "Bulusan"},
        {"lat": 10.4117, "lon": 123.1319, "name": "Kanlaon"},
        {"lat": 9.1969, "lon": 124.6578, "name": "Hibok-Hibok"},
        {"lat": 6.9876, "lon": 125.2694, "name": "Mount Apo"},
        {"lat": 14.0697, "lon": 121.4844, "name": "Mount Banahaw"},
        {"lat": 14.1308, "lon": 121.1956, "name": "Mount Makiling"},
        {"lat": 13.3200, "lon": 123.7000, "name": "Malinao"},
        {"lat": 13.2200, "lon": 123.6000, "name": "Masaraga"},
        {"lat": 11.5200, "lon": 124.4500, "name": "Biliran"},
        {"lat": 8.0000, "lon": 123.2000, "name": "Camiguin"},
        {"lat": 7.9000, "lon": 124.3000, "name": "Ragang"},
        {"lat": 6.9800, "lon": 121.9500, "name": "Matutum"},
    ]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(volcanoes, f, indent=2)
    logger.info("Wrote %d Philippine volcanoes to %s", len(volcanoes), out)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `open()`, `dump()`, `info()`, `len()`.

### `_write_philippine_faults`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `215-238`
- **Signature:** `def _write_philippine_faults() -> None:`
- **Purpose:** Generate hardcoded fault line midpoints for the Philippines.

**Code:**
```python
def _write_philippine_faults() -> None:
    """Generate hardcoded fault line midpoints for the Philippines.
    The source KMZ is a raster overlay; we use known fault segments."""
    out = _LOCAL_DATA_DIR / "geothermal_faults.json"
    faults = [
        # Philippine Fault segments
        {"lat": 16.5, "lon": 121.5, "name": "Philippine Fault N-Luzon", "length_km": 300},
        {"lat": 15.5, "lon": 121.0, "name": "Philippine Fault C-Luzon", "length_km": 250},
        {"lat": 14.0, "lon": 122.0, "name": "Philippine Fault S-Luzon", "length_km": 200},
        {"lat": 11.5, "lon": 125.0, "name": "Philippine Fault Visayas", "length_km": 300},
        {"lat": 8.0, "lon": 126.0, "name": "Philippine Fault Mindanao", "length_km": 350},
        # Other major faults
        {"lat": 14.6, "lon": 121.1, "name": "Marikina Valley Fault", "length_km": 80},
        {"lat": 14.0, "lon": 120.0, "name": "Western Philippine Fault", "length_km": 150},
        {"lat": 14.5, "lon": 123.0, "name": "Eastern Philippine Fault", "length_km": 180},
        {"lat": 7.0, "lon": 125.0, "name": "Central Mindanao Fault", "length_km": 200},
        {"lat": 9.5, "lon": 125.5, "name": "Surigao Fault", "length_km": 120},
        {"lat": 13.5, "lon": 122.0, "name": "Macolod Corridor", "length_km": 100},
        {"lat": 15.0, "lon": 120.5, "name": "Lubao Fault", "length_km": 60},
        {"lat": 13.8, "lon": 121.0, "name": "Verde Passage Fault", "length_km": 70},
    ]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(faults, f, indent=2)
    logger.info("Wrote %d Philippine fault segments to %s", len(faults), out)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `open()`, `dump()`, `info()`, `len()`.

### `main`

- **File:** `fastapi-backend/app/services/geothermal/extract_kmz.py`
- **Lines:** `241-257`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    logger.info("Starting KMZ/heatflow extraction...")
    extract_faults()
    extract_volcanoes()
    extract_heatflow()

    # The source KMZ files are raster overlays without Placemark vector data.
    # Populate hardcoded Philippine coordinates when extraction yields nothing.
    faults_out = _LOCAL_DATA_DIR / "geothermal_faults.json"
    if not faults_out.exists() or json.load(open(faults_out, "r", encoding="utf-8")) == []:
        _write_philippine_faults()

    volc_out = _LOCAL_DATA_DIR / "geothermal_volcanoes.json"
    if not volc_out.exists() or json.load(open(volc_out, "r", encoding="utf-8")) == []:
        _write_philippine_volcanoes()

    logger.info("Extraction complete. Files saved to %s", _LOCAL_DATA_DIR)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `info()`, `extract_faults()`, `extract_volcanoes()`, `extract_heatflow()`, `_write_philippine_faults()`.


## `fastapi-backend/app/services/geothermal/features.py`

**File:** `fastapi-backend/app/services/geothermal/features.py`

**Summary:** Geothermal feature engineering for LUMI.

### `_haversine`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `49-60`
- **Signature:** `def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:`
- **Purpose:** Return distance between two lat/lon points in kilometres.

**Code:**
```python
def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance between two lat/lon points in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
```

**Explanation:** It accepts `lat1`, `lon1`, `lat2`, `lon2` and returns `float`. See the code below for the full implementation. Key calls include `radians()`, `sin()`, `cos()`, `atan2()`, `sqrt()`.

### `_normalize`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `63-66`
- **Signature:** `def _normalize(value: float | None, min_v: float, max_v: float) -> float:`
- **Purpose:** Handles  normalize.

**Code:**
```python
def _normalize(value: float | None, min_v: float, max_v: float) -> float:
    if value is None or max_v == min_v:
        return 0.0
    return max(0.0, min(1.0, (value - min_v) / (max_v - min_v)))
```

**Explanation:** It accepts `value`, `min_v`, `max_v` and returns `float`. See the code below for the full implementation. Key calls include `max()`, `min()`.

### `_load_local_geothermal_datasets`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `69-110`
- **Signature:** `def _load_local_geothermal_datasets() -> dict[str, Any]:`
- **Purpose:** Original local-file loader used when USE_LOCAL_DATA_FALLBACK is enabled.

**Code:**
```python
def _load_local_geothermal_datasets() -> dict[str, Any]:
    """Original local-file loader used when USE_LOCAL_DATA_FALLBACK is enabled."""
    datasets: dict[str, Any] = {"faults": [], "volcanoes": [], "heatflow": None, "aquifers": None, "aquifers_gdf": None}

    if _FAULTS_JSON.exists():
        with open(_FAULTS_JSON, "r", encoding="utf-8") as f:
            datasets["faults"] = json.load(f)
    else:
        logger.warning("Fault data not found at %s", _FAULTS_JSON)

    if _VOLCANOES_JSON.exists():
        with open(_VOLCANOES_JSON, "r", encoding="utf-8") as f:
            datasets["volcanoes"] = json.load(f)
    else:
        logger.warning("Volcano data not found at %s", _VOLCANOES_JSON)

    if _HEATFLOW_CSV.exists():
        datasets["heatflow"] = pd.read_csv(_HEATFLOW_CSV)
    else:
        logger.warning("Heatflow data not found at %s", _HEATFLOW_CSV)

    # Prefer spatial aquifer GeoJSON (municipality-level) over legacy CSV
    aquifer_geojson = _LOCAL_DATA_DIR / "aquifers_ph.geojson"
    if aquifer_geojson.exists():
        try:
            import geopandas as gpd
            datasets["aquifers_gdf"] = gpd.read_file(aquifer_geojson)
            logger.info("Loaded spatial aquifer data: %d polygons", len(datasets["aquifers_gdf"]))
        except Exception as exc:
            logger.warning("Failed to load local aquifer GeoJSON: %s", exc)
            datasets["aquifers_gdf"] = None
    else:
        datasets["aquifers_gdf"] = None

    # Legacy CSV fallback
    aquifer_path = _DATASET_DIR / "aquifer_properties.csv"
    if aquifer_path.exists():
        datasets["aquifers"] = pd.read_csv(aquifer_path)
    else:
        logger.warning("Aquifer data not found at %s", aquifer_path)

    return datasets
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `exists()`, `warning()`, `open()`, `load()`, `read_csv()`.

### `load_geothermal_datasets`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `113-165`
- **Signature:** `def load_geothermal_datasets() -> dict[str, Any]:`
- **Purpose:** Load pre-extracted geothermal datasets into memory.

**Code:**
```python
def load_geothermal_datasets() -> dict[str, Any]:
    """Load pre-extracted geothermal datasets into memory.

    Returns dict with keys: faults, volcanoes, heatflow, aquifers, aquifers_gdf.
    Small datasets are cached in Redis; the heavy aquifer GeoJSON is no longer
    loaded at runtime unless local fallback is enabled.
    """
    global _geothermal_datasets
    if _geothermal_datasets is not None:
        return _geothermal_datasets

    cache_key = "geothermal:datasets"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        _geothermal_datasets = {
            "faults": cached.get("faults", []),
            "volcanoes": cached.get("volcanoes", []),
            "heatflow": pd.DataFrame(cached.get("heatflow", [])) if cached.get("heatflow") else None,
            "aquifers": None,
            "aquifers_gdf": None,
        }
        return _geothermal_datasets

    try:
        client = get_supabase_client()
        faults_resp = client.table("geothermal_faults").select("*").execute()
        volcanoes_resp = client.table("geothermal_volcanoes").select("*").execute()
        heatflow_resp = client.table("geothermal_heatflow").select("*").execute()

        datasets = {
            "faults": faults_resp.data or [],
            "volcanoes": volcanoes_resp.data or [],
            "heatflow": pd.DataFrame(heatflow_resp.data) if heatflow_resp.data else None,
            "aquifers": None,
            "aquifers_gdf": None,
        }

        cache_payload = {
            "faults": datasets["faults"],
            "volcanoes": datasets["volcanoes"],
            "heatflow": heatflow_resp.data or [],
        }
        cache_set_sync(cache_key, cache_payload, ttl=86400)
        _geothermal_datasets = datasets
        return datasets
    except Exception as exc:
        logger.warning("Failed to load geothermal datasets from Supabase: %s", exc)

    if os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true":
        _geothermal_datasets = _load_local_geothermal_datasets()
        return _geothermal_datasets

    return {"faults": [], "volcanoes": [], "heatflow": None, "aquifers": None, "aquifers_gdf": None}
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `cache_get_sync()`, `get()`, `DataFrame()`, `get_supabase_client()`, `execute()`.

### `query_aquifer_by_location`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `168-201`
- **Signature:** `def query_aquifer_by_location(`
- **Purpose:** Point-in-polygon query for aquifer properties.

**Code:**
```python
def query_aquifer_by_location(
    lat: float, lon: float, gdf: Any | None
) -> dict[str, float | None] | None:
    """Point-in-polygon query for aquifer properties.

    Args:
        lat: Latitude (WGS84).
        lon: Longitude (WGS84).
        gdf: GeoDataFrame with aquifer polygons (must be in EPSG:4326).

    Returns:
        Dict with porosity, permeability_log10, thickness_m, depth_m, basin_name,
        or None if point is not inside any polygon.
    """
    if gdf is None or gdf.empty:
        return None

    from shapely.geometry import Point

    point = Point(lon, lat)
    # GeoPandas spatial query
    matches = gdf[gdf.geometry.contains(point)]
    if matches.empty:
        return None

    # If multiple polygons overlap, take the first (or could average)
    row = matches.iloc[0]
    return {
        "porosity": float(row["porosity"]) if "porosity" in row else None,
        "permeability_log10": float(row["permeability_log10"]) if "permeability_log10" in row else None,
        "thickness_m": float(row["thickness_m"]) if "thickness_m" in row else None,
        "depth_m": float(row["depth_m"]) if "depth_m" in row else None,
        "basin_name": str(row["basin_name"]) if "basin_name" in row else None,
    }
```

**Explanation:** It accepts `lat`, `lon`, `gdf` and returns `dict[str, float | None] | None`. See the code below for the full implementation. Key calls include `Point()`, `contains()`, `float()`, `str()`.

### `query_aquifer_by_municipality`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `204-234`
- **Signature:** `def query_aquifer_by_municipality(municipality_id: int | None) -> dict[str, Any] | None:`
- **Purpose:** Fetch pre-computed aquifer properties for a municipality from Supabase.

**Code:**
```python
def query_aquifer_by_municipality(municipality_id: int | None) -> dict[str, Any] | None:
    """Fetch pre-computed aquifer properties for a municipality from Supabase."""
    if municipality_id is None:
        return None
    try:
        client = get_supabase_client()
        resp = (
            client.table("geothermal_suitability")
            .select(
                "aquifer_porosity,aquifer_permeability_log10,aquifer_thickness_m,"
                "aquifer_depth_m,aquifer_basin_name,aquifer_score,"
                "aquifer_fallback,aquifer_distance_km"
            )
            .eq("municipality_id", municipality_id)
            .single()
            .execute()
        )
        if resp.data:
            return {
                "porosity": resp.data.get("aquifer_porosity"),
                "permeability_log10": resp.data.get("aquifer_permeability_log10"),
                "thickness_m": resp.data.get("aquifer_thickness_m"),
                "depth_m": resp.data.get("aquifer_depth_m"),
                "basin_name": resp.data.get("aquifer_basin_name"),
                "aquifer_score": resp.data.get("aquifer_score"),
                "aquifer_fallback": resp.data.get("aquifer_fallback"),
                "aquifer_distance_km": resp.data.get("aquifer_distance_km"),
            }
    except Exception as exc:
        logger.warning("Supabase aquifer query failed for %s: %s", municipality_id, exc)
    return None
```

**Explanation:** It accepts `municipality_id` and returns `dict[str, Any] | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `warning()`, `single()`, `get()`.

### `calculate_fault_distance`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `237-263`
- **Signature:** `def calculate_fault_distance(muni_lat: float, muni_lon: float, faults: list[dict] | None = None) -> float | None:`
- **Purpose:** Return distance (km) from municipality to the nearest active fault.

**Code:**
```python
def calculate_fault_distance(muni_lat: float, muni_lon: float, faults: list[dict] | None = None) -> float | None:
    """Return distance (km) from municipality to the nearest active fault.

    Args:
        muni_lat: Municipality latitude.
        muni_lon: Municipality longitude.
        faults: List of fault dicts with 'lat', 'lon', 'length_km'. Loaded
            automatically if not provided.

    Returns:
        Distance in kilometres, or None if no fault data is available.
    """
    if faults is None:
        if not _FAULTS_JSON.exists():
            return None
        with open(_FAULTS_JSON, "r", encoding="utf-8") as f:
            faults = json.load(f)

    if not faults:
        return None

    min_dist = float("inf")
    for fault in faults:
        dist = _haversine(muni_lat, muni_lon, fault["lat"], fault["lon"])
        if dist < min_dist:
            min_dist = dist
    return round(min_dist, 2)
```

**Explanation:** It accepts `muni_lat`, `muni_lon`, `faults` and returns `float | None`. See the code below for the full implementation. Key calls include `exists()`, `open()`, `load()`, `float()`, `_haversine()`.

### `calculate_fault_density`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `266-273`
- **Signature:** `def calculate_fault_density(fault_lengths_km: float, municipality_area_km2: float) -> float | None:`
- **Purpose:** Return fault density = fault_length_km / municipality_area_km2.

**Code:**
```python
def calculate_fault_density(fault_lengths_km: float, municipality_area_km2: float) -> float | None:
    """Return fault density = fault_length_km / municipality_area_km2.

    Returns None if area is zero or missing.
    """
    if not municipality_area_km2 or municipality_area_km2 <= 0:
        return None
    return round(fault_lengths_km / municipality_area_km2, 6)
```

**Explanation:** It accepts `fault_lengths_km`, `municipality_area_km2` and returns `float | None`. See the code below for the full implementation. Key calls include `round()`.

### `calculate_volcano_distance`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `276-302`
- **Signature:** `def calculate_volcano_distance(muni_lat: float, muni_lon: float, volcanoes: list[dict] | None = None) -> float | None:`
- **Purpose:** Return distance (km) from municipality to the nearest volcano.

**Code:**
```python
def calculate_volcano_distance(muni_lat: float, muni_lon: float, volcanoes: list[dict] | None = None) -> float | None:
    """Return distance (km) from municipality to the nearest volcano.

    Args:
        muni_lat: Municipality latitude.
        muni_lon: Municipality longitude.
        volcanoes: List of volcano dicts with 'lat', 'lon', 'name'. Loaded
            automatically if not provided.

    Returns:
        Distance in kilometres, or None if no volcano data is available.
    """
    if volcanoes is None:
        if not _VOLCANOES_JSON.exists():
            return None
        with open(_VOLCANOES_JSON, "r", encoding="utf-8") as f:
            volcanoes = json.load(f)

    if not volcanoes:
        return None

    min_dist = float("inf")
    for vol in volcanoes:
        dist = _haversine(muni_lat, muni_lon, vol["lat"], vol["lon"])
        if dist < min_dist:
            min_dist = dist
    return round(min_dist, 2)
```

**Explanation:** It accepts `muni_lat`, `muni_lon`, `volcanoes` and returns `float | None`. See the code below for the full implementation. Key calls include `exists()`, `open()`, `load()`, `float()`, `_haversine()`.

### `idw_heat_flow`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `305-352`
- **Signature:** `def idw_heat_flow(`
- **Purpose:** Inverse Distance Weighting for heat-flow point data.

**Code:**
```python
def idw_heat_flow(
    lat: float,
    lon: float,
    measurements: pd.DataFrame,
    radius_km: float = 300.0,
    power: float = 2.0,
    min_points: int = 3,
    prefer_onshore: bool = True,
) -> float | None:
    """Inverse Distance Weighting for heat-flow point data.

    Args:
        lat: Target latitude.
        lon: Target longitude.
        measurements: DataFrame with columns lat, lon, heat_flow_mw_m2,
            and optionally 'environment' and 'elevation'.
        radius_km: Maximum search radius (km). Default 300 km covers
            Philippines from nearby land measurements (S. China, Taiwan,
            Indonesia) when local data is sparse.
        power: IDW power. p=2 is standard for heat-flow interpolation.
        min_points: Minimum neighbours required for a reliable estimate.
        prefer_onshore: If True, give 2x weight to onshore measurements.

    Returns:
        Interpolated heat flow (mW/m²), or None if insufficient neighbours.
    """
    if measurements is None or measurements.empty:
        return None

    weights = []
    values = []

    for _, row in measurements.iterrows():
        d = _haversine(lat, lon, float(row["lat"]), float(row["lon"]))
        if d == 0.0:
            # Exact match: no interpolation needed.
            return float(row["heat_flow_mw_m2"])
        if 0 < d < radius_km:
            w = 1.0 / (d ** power)
            if prefer_onshore and "onshore" in str(row.get("environment", "")).lower():
                w *= 2.0
            weights.append(w)
            values.append(float(row["heat_flow_mw_m2"]))

    if len(weights) < min_points:
        return None

    return sum(w * v for w, v in zip(weights, values)) / sum(weights)
```

**Explanation:** It accepts `lat`, `lon`, `measurements`, `radius_km`, `power`, `min_points`, `prefer_onshore` and returns `float | None`. See the code below for the full implementation. Key calls include `iterrows()`, `_haversine()`, `float()`, `append()`, `lower()`.

### `calculate_heatflow_score`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `355-366`
- **Signature:** `def calculate_heatflow_score(heat_flow_mw_m2: float | None) -> float | None:`
- **Purpose:** Normalize heat flow (mW/m2) to a 0-1 score using 40-120 range.

**Code:**
```python
def calculate_heatflow_score(heat_flow_mw_m2: float | None) -> float | None:
    """Normalize heat flow (mW/m2) to a 0-1 score using 40-120 range.

    Args:
        heat_flow_mw_m2: Heat flow value in mW/m2.

    Returns:
        Normalized score (0-1), or None if input is missing.
    """
    if heat_flow_mw_m2 is None:
        return None
    return round(_normalize(heat_flow_mw_m2, 40.0, 120.0), 4)
```

**Explanation:** It accepts `heat_flow_mw_m2` and returns `float | None`. See the code below for the full implementation. Key calls include `round()`, `_normalize()`.

### `calculate_aquifer_score`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `369-397`
- **Signature:** `def calculate_aquifer_score(`
- **Purpose:** Compute a composite aquifer suitability score (0-1).

**Code:**
```python
def calculate_aquifer_score(
    permeability: float | None,
    porosity: float | None,
    thickness: float | None,
) -> float | None:
    """Compute a composite aquifer suitability score (0-1).

    Weights: permeability 0.5, porosity 0.3, thickness 0.2.
    Uses log-scaled permeability because aquifer_properties.csv stores
    it as log10(m2) (negative values common).

    Args:
        permeability: Permeability (log10 m2) from aquifer dataset.
        porosity: Porosity fraction (0-1).
        thickness: Aquifer thickness in metres.

    Returns:
        Composite score 0-1, or None if any input is missing.
    """
    if permeability is None or porosity is None or thickness is None:
        return None

    # Permeability in dataset is log10(m2); typical range -17 to -11
    perm_score = _normalize(permeability, -17.0, -11.0)
    poro_score = _normalize(porosity, 0.0, 0.35)
    thick_score = _normalize(thickness, 0.0, 2000.0)

    score = (0.5 * perm_score) + (0.3 * poro_score) + (0.2 * thick_score)
    return round(max(0.0, min(1.0, score)), 4)
```

**Explanation:** It accepts `permeability`, `porosity`, `thickness` and returns `float | None`. See the code below for the full implementation. Key calls include `_normalize()`, `round()`, `max()`, `min()`.

### `calculate_geothermal_gradient`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `400-421`
- **Signature:** `def calculate_geothermal_gradient(`
- **Purpose:** Estimate geothermal gradient (C/km) from heat flow.

**Code:**
```python
def calculate_geothermal_gradient(
    heat_flow_mw_m2: float | None, thermal_conductivity_wm_k: float = 2.5
) -> float | None:
    """Estimate geothermal gradient (C/km) from heat flow.

    Formula: G = q / k  where q = heat flow (W/m2) and k = thermal conductivity.
    We convert mW/m2 -> W/m2 by dividing by 1000.

    Args:
        heat_flow_mw_m2: Heat flow in mW/m2.
        thermal_conductivity_wm_k: Thermal conductivity in W/(m*K). Default 2.5
            for typical crustal rock.

    Returns:
        Gradient in C/km, or None if input is missing.
    """
    if heat_flow_mw_m2 is None or thermal_conductivity_wm_k <= 0:
        return None
    q_wm2 = heat_flow_mw_m2 / 1000.0
    gradient_c_m = q_wm2 / thermal_conductivity_wm_k
    gradient_c_km = gradient_c_m * 1000.0
    return round(gradient_c_km, 3)
```

**Explanation:** It accepts `heat_flow_mw_m2`, `thermal_conductivity_wm_k` and returns `float | None`. See the code below for the full implementation. Key calls include `round()`.

### `calculate_reservoir_temperature`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `424-443`
- **Signature:** `def calculate_reservoir_temperature(`
- **Purpose:** Estimate reservoir temperature using Ts + (G * Depth).

**Code:**
```python
def calculate_reservoir_temperature(
    surface_temp_c: float | None,
    gradient_c_km: float | None,
    depth_m: float = DEFAULT_RESERVOIR_DEPTH_M,
) -> float | None:
    """Estimate reservoir temperature using Ts + (G * Depth).

    Args:
        surface_temp_c: NASA POWER average surface temperature (C).
        gradient_c_km: Geothermal gradient (C/km).
        depth_m: Estimated reservoir depth in metres. Default 2000 m.

    Returns:
        Reservoir temperature in C, or None if inputs are missing.
    """
    if surface_temp_c is None or gradient_c_km is None:
        return None
    depth_km = depth_m / 1000.0
    temp = surface_temp_c + (gradient_c_km * depth_km)
    return round(temp, 2)
```

**Explanation:** It accepts `surface_temp_c`, `gradient_c_km`, `depth_m` and returns `float | None`. See the code below for the full implementation. Key calls include `round()`.

### `estimate_flow_rate`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `446-470`
- **Signature:** `def estimate_flow_rate(`
- **Purpose:** Estimate geothermal flow rate (kg/s) from aquifer properties.

**Code:**
```python
def estimate_flow_rate(
    aquifer_score: float | None,
    permeability_log10_m2: float | None,
) -> float | None:
    """Estimate geothermal flow rate (kg/s) from aquifer properties.

    When direct flow data is unavailable, we infer a plausible flow
    from aquifer permeability and score. Based on literature ranges
    for small-to-medium geothermal fields (10-500 kg/s).

    Args:
        aquifer_score: Composite aquifer suitability (0-1).
        permeability_log10_m2: Log10 permeability (m2).

    Returns:
        Estimated flow rate in kg/s, or None if inputs are missing.
    """
    if aquifer_score is None or permeability_log10_m2 is None:
        return None

    # Base estimate scales with aquifer quality and permeability
    # Higher permeability (less negative log10) -> higher flow
    perm_factor = max(0.0, _normalize(permeability_log10_m2, -17.0, -11.0))
    flow = 10.0 + (aquifer_score * perm_factor * 400.0)
    return round(flow, 2)
```

**Explanation:** It accepts `aquifer_score`, `permeability_log10_m2` and returns `float | None`. See the code below for the full implementation. Key calls include `max()`, `_normalize()`, `round()`.

### `compute_geothermal_suitability`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `473-620`
- **Signature:** `def compute_geothermal_suitability(`
- **Purpose:** Compute all geothermal suitability metrics for a municipality.

**Code:**
```python
def compute_geothermal_suitability(
    muni_lat: float,
    muni_lon: float,
    surface_temp_c: float | None,
    datasets: dict[str, Any] | None = None,
    municipality_area_km2: float = 50.0,
    municipality_id: int | None = None,
) -> dict[str, Any]:
    """Compute all geothermal suitability metrics for a municipality.

    Args:
        muni_lat: Municipality latitude.
        muni_lon: Municipality longitude.
        surface_temp_c: NASA POWER average surface temperature (C).
        datasets: Pre-loaded datasets dict from load_geothermal_datasets().
        municipality_area_km2: Municipality area in km2 (used for fault density).

    Returns:
        Dict with all suitability fields and an overall score + classification.
    """
    if datasets is None:
        datasets = load_geothermal_datasets()

    # Fault / volcano distances
    fault_dist = calculate_fault_distance(muni_lat, muni_lon, datasets.get("faults"))
    volcano_dist = calculate_volcano_distance(muni_lat, muni_lon, datasets.get("volcanoes"))

    # Heat flow (IDW interpolation from nearest measurements)
    heat_flow_val: float | None = None
    heat_flow_score: float | None = None
    gradient: float | None = None
    hf_df = datasets.get("heatflow")
    if hf_df is not None and not hf_df.empty:
        heat_flow_val = idw_heat_flow(
            muni_lat, muni_lon, hf_df, radius_km=300.0, power=2.0, min_points=3
        )
        heat_flow_score = calculate_heatflow_score(heat_flow_val)
        gradient = calculate_geothermal_gradient(heat_flow_val)

    # Aquifer: prefer point-in-polygon spatial query, fall back to CSV median
    aquifer_score: float | None = None
    perm_val: float | None = None
    poro_val: float | None = None
    thick_val: float | None = None
    basin_name: str | None = None

    # 1. Try pre-computed Supabase table first; fall back to spatial GeoJSON if local data is available
    aq_match = query_aquifer_by_municipality(municipality_id)
    if aq_match is None and datasets is not None:
        gdf = datasets.get("aquifers_gdf")
        if gdf is not None and not gdf.empty:
            aq_match = query_aquifer_by_location(muni_lat, muni_lon, gdf)

    if aq_match:
        poro_val = aq_match.get("porosity")
        perm_val = aq_match.get("permeability_log10")
        thick_val = aq_match.get("thickness_m")
        basin_name = aq_match.get("basin_name")
        aquifer_score = aq_match.get("aquifer_score")
        if aquifer_score is None and perm_val is not None and poro_val is not None and thick_val is not None:
            aquifer_score = calculate_aquifer_score(perm_val, poro_val, thick_val)

    # 2. Fallback to legacy CSV median if spatial query returns nothing
    if aquifer_score is None:
        aq_df = datasets.get("aquifers")
        if aq_df is not None and not aq_df.empty:
            country_col = "Country"
            if country_col in aq_df.columns:
                ph_aq = aq_df[aq_df[country_col].astype(str).str.contains("Philippines", case=False, na=False)]
            else:
                ph_aq = aq_df
            if not ph_aq.empty:
                perm_val = float(ph_aq["Permeability"].median()) if "Permeability" in ph_aq.columns else None
                poro_val = float(ph_aq["Porosity"].median()) if "Porosity" in ph_aq.columns else None
                thick_val = float(ph_aq["Aquifer_thickness"].median()) if "Aquifer_thickness" in ph_aq.columns else None
                if perm_val is not None and poro_val is not None and thick_val is not None:
                    aquifer_score = calculate_aquifer_score(perm_val, poro_val, thick_val)

    # Temperature score (normalize surface temp 20-35 C as proxy)
    temp_score = _normalize(surface_temp_c, 20.0, 35.0) if surface_temp_c is not None else None

    # Fault density (simplified: assume one fault segment near municipality)
    fault_density = calculate_fault_density(5.0, municipality_area_km2) if fault_dist is not None else None

    # --- AHP-based MCDA scoring (Section 6.2 of plan) ---
    # Load dynamic weights from DB; fall back to defaults if unavailable
    try:
        from app.services.mcda_weights_service import get_weights
        ahp_weights = get_weights("geothermal")
    except Exception:
        ahp_weights = {
            "heat_flow": 0.30,
            "fault": 0.15,
            "volcano": 0.10,
            "aquifer": 0.15,
            "temperature": 0.10,
        }

    # Sub-scores (all 0-1)
    sub_scores = {
        "heat_flow": heat_flow_score or 0.0,
        "fault": math.exp(-(fault_dist if fault_dist is not None else 100) / 20.0),
        "volcano": math.exp(-(volcano_dist if volcano_dist is not None else 100) / 30.0),
        "aquifer": aquifer_score or 0.0,
        "temperature": temp_score or 0.0,
    }

    # Availability flags (1.0 if data exists, 0.0 otherwise)
    avail = {
        k: 1.0 if sub_scores[k] > 0 or (k == "fault" and fault_dist is not None) or (k == "volcano" and volcano_dist is not None) else 0.0
        for k in sub_scores
    }

    total_weight = sum(ahp_weights[k] * avail[k] for k in ahp_weights)
    if total_weight > 0:
        geothermal_score = sum(sub_scores[k] * ahp_weights[k] * avail[k] for k in ahp_weights) / total_weight
    else:
        geothermal_score = 0.0

    # Clamp and round
    geothermal_score = max(0.0, min(1.0, geothermal_score))

    # Classification
    if geothermal_score >= 0.80:
        classification = "High"
    elif geothermal_score >= 0.60:
        classification = "Good"
    elif geothermal_score >= 0.40:
        classification = "Moderate"
    else:
        classification = "Low"

    return {
        "heat_flow_score": round(heat_flow_score, 4) if heat_flow_score is not None else None,
        "fault_density": fault_density,
        "fault_distance_km": fault_dist,
        "volcano_distance_km": volcano_dist,
        "aquifer_score": round(aquifer_score, 4) if aquifer_score is not None else None,
        "temperature_score": round(temp_score, 4) if temp_score is not None else None,
        "geothermal_score": round(geothermal_score, 4),
        "classification": classification,
        "_heat_flow_mw_m2": round(heat_flow_val, 2) if heat_flow_val is not None else None,
        "_gradient_c_km": gradient,
        "_perm_log10": perm_val,
        "_porosity": poro_val,
        "_thickness_m": thick_val,
        "_basin_name": basin_name,
    }
```

**Explanation:** It accepts `muni_lat`, `muni_lon`, `surface_temp_c`, `datasets`, `municipality_area_km2`, `municipality_id` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `load_geothermal_datasets()`, `calculate_fault_distance()`, `get()`, `calculate_volcano_distance()`, `idw_heat_flow()`.

### `compute_geothermal_output`

- **File:** `fastapi-backend/app/services/geothermal/features.py`
- **Lines:** `623-707`
- **Signature:** `def compute_geothermal_output(`
- **Purpose:** Compute geothermal energy output for a municipality.

**Code:**
```python
def compute_geothermal_output(
    surface_temp_c: float | None,
    gradient_c_km: float | None,
    aquifer_score: float | None,
    permeability_log10_m2: float | None,
    depth_m: float = DEFAULT_RESERVOIR_DEPTH_M,
    plant_type: str = "binary",
) -> dict[str, Any]:
    """Compute geothermal energy output for a municipality.

    Uses physics-based formulas:
        Q = m * Cp * delta_T   (thermal power)
        P = Q * efficiency     (electric power)

    Args:
        surface_temp_c: NASA POWER surface temperature (C).
        gradient_c_km: Geothermal gradient (C/km).
        aquifer_score: Composite aquifer score (0-1).
        permeability_log10_m2: Log10 permeability (m2).
        depth_m: Estimated reservoir depth (m). Default 2000.
        plant_type: "binary" (0.12 eff) or "flash" (0.15 eff).

    Returns:
        Dict with thermal_power_mw, electric_power_mw, annual_energy_gwh,
        confidence_score, source, and assumption.
    """
    # Fallback: Philippine average surface temp when climate data is unavailable
    used_fallback_temp = False
    if surface_temp_c is None and gradient_c_km is not None:
        surface_temp_c = 27.0  # Philippine tropical average (C)
        used_fallback_temp = True

    reservoir_temp = calculate_reservoir_temperature(surface_temp_c, gradient_c_km, depth_m)
    flow_rate = estimate_flow_rate(aquifer_score, permeability_log10_m2)

    if reservoir_temp is None or flow_rate is None:
        return {
            "reservoir_temperature_c": None,
            "estimated_flow_rate_kg_s": None,
            "thermal_power_mw": None,
            "electric_power_mw": None,
            "annual_energy_gwh": None,
            "confidence_score": 0.0,
            "source": "Insufficient data",
            "assumption": "Missing measured heat flow or aquifer data for output estimation.",
        }

    delta_t = reservoir_temp - REINJECTION_TEMP_C
    if delta_t <= 0:
        delta_t = 1.0  # prevent zero/negative thermal power

    # Thermal power: Q = m_dot * Cp * delta_T  (Cp in kJ/kgC, convert to MW)
    # m_dot [kg/s] * Cp [kJ/kgC] * delta_T [C] = kJ/s = kW -> divide by 1000 for MW
    thermal_power_mw = (flow_rate * CP_KJ_KG_C * delta_t) / 1000.0

    efficiency = FLASH_EFFICIENCY if plant_type == "flash" else BINARY_EFFICIENCY
    electric_power_mw = thermal_power_mw * efficiency

    # Annual energy: MW * 8760 hours / 1000 = GWh
    annual_energy_gwh = (electric_power_mw * 8760.0) / 1000.0

    # Confidence based on data availability
    avail_heat = 1.0 if gradient_c_km is not None else 0.0
    avail_aq = 1.0 if aquifer_score is not None else 0.0
    avail_temp = 0.5 if used_fallback_temp else 1.0  # lower confidence if fallback
    confidence = (0.5 * avail_heat) + (0.3 * avail_aq) + (0.2 * avail_temp)
    confidence = round(min(1.0, confidence), 3)

    temp_note = "NASA POWER temperature (measured)" if not used_fallback_temp else "NASA POWER temperature unavailable; used Philippine average 27 C fallback"

    return {
        "reservoir_temperature_c": round(reservoir_temp, 2),
        "estimated_flow_rate_kg_s": round(flow_rate, 2),
        "thermal_power_mw": round(thermal_power_mw, 3),
        "electric_power_mw": round(electric_power_mw, 3),
        "annual_energy_gwh": round(annual_energy_gwh, 3),
        "confidence_score": confidence,
        "source": f"IHFC heat flow (measured), Zenodo aquifer properties (measured), {temp_note}.",
        "assumption": (
            f"Reservoir depth assumed {depth_m} m; "
            f"reinjection temperature {REINJECTION_TEMP_C} C; "
            f"plant type '{plant_type}' with efficiency {efficiency}. "
            f"Flow rate inferred from aquifer permeability when direct measurement unavailable."
        ),
    }
```

**Explanation:** It accepts `surface_temp_c`, `gradient_c_km`, `aquifer_score`, `permeability_log10_m2`, `depth_m`, `plant_type` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `calculate_reservoir_temperature()`, `estimate_flow_rate()`, `round()`, `min()`.


## `fastapi-backend/app/services/geothermal/ml_classifier.py`

**File:** `fastapi-backend/app/services/geothermal/ml_classifier.py`

**Summary:** Optional ML extension for geothermal classification.

### `fetch_training_data`

- **File:** `fastapi-backend/app/services/geothermal/ml_classifier.py`
- **Lines:** `27-71`
- **Signature:** `def fetch_training_data() -> tuple[list[dict[str, Any]], list[str]]:`
- **Purpose:** Load features and target from Supabase for all municipalities.

**Code:**
```python
def fetch_training_data() -> tuple[list[dict[str, Any]], list[str]]:
    """Load features and target from Supabase for all municipalities."""
    client = get_supabase_client()

    suit_resp = client.table("geothermal_suitability").select("*").limit(10000).execute()
    climate_resp = client.table("municipality_climate_monthly").select(
        "municipality_id,t2m"
    ).limit(10000).execute()
    hydro_resp = client.table("hydropower_suitability").select(
        "municipality_id,mean_elevation_m,mean_slope_deg"
    ).limit(10000).execute()

    suit_rows = {r["municipality_id"]: r for r in (suit_resp.data or [])}
    climate_rows = {r["municipality_id"]: r for r in (climate_resp.data or [])}
    hydro_rows = {r["municipality_id"]: r for r in (hydro_resp.data or [])}

    features: list[dict[str, float]] = []
    targets: list[str] = []

    for mid, row in suit_rows.items():
        cls = row.get("classification")
        if not cls:
            continue

        feat: dict[str, float] = {
            "heat_flow_score": float(row.get("heat_flow_score") or 0),
            "fault_distance_km": float(row.get("fault_distance_km") or 0),
            "fault_density": float(row.get("fault_density") or 0),
            "volcano_distance_km": float(row.get("volcano_distance_km") or 0),
            "aquifer_score": float(row.get("aquifer_score") or 0),
            "temperature_score": float(row.get("temperature_score") or 0),
            "geothermal_score": float(row.get("geothermal_score") or 0),
        }

        c = climate_rows.get(mid, {})
        feat["temperature"] = float(c.get("t2m") or 0)

        h = hydro_rows.get(mid, {})
        feat["elevation"] = float(h.get("mean_elevation_m") or 0)
        feat["slope"] = float(h.get("mean_slope_deg") or 0)

        features.append(feat)
        targets.append(cls)

    return features, targets
```

**Explanation:** It accepts zero arguments and returns `tuple[list[dict[str, Any]], list[str]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `limit()`, `select()`, `table()`.

### `train_model`

- **File:** `fastapi-backend/app/services/geothermal/ml_classifier.py`
- **Lines:** `74-119`
- **Signature:** `def train_model(features: list[dict[str, float]], targets: list[str]) -> dict[str, Any]:`
- **Purpose:** Train a RandomForestClassifier and return feature importance.

**Code:**
```python
def train_model(features: list[dict[str, float]], targets: list[str]) -> dict[str, Any]:
    """Train a RandomForestClassifier and return feature importance."""
    try:
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:
        logger.error("scikit-learn is not installed. Install it to use the ML extension.")
        return {"error": "scikit-learn not installed"}

    if not features or not targets:
        return {"error": "Insufficient training data"}

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    X = pd.DataFrame(features)
    y = pd.Series(targets)

    # Fill missing values with column median
    X = X.fillna(X.median())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    importance = dict(zip(X.columns, clf.feature_importances_.tolist()))
    importance = {k: round(v, 4) for k, v in sorted(importance.items(), key=lambda x: x[1], reverse=True)}

    return {
        "accuracy": round(acc, 4),
        "feature_importance": importance,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": list(clf.classes_),
    }
```

**Explanation:** It accepts `features`, `targets` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `error()`, `DataFrame()`, `Series()`, `fillna()`, `median()`.

### `main`

- **File:** `fastapi-backend/app/services/geothermal/ml_classifier.py`
- **Lines:** `122-128`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    logger.info("Fetching training data...")
    features, targets = fetch_training_data()
    logger.info("Loaded %d samples.", len(features))

    result = train_model(features, targets)
    print(json.dumps(result, indent=2))
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `info()`, `fetch_training_data()`, `len()`, `train_model()`, `dumps()`.


## `fastapi-backend/app/services/geothermal/plants.py`

**File:** `fastapi-backend/app/services/geothermal/plants.py`

**Summary:** Philippines geothermal power plant data loader and proximity utilities.

### `_haversine`

- **File:** `fastapi-backend/app/services/geothermal/plants.py`
- **Lines:** `30-40`
- **Signature:** `def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:`
- **Purpose:** Return distance between two lat/lon points in kilometres.

**Code:**
```python
def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance between two lat/lon points in kilometres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R_EARTH_KM * c
```

**Explanation:** It accepts `lat1`, `lon1`, `lat2`, `lon2` and returns `float`. See the code below for the full implementation. Key calls include `radians()`, `sin()`, `cos()`, `atan2()`, `sqrt()`.

### `_load_plants`

- **File:** `fastapi-backend/app/services/geothermal/plants.py`
- **Lines:** `43-71`
- **Signature:** `def _load_plants() -> list[dict[str, Any]]:`
- **Purpose:** Load the Philippines geothermal plant JSON once and cache it.

**Code:**
```python
def _load_plants() -> list[dict[str, Any]]:
    """Load the Philippines geothermal plant JSON once and cache it."""
    global _plants
    if _plants is not None:
        return _plants

    repo_root = Path(__file__).resolve().parents[4]
    json_path = (
        repo_root
        / "fastapi-backend"
        / "app"
        / "services"
        / "local_data"
        / "ph_geothermal_plants.json"
    )

    if not json_path.exists():
        logger.warning("Geothermal plant data not found at %s", json_path)
        _plants = []
        return _plants

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            _plants = json.load(f)
    except Exception as exc:
        logger.warning("Failed to load geothermal plant data: %s", exc)
        _plants = []

    return _plants
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `resolve()`, `Path()`, `exists()`, `warning()`, `open()`.

### `get_all_ph_geothermal_plants`

- **File:** `fastapi-backend/app/services/geothermal/plants.py`
- **Lines:** `74-76`
- **Signature:** `def get_all_ph_geothermal_plants() -> list[dict[str, Any]]:`
- **Purpose:** Return the full list of Philippines geothermal power plants.

**Code:**
```python
def get_all_ph_geothermal_plants() -> list[dict[str, Any]]:
    """Return the full list of Philippines geothermal power plants."""
    return _load_plants()
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_load_plants()`.

### `get_operating_plants`

- **File:** `fastapi-backend/app/services/geothermal/plants.py`
- **Lines:** `79-81`
- **Signature:** `def get_operating_plants() -> list[dict[str, Any]]:`
- **Purpose:** Return only plants with status == 'operating'.

**Code:**
```python
def get_operating_plants() -> list[dict[str, Any]]:
    """Return only plants with status == 'operating'."""
    return [p for p in _load_plants() if p.get("status") == "operating"]
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_load_plants()`, `get()`.

### `get_plants_near`

- **File:** `fastapi-backend/app/services/geothermal/plants.py`
- **Lines:** `84-103`
- **Signature:** `def get_plants_near(`
- **Purpose:** Return plants within *radius_km* of the given lat/lon.

**Code:**
```python
def get_plants_near(
    lat: float,
    lon: float,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM,
    only_operating: bool = True,
) -> list[dict[str, Any]]:
    """Return plants within *radius_km* of the given lat/lon.

    Each returned dict includes an extra key ``distance_km``.
    """
    plants = get_operating_plants() if only_operating else _load_plants()
    nearby = []
    for p in plants:
        d = _haversine(lat, lon, p["latitude"], p["longitude"])
        if d <= radius_km:
            entry = {**p, "distance_km": round(d, 2)}
            nearby.append(entry)
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby
```

**Explanation:** It accepts `lat`, `lon`, `radius_km`, `only_operating` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_operating_plants()`, `_load_plants()`, `_haversine()`, `append()`, `round()`.

### `calculate_proximity_boost`

- **File:** `fastapi-backend/app/services/geothermal/plants.py`
- **Lines:** `106-134`
- **Signature:** `def calculate_proximity_boost(`
- **Purpose:** Boost a geothermal suitability score based on proximity to operating plants.

**Code:**
```python
def calculate_proximity_boost(
    lat: float,
    lon: float,
    base_score: float,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM,
    max_bonus: float = 30.0,
) -> tuple[float, list[dict[str, Any]]]:
    """Boost a geothermal suitability score based on proximity to operating plants.

    The bonus is linearly tapered from *max_bonus* at 0 km down to 0 at *radius_km*.
    The final score is capped at 100.

    Returns:
        (boosted_score, nearby_plants)
    """
    nearby = get_plants_near(lat, lon, radius_km, only_operating=True)
    if not nearby:
        return base_score, []

    # Use the closest plant for the bonus calculation
    closest = nearby[0]
    distance = closest["distance_km"]

    # Linear taper: bonus = max_bonus * (1 - distance / radius_km)
    bonus = max_bonus * (1.0 - distance / radius_km)
    bonus = max(0.0, bonus)

    boosted = min(base_score + bonus, 100.0)
    return round(boosted, 2), nearby
```

**Explanation:** It accepts `lat`, `lon`, `base_score`, `radius_km`, `max_bonus` and returns `tuple[float, list[dict[str, Any]]]`. See the code below for the full implementation. Key calls include `get_plants_near()`, `max()`, `min()`, `round()`.


## `fastapi-backend/app/services/groq_client.py`

**File:** `fastapi-backend/app/services/groq_client.py`

**Summary:** Groq LLM client — free-tier alternative to Gemini.

### `_get_groq_client`

- **File:** `fastapi-backend/app/services/groq_client.py`
- **Lines:** `42-54`
- **Signature:** `def _get_groq_client() -> Any:`
- **Purpose:** Handles  get groq client.

**Code:**
```python
def _get_groq_client() -> Any:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY is not set")
            raise ValueError("GROQ_API_KEY is not set")
        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError("groq package is not installed. Run: pip install groq") from exc
        _groq_client = Groq(api_key=api_key)
    return _groq_client
```

**Explanation:** It accepts zero arguments and returns `Any`. See the code below for the full implementation. Key calls include `getenv()`, `Groq()`, `error()`, `ValueError()`, `ImportError()`.

### `generate_groq_response`

- **File:** `fastapi-backend/app/services/groq_client.py`
- **Lines:** `57-129`
- **Signature:** `def generate_groq_response(`
- **Purpose:** Generate a response from Groq with retry + model fallback.

**Code:**
```python
def generate_groq_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    max_retries: int = 3,
) -> str:
    """
    Generate a response from Groq with retry + model fallback.
    Forces JSON output via response_format.
    """
    client = _get_groq_client()
    model_name = model or DEFAULT_GROQ_MODEL
    temp_value = DEFAULT_TEMPERATURE if temperature is None else temperature
    token_limit = DEFAULT_MAX_TOKENS if max_tokens is None else max_tokens

    models_to_try = [model_name]
    for fallback in FALLBACK_GROQ_MODELS:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error: Exception | None = None

    for attempt_model in models_to_try:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("Groq attempt %s/%s on model=%s", attempt, max_retries, attempt_model)
                response = client.chat.completions.create(
                    model=attempt_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a friendly energy advisor speaking to a Filipino homeowner who has NO technical background. "
                                "You must always return valid JSON. Do not include markdown formatting, explanations, or anything outside the JSON object. "
                                "Rules for all text you generate inside the JSON:"
                                "\n- Use plain English. Avoid jargon. If you must use a technical term, explain it immediately in simple words."
                                "\n- Example: Instead of 'solar irradiance is 5.8 kWh/m²/day', say 'Your area gets plenty of sunlight — about 5.8 hours of strong sun each day, which is excellent for solar panels.'"
                                "\n- Example: Instead of 'capacity factor', say 'how efficiently the system runs compared to its best possible performance.'"
                                "\n- Always explain WHY something matters to the user's wallet or home."
                                "\n- Keep sentences short and conversational."
                                "\n- Use everyday comparisons: 'That's like leaving 10 light bulbs on all day.'"
                                "\n- Never assume the user knows what kWh, MW, GWh, or capacity factor mean."
                                "\n- If giving a number, always pair it with a plain-English interpretation."
                                "\n- The target audience includes teenagers and homeowners with zero engineering knowledge."
                            ),
                        },
                        {"role": "user", "content": content},
                    ],
                    temperature=temp_value,
                    max_tokens=token_limit,
                    response_format={"type": "json_object"},
                )
                text = response.choices[0].message.content or ""
                if text:
                    return text
                logger.warning("Groq returned empty content for model=%s", attempt_model)
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Groq model=%s attempt=%s failed: %s",
                    attempt_model,
                    attempt,
                    exc,
                )
                if attempt < max_retries:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    logger.warning("Groq model=%s exhausted retries.", attempt_model)

    raise last_error or RuntimeError("All Groq models failed")
```

**Explanation:** It accepts `content` and returns `str`. See the code below for the full implementation. Key calls include `_get_groq_client()`, `append()`, `range()`, `info()`, `create()`.


## `fastapi-backend/app/services/hydro_output_calc.py`

**File:** `fastapi-backend/app/services/hydro_output_calc.py`

**Summary:** Source file `fastapi-backend/app/services/hydro_output_calc.py`.

### `normalize`

- **File:** `fastapi-backend/app/services/hydro_output_calc.py`
- **Lines:** `6-11`
- **Signature:** `def normalize(value, min_value, max_value):`
- **Purpose:** Handles normalize.

**Code:**
```python
def normalize(value, min_value, max_value):
    if value is None:
        return 0.0
    if max_value == min_value:
        return 0.0
    return max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))
```

**Explanation:** It accepts `value`, `min_value`, `max_value`. See the code below for the full implementation. Key calls include `max()`, `min()`.

### `estimate_runoff_coefficient`

- **File:** `fastapi-backend/app/services/hydro_output_calc.py`
- **Lines:** `14-32`
- **Signature:** `def estimate_runoff_coefficient(slope_deg: float | None) -> float:`
- **Purpose:** Runoff coefficient for small catchments.

**Code:**
```python
def estimate_runoff_coefficient(slope_deg: float | None) -> float:
    """
    Runoff coefficient for small catchments.

    Based on terrain slope literature (Javadinejad et al., 2022):
    - Gentle slopes (<3°): C = 0.30 (forested/pasture)
    - Moderate slopes (3–10°): C = 0.45 (mixed land use)
    - Steep slopes (10–20°): C = 0.60 (cultivated/hilly)
    - Very steep (>20°): C = 0.75 (rocky/urban)
    """
    if slope_deg is None:
        return 0.45
    if slope_deg < 3:
        return 0.30
    if slope_deg < 10:
        return 0.45
    if slope_deg < 20:
        return 0.60
    return 0.75
```

**Explanation:** It accepts `slope_deg` and returns `float`. See the code below for the full implementation.

### `estimated_flow_rate`

- **File:** `fastapi-backend/app/services/hydro_output_calc.py`
- **Lines:** `35-97`
- **Signature:** `def estimated_flow_rate(`
- **Purpose:** Small-catchment runoff estimation for household micro-hydro.

**Code:**
```python
def estimated_flow_rate(
    rainfall_mm_monthly: float,
    runoff_potential: float,
    watershed_gradient: float,
    mean_slope_deg: float,
    gravity_flow_potential: float,
    catchment_area_km2: float = 0.5,
) -> float:
    """
    Small-catchment runoff estimation for household micro-hydro.

    Uses a rational-method inspired approach adapted for
    ungauged small catchments (Javadinejad et al., 2022):

        Q_design = (C × P × A) / seconds_month × design_factor

    where:
        C = runoff coefficient (0.30–0.75)
        P = monthly precipitation (m)
        A = catchment area (m²)
        design_factor = fraction of flow usable for power
                        (accounts for environmental reserve)

    Args:
        rainfall_mm_monthly: Monthly rainfall in mm (NASA POWER prectotcorr)
        runoff_potential: Terrain runoff potential (0–1)
        watershed_gradient: Watershed steepness proxy (0–1)
        mean_slope_deg: Mean terrain slope in degrees
        gravity_flow_potential: Gravity flow feasibility (0–1)
        catchment_area_km2: Small local catchment in km² (default 0.5)

    Returns:
        Design flow rate in m³/s suitable for a micro-hydro intake.
    """
    # Small-catchment area (m²) — typical household micro-hydro
    # draws from 0.05–1.0 km² (Butchers et al., 2021; Feyissa et al., 2024)
    catchment_area_m2 = catchment_area_km2 * 1_000_000

    # Monthly precipitation depth (m)
    monthly_precip_m = rainfall_mm_monthly / 1000.0

    # Base runoff coefficient from slope (Javadinejad et al., 2022)
    c_base = estimate_runoff_coefficient(mean_slope_deg)

    # Adjust by terrain suitability factors.
    # Runoff potential and watershed gradient moderate the coefficient.
    c_effective = c_base * (0.5 + 0.5 * runoff_potential) * (0.7 + 0.3 * watershed_gradient)

    # Total monthly runoff volume (m³)
    monthly_runoff_m3 = c_effective * monthly_precip_m * catchment_area_m2

    # Average flow over the month (m³/s)
    seconds_month = 30 * 24 * 3600  # ~30 days
    avg_flow_cms = monthly_runoff_m3 / seconds_month

    # Design flow = 40 % of average flow × gravity-flow feasibility.
    # 40–60 % environmental flow reserve is standard for run-of-river
    # (Wang et al., 2025; Lillo et al., 2021)
    design_flow_cms = avg_flow_cms * 0.40 * max(gravity_flow_potential, 0.1)

    # Realistic bounds for household micro-hydro intake.
    # Typical small streams: 0.001 – 0.5 m³/s (Butchers et al., 2021)
    return round(max(min(design_flow_cms, 0.5), 0.001), 6)
```

**Explanation:** It accepts `rainfall_mm_monthly`, `runoff_potential`, `watershed_gradient`, `mean_slope_deg`, `gravity_flow_potential`, `catchment_area_km2` and returns `float`. See the code below for the full implementation. Key calls include `estimate_runoff_coefficient()`, `max()`, `round()`, `min()`.

### `estimate_discharge`

- **File:** `fastapi-backend/app/services/hydro_output_calc.py`
- **Lines:** `100-123`
- **Signature:** `def estimate_discharge(`
- **Purpose:** Rational-method inspired runoff estimation.

**Code:**
```python
def estimate_discharge(
    rainfall_mm_monthly: float,
    basin_area_km2: float,
    runoff_coefficient: float,
) -> float:
    """
    Rational-method inspired runoff estimation.

    Q = (P × A × C) / seconds_month
    """
    monthly_precip_m = rainfall_mm_monthly / 1000.0

    basin_area_m2 = basin_area_km2 * 1_000_000
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    seconds_month = datetime.timedelta(days=days_in_month).total_seconds()

    q = (
        monthly_precip_m *
        basin_area_m2 *
        runoff_coefficient
    ) / seconds_month

    return max(q, 0.0)
```

**Explanation:** It accepts `rainfall_mm_monthly`, `basin_area_km2`, `runoff_coefficient` and returns `float`. See the code below for the full implementation. Key calls include `now()`, `monthrange()`, `total_seconds()`, `timedelta()`, `max()`.

### `calculate_hydropower`

- **File:** `fastapi-backend/app/services/hydro_output_calc.py`
- **Lines:** `126-198`
- **Signature:** `def calculate_hydropower(`
- **Purpose:** Micro-hydropower output calculation.

**Code:**
```python
def calculate_hydropower(
    days_in_month: int,
    flow_rate_cms: float,
    head_m: float,
    water_density: float = 1000.0,
    gravity: float = 9.81,
    turbine_efficiency: float = 0.75,
    generator_efficiency: float = 0.90,
):
    """
    Micro-hydropower output calculation.

    P_elec = η_turbine × η_generator × ρ × g × Q × H

    Standard hydropower equation for run-of-river micro-hydro
    (Feyissa et al., 2024; Wang et al., 2025).

    Args:
        days_in_month: Days in current month
        flow_rate_cms: Design flow rate (m³/s)
        head_m: Hydraulic head (m) — DEM-derived municipal elevation drop
        water_density: 1000 kg/m³
        gravity: 9.81 m/s²
        turbine_efficiency: 0.70–0.85 for micro-hydro turbines
        generator_efficiency: 0.85–0.95

    Returns:
        Dict with available_power_kw, daily_energy_kwh, monthly_energy_kwh,
        hydro_score, design_flow_cms, and realistic_head_m.
    """
    # Realistic bounds for household micro-hydro.
    # Typical run-of-river micro-hydro: 0.001 – 0.5 m³/s
    # (Butchers et al., 2021; Lillo et al., 2021)
    flow_rate_cms = min(max(flow_rate_cms, 0.0), 0.5)

    # Realistic household-accessible head.
    # DEM-derived municipal head is scaled to a local intake-to-turbine drop.
    # Typical micro-hydro head: 2–25 m (Feyissa et al., 2024).
    # We assume only ~12 % of maximum municipal elevation drop is usable
    # for a single household run-of-river scheme.
    realistic_head_m = min(max(head_m * 0.12, 2.0), 25.0)

    # Hydraulic power (kW) = ρ × g × Q × H / 1000
    hydraulic_power_kw = (
        water_density * gravity * flow_rate_cms * realistic_head_m
    ) / 1000.0

    # Overall efficiency = turbine × generator.
    # Micro-hydro systems typically achieve 0.50–0.70 overall
    # (Feyissa et al., 2024; Wang et al., 2025)
    overall_efficiency = turbine_efficiency * generator_efficiency

    # Electrical power output (kW)
    electrical_power_kw = hydraulic_power_kw * overall_efficiency

    # Daily and monthly energy (kWh)
    daily_energy = electrical_power_kw * 24.0
    monthly_energy = daily_energy * days_in_month

    # Hydro suitability score (0–100).
    # Normalise against a realistic "excellent" micro-hydro output
    # of ~1 000 kWh/month for a household system.
    # (Feyissa et al., 2024 report 500–2 000 kWh/month for rural homes)
    hydro_score = normalize(monthly_energy, 0, 1000) * 100

    return {
        "available_power_kw": round(electrical_power_kw, 3),
        "daily_energy_kwh": round(daily_energy, 3),
        "monthly_energy_kwh": round(monthly_energy, 3),
        "hydro_score": round(hydro_score, 2),
        "design_flow_cms": round(flow_rate_cms, 6),
        "realistic_head_m": round(realistic_head_m, 2),
    }
```

**Explanation:** It accepts `days_in_month`, `flow_rate_cms`, `head_m`, `water_density`, `gravity`, `turbine_efficiency`, `generator_efficiency`. See the code below for the full implementation. Key calls include `min()`, `max()`, `normalize()`, `round()`.


## `fastapi-backend/app/services/llm_client.py`

**File:** `fastapi-backend/app/services/llm_client.py`

**Summary:** Unified LLM client.

### `generate_response`

- **File:** `fastapi-backend/app/services/llm_client.py`
- **Lines:** `28-79`
- **Signature:** `def generate_response(`
- **Purpose:** Generate a response from the configured LLM provider.

**Code:**
```python
def generate_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    max_retries: int = 3,
) -> str:
    """
    Generate a response from the configured LLM provider.

    Drop-in replacement for ``generate_gemini_response``.

    If the configured provider is Gemini and *all* Gemini models fail,
    we automatically fall back to Groq when GROQ_API_KEY is present.
    """
    if LLM_PROVIDER == "groq":
        from app.services.groq_client import generate_groq_response
        return generate_groq_response(
            content,
            model=model,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
        )

    # Default: Gemini (with built-in retry + model fallback)
    from app.services.gemini_funcs import generate_gemini_response
    try:
        return generate_gemini_response(
            content,
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            max_retries=max_retries,
        )
    except Exception:
        # All Gemini models failed — try Groq as emergency fallback
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            logger.warning(
                "All Gemini models failed; falling back to Groq emergency path."
            )
            from app.services.groq_client import generate_groq_response
            return generate_groq_response(
                content,
                model=None,
                temperature=temperature,
                max_tokens=max_output_tokens,
                max_retries=max_retries,
            )
        raise
```

**Explanation:** It accepts `content` and returns `str`. See the code below for the full implementation. Key calls include `generate_groq_response()`, `generate_gemini_response()`, `getenv()`, `warning()`.

### `parse_json_response`

- **File:** `fastapi-backend/app/services/llm_client.py`
- **Lines:** `82-96`
- **Signature:** `def parse_json_response(text: str) -> dict[str, Any]:`
- **Purpose:** Parse a JSON response — works for both Gemini and Groq.

**Code:**
```python
def parse_json_response(text: str) -> dict[str, Any]:
    """Parse a JSON response — works for both Gemini and Groq."""
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON block from LLM response")
        return {}
```

**Explanation:** It accepts `text` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `loads()`, `search()`, `group()`, `warning()`.


## `fastapi-backend/app/services/llm_sanitizer.py`

**File:** `fastapi-backend/app/services/llm_sanitizer.py`

**Summary:** LLM output sanitization utilities.

### `strip_markdown_fences`

- **File:** `fastapi-backend/app/services/llm_sanitizer.py`
- **Lines:** `17-29`
- **Signature:** `def strip_markdown_fences(text: str) -> str:`
- **Purpose:** Remove ```json ... ``` or ``` ... ``` wrappers.

**Code:**
```python
def strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers."""
    if not text:
        return ""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `startswith()`, `splitlines()`, `join()`.

### `strip_json_wrappers`

- **File:** `fastapi-backend/app/services/llm_sanitizer.py`
- **Lines:** `32-45`
- **Signature:** `def strip_json_wrappers(text: str) -> str:`
- **Purpose:** If the whole text is a JSON object, extract the most narrative value.

**Code:**
```python
def strip_json_wrappers(text: str) -> str:
    """If the whole text is a JSON object, extract the most narrative value."""
    if not text:
        return ""
    text = text.strip()
    if text.startswith(("{", "[")) and text.endswith(("}", "]")):
        try:
            parsed = json.loads(text)
            extracted = _extract_text(parsed)
            if extracted and len(extracted) > 20:
                return extracted
        except json.JSONDecodeError:
            pass
    return text
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `startswith()`, `endswith()`, `loads()`, `_extract_text()`.

### `strip_key_value_formatting`

- **File:** `fastapi-backend/app/services/llm_sanitizer.py`
- **Lines:** `48-67`
- **Signature:** `def strip_key_value_formatting(text: str) -> str:`
- **Purpose:** Remove lines that look like JSON keys or bullet-point key-value pairs.

**Code:**
```python
def strip_key_value_formatting(text: str) -> str:
    """Remove lines that look like JSON keys or bullet-point key-value pairs."""
    if not text:
        return ""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just JSON keys like "summary": "..."
        if re.match(r'^"?\w+"?\s*:\s*"', stripped):
            # Extract the value part after the colon+quote
            match = re.search(r':\s*"(.*)"\s*,?\s*$', stripped)
            if match:
                cleaned.append(match.group(1))
            continue
        # Skip lines that are just structural JSON symbols
        if stripped in ("{", "}", "[", "]", "}", "{"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `splitlines()`, `strip()`, `match()`, `append()`, `search()`.

### `normalize_whitespace`

- **File:** `fastapi-backend/app/services/llm_sanitizer.py`
- **Lines:** `70-93`
- **Signature:** `def normalize_whitespace(text: str) -> str:`
- **Purpose:** Collapse multiple blank lines, strip leading/trailing whitespace.

**Code:**
```python
def normalize_whitespace(text: str) -> str:
    """Collapse multiple blank lines, strip leading/trailing whitespace."""
    if not text:
        return ""
    text = text.replace("\\n", "\n").replace("\\t", "\t")
    # Remove outer quotes if the whole thing is a quoted string
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            text = text[1:-1]
    # Collapse multiple blank lines to one
    lines = text.splitlines()
    result = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return "\n".join(result).strip()
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `replace()`, `startswith()`, `endswith()`, `loads()`, `splitlines()`.

### `_extract_text`

- **File:** `fastapi-backend/app/services/llm_sanitizer.py`
- **Lines:** `96-118`
- **Signature:** `def _extract_text(obj: Any) -> str:`
- **Purpose:** Recursively extract narrative text from parsed JSON.

**Code:**
```python
def _extract_text(obj: Any) -> str:
    """Recursively extract narrative text from parsed JSON."""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, list):
        parts = [_extract_text(item) for item in obj if item is not None]
        return "\n\n".join(p for p in parts if p)
    if isinstance(obj, dict):
        for key in (
            "observation", "interpretation", "recommendation", "reason",
            "analysis", "insight", "explanation", "response", "text",
            "content", "result", "answer", "narrative", "summary",
        ):
            if key in obj:
                return _extract_text(obj[key])
        # Fallback: concatenate all values
        parts = []
        for v in obj.values():
            extracted = _extract_text(v)
            if extracted:
                parts.append(extracted)
        return "\n\n".join(parts)
    return str(obj) if obj is not None else ""
```

**Explanation:** It accepts `obj` and returns `str`. See the code below for the full implementation. Key calls include `isinstance()`, `strip()`, `join()`, `_extract_text()`, `values()`.

### `sanitize_llm_output`

- **File:** `fastapi-backend/app/services/llm_sanitizer.py`
- **Lines:** `121-129`
- **Signature:** `def sanitize_llm_output(text: str) -> str:`
- **Purpose:** Full sanitization pipeline: fences → JSON wrappers → key-value → whitespace.

**Code:**
```python
def sanitize_llm_output(text: str) -> str:
    """Full sanitization pipeline: fences → JSON wrappers → key-value → whitespace."""
    if not text:
        return ""
    text = strip_markdown_fences(text)
    text = strip_json_wrappers(text)
    text = strip_key_value_formatting(text)
    text = normalize_whitespace(text)
    return text
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `strip_markdown_fences()`, `strip_json_wrappers()`, `strip_key_value_formatting()`, `normalize_whitespace()`.

### `extract_prescriptive_recommendation`

- **File:** `fastapi-backend/app/services/llm_sanitizer.py`
- **Lines:** `132-166`
- **Signature:** `def extract_prescriptive_recommendation(text: str) -> dict[str, str]:`
- **Purpose:** Extract the 4-part prescriptive structure from LLM text.

**Code:**
```python
def extract_prescriptive_recommendation(text: str) -> dict[str, str]:
    """Extract the 4-part prescriptive structure from LLM text.

    Returns:
        dict with keys: observation, interpretation, recommendation, reason
    """
    result = {
        "observation": "",
        "interpretation": "",
        "recommendation": "",
        "reason": "",
    }
    if not text:
        return result

    text = sanitize_llm_output(text)

    # Try to find sections by heading patterns (supports markdown ## headers)
    patterns = {
        "observation": r"(?:##?\s*)?(?:Observation|OBSERVATION|What the data shows)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Interpretation|INTERPRETATION|What this means)|$)",
        "interpretation": r"(?:##?\s*)?(?:Interpretation|INTERPRETATION|What this means)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Recommendation|RECOMMENDATION|What to consider)|$)",
        "recommendation": r"(?:##?\s*)?(?:Recommendation|RECOMMENDATION|What to consider|Suggested action)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Reason|REASON|Why|Rationale)|$)",
        "reason": r"(?:##?\s*)?(?:Reason|REASON|Why|Rationale)[\s:]*\n?(.*?)$",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            result[key] = match.group(1).strip()

    # Fallback: if no sections found, put everything in recommendation
    if not any(result.values()):
        result["recommendation"] = text

    return result
```

**Explanation:** It accepts `text` and returns `dict[str, str]`. See the code below for the full implementation. Key calls include `sanitize_llm_output()`, `items()`, `search()`, `strip()`, `group()`.


## `fastapi-backend/app/services/map_service.py`

**File:** `fastapi-backend/app/services/map_service.py`

**Summary:** Map data service for LUMI GIS/mapping.

### `validate_wgs84`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `62-89`
- **Signature:** `def validate_wgs84(lat: float, lon: float) -> bool:`
- **Purpose:** Validate that coordinates are within WGS84 (EPSG:4326) bounds.

**Code:**
```python
def validate_wgs84(lat: float, lon: float) -> bool:
    """Validate that coordinates are within WGS84 (EPSG:4326) bounds.

    Philippine bounds: lat [4.5, 21.5], lon [116.0, 127.0]
    """
    if lat is None or lon is None:
        return False
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return False

    # Global WGS84 bounds
    if not (-90 <= lat_f <= 90):
        return False
    if not (-180 <= lon_f <= 180):
        return False

    # Philippine bounds (with small margin)
    if not (4.0 <= lat_f <= 22.0):
        logger.warning("Latitude %s outside Philippine bounds", lat_f)
        return False
    if not (115.0 <= lon_f <= 128.0):
        logger.warning("Longitude %s outside Philippine bounds", lon_f)
        return False

    return True
```

**Explanation:** It accepts `lat`, `lon` and returns `bool`. See the code below for the full implementation. Key calls include `float()`, `warning()`.

### `_format_score`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `96-102`
- **Signature:** `def _format_score(score: Any) -> float:`
- **Purpose:** Scale normalized (0-1) scores to 0-100; leave percentage scores as-is.

**Code:**
```python
def _format_score(score: Any) -> float:
    """Scale normalized (0-1) scores to 0-100; leave percentage scores as-is."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return 0.0
    return round(s * 100, 2) if s <= 1.0 else round(s, 2)
```

**Explanation:** It accepts `score` and returns `float`. See the code below for the full implementation. Key calls include `float()`, `round()`.

### `_aggregate_to_province`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `105-150`
- **Signature:** `def _aggregate_to_province(`
- **Purpose:** Group municipality scores by province and average them.

**Code:**
```python
def _aggregate_to_province(
    client,
    municipality_rows: list[dict[str, Any]],
    renewable_type: str,
) -> list[dict[str, Any]]:
    """Group municipality scores by province and average them."""
    province_scores: dict[int, list[float]] = {}
    for row in municipality_rows:
        pid = row.get("province_id")
        if pid is None:
            continue
        pid = int(pid)
        province_scores.setdefault(pid, []).append(float(row["score"]))

    if not province_scores:
        return []

    try:
        resp = client.table("provinces").select("province_id,name,lat,lon").limit(50000).execute()
        province_lookup = {
            p["province_id"]: p for p in (resp.data or []) if p.get("province_id") is not None
        }
    except Exception as exc:
        logger.warning("Failed to fetch provinces for aggregation: %s", exc)
        return []

    result = []
    for pid, scores in province_scores.items():
        prov = province_lookup.get(pid)
        if not prov:
            continue
        lat = prov.get("lat")
        lon = prov.get("lon")
        if not (lat and lon and validate_wgs84(float(lat), float(lon))):
            continue
        result.append({
            "geo_id": pid,
            "name": prov.get("name"),
            "lat": float(lat),
            "lon": float(lon),
            "score": round(sum(scores) / len(scores), 2),
            "renewable_type": renewable_type,
            "level": "province",
            "province_id": None,
        })
    return result
```

**Explanation:** It accepts `client`, `municipality_rows`, `renewable_type` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get()`, `int()`, `append()`, `float()`, `setdefault()`.

### `_fetch_municipality_scores`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `153-241`
- **Signature:** `def _fetch_municipality_scores(`
- **Purpose:** Return municipality-level rows with name, lat, lon, score, and province_id.

**Code:**
```python
def _fetch_municipality_scores(
    client,
    renewable_type: str,
) -> list[dict[str, Any]]:
    """Return municipality-level rows with name, lat, lon, score, and province_id."""
    score_source = {
        "solar": (None, "solar_suitability_score"),
        "wind": (None, "wind_suitability_score"),
        "hydro": ("hydropower_suitability", "hydro_suitability_score"),
        "geothermal": ("geothermal_suitability", "geothermal_score"),
    }.get(renewable_type)

    if not score_source:
        logger.warning("Unknown renewable type: %s", renewable_type)
        return []

    suit_table, score_col = score_source

    if suit_table is None:
        # solar / wind: scores live directly on the municipalities table
        resp = client.table("municipalities").select(
            f"municipality_id,name,lat,lon,province_id,{score_col}"
        ).limit(50000).execute()
        rows = resp.data or []
        result = []
        for r in rows:
            score = r.get(score_col)
            lat = r.get("lat")
            lon = r.get("lon")
            if score is None or lat is None or lon is None:
                continue
            if not validate_wgs84(float(lat), float(lon)):
                continue
            result.append({
                "geo_id": r.get("municipality_id"),
                "name": r.get("name"),
                "lat": float(lat),
                "lon": float(lon),
                "score": _format_score(score),
                "renewable_type": renewable_type,
                "level": "municipality",
                "province_id": r.get("province_id"),
            })
        return result

    # hydro / geothermal: separate source table, joined to municipalities
    suit_resp = client.table(suit_table).select(
        f"municipality_id,{score_col}"
    ).limit(50000).execute()
    suit_rows = {
        r.get("municipality_id"): r.get(score_col)
        for r in (suit_resp.data or [])
        if r.get(score_col) is not None
    }

    if not suit_rows:
        return []

    muni_resp = client.table("municipalities").select(
        "municipality_id,name,lat,lon,province_id"
    ).limit(50000).execute()
    muni_lookup = {
        r.get("municipality_id"): r
        for r in (muni_resp.data or [])
        if r.get("municipality_id") is not None
    }

    result = []
    for muni_id, score in suit_rows.items():
        muni = muni_lookup.get(muni_id)
        if not muni:
            continue
        lat = muni.get("lat")
        lon = muni.get("lon")
        if lat is None or lon is None:
            continue
        if not validate_wgs84(float(lat), float(lon)):
            continue
        result.append({
            "geo_id": muni_id,
            "name": muni.get("name"),
            "lat": float(lat),
            "lon": float(lon),
            "score": _format_score(score),
            "renewable_type": renewable_type,
            "level": "municipality",
            "province_id": muni.get("province_id"),
        })
    return result
```

**Explanation:** It accepts `client`, `renewable_type` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get()`, `warning()`, `execute()`, `append()`, `limit()`.

### `get_map_data`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `244-281`
- **Signature:** `def get_map_data(`
- **Purpose:** Fetch map data (suitability scores + centroids) for a renewable type.

**Code:**
```python
def get_map_data(
    renewable_type: str,
    level: str = "municipality",
    use_cache: bool = True,
    use_materialized_view: bool = True,
) -> list[dict[str, Any]]:
    """Fetch map data (suitability scores + centroids) for a renewable type.

    Uses the actual Supabase schema:
    - solar/wind scores are columns on municipalities
    - hydro scores are in hydropower_suitability
    - geothermal scores are in geothermal_suitability
    """
    normalized_level = (level or "municipality").split(":")[0].lower().strip()
    if normalized_level not in {"municipality", "province"}:
        normalized_level = "municipality"

    if use_cache:
        cached = get_suitability_cache_sync(renewable_type, normalized_level)
        if cached:
            return cached

    try:
        client = get_supabase_client()
        municipality_rows = _fetch_municipality_scores(client, renewable_type)

        if normalized_level == "province":
            data = _aggregate_to_province(client, municipality_rows, renewable_type)
        else:
            data = municipality_rows

        if use_cache and data:
            set_suitability_cache_sync(renewable_type, normalized_level, data)
        return data

    except Exception as exc:
        logger.warning("Map data fetch failed for %s/%s: %s", renewable_type, normalized_level, exc)
        return []
```

**Explanation:** It accepts `renewable_type`, `level`, `use_cache`, `use_materialized_view` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `strip()`, `lower()`, `split()`, `get_suitability_cache_sync()`, `get_supabase_client()`.

### `_fetch_from_materialized_view`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `284-332`
- **Signature:** `def _fetch_from_materialized_view(`
- **Purpose:** Fetch from materialized view (mv_municipality_map_data or mv_province_map_data).

**Code:**
```python
def _fetch_from_materialized_view(
    renewable_type: str,
    level: str,
) -> list[dict[str, Any]]:
    """Fetch from materialized view (mv_municipality_map_data or mv_province_map_data).

    These views join admin boundaries with suitability scores and centroids.
    """
    mv_table = _MV_TABLES.get(level)
    if not mv_table:
        return []

    score_col_map = {
        "solar": "solar_score",
        "wind": "wind_score",
        "hydro": "hydro_score",
        "geothermal": "geothermal_score",
    }
    score_col = score_col_map.get(renewable_type)
    if not score_col:
        return []

    client = get_supabase_client()
    try:
        # Select all columns from the MV
        resp = (
            client.table(mv_table)
            .select(f"*")
            .limit(50000)
            .execute()
        )
        rows = resp.data or []

        # Filter to rows where the relevant score is not null
        filtered = [r for r in rows if r.get(score_col) is not None]

        # Validate coordinates
        result = []
        for r in filtered:
            lat = r.get("lat") or r.get("centroid_lat")
            lon = r.get("lon") or r.get("centroid_lon")
            if lat and lon and validate_wgs84(float(lat), float(lon)):
                result.append(r)

        return result

    except Exception as exc:
        logger.warning("Materialized view fetch failed for %s/%s: %s", renewable_type, level, exc)
        return []
```

**Explanation:** It accepts `renewable_type`, `level` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get()`, `get_supabase_client()`, `execute()`, `warning()`, `limit()`.

### `_fetch_from_table_join`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `335-420`
- **Signature:** `def _fetch_from_table_join(`
- **Purpose:** Fetch map data by joining admin table with suitability table.

**Code:**
```python
def _fetch_from_table_join(
    renewable_type: str,
    level: str,
) -> list[dict[str, Any]]:
    """Fetch map data by joining admin table with suitability table.

    Fallback when materialized views are not available or empty.
    """
    suit_info = _SUITABILITY_TABLES.get(renewable_type)
    if not suit_info:
        logger.warning("Unknown renewable type: %s", renewable_type)
        return []

    suit_table = suit_info["table"]
    score_col = suit_info["score_col"]
    id_col = suit_info["id_col"]

    if level == "province":
        admin_table = "provinces"
        admin_pk = "province_id"
        select_cols = f"{admin_pk},name,lat,lon"
    else:
        admin_table = "municipalities"
        admin_pk = "municipality_id"
        select_cols = f"{admin_pk},name,lat,lon,province_id"

    client = get_supabase_client()

    try:
        # Fetch admin units with lat/lon
        admin_resp = (
            client.table(admin_table)
            .select(select_cols)
            .limit(50000)
            .execute()
        )
        admin_rows = admin_resp.data or []
        if not admin_rows:
            return []

        # Fetch suitability scores
        suit_resp = (
            client.table(suit_table)
            .select(f"{id_col},{score_col}")
            .limit(50000)
            .execute()
        )
        suit_rows = suit_resp.data or []

        # Build score lookup
        score_lookup: dict[int, float] = {}
        for row in suit_rows:
            geo_id = row.get(id_col)
            score = row.get(score_col)
            if geo_id is not None and score is not None:
                score_lookup[int(geo_id)] = float(score)

        # Join
        result = []
        for row in admin_rows:
            geo_id = row.get(admin_pk)
            lat = row.get("lat")
            lon = row.get("lon")
            score = score_lookup.get(int(geo_id)) if geo_id else None

            if score is None:
                continue
            if not (lat and lon and validate_wgs84(float(lat), float(lon))):
                continue

            result.append({
                "geo_id": geo_id,
                "name": row.get("name"),
                "lat": float(lat),
                "lon": float(lon),
                "score": round(score * 100, 2) if score <= 1.0 else round(score, 2),
                "renewable_type": renewable_type,
                "level": level,
                "province_id": row.get("province_id") if level == "municipality" else None,
            })

        return result

    except Exception as exc:
        logger.warning("Table join fetch failed for %s/%s: %s", renewable_type, level, exc)
        return []
```

**Explanation:** It accepts `renewable_type`, `level` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get()`, `warning()`, `get_supabase_client()`, `execute()`, `append()`.

### `get_psgc_hierarchy`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `427-521`
- **Signature:** `def get_psgc_hierarchy(`
- **Purpose:** Fetch PSGC administrative hierarchy for a given unit.

**Code:**
```python
def get_psgc_hierarchy(
    municipality_id: int | None = None,
    province_id: int | None = None,
) -> dict[str, Any]:
    """Fetch PSGC administrative hierarchy for a given unit.

    Returns the full chain: region → province → municipality → barangays

    Args:
        municipality_id: Optional municipality ID
        province_id: Optional province ID

    Returns:
        Dict with hierarchy levels and metadata
    """
    client = get_supabase_client()
    hierarchy: dict[str, Any] = {}

    try:
        if municipality_id:
            # Fetch municipality with province and region
            resp = (
                client.table("municipalities")
                .select("municipality_id,name,lat,lon,provinces(province_id,name,regions(region_id,name))")
                .eq("municipality_id", str(municipality_id))
                .single()
                .execute()
            )
            if resp.data:
                muni = resp.data
                prov = muni.get("provinces") or {}
                region = prov.get("regions") or {}

                hierarchy["municipality"] = {
                    "id": muni.get("municipality_id"),
                    "name": muni.get("name"),
                    "lat": muni.get("lat"),
                    "lon": muni.get("lon"),
                }
                hierarchy["province"] = {
                    "id": prov.get("province_id"),
                    "name": prov.get("name"),
                }
                hierarchy["region"] = {
                    "id": region.get("region_id"),
                    "name": region.get("name"),
                }

                # Fetch barangays
                brgy_resp = (
                    client.table("barangays")
                    .select("barangay_id,name,lat,lon")
                    .eq("municipality_id", str(municipality_id))
                    .order("name")
                    .execute()
                )
                hierarchy["barangays"] = brgy_resp.data or []

        elif province_id:
            resp = (
                client.table("provinces")
                .select("province_id,name,lat,lon,regions(region_id,name)")
                .eq("province_id", str(province_id))
                .single()
                .execute()
            )
            if resp.data:
                prov = resp.data
                region = prov.get("regions") or {}

                hierarchy["province"] = {
                    "id": prov.get("province_id"),
                    "name": prov.get("name"),
                    "lat": prov.get("lat"),
                    "lon": prov.get("lon"),
                }
                hierarchy["region"] = {
                    "id": region.get("region_id"),
                    "name": region.get("name"),
                }

                # Fetch municipalities
                muni_resp = (
                    client.table("municipalities")
                    .select("municipality_id,name,lat,lon")
                    .eq("province_id", str(province_id))
                    .order("name")
                    .execute()
                )
                hierarchy["municipalities"] = muni_resp.data or []

    except Exception as exc:
        logger.warning("PSGC hierarchy fetch failed: %s", exc)

    return hierarchy
```

**Explanation:** It accepts `municipality_id`, `province_id` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `warning()`, `single()`, `get()`.

### `get_coverage_summary`

- **File:** `fastapi-backend/app/services/map_service.py`
- **Lines:** `528-574`
- **Signature:** `def get_coverage_summary(level: str = "municipality") -> dict[str, Any]:`
- **Purpose:** Fetch data coverage summary for a given admin level.

**Code:**
```python
def get_coverage_summary(level: str = "municipality") -> dict[str, Any]:
    """Fetch data coverage summary for a given admin level.

    Returns counts of units with/without climate data, suitability scores, etc.
    """
    normalized_level = (level or "municipality").split(":")[0].lower().strip()
    if normalized_level not in {"municipality", "province"}:
        normalized_level = "municipality"

    client = get_supabase_client()

    # Try a pre-computed coverage_summary table first
    try:
        resp = (
            client.table("coverage_summary")
            .select("*")
            .eq("level", normalized_level)
            .execute()
        )
        rows = resp.data or []
        if rows:
            return {"level": normalized_level, "items": rows}
    except Exception as exc:
        logger.warning("Pre-computed coverage_summary not available: %s", exc)

    # Fallback: compute on-the-fly for municipalities
    if normalized_level == "municipality":
        try:
            total_resp = client.table("municipalities").select("municipality_id", count="exact").execute()
            total = getattr(total_resp, "count", None) or len(total_resp.data or [])

            climate_resp = client.table("municipalities").select(
                "municipality_id,municipality_climate_monthly!inner(municipality_id)",
                count="exact",
            ).execute()
            with_climate = getattr(climate_resp, "count", None) or len(climate_resp.data or [])

            return {
                "level": normalized_level,
                "total_units": total,
                "with_climate_data": with_climate,
                "coverage_pct": round(with_climate / total * 100, 1) if total else 0,
            }
        except Exception as exc:
            logger.warning("Coverage on-the-fly count failed: %s", exc)

    return {"level": normalized_level, "items": []}
```

**Explanation:** It accepts `level` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `strip()`, `lower()`, `split()`, `get_supabase_client()`, `execute()`.


## `fastapi-backend/app/services/mcda.py`

**File:** `fastapi-backend/app/services/mcda.py`

**Summary:** MCDA module for LUMI — AHP weight validation and PROMETHEE ranking.

### `ahp_consistency_ratio`

- **File:** `fastapi-backend/app/services/mcda.py`
- **Lines:** `16-60`
- **Signature:** `def ahp_consistency_ratio(matrix: list[list[float]]) -> dict[str, Any]:`
- **Purpose:** Check AHP pairwise comparison matrix consistency.

**Code:**
```python
def ahp_consistency_ratio(matrix: list[list[float]]) -> dict[str, Any]:
    """Check AHP pairwise comparison matrix consistency.

    Args:
        matrix: NxN pairwise comparison matrix (Saaty scale 1-9)

    Returns:
        Dict with consistency_ratio, is_consistent, lambda_max, n
    """
    n = len(matrix)
    if n < 2:
        return {"consistency_ratio": 0.0, "is_consistent": True, "lambda_max": float(n), "n": n}

    # Calculate priority vector (eigenvector approximation)
    col_sums = [sum(matrix[i][j] for i in range(n)) for j in range(n)]
    normalized = [
        [matrix[i][j] / col_sums[j] if col_sums[j] > 0 else 0 for j in range(n)]
        for i in range(n)
    ]
    priority = [sum(normalized[i]) / n for i in range(n)]

    # Calculate lambda_max
    weighted_sums = [
        sum(matrix[i][j] * priority[j] for j in range(n))
        for i in range(n)
    ]
    lambda_max = sum(weighted_sums[i] / priority[i] for i in range(n) if priority[i] > 0) / n

    # Consistency index
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0

    # Random consistency index (Saaty)
    rci_table = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    rci = rci_table.get(n, 1.49)

    cr = ci / rci if rci > 0 else 0.0

    return {
        "consistency_ratio": round(cr, 4),
        "is_consistent": cr < 0.10,
        "lambda_max": round(lambda_max, 4),
        "consistency_index": round(ci, 4),
        "n": n,
        "priority_vector": [round(p, 4) for p in priority],
    }
```

**Explanation:** It accepts `matrix` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `len()`, `float()`, `sum()`, `range()`, `get()`.

### `aggregate_score`

- **File:** `fastapi-backend/app/services/mcda.py`
- **Lines:** `63-123`
- **Signature:** `def aggregate_score(`
- **Purpose:** Aggregate criteria scores into a single suitability score using weighted sum.

**Code:**
```python
def aggregate_score(
    criteria_scores: dict[str, float],
    weights: dict[str, float] | None = None,
    energy_type: str = "",
    client=None,
) -> dict[str, Any]:
    """Aggregate criteria scores into a single suitability score using weighted sum.

    Args:
        criteria_scores: Dict mapping criterion name to score (0-100)
        weights: Optional weight dict. If None, loads from DB/defaults.
        energy_type: Energy type for loading default weights
        client: Optional Supabase client

    Returns:
        Dict with aggregated_score, classification, weights_used, contributions
    """
    if weights is None:
        weights = get_weights(energy_type, client) if energy_type else {}

    if not weights:
        # Equal weights fallback
        keys = list(criteria_scores.keys())
        weights = {k: 1.0 / len(keys) for k in keys} if keys else {}

    # Normalize weights to sum to 1
    total_weight = sum(weights.values())
    if total_weight > 0:
        norm_weights = {k: v / total_weight for k, v in weights.items()}
    else:
        norm_weights = weights

    # Calculate weighted score
    contributions = {}
    weighted_sum = 0.0
    for criterion, score in criteria_scores.items():
        w = norm_weights.get(criterion, 0.0)
        contribution = score * w
        contributions[criterion] = round(contribution, 2)
        weighted_sum += contribution

    score = round(min(max(weighted_sum, 0), 100), 2)

    # Classification
    if score >= 81:
        classification = "Very High"
    elif score >= 61:
        classification = "High"
    elif score >= 41:
        classification = "Moderate"
    elif score >= 21:
        classification = "Low"
    else:
        classification = "Very Low"

    return {
        "aggregated_score": score,
        "classification": classification,
        "weights_used": norm_weights,
        "contributions": contributions,
    }
```

**Explanation:** It accepts `criteria_scores`, `weights`, `energy_type`, `client` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_weights()`, `list()`, `keys()`, `len()`, `sum()`.

### `promethee_ii`

- **File:** `fastapi-backend/app/services/mcda.py`
- **Lines:** `126-213`
- **Signature:** `def promethee_ii(`
- **Purpose:** PROMETHEE II outranking method for multi-criteria comparison.

**Code:**
```python
def promethee_ii(
    alternatives: list[dict[str, Any]],
    criteria: list[str],
    weights: dict[str, float],
    preference_thresholds: dict[str, float] | None = None,
    maximize: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """PROMETHEE II outranking method for multi-criteria comparison.

    Args:
        alternatives: List of dicts with criteria values
        criteria: List of criterion names
        weights: Criterion weights (will be normalized)
        preference_thresholds: Per-criterion preference threshold (q). Default: 10% of range.
        maximize: Dict of criterion -> True if higher is better. Default: all True.

    Returns:
        Dict with rankings, net_outranking_flows, positive_flows, negative_flows
    """
    n = len(alternatives)
    if n == 0:
        return {"rankings": [], "net_outranking_flows": [], "positive_flows": [], "negative_flows": []}

    # Defaults
    if maximize is None:
        maximize = {c: True for c in criteria}
    if preference_thresholds is None:
        preference_thresholds = {}
        for c in criteria:
            values = [a.get(c, 0) for a in alternatives]
            if values:
                preference_thresholds[c] = 0.1 * (max(values) - min(values))
            else:
                preference_thresholds[c] = 1.0

    # Normalize weights
    total_w = sum(weights.get(c, 0) for c in criteria)
    norm_w = {c: weights.get(c, 0) / total_w for c in criteria} if total_w > 0 else {c: 1.0 / len(criteria) for c in criteria}

    # Pairwise preference function (Type 5 — linear with indifference)
    def preference(a_val: float, b_val: float, criterion: str) -> float:
        diff = a_val - b_val if maximize.get(criterion, True) else b_val - a_val
        q = preference_thresholds.get(criterion, 1.0)
        if diff <= 0:
            return 0.0
        if diff <= q:
            return diff / q
        return 1.0

    # Calculate pairwise preference indices
    pi = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            total = 0.0
            for c in criteria:
                total += norm_w[c] * preference(alternatives[i].get(c, 0), alternatives[j].get(c, 0), c)
            pi[i][j] = total

    # Positive and negative outranking flows
    positive = [sum(pi[i]) / (n - 1) for i in range(n)]
    negative = [sum(pi[j][i]) / (n - 1) for j in range(n) for i in [i]]  # fix
    negative = [sum(pi[j][i] for j in range(n) if j != i) / (n - 1) for i in range(n)]

    # Net outranking flow
    net = [positive[i] - negative[i] for i in range(n)]

    # Rank alternatives
    ranked_indices = sorted(range(n), key=lambda i: net[i], reverse=True)

    rankings = []
    for rank, idx in enumerate(ranked_indices, 1):
        rankings.append({
            "rank": rank,
            "alternative_index": idx,
            "name": alternatives[idx].get("name", f"Option {idx+1}"),
            "net_flow": round(net[idx], 4),
            "positive_flow": round(positive[idx], 4),
            "negative_flow": round(negative[idx], 4),
        })

    return {
        "rankings": rankings,
        "net_outranking_flows": [round(x, 4) for x in net],
        "positive_flows": [round(x, 4) for x in positive],
        "negative_flows": [round(x, 4) for x in negative],
    }
```

**Explanation:** It accepts `alternatives`, `criteria`, `weights`, `preference_thresholds`, `maximize` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `len()`, `get()`, `max()`, `min()`, `sum()`.


## `fastapi-backend/app/services/mcda_weights_service.py`

**File:** `fastapi-backend/app/services/mcda_weights_service.py`

**Summary:** MCDA weights loader.

### `load_mcda_weights`

- **File:** `fastapi-backend/app/services/mcda_weights_service.py`
- **Lines:** `49-92`
- **Signature:** `def load_mcda_weights(client=None) -> dict[str, dict[str, float]]:`
- **Purpose:** Fetch active MCDA weights from Supabase or return defaults.

**Code:**
```python
def load_mcda_weights(client=None) -> dict[str, dict[str, float]]:
    """Fetch active MCDA weights from Supabase or return defaults.

    Args:
        client: Optional Supabase client. If None, a new client is created.

    Returns:
        Dict mapping energy_type -> {criterion: weight}
    """
    global _weights_cache

    if _weights_cache is not None:
        return _weights_cache

    try:
        if client is None:
            from app.services.supabase_service import get_supabase_client
            client = get_supabase_client()

        resp = (
            client.table("mcda_weights")
            .select("energy_type, criterion, weight")
            .eq("is_active", True)
            .execute()
        )
        rows = resp.data or []

        weights: dict[str, dict[str, float]] = {}
        for r in rows:
            etype = r.get("energy_type")
            crit = r.get("criterion")
            w = r.get("weight")
            if etype and crit and w is not None:
                weights.setdefault(etype, {})[crit] = float(w)

        if weights:
            logger.info("Loaded MCDA weights from DB for %s energy types", len(weights))
            _weights_cache = weights
            return weights
    except Exception as exc:
        logger.warning("Failed to load MCDA weights from DB: %s. Using defaults.", exc)

    _weights_cache = _DEFAULT_WEIGHTS
    return _DEFAULT_WEIGHTS
```

**Explanation:** It accepts `client` and returns `dict[str, dict[str, float]]`. See the code below for the full implementation. Key calls include `execute()`, `get_supabase_client()`, `get()`, `info()`, `warning()`.

### `get_weights`

- **File:** `fastapi-backend/app/services/mcda_weights_service.py`
- **Lines:** `95-106`
- **Signature:** `def get_weights(energy_type: str, client=None) -> dict[str, float]:`
- **Purpose:** Return weights for a specific energy type.

**Code:**
```python
def get_weights(energy_type: str, client=None) -> dict[str, float]:
    """Return weights for a specific energy type.

    Args:
        energy_type: e.g. 'geothermal', 'solar', 'wind', 'hydro'
        client: Optional Supabase client.

    Returns:
        Dict mapping criterion -> weight. Falls back to defaults.
    """
    all_weights = load_mcda_weights(client)
    return all_weights.get(energy_type, _DEFAULT_WEIGHTS.get(energy_type, {}))
```

**Explanation:** It accepts `energy_type`, `client` and returns `dict[str, float]`. See the code below for the full implementation. Key calls include `load_mcda_weights()`, `get()`.

### `invalidate_weights_cache`

- **File:** `fastapi-backend/app/services/mcda_weights_service.py`
- **Lines:** `109-113`
- **Signature:** `def invalidate_weights_cache() -> None:`
- **Purpose:** Clear the in-memory weights cache (call after admin updates).

**Code:**
```python
def invalidate_weights_cache() -> None:
    """Clear the in-memory weights cache (call after admin updates)."""
    global _weights_cache
    _weights_cache = None
    logger.info("MCDA weights cache invalidated")
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `info()`.


## `fastapi-backend/app/services/ml_worker_proxy.py`

**File:** `fastapi-backend/app/services/ml_worker_proxy.py`

**Summary:** Optional ML-worker proxy for Vercel.

### `_proxy_prefixes`

- **File:** `fastapi-backend/app/services/ml_worker_proxy.py`
- **Lines:** `25-29`
- **Signature:** `def _proxy_prefixes() -> list[str]:`
- **Purpose:** Handles  proxy prefixes.

**Code:**
```python
def _proxy_prefixes() -> list[str]:
    extra = os.environ.get("ML_WORKER_PROXY_PREFIXES")
    if extra:
        return [p.strip() for p in extra.split(",") if p.strip()]
    return DEFAULT_PROXY_PREFIXES
```

**Explanation:** It accepts zero arguments and returns `list[str]`. See the code below for the full implementation. Key calls include `get()`, `strip()`, `split()`.

### `MLWorkerProxyMiddleware.__init__`

- **File:** `fastapi-backend/app/services/ml_worker_proxy.py`
- **Lines:** `35-38`
- **Signature:** `def __init__(self, app, worker_url: str | None = None) -> None:`
- **Purpose:** Method of `MLWorkerProxyMiddleware` that handles   init  .

**Code:**
```python
def __init__(self, app, worker_url: str | None = None) -> None:
        super().__init__(app)
        self.worker_url = (worker_url or os.environ.get("ML_WORKER_URL", "")).rstrip("/")
        self.proxy_prefixes = _proxy_prefixes()
```

**Explanation:** It accepts `app`, `worker_url` and returns `None`. See the code below for the full implementation. Key calls include `__init__()`, `super()`, `rstrip()`, `get()`, `_proxy_prefixes()`.

### `MLWorkerProxyMiddleware._should_proxy`

- **File:** `fastapi-backend/app/services/ml_worker_proxy.py`
- **Lines:** `40-47`
- **Signature:** `def _should_proxy(self, path: str) -> bool:`
- **Purpose:** Method of `MLWorkerProxyMiddleware` that handles  should proxy.

**Code:**
```python
def _should_proxy(self, path: str) -> bool:
        if not self.worker_url:
            return False
        path = path.rstrip("/")
        for prefix in self.proxy_prefixes:
            if path == prefix or path.startswith(prefix + "/"):
                return True
        return False
```

**Explanation:** It accepts `path` and returns `bool`. See the code below for the full implementation. Key calls include `rstrip()`, `startswith()`.

### `MLWorkerProxyMiddleware.dispatch`

- **File:** `fastapi-backend/app/services/ml_worker_proxy.py`
- **Lines:** `49-93`
- **Signature:** `async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:`
- **Purpose:** Method of `MLWorkerProxyMiddleware` that handles dispatch.

**Code:**
```python
async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:
        if not self._should_proxy(request.url.path):
            return await call_next(request)

        # Keep CORS preflights local.
        if request.method == "OPTIONS":
            return await call_next(request)

        target = f"{self.worker_url}{request.url.path}"
        if request.url.query:
            target += f"?{request.url.query}"

        body = await request.body()
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in {"host", "content-length", "accept-encoding"}
        }

        try:
            async with httpx.AsyncClient(timeout=55.0) as client:
                worker_resp = await client.request(
                    method=request.method,
                    url=target,
                    headers=headers,
                    content=body,
                    follow_redirects=True,
                )
        except Exception as exc:
            logger.exception("ML worker proxy failed for %s: %s", target, exc)
            return Response(
                content=json.dumps({"detail": f"ML worker unavailable: {exc}"}),
                status_code=503,
                media_type="application/json",
            )

        return Response(
            content=worker_resp.content,
            status_code=worker_resp.status_code,
            headers={
                "content-type": worker_resp.headers.get(
                    "content-type", "application/json"
                )
            },
        )
```

**Explanation:** It accepts `request`, `call_next` and returns `Any`. See the code below for the full implementation. Key calls include `_should_proxy()`, `call_next()`, `body()`, `items()`, `lower()`.


## `fastapi-backend/app/services/municipality_suitability_builder.py`

**File:** `fastapi-backend/app/services/municipality_suitability_builder.py`

**Summary:** Municipality-level renewable energy suitability builder.

### `get_classification`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `41-47`
- **Signature:** `def get_classification(score: float | None) -> str | None:`
- **Purpose:** Retrieves classification.

**Code:**
```python
def get_classification(score: float | None) -> str | None:
    if score is None:
        return None
    for threshold, label in _CLASSIFICATION_THRESHOLDS:
        if score >= threshold:
            return label
    return "Very Low"
```

**Explanation:** It accepts `score` and returns `str | None`. See the code below for the full implementation.

### `_estimate_solar_from_lat`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `54-61`
- **Signature:** `def _estimate_solar_from_lat(lat: float) -> tuple[float, float]:`
- **Purpose:** Estimate solar irradiance (kWh/m2/day) and temperature (C) from latitude.

**Code:**
```python
def _estimate_solar_from_lat(lat: float) -> tuple[float, float]:
    """Estimate solar irradiance (kWh/m2/day) and temperature (C) from latitude.
    Philippines: ~5-20°N. Lower latitudes = higher irradiance.
    """
    abs_lat = abs(lat)
    irradiance = max(5.0 - (abs_lat / 20.0) * 1.5, 3.5)
    temperature = 26.0 + (abs_lat / 20.0) * 4.0
    return round(irradiance, 2), round(temperature, 1)
```

**Explanation:** It accepts `lat` and returns `tuple[float, float]`. See the code below for the full implementation. Key calls include `abs()`, `max()`, `round()`.

### `_estimate_wind_from_lat`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `64-66`
- **Signature:** `def _estimate_wind_from_lat(lat: float, lon: float) -> float:`
- **Purpose:** Estimate wind speed from coordinates. Philippines average ~3.2 m/s.

**Code:**
```python
def _estimate_wind_from_lat(lat: float, lon: float) -> float:
    """Estimate wind speed from coordinates. Philippines average ~3.2 m/s."""
    return 3.2
```

**Explanation:** It accepts `lat`, `lon` and returns `float`. See the code below for the full implementation.

### `_compute_solar_score`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `69-76`
- **Signature:** `def _compute_solar_score(irradiance: float | None, temperature: float | None) -> tuple[float | None, dict[str, Any]]:`
- **Purpose:** Handles  compute solar score.

**Code:**
```python
def _compute_solar_score(irradiance: float | None, temperature: float | None) -> tuple[float | None, dict[str, Any]]:
    if irradiance is None:
        return None, {}
    score = min((irradiance / 5.0) * 100, 100.0)
    factors = {"irradiance_kwh_m2_day": round(irradiance, 2)}
    if temperature is not None:
        factors["avg_temperature_c"] = round(temperature, 1)
    return round(score, 2), factors
```

**Explanation:** It accepts `irradiance`, `temperature` and returns `tuple[float | None, dict[str, Any]]`. See the code below for the full implementation. Key calls include `min()`, `round()`.

### `_compute_wind_score`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `79-84`
- **Signature:** `def _compute_wind_score(wind_speed: float | None) -> tuple[float | None, dict[str, Any]]:`
- **Purpose:** Handles  compute wind score.

**Code:**
```python
def _compute_wind_score(wind_speed: float | None) -> tuple[float | None, dict[str, Any]]:
    if wind_speed is None:
        return None, {}
    score = min((wind_speed / 7.0) * 100, 100.0)
    factors = {"wind_speed_ms": round(wind_speed, 2)}
    return round(score, 2), factors
```

**Explanation:** It accepts `wind_speed` and returns `tuple[float | None, dict[str, Any]]`. See the code below for the full implementation. Key calls include `min()`, `round()`.

### `_compute_hydro_score`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `87-94`
- **Signature:** `def _compute_hydro_score(hydro_suitability: float | None, hydraulic_head: float | None) -> tuple[float | None, dict[str, Any]]:`
- **Purpose:** Handles  compute hydro score.

**Code:**
```python
def _compute_hydro_score(hydro_suitability: float | None, hydraulic_head: float | None) -> tuple[float | None, dict[str, Any]]:
    if hydro_suitability is None:
        return None, {}
    score = min(hydro_suitability * 100, 100.0)
    factors = {"hydro_suitability_raw": round(hydro_suitability, 4)}
    if hydraulic_head is not None:
        factors["hydraulic_head_m"] = round(hydraulic_head, 1)
    return round(score, 2), factors
```

**Explanation:** It accepts `hydro_suitability`, `hydraulic_head` and returns `tuple[float | None, dict[str, Any]]`. See the code below for the full implementation. Key calls include `min()`, `round()`.

### `_compute_geothermal_score`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `97-110`
- **Signature:** `def _compute_geothermal_score(`
- **Purpose:** Handles  compute geothermal score.

**Code:**
```python
def _compute_geothermal_score(
    geothermal_score: float | None,
    reservoir_temp: float | None,
    temperature_score: float | None = None,
) -> tuple[float | None, dict[str, Any]]:
    if geothermal_score is None:
        return None, {}
    score = min(geothermal_score * 100, 100.0)
    factors = {"geothermal_score_raw": round(geothermal_score, 4)}
    if reservoir_temp is not None:
        factors["reservoir_temperature_c"] = round(reservoir_temp, 1)
    elif temperature_score is not None:
        factors["temperature_score"] = round(temperature_score, 4)
    return round(score, 2), factors
```

**Explanation:** It accepts `geothermal_score`, `reservoir_temp`, `temperature_score` and returns `tuple[float | None, dict[str, Any]]`. See the code below for the full implementation. Key calls include `min()`, `round()`.

### `_compute_composite`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `113-119`
- **Signature:** `def _compute_composite(scores: dict[str, float | None]) -> tuple[float | None, dict[str, Any]]:`
- **Purpose:** Handles  compute composite.

**Code:**
```python
def _compute_composite(scores: dict[str, float | None]) -> tuple[float | None, dict[str, Any]]:
    available = [v for v in scores.values() if v is not None]
    if not available:
        return None, {}
    avg = sum(available) / len(available)
    factors = {k: v for k, v in scores.items() if v is not None}
    return round(avg, 2), factors
```

**Explanation:** It accepts `scores` and returns `tuple[float | None, dict[str, Any]]`. See the code below for the full implementation. Key calls include `values()`, `sum()`, `len()`, `items()`, `round()`.

### `_fetch_all_municipalities`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `126-145`
- **Signature:** `def _fetch_all_municipalities(client) -> list[dict[str, Any]]:`
- **Purpose:** Handles  fetch all municipalities.

**Code:**
```python
def _fetch_all_municipalities(client) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    start = 0
    batch = 1000
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id, name, province_id, lat, lon, provinces(name)")
            .range(start, start + batch - 1)
            .execute()
        )
        rows = resp.data or []
        for r in rows:
            province_obj = r.pop("provinces", None)
            r["province_name"] = province_obj.get("name", "") if province_obj else ""
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        start += batch
    return all_rows
```

**Explanation:** It accepts `client` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `execute()`, `extend()`, `pop()`, `len()`, `range()`.

### `_fetch_climate_data`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `148-171`
- **Signature:** `def _fetch_climate_data(client) -> dict[int, dict[str, Any]]:`
- **Purpose:** Fetch multi-year annual averages per municipality (all available years).

**Code:**
```python
def _fetch_climate_data(client) -> dict[int, dict[str, Any]]:
    """Fetch multi-year annual averages per municipality (all available years)."""
    resp = client.table("municipality_climate_monthly").select(
        "municipality_id, allsky_sfc_sw_dwn, ws10m, t2m, cloud_amt"
    ).limit(10000).execute()
    rows = resp.data or []
    data: dict[int, dict[str, Any]] = defaultdict(dict)
    for r in rows:
        mid = r.get("municipality_id")
        if mid is None:
            continue
        entry = data[mid]
        for key in ("allsky_sfc_sw_dwn", "ws10m", "t2m", "cloud_amt"):
            val = r.get(key)
            if val is not None:
                entry.setdefault(key, []).append(float(val))
    # Average across all months/years
    averaged: dict[int, dict[str, Any]] = {}
    for mid, vals in data.items():
        averaged[mid] = {}
        for key, arr in vals.items():
            if arr:
                averaged[mid][key] = sum(arr) / len(arr)
    return averaged
```

**Explanation:** It accepts `client` and returns `dict[int, dict[str, Any]]`. See the code below for the full implementation. Key calls include `execute()`, `limit()`, `select()`, `table()`, `defaultdict()`.

### `_fetch_hydro_data`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `174-187`
- **Signature:** `def _fetch_hydro_data(client) -> dict[int, dict[str, Any]]:`
- **Purpose:** Handles  fetch hydro data.

**Code:**
```python
def _fetch_hydro_data(client) -> dict[int, dict[str, Any]]:
    resp = client.table("hydropower_suitability").select(
        "municipality_id, hydro_suitability_score, hydraulic_head_m"
    ).limit(10000).execute()
    rows = resp.data or []
    data: dict[int, dict[str, Any]] = {}
    for r in rows:
        mid = r.get("municipality_id")
        if mid is not None:
            data[mid] = {
                "hydro_suitability_score": r.get("hydro_suitability_score"),
                "hydraulic_head_m": r.get("hydraulic_head_m"),
            }
    return data
```

**Explanation:** It accepts `client` and returns `dict[int, dict[str, Any]]`. See the code below for the full implementation. Key calls include `execute()`, `limit()`, `select()`, `table()`, `get()`.

### `_fetch_geothermal_data`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `190-220`
- **Signature:** `def _fetch_geothermal_data(client) -> dict[int, dict[str, Any]]:`
- **Purpose:** Handles  fetch geothermal data.

**Code:**
```python
def _fetch_geothermal_data(client) -> dict[int, dict[str, Any]]:
    # 1. Fetch suitability scores (geothermal_score, temperature_score, mcda)
    resp = client.table("geothermal_suitability").select(
        "municipality_id, geothermal_score, geothermal_score_mcda, temperature_score"
    ).limit(10000).execute()
    rows = resp.data or []
    data: dict[int, dict[str, Any]] = {}
    for r in rows:
        mid = r.get("municipality_id")
        if mid is not None:
            data[mid] = {
                "geothermal_score": r.get("geothermal_score"),
                "geothermal_score_mcda": r.get("geothermal_score_mcda"),
                "temperature_score": r.get("temperature_score"),
            }

    # 2. Fetch actual reservoir temperature from geothermal_output
    try:
        out_resp = client.table("geothermal_output").select(
            "municipality_id, reservoir_temperature_c"
        ).limit(10000).execute()
        out_rows = out_resp.data or []
        for r in out_rows:
            mid = r.get("municipality_id")
            if mid is not None and mid in data:
                data[mid]["reservoir_temperature_c"] = r.get("reservoir_temperature_c")
    except Exception:
        # geothermal_output may not exist or have no data; skip gracefully
        pass

    return data
```

**Explanation:** It accepts `client` and returns `dict[int, dict[str, Any]]`. See the code below for the full implementation. Key calls include `execute()`, `limit()`, `select()`, `table()`, `get()`.

### `build_suitability_for_municipality`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `227-294`
- **Signature:** `def build_suitability_for_municipality(`
- **Purpose:** Builds suitability for municipality.

**Code:**
```python
def build_suitability_for_municipality(
    muni: dict[str, Any],
    climate: dict[int, dict[str, Any]],
    hydro: dict[int, dict[str, Any]],
    geo: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    mid = muni["municipality_id"]
    c = climate.get(mid, {})
    h = hydro.get(mid, {})
    g = geo.get(mid, {})

    # Use actual NASA POWER data if available; otherwise fall back to lat-based estimates
    irradiance = c.get("allsky_sfc_sw_dwn")
    temperature = c.get("t2m")
    wind_speed = c.get("ws10m")

    if irradiance is None or temperature is None:
        lat = muni.get("lat")
        if lat is not None:
            est_irr, est_temp = _estimate_solar_from_lat(float(lat))
            if irradiance is None:
                irradiance = est_irr
            if temperature is None:
                temperature = est_temp

    if wind_speed is None:
        lat = muni.get("lat")
        lon = muni.get("lon")
        if lat is not None and lon is not None:
            wind_speed = _estimate_wind_from_lat(float(lat), float(lon))

    solar_score, solar_factors = _compute_solar_score(irradiance, temperature)
    wind_score, wind_factors = _compute_wind_score(wind_speed)
    hydro_score, hydro_factors = _compute_hydro_score(
        h.get("hydro_suitability_score"), h.get("hydraulic_head_m")
    )
    geo_score, geo_factors = _compute_geothermal_score(
        g.get("geothermal_score"),
        g.get("reservoir_temperature_c"),
        g.get("temperature_score"),
    )

    composite, composite_factors = _compute_composite({
        "solar": solar_score,
        "wind": wind_score,
        "hydro": hydro_score,
        "geothermal": geo_score,
    })

    return {
        "municipality_id": mid,
        "solar_suitability_score": solar_score,
        "solar_classification": get_classification(solar_score),
        "solar_factors": json.dumps(solar_factors) if solar_factors else None,
        "wind_suitability_score": wind_score,
        "wind_classification": get_classification(wind_score),
        "wind_factors": json.dumps(wind_factors) if wind_factors else None,
        "hydro_suitability_score": hydro_score,
        "hydro_classification": get_classification(hydro_score),
        "hydro_factors": json.dumps(hydro_factors) if hydro_factors else None,
        "geothermal_suitability_score": geo_score,
        "geothermal_classification": get_classification(geo_score),
        "geothermal_score_mcda": g.get("geothermal_score_mcda"),
        "geothermal_factors": json.dumps(geo_factors) if geo_factors else None,
        "composite_suitability_score": composite,
        "composite_classification": get_classification(composite),
        "suitability_updated_at": datetime.now(timezone.utc).isoformat(),
    }
```

**Explanation:** It accepts `muni`, `climate`, `hydro`, `geo` and returns `dict[str, Any] | None`. See the code below for the full implementation. Key calls include `get()`, `_estimate_solar_from_lat()`, `float()`, `_estimate_wind_from_lat()`, `_compute_solar_score()`.

### `persist_batch`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `297-303`
- **Signature:** `def persist_batch(client, updates: list[dict[str, Any]]) -> None:`
- **Purpose:** Handles persist batch.

**Code:**
```python
def persist_batch(client, updates: list[dict[str, Any]]) -> None:
    if not updates:
        return
    for up in updates:
        mid = up.pop("municipality_id")
        client.table("municipalities").update(up).eq("municipality_id", mid).execute()
    logger.info("Persisted %s municipality suitability records", len(updates))
```

**Explanation:** It accepts `client`, `updates` and returns `None`. See the code below for the full implementation. Key calls include `pop()`, `execute()`, `eq()`, `update()`, `table()`.

### `invalidate_suitability_cache`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `306-315`
- **Signature:** `def invalidate_suitability_cache() -> None:`
- **Purpose:** Handles invalidate suitability cache.

**Code:**
```python
def invalidate_suitability_cache() -> None:
    try:
        from app.services.redis_client import get_redis_sync
        redis = get_redis_sync()
        keys = redis.keys("lumi:suitability:*")
        if keys:
            redis.delete(*keys)
            logger.info("Invalidated %s suitability cache keys", len(keys))
    except Exception as exc:
        logger.warning("Cache invalidation failed (non-critical): %s", exc)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `keys()`, `delete()`, `info()`, `warning()`.

### `warm_suitability_cache`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `318-380`
- **Signature:** `def warm_suitability_cache(client) -> None:`
- **Purpose:** Pre-populate Redis cache for all renewable types after build.

**Code:**
```python
def warm_suitability_cache(client) -> None:
    """Pre-populate Redis cache for all renewable types after build."""
    from app.services.redis_client import set_suitability_cache_sync
    prefixes = {
        "solar": "solar",
        "wind": "wind",
        "hydro": "hydro",
        "geothermal": "geothermal",
        "composite": "renewable_potential",
    }
    for prefix, metric_name in prefixes.items():
        try:
            score_col = f"{prefix}_suitability_score"
            class_col = f"{prefix}_classification"
            factors_col = f"{prefix}_factors"
            has_factors = prefix != "composite"
            select_cols = (
                f"municipality_id, name, province_id, lat, lon, "
                f"provinces(name), {score_col}, {class_col}"
            )
            if has_factors:
                select_cols += f", {factors_col}"

            # Paginate through all municipalities with scores
            all_rows = []
            offset = 0
            batch = 1000
            while True:
                resp = (
                    client.table("municipalities")
                    .select(select_cols)
                    .not_.is_(score_col, "null")
                    .range(offset, offset + batch - 1)
                    .execute()
                )
                rows = resp.data or []
                if not rows:
                    break
                all_rows.extend(rows)
                if len(rows) < batch:
                    break
                offset += batch

            items = []
            for r in all_rows:
                province_obj = r.get("provinces")
                province_name = province_obj.get("name", "") if province_obj else ""
                items.append({
                    "region": "",
                    "province": province_name,
                    "municipality": r.get("name"),
                    "municipality_id": r.get("municipality_id"),
                    "value": float(r.get(score_col) or 0),
                    "classification": r.get(class_col),
                    "factors": r.get(factors_col) if has_factors else None,
                    "metric": metric_name,
                    "lat": r.get("lat"),
                    "lon": r.get("lon"),
                })
            set_suitability_cache_sync(metric_name, "municipality", items)
            logger.info("Warmed cache for %s with %s items", metric_name, len(items))
        except Exception as exc:
            logger.warning("Cache warm failed for %s: %s", metric_name, exc)
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `items()`, `set_suitability_cache_sync()`, `info()`, `execute()`, `extend()`.

### `build_all_municipality_suitability`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `387-425`
- **Signature:** `def build_all_municipality_suitability(batch_size: int = 200) -> dict[str, Any]:`
- **Purpose:** Builds all municipality suitability.

**Code:**
```python
def build_all_municipality_suitability(batch_size: int = 200) -> dict[str, Any]:
    logger.info("Starting full municipality suitability build...")
    client = get_supabase_client()

    municipalities = _fetch_all_municipalities(client)
    logger.info("Fetched %s municipalities", len(municipalities))

    climate = _fetch_climate_data(client)
    hydro = _fetch_hydro_data(client)
    geo = _fetch_geothermal_data(client)

    updates: list[dict[str, Any]] = []
    all_updates: list[dict[str, Any]] = []
    processed = 0
    for muni in municipalities:
        up = build_suitability_for_municipality(muni, climate, hydro, geo)
        if up:
            updates.append(up)
            all_updates.append(up)
        processed += 1
        if len(updates) >= batch_size:
            persist_batch(client, updates)
            updates = []
            logger.info("Progress: %s/%s municipalities", processed, len(municipalities))

    persist_batch(client, updates)
    invalidate_suitability_cache()
    warm_suitability_cache(client)

    summary = {
        "total_municipalities": len(municipalities),
        "processed": processed,
        "with_solar": sum(1 for u in all_updates if u.get("solar_suitability_score") is not None),
        "with_wind": sum(1 for u in all_updates if u.get("wind_suitability_score") is not None),
        "with_hydro": sum(1 for u in all_updates if u.get("hydro_suitability_score") is not None),
        "with_geothermal": sum(1 for u in all_updates if u.get("geothermal_suitability_score") is not None),
    }
    logger.info("Build complete: %s", summary)
    return summary
```

**Explanation:** It accepts `batch_size` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `info()`, `get_supabase_client()`, `_fetch_all_municipalities()`, `len()`, `_fetch_climate_data()`.

### `refresh_municipality_suitability`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `428-459`
- **Signature:** `def refresh_municipality_suitability(municipality_ids: list[int]) -> dict[str, Any]:`
- **Purpose:** Handles refresh municipality suitability.

**Code:**
```python
def refresh_municipality_suitability(municipality_ids: list[int]) -> dict[str, Any]:
    logger.info("Refreshing suitability for %s municipalities", len(municipality_ids))
    client = get_supabase_client()

    municipalities = []
    for mid in municipality_ids:
        resp = client.table("municipalities").select(
            "municipality_id, name, province_id, provinces(name)"
        ).eq("municipality_id", mid).execute()
        row = resp.data[0] if resp.data else None
        if row:
            province_obj = row.pop("provinces", None)
            row["province_name"] = province_obj.get("name", "") if province_obj else ""
            municipalities.append(row)

    climate = _fetch_climate_data(client)
    hydro = _fetch_hydro_data(client)
    geo = _fetch_geothermal_data(client)

    updates = []
    for muni in municipalities:
        up = build_suitability_for_municipality(muni, climate, hydro, geo)
        if up:
            updates.append(up)

    persist_batch(client, updates)
    invalidate_suitability_cache()

    return {
        "refreshed": len(updates),
        "requested": len(municipality_ids),
    }
```

**Explanation:** It accepts `municipality_ids` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `info()`, `len()`, `get_supabase_client()`, `execute()`, `pop()`.

### `main`

- **File:** `fastapi-backend/app/services/municipality_suitability_builder.py`
- **Lines:** `466-480`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Build or refresh municipality suitability scores")
    parser.add_argument("--action", choices=["build", "refresh"], default="build",
                        help="build = full rebuild, refresh = selective update")
    parser.add_argument("--municipality-ids", nargs="+", type=int, default=None,
                        help="Specific municipality IDs to refresh (only for --action refresh)")
    args = parser.parse_args()

    if args.action == "build":
        build_all_municipality_suitability()
    elif args.action == "refresh":
        if not args.municipality_ids:
            logger.error("--municipality-ids required for refresh action")
            return
        refresh_municipality_suitability(args.municipality_ids)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `parse_args()`, `build_all_municipality_suitability()`, `refresh_municipality_suitability()`.


## `fastapi-backend/app/services/products.py`

**File:** `fastapi-backend/app/services/products.py`

**Summary:** Product Recommendation Service

### `_load_products`

- **File:** `fastapi-backend/app/services/products.py`
- **Lines:** `32-67`
- **Signature:** `def _load_products() -> pd.DataFrame:`
- **Purpose:** Handles  load products.

**Code:**
```python
def _load_products() -> pd.DataFrame:
    global _products_df
    with _products_lock:
        if _products_df is not None:
            return _products_df

        cache_key = "products:dataframe"
        cached = cache_get_sync(cache_key)
        if cached is not None:
            _products_df = pd.DataFrame(cached)
            return _products_df

        try:
            client = get_supabase_client()
            resp = client.table("products").select("*").execute()
            rows = resp.data or []
            if rows:
                df = pd.DataFrame(rows)
                df["price_value"] = pd.to_numeric(df["price_value"], errors="coerce")
                df["energy_category"] = df.apply(_fix_category, axis=1)
                cache_set_sync(cache_key, rows, ttl=1800)
                _products_df = df
                return _products_df
        except Exception as exc:
            logger.warning("Failed to load products from Supabase: %s", exc)

        if os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true" and _PRODUCTS_CSV.exists():
            _products_df = pd.read_csv(_PRODUCTS_CSV)
            _products_df["price_value"] = pd.to_numeric(_products_df["price_value"], errors="coerce")
            _products_df["energy_category"] = _products_df.apply(_fix_category, axis=1)
            return _products_df

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Product dataset not available.",
        )
```

**Explanation:** It accepts zero arguments and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `cache_get_sync()`, `HTTPException()`, `DataFrame()`, `get_supabase_client()`, `execute()`.

### `_fix_category`

- **File:** `fastapi-backend/app/services/products.py`
- **Lines:** `70-84`
- **Signature:** `def _fix_category(row: pd.Series) -> str:`
- **Purpose:** Correct misclassified categories using source_file hints.

**Code:**
```python
def _fix_category(row: pd.Series) -> str:
    """Correct misclassified categories using source_file hints."""
    cat = str(row.get("energy_category", "")).lower().strip()
    src = str(row.get("source_file", "")).lower()
    base = src.split("/")[-1].split("\\")[-1]
    # Only override when the source file name explicitly indicates the category
    if base.endswith("_hydro.csv") and cat == "wind":
        return "hydro"
    if base.endswith("_solar.csv") and cat != "solar":
        return "solar"
    if base.endswith("_wind.csv") and cat != "wind":
        return "wind"
    if base.endswith("_geothermal.csv") and cat != "geothermal":
        return "geothermal"
    return cat
```

**Explanation:** It accepts `row` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `lower()`, `str()`, `get()`, `split()`.

### `_row_to_dict`

- **File:** `fastapi-backend/app/services/products.py`
- **Lines:** `87-109`
- **Signature:** `def _row_to_dict(row: pd.Series) -> dict:`
- **Purpose:** Serialize a product row for API responses.

**Code:**
```python
def _row_to_dict(row: pd.Series) -> dict:
    """Serialize a product row for API responses."""
    def _clean(val):
        if val is None:
            return None
        try:
            if pd.isna(val):
                return None
        except (TypeError, ValueError):
            pass
        return val

    return {
        "product_name": _clean(row.get("product_name")),
        "price_value": round(row.get("price_value"), 2) if pd.notna(row.get("price_value")) else None,
        "currency": _clean(row.get("currency")),
        "energy_category": _clean(row.get("energy_category")),
        "energy_subcategory": _clean(row.get("energy_subcategory")),
        "source_site": _clean(row.get("source_site")),
        "url": _clean(row.get("url")),
        "ratings": _clean(row.get("ratings")),
        "reviews": _clean(row.get("reviews")),
    }
```

**Explanation:** It accepts `row` and returns `dict`. See the code below for the full implementation. Key calls include `isna()`, `_clean()`, `get()`, `notna()`, `round()`.

### `get_product_recommendations`

- **File:** `fastapi-backend/app/services/products.py`
- **Lines:** `112-155`
- **Signature:** `def get_product_recommendations(energy_type: str, budget_php: float | None = None, limit: int = 5) -> dict:`
- **Purpose:** Return top-N matching products for a given renewable energy type.

**Code:**
```python
def get_product_recommendations(energy_type: str, budget_php: float | None = None, limit: int = 5) -> dict:
    """Return top-N matching products for a given renewable energy type."""
    df = _load_products()
    et = energy_type.lower().strip()

    # Map frontend names to CSV categories
    category_map = {
        "solar": "solar",
        "wind": "wind",
        "hydropower": "hydro",
        "hydro": "hydro",
        "geothermal": "geothermal",
    }
    target_cat = category_map.get(et, et)

    filtered = df[df["energy_category"] == target_cat]
    # Only recommend products with valid URLs
    filtered = filtered[filtered["url"].notna() & (filtered["url"].str.strip() != "")]

    # Rough conversion: assume USD if currency is USD, otherwise use as-is
    def in_php(row):
        val = row["price_value"]
        if pd.isna(val):
            return float("inf")
        curr = str(row.get("currency", "")).upper()
        if "USD" in curr:
            return val * 56.0  # configurable fallback rate
        return val

    if budget_php is not None and budget_php > 0:
        filtered = filtered[filtered.apply(lambda r: in_php(r) <= budget_php, axis=1)]

    filtered = filtered.copy()
    filtered["price_in_php"] = filtered.apply(in_php, axis=1)
    filtered = filtered.sort_values("price_in_php", na_position="last").head(limit)
    filtered = filtered.drop(columns=["price_in_php"])
    items = [_row_to_dict(r) for _, r in filtered.iterrows()]

    return {
        "energy_type": energy_type,
        "items": items,
        "count": len(items),
        "note": "Prices converted from USD using PHP 56 = 1 USD when applicable. Links may be outdated; verify before purchase.",
    }
```

**Explanation:** It accepts `energy_type`, `budget_php`, `limit` and returns `dict`. See the code below for the full implementation. Key calls include `_load_products()`, `strip()`, `lower()`, `get()`, `notna()`.

### `browse_products`

- **File:** `fastapi-backend/app/services/products.py`
- **Lines:** `158-193`
- **Signature:** `def browse_products(`
- **Purpose:** Paginated product browser with filters.

**Code:**
```python
def browse_products(
    category: str | None = None,
    subcategory: str | None = None,
    source_site: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Paginated product browser with filters."""
    df = _load_products()

    if category:
        df = df[df["energy_category"] == category.lower().strip()]
    if subcategory:
        df = df[df["energy_subcategory"] == subcategory.lower().strip()]
    if source_site:
        df = df[df["source_site"].str.lower() == source_site.lower().strip()]
    if min_price is not None and min_price > 0:
        df = df[df["price_value"] >= min_price]
    if max_price is not None and max_price > 0:
        df = df[df["price_value"] <= max_price]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = df.iloc[start:end]

    items = [_row_to_dict(r) for _, r in paginated.iterrows()]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "note": "Prices may be in USD or local currency. Verify links before purchase.",
    }
```

**Explanation:** It accepts `category`, `subcategory`, `source_site`, `min_price`, `max_price`, `page`, `page_size` and returns `dict`. See the code below for the full implementation. Key calls include `_load_products()`, `strip()`, `lower()`, `len()`, `_row_to_dict()`.

### `get_product_data_audit`

- **File:** `fastapi-backend/app/services/products.py`
- **Lines:** `196-224`
- **Signature:** `def get_product_data_audit() -> dict:`
- **Purpose:** Return a data quality audit of the scraped product dataset.

**Code:**
```python
def get_product_data_audit() -> dict:
    """Return a data quality audit of the scraped product dataset."""
    df = _load_products()
    total = len(df)
    with_url = df["url"].notna() & (df["url"].str.strip() != "")
    without_url = total - with_url.sum()

    # Categorization audit
    hydro_misclassified = len(df[(df["energy_category"] == "wind") & (df["source_file"].str.contains("hydro", case=False, na=False))])
    solar_misclassified = len(df[(df["energy_category"] != "solar") & (df["source_file"].str.contains("solar", case=False, na=False))])

    category_counts = df["energy_category"].value_counts().to_dict()
    source_counts = df["source_site"].value_counts().to_dict()

    return {
        "total_products": total,
        "with_url": int(with_url.sum()),
        "without_url": int(without_url),
        "hydro_misclassified_as_wind": int(hydro_misclassified),
        "solar_misclassified": int(solar_misclassified),
        "category_counts": category_counts,
        "source_counts": source_counts,
        "recommendations": [
            "Fix scraper categorization logic for hydro products (currently tagged as wind).",
            "Add product image and description fields to scraper output.",
            "Verify and update stale marketplace URLs quarterly.",
            "Add availability / stock status scraping.",
        ],
    }
```

**Explanation:** It accepts zero arguments and returns `dict`. See the code below for the full implementation. Key calls include `_load_products()`, `len()`, `notna()`, `strip()`, `sum()`.


## `fastapi-backend/app/services/rag_embeddings_client.py`

**File:** `fastapi-backend/app/services/rag_embeddings_client.py`

**Summary:** Source file `fastapi-backend/app/services/rag_embeddings_client.py`.

### `_cache_key`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `24-27`
- **Signature:** `def _cache_key(text: str) -> str:`
- **Purpose:** Handles  cache key.

**Code:**
```python
def _cache_key(text: str) -> str:
    normalized = text.strip().lower()
    digest = hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]
    return f'{_EMBEDDING_CACHE_PREFIX}:{digest}'
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `strip()`, `hexdigest()`, `sha256()`, `encode()`.

### `_get_cached_embedding`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `30-40`
- **Signature:** `def _get_cached_embedding(key: str) -> list[float] | None:`
- **Purpose:** Handles  get cached embedding.

**Code:**
```python
def _get_cached_embedding(key: str) -> list[float] | None:
    try:
        redis = get_redis_sync()
        if redis is None:
            return None
        cached = redis.get(key)
        if cached:
            return json.loads(cached)
    except Exception as exc:
        logger.debug('Embedding cache read failed: %s', exc)
    return None
```

**Explanation:** It accepts `key` and returns `list[float] | None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `get()`, `loads()`, `debug()`.

### `_save_cached_embedding`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `43-50`
- **Signature:** `def _save_cached_embedding(key: str, embedding: list[float]) -> None:`
- **Purpose:** Handles  save cached embedding.

**Code:**
```python
def _save_cached_embedding(key: str, embedding: list[float]) -> None:
    try:
        redis = get_redis_sync()
        if redis is None:
            return
        redis.setex(key, _EMBEDDING_CACHE_TTL_SECONDS, json.dumps(embedding))
    except Exception as exc:
        logger.debug('Embedding cache write failed: %s', exc)
```

**Explanation:** It accepts `key`, `embedding` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `setex()`, `dumps()`, `debug()`.

### `_format_embeddings`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `53-69`
- **Signature:** `def _format_embeddings(raw: Any, count: int) -> list[list[float]]:`
- **Purpose:** Normalize HuggingFace / OpenAI responses into a list of float lists.

**Code:**
```python
def _format_embeddings(raw: Any, count: int) -> list[list[float]]:
    '''Normalize HuggingFace / OpenAI responses into a list of float lists.'''
    if not isinstance(raw, list):
        raise ValueError(f'Unexpected embedding response type: {type(raw)}')
    if count == 1:
        if not raw:
            raise ValueError('Empty embedding response for single input')
        if isinstance(raw[0], (int, float)):
            return [raw]
        if isinstance(raw[0], list) and len(raw) == 1:
            return raw
        raise ValueError('Unexpected single embedding response shape')
    if not all(isinstance(item, list) for item in raw):
        raise ValueError('Batch embedding response must be a list of lists')
    if len(raw) != count:
        raise ValueError(f'Expected {count} embeddings, got {len(raw)}')
    return raw
```

**Explanation:** It accepts `raw`, `count` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `isinstance()`, `ValueError()`, `type()`, `len()`, `all()`.

### `_embed_with_huggingface`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `72-111`
- **Signature:** `def _embed_with_huggingface(`
- **Purpose:** Handles  embed with huggingface.

**Code:**
```python
def _embed_with_huggingface(
    texts: list[str],
    model: str,
    token: str | None,
    batch_size: int,
) -> list[list[float]]:
    url = _HUGGINGFACE_INFERENCE_URL.format(model=model)
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    results: list[list[float]] = []
    with httpx.Client(timeout=60.0) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {'inputs': batch}
            for attempt in range(3):
                try:
                    resp = client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        results.extend(_format_embeddings(data, len(batch)))
                        break
                    if resp.status_code == 503 and attempt < 2:
                        logger.warning('HuggingFace inference is loading, retrying...')
                        time.sleep(2 ** attempt)
                        continue
                    raise RuntimeError(
                        f'HuggingFace inference error {resp.status_code}: {resp.text}'
                    )
                except (RuntimeError, ValueError):
                    raise
                except Exception as exc:
                    if attempt == 2:
                        raise RuntimeError(
                            f'HuggingFace inference call failed: {exc}'
                        ) from exc
                    logger.warning('HuggingFace inference call failed, retrying: %s', exc)
                    time.sleep(2 ** attempt)
    return results
```

**Explanation:** It accepts `texts`, `model`, `token`, `batch_size` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `format()`, `Client()`, `range()`, `len()`, `post()`.

### `_embed_with_openai`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `114-134`
- **Signature:** `def _embed_with_openai(`
- **Purpose:** Handles  embed with openai.

**Code:**
```python
def _embed_with_openai(
    texts: list[str],
    model: str,
    token: str | None,
    batch_size: int,
) -> list[list[float]]:
    if not token:
        raise ValueError('OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai')
    url = 'https://api.openai.com/v1/embeddings'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    results: list[list[float]] = []
    with httpx.Client(timeout=60.0) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {'input': batch, 'model': model}
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json().get('data', [])
            results.extend([item['embedding'] for item in data])
    return results
```

**Explanation:** It accepts `texts`, `model`, `token`, `batch_size` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `ValueError()`, `Client()`, `range()`, `len()`, `post()`.

### `_embed_with_sentence_transformers`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `137-160`
- **Signature:** `def _embed_with_sentence_transformers(texts: list[str], model: str, batch_size: int) -> list[list[float]]:`
- **Purpose:** Handles  embed with sentence transformers.

**Code:**
```python
def _embed_with_sentence_transformers(texts: list[str], model: str, batch_size: int) -> list[list[float]]:
    global _local_embedder
    if _local_embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                'sentence-transformers is required for the local embedding provider. '
                'Install it or set EMBEDDING_PROVIDER=huggingface-inference.'
            ) from exc
        logger.info('Loading local embedding model %s ...', model)
        _local_embedder = SentenceTransformer(model)

    results: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        arrays = _local_embedder.encode(
            batch,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        results.extend(arrays.astype('float32').tolist())
    return results
```

**Explanation:** It accepts `texts`, `model`, `batch_size` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `info()`, `SentenceTransformer()`, `ImportError()`, `range()`, `len()`.

### `_embed_batch`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `163-177`
- **Signature:** `def _embed_batch(texts: list[str]) -> list[list[float]]:`
- **Purpose:** Handles  embed batch.

**Code:**
```python
def _embed_batch(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    provider = settings.embedding_provider.lower() if settings.embedding_provider else 'huggingface-inference'
    model = settings.embedding_model or 'sentence-transformers/all-MiniLM-L6-v2'
    batch_size = max(1, settings.embedding_batch_size or 32)

    if provider in ('huggingface', 'huggingface-inference', 'hf'):
        token = settings.hf_token or settings.embedding_api_key or None
        return _embed_with_huggingface(texts, model, token, batch_size)
    if provider == 'openai':
        token = settings.openai_api_key or settings.embedding_api_key or None
        return _embed_with_openai(texts, model, token, batch_size)
    if provider in ('sentence-transformers', 'local', 'st'):
        return _embed_with_sentence_transformers(texts, model, batch_size)
    raise ValueError(f'Unsupported embedding provider: {settings.embedding_provider}')
```

**Explanation:** It accepts `texts` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `get_settings()`, `lower()`, `max()`, `_embed_with_huggingface()`, `_embed_with_openai()`.

### `encode`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `180-219`
- **Signature:** `def encode(texts: str | list[str]) -> list[list[float]]:`
- **Purpose:** Encode one or more texts, using Redis cache to avoid repeated API calls.

**Code:**
```python
def encode(texts: str | list[str]) -> list[list[float]]:
    '''Encode one or more texts, using Redis cache to avoid repeated API calls.'''
    if isinstance(texts, str):
        texts = [texts]
    if not texts:
        return []

    results: list[list[float] | None] = [None] * len(texts)
    unique_texts: list[str] = []
    unique_norms: list[str] = []
    norm_to_indices: dict[str, list[int]] = {}

    for idx, text in enumerate(texts):
        normalized = text.strip().lower()
        if normalized not in norm_to_indices:
            norm_to_indices[normalized] = []
            unique_texts.append(text)
            unique_norms.append(normalized)
        norm_to_indices[normalized].append(idx)

    missing_texts: list[str] = []
    missing_norms: list[str] = []
    for text, norm in zip(unique_texts, unique_norms):
        cache_key = _cache_key(norm)
        cached = _get_cached_embedding(cache_key)
        if cached:
            for idx in norm_to_indices[norm]:
                results[idx] = cached
        else:
            missing_texts.append(text)
            missing_norms.append(norm)

    if missing_texts:
        embeddings = _embed_batch(missing_texts)
        for norm, emb in zip(missing_norms, embeddings):
            _save_cached_embedding(_cache_key(norm), emb)
            for idx in norm_to_indices[norm]:
                results[idx] = emb

    return [r for r in results if r is not None]
```

**Explanation:** It accepts `texts` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `isinstance()`, `len()`, `enumerate()`, `lower()`, `append()`.

### `encode_query`

- **File:** `fastapi-backend/app/services/rag_embeddings_client.py`
- **Lines:** `222-227`
- **Signature:** `def encode_query(query: str) -> list[float]:`
- **Purpose:** Convenience helper for a single query.

**Code:**
```python
def encode_query(query: str) -> list[float]:
    '''Convenience helper for a single query.'''
    embeddings = encode(query)
    if not embeddings:
        raise RuntimeError('Failed to encode query')
    return embeddings[0]
```

**Explanation:** It accepts `query` and returns `list[float]`. See the code below for the full implementation. Key calls include `encode()`, `RuntimeError()`.


## `fastapi-backend/app/services/rag_faiss.py`

**File:** `fastapi-backend/app/services/rag_faiss.py`

**Summary:** RAG Pipeline: semantic chunking, embedding, and FAISS retrieval for LUMI.

### `_index_is_stale`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `42-48`
- **Signature:** `def _index_is_stale() -> bool:`
- **Purpose:** Return True if the knowledge base JSON is newer than the FAISS index.

**Code:**
```python
def _index_is_stale() -> bool:
    """Return True if the knowledge base JSON is newer than the FAISS index."""
    if not KNOWLEDGE_JSON_PATH.exists():
        return False  # no knowledge base to compare
    if not INDEX_PATH.exists():
        return True
    return KNOWLEDGE_JSON_PATH.stat().st_mtime > INDEX_PATH.stat().st_mtime
```

**Explanation:** It accepts zero arguments and returns `bool`. See the code below for the full implementation. Key calls include `exists()`, `stat()`.

### `_get_embedder`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `62-74`
- **Signature:** `def _get_embedder(model_name: str = DEFAULT_EMBEDDING_MODEL):`
- **Purpose:** Handles  get embedder.

**Code:**
```python
def _get_embedder(model_name: str = DEFAULT_EMBEDDING_MODEL):
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for RAG. "
                "Add it to fastapi-backend/requirements.txt"
            ) from exc
        logger.info("Loading embedding model %s ...", model_name)
        _embedder = SentenceTransformer(model_name)
    return _embedder
```

**Explanation:** It accepts `model_name`. See the code below for the full implementation. Key calls include `info()`, `SentenceTransformer()`, `ImportError()`.

### `_sentences`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `81-86`
- **Signature:** `def _sentences(text: str) -> list[str]:`
- **Purpose:** Split text into sentences without breaking on decimals or abbreviations.

**Code:**
```python
def _sentences(text: str) -> list[str]:
    """Split text into sentences without breaking on decimals or abbreviations."""
    # Simple regex that preserves decimal numbers and common abbreviations
    pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p.strip()]
```

**Explanation:** It accepts `text` and returns `list[str]`. See the code below for the full implementation. Key calls include `split()`, `strip()`.

### `_semantic_chunks`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `89-134`
- **Signature:** `def _semantic_chunks(`
- **Purpose:** Build chunks that respect sentence boundaries.

**Code:**
```python
def _semantic_chunks(
    text: str,
    max_words: int = 150,
    overlap_sentences: int = 1,
) -> list[str]:
    """
    Build chunks that respect sentence boundaries.

    Strategy:
    - Walk through sentences.
    - Add sentences to current chunk while word count <= max_words.
    - When the next sentence would overflow, emit chunk and start next chunk
      with the last *overlap_sentences* sentence(s) for continuity.
    """
    sents = _sentences(text)
    if not sents:
        return [text] if text.strip() else []

    # If the whole text is small enough, keep it as one chunk
    total_words = len(text.split())
    if total_words <= max_words:
        return [text]

    chunks: list[str] = []
    current_sents: list[str] = []
    current_words = 0

    for sent in sents:
        sent_words = len(sent.split())
        if current_words + sent_words > max_words and current_sents:
            chunks.append(" ".join(current_sents))
            # overlap
            if overlap_sentences > 0:
                current_sents = current_sents[-overlap_sentences:] + [sent]
                current_words = sum(len(s.split()) for s in current_sents)
            else:
                current_sents = [sent]
                current_words = sent_words
        else:
            current_sents.append(sent)
            current_words += sent_words

    if current_sents:
        chunks.append(" ".join(current_sents))

    return chunks
```

**Explanation:** It accepts `text`, `max_words`, `overlap_sentences` and returns `list[str]`. See the code below for the full implementation. Key calls include `_sentences()`, `strip()`, `len()`, `split()`, `append()`.

### `_clean_text`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `137-142`
- **Signature:** `def _clean_text(text: str) -> str:`
- **Purpose:** Handles  clean text.

**Code:**
```python
def _clean_text(text: str) -> str:
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `sub()`, `strip()`.

### `_chunk_documents`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `149-167`
- **Signature:** `def _chunk_documents(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:`
- **Purpose:** Turn knowledge documents into chunked records with preserved metadata.

**Code:**
```python
def _chunk_documents(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Turn knowledge documents into chunked records with preserved metadata.
    """
    chunks: list[dict[str, Any]] = []
    for doc in docs:
        content = _clean_text(doc.get("content", ""))
        if not content:
            continue

        for chunk_text in _semantic_chunks(content):
            chunks.append({
                "text": chunk_text,
                "renewable_type": doc.get("renewable_type", ""),
                "category": doc.get("category", ""),
                "product_type": doc.get("product_type", ""),
                "sources": doc.get("sources", []),
            })
    return chunks
```

**Explanation:** It accepts `docs` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_clean_text()`, `_semantic_chunks()`, `get()`, `append()`.

### `build_faiss_index`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `174-229`
- **Signature:** `def build_faiss_index(`
- **Purpose:** Build a FAISS index from knowledge documents.

**Code:**
```python
def build_faiss_index(
    docs: list[dict[str, Any]],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    save: bool = True,
) -> dict[str, Any]:
    """
    Build a FAISS index from knowledge documents.

    Returns metadata about the index.  The index itself is kept in memory
    and optionally written to disk.
    """
    global _index, _chunks

    try:
        import faiss
    except ImportError as exc:
        raise ImportError(
            "faiss-cpu is required for RAG. Add it to fastapi-backend/requirements.txt"
        ) from exc

    chunks = _chunk_documents(docs)
    if not chunks:
        raise ValueError("No chunks generated from documents")

    texts = [c["text"] for c in chunks]
    embedder = _get_embedder(model_name)
    logger.info("Encoding %s chunks ...", len(texts))
    embeddings = embedder.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    embeddings = embeddings.astype("float32")

    # Inner-product index on *normalized* vectors = cosine similarity
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    _index = index
    _chunks = chunks

    if save:
        faiss.write_index(index, str(INDEX_PATH))
        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        logger.info("Saved FAISS index to %s", INDEX_PATH)

    return {
        "documents": len(docs),
        "chunks": len(chunks),
        "dimension": dimension,
        "index_path": str(INDEX_PATH),
        "chunks_path": str(CHUNKS_PATH),
    }
```

**Explanation:** It accepts `docs`, `model_name`, `save` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `ImportError()`, `_chunk_documents()`, `ValueError()`, `_get_embedder()`, `info()`.

### `load_faiss_index`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `232-262`
- **Signature:** `def load_faiss_index(`
- **Purpose:** Load a previously built FAISS index from disk.

**Code:**
```python
def load_faiss_index(
    index_path: Path = INDEX_PATH,
    chunks_path: Path = CHUNKS_PATH,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> bool:
    """
    Load a previously built FAISS index from disk.

    Returns True if loaded successfully, False if files are missing.
    """
    global _index, _chunks

    if not index_path.exists() or not chunks_path.exists():
        logger.warning("FAISS index or chunks file missing; needs rebuild.")
        return False

    try:
        import faiss
    except ImportError:
        logger.error("faiss-cpu not installed")
        return False

    _index = faiss.read_index(str(index_path))
    with open(chunks_path, "r", encoding="utf-8") as f:
        _chunks = json.load(f)

    # sanity-check embedder is loadable (we don't need it yet, but we want early failure)
    _get_embedder(model_name)

    logger.info("Loaded FAISS index with %s chunks", len(_chunks))
    return True
```

**Explanation:** It accepts `index_path`, `chunks_path`, `model_name` and returns `bool`. See the code below for the full implementation. Key calls include `warning()`, `exists()`, `error()`, `read_index()`, `str()`.

### `ensure_index_built`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `265-294`
- **Signature:** `def ensure_index_built(`
- **Purpose:** Idempotent helper: load existing index, or build from *docs* if missing.

**Code:**
```python
def ensure_index_built(
    docs: list[dict[str, Any]] | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> None:
    """
    Idempotent helper: load existing index, or build from *docs* if missing.
    If the knowledge-base JSON is also missing or newer than the index, rebuild.
    """
    global _index, _chunks
    if _index is not None and not _index_is_stale():
        return
    if _index_is_stale():
        logger.info("Knowledge base is newer than FAISS index; rebuilding index...")
        _index = None
        _chunks = []
    elif load_faiss_index(model_name=model_name):
        return
    if docs is None:
        from app.services.rag_knowledge_builder import (
            build_knowledge_base,
            load_knowledge_base,
            save_knowledge_base,
        )
        try:
            docs = load_knowledge_base()
        except FileNotFoundError:
            logger.info("Knowledge base JSON missing; rebuilding from CSV...")
            docs = build_knowledge_base()
            save_knowledge_base(docs)
    build_faiss_index(docs, model_name=model_name)
```

**Explanation:** It accepts `docs`, `model_name` and returns `None`. See the code below for the full implementation. Key calls include `_index_is_stale()`, `info()`, `load_faiss_index()`, `load_knowledge_base()`, `build_knowledge_base()`.

### `_rag_cache_key`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `301-312`
- **Signature:** `def _rag_cache_key(`
- **Purpose:** Stable cache key for a retrieval call.

**Code:**
```python
def _rag_cache_key(
    query: str,
    model_name: str,
    top_k: int,
    score_threshold: float,
    renewable_type: str | None,
    category: str | None,
) -> str:
    """Stable cache key for a retrieval call."""
    payload = f"{query}:{model_name}:{top_k}:{score_threshold}:{renewable_type}:{category}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return f"{_RAG_CACHE_PREFIX}:{digest}"
```

**Explanation:** It accepts `query`, `model_name`, `top_k`, `score_threshold`, `renewable_type`, `category` and returns `str`. See the code below for the full implementation. Key calls include `hexdigest()`, `sha256()`, `encode()`.

### `_query_tokens`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `315-317`
- **Signature:** `def _query_tokens(query: str) -> set[str]:`
- **Purpose:** Simple lowercase, non-empty token set for keyword matching.

**Code:**
```python
def _query_tokens(query: str) -> set[str]:
    """Simple lowercase, non-empty token set for keyword matching."""
    return {t.lower() for t in re.findall(r"\b\w+\b", query) if len(t) > 2}
```

**Explanation:** It accepts `query` and returns `set[str]`. See the code below for the full implementation. Key calls include `lower()`, `findall()`, `len()`.

### `_keyword_score`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `320-329`
- **Signature:** `def _keyword_score(query: str, text: str) -> float:`
- **Purpose:** Jaccard-ish overlap between query and chunk tokens.

**Code:**
```python
def _keyword_score(query: str, text: str) -> float:
    """Jaccard-ish overlap between query and chunk tokens."""
    q = _query_tokens(query)
    if not q:
        return 0.0
    t = {tok.lower() for tok in re.findall(r"\b\w+\b", text) if len(tok) > 2}
    if not t:
        return 0.0
    overlap = len(q & t)
    return overlap / len(q)
```

**Explanation:** It accepts `query`, `text` and returns `float`. See the code below for the full implementation. Key calls include `_query_tokens()`, `lower()`, `findall()`, `len()`.

### `_hybrid_score`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `332-357`
- **Signature:** `def _hybrid_score(`
- **Purpose:** Combine semantic similarity, keyword overlap, and metadata boosts.

**Code:**
```python
def _hybrid_score(
    semantic_score: float,
    keyword_score: float,
    chunk: dict[str, Any],
    query: str,
    renewable_type: str | None,
    category: str | None,
) -> float:
    """Combine semantic similarity, keyword overlap, and metadata boosts."""
    score = 0.7 * semantic_score + 0.3 * keyword_score

    # Normalize query for matching
    q = query.lower()

    # Metadata boost when explicit filters match
    if renewable_type and chunk.get("renewable_type", "").lower() == renewable_type.lower():
        score += 0.05
    if category and chunk.get("category", "").lower() == category.lower():
        score += 0.05

    # Soft boost if the renewable type keyword appears in the query
    rtype = chunk.get("renewable_type", "").lower()
    if rtype and rtype in q:
        score += 0.04

    return min(score, 1.0)
```

**Explanation:** It accepts `semantic_score`, `keyword_score`, `chunk`, `query`, `renewable_type`, `category` and returns `float`. See the code below for the full implementation. Key calls include `lower()`, `get()`, `min()`.

### `_rerank_results`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `360-380`
- **Signature:** `def _rerank_results(`
- **Purpose:** Re-rank candidates using semantic + keyword + metadata signals.

**Code:**
```python
def _rerank_results(
    query: str,
    candidates: list[dict[str, Any]],
    renewable_type: str | None,
    category: str | None,
) -> list[dict[str, Any]]:
    """Re-rank candidates using semantic + keyword + metadata signals."""
    for c in candidates:
        c["hybrid_score"] = round(
            _hybrid_score(
                c.get("score", 0.0),
                _keyword_score(query, c.get("text", "")),
                c,
                query,
                renewable_type,
                category,
            ),
            4,
        )
    ranked = sorted(candidates, key=lambda x: x["hybrid_score"], reverse=True)
    return [{**c, "score": c["hybrid_score"]} for c in ranked]
```

**Explanation:** It accepts `query`, `candidates`, `renewable_type`, `category` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `round()`, `_hybrid_score()`, `get()`, `_keyword_score()`, `sorted()`.

### `retrieve_context`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `383-453`
- **Signature:** `def retrieve_context(`
- **Purpose:** Retrieve the most semantically similar chunks for a query.

**Code:**
```python
def retrieve_context(
    query: str,
    top_k: int = 5,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    """
    Retrieve the most semantically similar chunks for a query.

    Uses FAISS for approximate semantic search, then re-ranks with keyword
    overlap and metadata boosts.  Results are short-cached in Redis.
    """
    cache_key = _rag_cache_key(query, model_name, top_k, score_threshold, None, None)
    if use_cache:
        try:
            redis = get_redis_sync()
            cached = redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as exc:
            logger.debug("RAG cache read failed: %s", exc)

    if _index is None:
        ensure_index_built(model_name=model_name)

    if _index is None or not _chunks:
        raise RuntimeError("FAISS index is not available")

    # Retrieve extra candidates so reranking has a good candidate pool.
    fetch_k = max(top_k * 4, 20)
    embedder = _get_embedder(model_name)
    query_emb = embedder.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    query_emb = query_emb.astype("float32")

    scores, indices = _index.search(query_emb, fetch_k)
    candidates: list[dict[str, Any]] = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_chunks):
            continue
        if score < score_threshold:
            continue
        chunk = _chunks[idx]
        candidates.append({
            "text": chunk["text"],
            "score": round(float(score), 4),
            "renewable_type": chunk.get("renewable_type", ""),
            "category": chunk.get("category", ""),
            "product_type": chunk.get("product_type", ""),
            "sources": chunk.get("sources", []),
        })

    ranked = _rerank_results(query, candidates, None, None)[:top_k]

    if use_cache:
        try:
            redis = get_redis_sync()
            redis.setex(
                cache_key,
                _RAG_CACHE_TTL_SECONDS,
                json.dumps(ranked, default=str),
            )
        except Exception as exc:
            logger.debug("RAG cache write failed: %s", exc)

    return ranked
```

**Explanation:** It accepts `query`, `top_k`, `model_name`, `score_threshold`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_rag_cache_key()`, `get_redis_sync()`, `get()`, `loads()`, `debug()`.

### `retrieve_with_filter`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `456-505`
- **Signature:** `def retrieve_with_filter(`
- **Purpose:** Same as retrieve_context but allows post-filtering by metadata fields.

**Code:**
```python
def retrieve_with_filter(
    query: str,
    top_k: int = 5,
    renewable_type: str | None = None,
    category: str | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    """
    Same as retrieve_context but allows post-filtering by metadata fields.
    Retrieves more candidates than top_k so filtering still yields results.
    """
    cache_key = _rag_cache_key(query, model_name, top_k, score_threshold, renewable_type, category)
    if use_cache:
        try:
            redis = get_redis_sync()
            cached = redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as exc:
            logger.debug("RAG filtered cache read failed: %s", exc)

    candidates = retrieve_context(
        query,
        top_k=top_k * 4,
        model_name=model_name,
        score_threshold=score_threshold,
        use_cache=False,
    )

    if renewable_type:
        candidates = [c for c in candidates if c.get("renewable_type", "").lower() == renewable_type.lower()]
    if category:
        candidates = [c for c in candidates if c.get("category", "").lower() == category.lower()]

    ranked = _rerank_results(query, candidates, renewable_type, category)[:top_k]

    if use_cache:
        try:
            redis = get_redis_sync()
            redis.setex(
                cache_key,
                _RAG_CACHE_TTL_SECONDS,
                json.dumps(ranked, default=str),
            )
        except Exception as exc:
            logger.debug("RAG filtered cache write failed: %s", exc)

    return ranked
```

**Explanation:** It accepts `query`, `top_k`, `renewable_type`, `category`, `model_name`, `score_threshold`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_rag_cache_key()`, `get_redis_sync()`, `get()`, `loads()`, `debug()`.

### `index_stats`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `512-518`
- **Signature:** `def index_stats() -> dict[str, Any]:`
- **Purpose:** Handles index stats.

**Code:**
```python
def index_stats() -> dict[str, Any]:
    return {
        "chunks_loaded": len(_chunks) if _chunks is not None else 0,
        "index_present": _index is not None,
        "index_path_exists": INDEX_PATH.exists(),
        "chunks_path_exists": CHUNKS_PATH.exists(),
    }
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `exists()`, `len()`.

### `sample_chunks`

- **File:** `fastapi-backend/app/services/rag_faiss.py`
- **Lines:** `521-525`
- **Signature:** `def sample_chunks(n: int = 3) -> list[dict[str, Any]]:`
- **Purpose:** Return a sample of stored chunks for debugging.

**Code:**
```python
def sample_chunks(n: int = 3) -> list[dict[str, Any]]:
    """Return a sample of stored chunks for debugging."""
    if _chunks is None:
        return []
    return _chunks[:n]
```

**Explanation:** It accepts `n` and returns `list[dict[str, Any]]`. See the code below for the full implementation.


## `fastapi-backend/app/services/rag_gemini_funcs.py`

**File:** `fastapi-backend/app/services/rag_gemini_funcs.py`

**Summary:** Source file `fastapi-backend/app/services/rag_gemini_funcs.py`.

### `_build_rag_prompt`

- **File:** `fastapi-backend/app/services/rag_gemini_funcs.py`
- **Lines:** `16-56`
- **Signature:** `def _build_rag_prompt(`
- **Purpose:** Handles  build rag prompt.

**Code:**
```python
def _build_rag_prompt(
    analysis_payload: dict[str, Any],
    user_query: str,
    retrieved_context: list[dict[str, Any]],
) -> str:
    simulation_payload = json.dumps(analysis_payload, ensure_ascii=True, indent=2)
    context_payload = json.dumps(retrieved_context, ensure_ascii=True, indent=2)

    return (
        "You are LUMI, an AI assistant for renewable energy decision support in the Philippines.\n\n"
        "GROUNDING RULES (STRICT):\n"
        "1. ALL facts, figures, and data in your response MUST come from the RETRIEVED KNOWLEDGE below.\n"
        "2. If the retrieved knowledge does not contain a specific number or fact, say so—do NOT hallucinate.\n"
        "3. Cite the relevant category when using data (e.g., 'solar panel equipment cost', 'national_energy_statistics', 'municipality_climate', 'terrain_metrics').\n"
        "4. Use the ECOSIM DATA to tailor recommendations to the municipality's climate and generation potential.\n"
        "5. Use NATIONAL ENERGY STATISTICS for context on Philippine energy trends, grid composition, and peak demand.\n"
        "6. Use MUNICIPALITY CLIMATE data to discuss local solar, wind, and temperature conditions.\n"
        "7. Use TERRAIN METRICS when discussing hydropower suitability or site-specific topography.\n"
        "8. Use GEOTHERMAL SUITABILITY data when discussing geothermal potential, fault lines, volcano proximity, and heat flow.\n"
        "9. Use HYDROPOWER SUITABILITY data when discussing stream flow, hydraulic head, and runoff potential.\n"
        "10. Do not use your internal parametric knowledge for Philippine-specific data—rely only on the retrieved knowledge.\n\n"
        "OUTPUT FORMAT: Return PLAIN TEXT only. Do NOT use JSON, markdown code blocks, bullet-point key-value formatting, or raw brackets.\n"
        "Write in clear paragraphs suitable for students and community members.\n\n"
        "STRUCTURE YOUR RESPONSE IN THESE EXACT SECTIONS:\n\n"
        "1. OBSERVATION — What does the data show?\n"
        "   Summarise the municipality's climate, terrain, and energy conditions using the ECOSIM DATA.\n\n"
        "2. INTERPRETATION — What does this mean for energy generation?\n"
        "   Explain how these conditions affect solar, wind, hydro, and geothermal potential.\n\n"
        "3. RECOMMENDATION — What renewable energy option should the user consider?\n"
        "   State clearly the best renewable source for this location and why. Include estimated generation, "
        "   approximate budget ranges in PHP (labelled as estimates), and payback expectations.\n\n"
        "4. REASON — Why is this the best choice compared to alternatives?\n"
        "   Compare against other renewable options and cite limitations or caveats from the retrieved knowledge.\n\n"
        "SYSTEM CONTEXT: LUMI renewable energy decision support\n\n"
        "ECOSIM DATA (municipality climate + generation estimates):\n"
        f"{simulation_payload}\n\n"
        "RETRIEVED KNOWLEDGE (use ONLY this for all facts and figures in your response):\n"
        f"{context_payload}\n\n"
        "USER QUESTION:\n"
        f"{user_query}\n"
    )
```

**Explanation:** It accepts `analysis_payload`, `user_query`, `retrieved_context` and returns `str`. See the code below for the full implementation. Key calls include `dumps()`.

### `_normalize_rag_output`

- **File:** `fastapi-backend/app/services/rag_gemini_funcs.py`
- **Lines:** `63-112`
- **Signature:** `def _normalize_rag_output(data: dict[str, Any]) -> dict[str, Any]:`
- **Purpose:** Normalise the RAG JSON into the shape expected by the ecosim layer,

**Code:**
```python
def _normalize_rag_output(data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalise the RAG JSON into the shape expected by the ecosim layer,
    while preserving the richer RAG-specific fields.
    """
    output: dict[str, Any] = {
        "recommended_energy_source": "",
        "estimated_budget": {
            "equipment": [],
            "installation": "",
            "maintenance": "",
        },
        "cost_range": "",
        "explanation": "",
        "limitations": "",
        # backward-compatible keys so callers that expect the old shape still get something reasonable
        "summary": "",
        "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
        "recommendation": {"best_option": "", "reason": ""},
        "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
        "environmental_impact": "",
    }

    if not isinstance(data, dict):
        return output

    # Map new keys -> output
    for key in ("recommended_energy_source", "cost_range", "explanation", "limitations"):
        if key in data:
            output[key] = data[key]

    if isinstance(data.get("estimated_budget"), dict):
        output["estimated_budget"].update(data["estimated_budget"])

    # Build backward-compatible fields from the new RAG fields
    output["summary"] = output["explanation"]
    output["recommendation"]["best_option"] = output["recommended_energy_source"]
    output["recommendation"]["reason"] = output["explanation"]

    # Populate cost_estimation for the recommended source
    source = output["recommended_energy_source"]
    if source:
        output["cost_estimation"][source] = {
            "equipment": output["estimated_budget"].get("equipment", []),
            "installation": output["estimated_budget"].get("installation", ""),
            "maintenance": output["estimated_budget"].get("maintenance", ""),
            "total_range": output["cost_range"],
        }

    return output
```

**Explanation:** It accepts `data` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `isinstance()`, `get()`, `update()`.

### `_smart_retrieve`

- **File:** `fastapi-backend/app/services/rag_gemini_funcs.py`
- **Lines:** `119-160`
- **Signature:** `def _smart_retrieve(`
- **Purpose:** Retrieve context using the new pipeline, with an optional boost for the

**Code:**
```python
def _smart_retrieve(
    user_query: str,
    analysis_payload: dict[str, Any],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve context using the new pipeline, with an optional boost for the
    best-scoring renewable source found in the simulation data.
    """
    # Ensure the knowledge base & index are ready
    rag_pipeline.ensure_index_built()

    # Try to detect which renewable source the query is about
    renewable_hint: str | None = None
    query_lower = user_query.lower()
    if "solar" in query_lower or "sun" in query_lower or "pv" in query_lower:
        renewable_hint = "solar"
    elif "wind" in query_lower or "turbine" in query_lower:
        renewable_hint = "wind"
    elif "hydro" in query_lower or "water" in query_lower or "hydropower" in query_lower:
        renewable_hint = "hydro"
    elif "geothermal" in query_lower or "heat" in query_lower or "volcano" in query_lower:
        renewable_hint = "geothermal"

    results = rag_pipeline.retrieve_context(user_query, top_k=top_k)

    # If we have a hint and not enough strong matches, do a second targeted retrieval
    if renewable_hint and len(results) < top_k:
        filtered = rag_pipeline.retrieve_with_filter(
            user_query,
            top_k=top_k,
            renewable_type=renewable_hint,
        )
        # Merge without duplicates (by text)
        seen = {r["text"] for r in results}
        for r in filtered:
            if r["text"] not in seen:
                results.append(r)
                seen.add(r["text"])
        results = results[:top_k]

    return results
```

**Explanation:** It accepts `user_query`, `analysis_payload`, `top_k` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `ensure_index_built()`, `lower()`, `retrieve_context()`, `retrieve_with_filter()`, `len()`.

### `analyze_with_rag`

- **File:** `fastapi-backend/app/services/rag_gemini_funcs.py`
- **Lines:** `167-214`
- **Signature:** `def analyze_with_rag(`
- **Purpose:** Handles analyze with rag.

**Code:**
```python
def analyze_with_rag(
    analysis_payload: dict[str, Any],
    user_query: str,
    top_k: int = 5,
) -> dict[str, Any]:
    try:
        retrieved_context = _smart_retrieve(user_query, analysis_payload, top_k=top_k)

        if not retrieved_context:
            logger.warning("RAG retrieved zero relevant chunks for query: %s", user_query)

        prompt = _build_rag_prompt(analysis_payload, user_query, retrieved_context)
        response_text = generate_response(prompt)

        from app.services.llm_sanitizer import sanitize_llm_output, extract_prescriptive_recommendation
        cleaned = sanitize_llm_output(response_text)
        prescriptive = extract_prescriptive_recommendation(cleaned)

        return {
            "recommended_energy_source": prescriptive.get("recommendation", ""),
            "estimated_budget": {"equipment": [], "installation": "", "maintenance": ""},
            "cost_range": "",
            "explanation": cleaned,
            "limitations": "",
            "summary": cleaned,
            "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
            "recommendation": {
                "best_option": prescriptive.get("recommendation", ""),
                "reason": prescriptive.get("reason", ""),
            },
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
            "environmental_impact": "",
            "prescriptive_recommendation": prescriptive,
        }
    except Exception:
        logger.exception("LLM RAG analysis failed")
        return {
            "recommended_energy_source": "",
            "estimated_budget": {"equipment": [], "installation": "", "maintenance": ""},
            "cost_range": "",
            "explanation": "LLM RAG analysis failed.",
            "limitations": "",
            "summary": "LLM RAG analysis failed.",
            "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
            "recommendation": {"best_option": "", "reason": ""},
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
            "environmental_impact": "",
        }
```

**Explanation:** It accepts `analysis_payload`, `user_query`, `top_k` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_smart_retrieve()`, `_build_rag_prompt()`, `generate_response()`, `sanitize_llm_output()`, `extract_prescriptive_recommendation()`.


## `fastapi-backend/app/services/rag_hybrid.py`

**File:** `fastapi-backend/app/services/rag_hybrid.py`

**Summary:** Hybrid search and reranking for LUMI RAG pipeline.

### `_tokenize`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `28-30`
- **Signature:** `def _tokenize(text: str) -> list[str]:`
- **Purpose:** Simple tokenizer: lowercase, split on non-alphanumeric.

**Code:**
```python
def _tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, split on non-alphanumeric."""
    return re.findall(r"[a-z0-9]+", text.lower())
```

**Explanation:** It accepts `text` and returns `list[str]`. See the code below for the full implementation. Key calls include `findall()`, `lower()`.

### `_bm25_scores`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `33-83`
- **Signature:** `def _bm25_scores(`
- **Purpose:** Compute BM25 scores for documents given a query.

**Code:**
```python
def _bm25_scores(
    query: str,
    documents: list[str],
    k1: float = 1.5,
    b: float = 0.75,
) -> list[float]:
    """Compute BM25 scores for documents given a query.

    Args:
        query: Search query
        documents: List of document texts
        k1: Term frequency saturation parameter
        b: Length normalization parameter

    Returns:
        List of BM25 scores (same length as documents)
    """
    if not documents:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return [0.0] * len(documents)

    # Tokenize all documents
    doc_tokens = [_tokenize(doc) for doc in documents]
    doc_lengths = [len(tokens) for tokens in doc_tokens]
    avg_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0

    # Document frequency for each query term
    df: dict[str, int] = {}
    for term in set(query_tokens):
        df[term] = sum(1 for tokens in doc_tokens if term in tokens)

    n = len(documents)
    scores = [0.0] * n

    for i, tokens in enumerate(doc_tokens):
        tf = Counter(tokens)
        doc_len = doc_lengths[i]

        for term in query_tokens:
            if term not in tf:
                continue

            idf = math.log((n - df[term] + 0.5) / (df[term] + 0.5) + 1)
            tf_val = tf[term]
            score = idf * (tf_val * (k1 + 1)) / (tf_val + k1 * (1 - b + b * doc_len / avg_length))
            scores[i] += score

    return scores
```

**Explanation:** It accepts `query`, `documents`, `k1`, `b` and returns `list[float]`. See the code below for the full implementation. Key calls include `_tokenize()`, `len()`, `sum()`, `set()`, `enumerate()`.

### `_reciprocal_rank_fusion`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `90-132`
- **Signature:** `def _reciprocal_rank_fusion(`
- **Purpose:** Fuse semantic and keyword results using Reciprocal Rank Fusion (RRF).

**Code:**
```python
def _reciprocal_rank_fusion(
    semantic_results: list[dict[str, Any]],
    keyword_results: list[tuple[int, float]],
    k: int = 60,
) -> list[dict[str, Any]]:
    """Fuse semantic and keyword results using Reciprocal Rank Fusion (RRF).

    Args:
        semantic_results: Results from FAISS semantic search
        keyword_results: List of (chunk_index, bm25_score) tuples
        k: RRF constant (default 60)

    Returns:
        Fused results sorted by combined RRF score
    """
    # Build rank maps
    semantic_rank: dict[int, int] = {}
    for rank, result in enumerate(semantic_results):
        # Use text hash as identifier
        text_hash = hash(result.get("text", ""))
        semantic_rank[text_hash] = rank + 1

    keyword_rank: dict[int, int] = {}
    for rank, (idx, _) in enumerate(sorted(keyword_results, key=lambda x: x[1], reverse=True)):
        keyword_rank[idx] = rank + 1

    # Compute RRF scores for semantic results
    fused: list[dict[str, Any]] = []
    for result in semantic_results:
        text_hash = hash(result.get("text", ""))
        rrf_score = 0.0
        if text_hash in semantic_rank:
            rrf_score += 1.0 / (k + semantic_rank[text_hash])
        # Add keyword contribution if this chunk has a BM25 score
        # (we'll match by index approximation)
        rrf_score += result.get("score", 0) * 0.01  # small semantic score boost
        result_copy = dict(result)
        result_copy["fused_score"] = round(rrf_score, 6)
        fused.append(result_copy)

    # Sort by fused score
    fused.sort(key=lambda x: x["fused_score"], reverse=True)
    return fused
```

**Explanation:** It accepts `semantic_results`, `keyword_results`, `k` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `enumerate()`, `hash()`, `get()`, `sorted()`, `dict()`.

### `hybrid_search`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `139-202`
- **Signature:** `def hybrid_search(`
- **Purpose:** Hybrid search combining semantic (FAISS) and keyword (BM25) retrieval.

**Code:**
```python
def hybrid_search(
    query: str,
    top_k: int = 5,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
    renewable_type: str | None = None,
    score_threshold: float = 0.15,
) -> list[dict[str, Any]]:
    """Hybrid search combining semantic (FAISS) and keyword (BM25) retrieval.

    Args:
        query: Search query
        top_k: Number of results to return
        semantic_weight: Weight for semantic scores (0-1)
        keyword_weight: Weight for keyword scores (0-1)
        renewable_type: Optional filter
        score_threshold: Minimum fused score

    Returns:
        List of result dicts with text, score, fused_score, sources, metadata
    """
    # Semantic search (retrieve more candidates for fusion)
    semantic_candidates = retrieve_context(
        query,
        top_k=top_k * 4,
        score_threshold=0.15,
    )

    if renewable_type:
        filtered = retrieve_with_filter(
            query,
            top_k=top_k * 2,
            renewable_type=renewable_type,
        )
        seen = {r["text"] for r in semantic_candidates}
        for r in filtered:
            if r["text"] not in seen:
                semantic_candidates.append(r)
                seen.add(r["text"])

    if not semantic_candidates:
        return []

    # Keyword search (BM25) over candidate texts
    candidate_texts = [c.get("text", "") for c in semantic_candidates]
    bm25_scores = _bm25_scores(query, candidate_texts)

    # Normalize BM25 scores to 0-1
    max_bm25 = max(bm25_scores) if bm25_scores and max(bm25_scores) > 0 else 1.0
    normalized_bm25 = [s / max_bm25 for s in bm25_scores]

    # Normalize semantic scores (already 0-1 from cosine similarity)
    max_sem = max(c.get("score", 0) for c in semantic_candidates) or 1.0
    for i, c in enumerate(semantic_candidates):
        sem_score = c.get("score", 0) / max_sem
        kw_score = normalized_bm25[i] if i < len(normalized_bm25) else 0.0
        c["fused_score"] = round(semantic_weight * sem_score + keyword_weight * kw_score, 6)

    # Sort by fused score
    semantic_candidates.sort(key=lambda x: x.get("fused_score", 0), reverse=True)

    # Filter by threshold and limit
    results = [c for c in semantic_candidates if c.get("fused_score", 0) >= score_threshold]
    return results[:top_k]
```

**Explanation:** It accepts `query`, `top_k`, `semantic_weight`, `keyword_weight`, `renewable_type`, `score_threshold` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `retrieve_context()`, `retrieve_with_filter()`, `append()`, `add()`, `get()`.

### `rerank_results`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `209-262`
- **Signature:** `def rerank_results(`
- **Purpose:** Rerank retrieval results using a reranking method.

**Code:**
```python
def rerank_results(
    query: str,
    results: list[dict[str, Any]],
    top_k: int = 5,
    method: str = "heuristic",
) -> list[dict[str, Any]]:
    """Rerank retrieval results using a reranking method.

    Args:
        query: Original query
        results: Results from hybrid search
        top_k: Number of results to return after reranking
        method: 'heuristic' or 'cross-encoder'

    Returns:
        Reranked results
    """
    if not results:
        return []

    if method == "cross-encoder":
        try:
            from sentence_transformers import CrossEncoder
            model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            pairs = [(query, r.get("text", "")) for r in results]
            scores = model.predict(pairs)
            for i, score in enumerate(scores):
                results[i]["rerank_score"] = float(score)
            results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
            return results[:top_k]
        except Exception as exc:
            logger.warning("Cross-encoder reranking failed, falling back to heuristic: %s", exc)

    # Heuristic reranking: boost results with source citations and exact term matches
    query_terms = set(_tokenize(query))
    for result in results:
        text = result.get("text", "").lower()
        sources = result.get("sources", [])

        # Term overlap boost
        text_terms = set(_tokenize(text))
        overlap = len(query_terms & text_terms) / max(len(query_terms), 1)

        # Source citation boost
        has_source = 1.0 if sources else 0.0

        # Renewable type match boost
        type_boost = 0.1 if result.get("renewable_type") else 0.0

        base_score = result.get("fused_score", result.get("score", 0))
        result["rerank_score"] = round(base_score + 0.15 * overlap + 0.1 * has_source + type_boost, 6)

    results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
    return results[:top_k]
```

**Explanation:** It accepts `query`, `results`, `top_k`, `method` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `CrossEncoder()`, `predict()`, `enumerate()`, `sort()`, `float()`.

### `verify_citations`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `269-345`
- **Signature:** `def verify_citations(`
- **Purpose:** Verify that citations in the LLM response match retrieved sources.

**Code:**
```python
def verify_citations(
    response_text: str,
    retrieved_chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Verify that citations in the LLM response match retrieved sources.

    Checks:
    - [Source N] references in the response
    - Each reference corresponds to a retrieved chunk
    - No fabricated citations

    Args:
        response_text: LLM-generated response
        retrieved_chunks: Chunks passed to the LLM as context

    Returns:
        Dict with verified citations, unverified references, and warnings
    """
    # Extract [Source N: Title] patterns
    citation_pattern = r"\[Source\s+(\d+)(?::\s*([^\]]+))?\]"
    found_citations = re.findall(citation_pattern, response_text)

    verified: list[dict[str, Any]] = []
    unverified: list[dict[str, Any]] = []
    warnings: list[str] = []

    for ref_num_str, ref_title in found_citations:
        ref_num = int(ref_num_str)
        if ref_num < 1 or ref_num > len(retrieved_chunks):
            unverified.append({
                "reference": f"[Source {ref_num}]",
                "reason": f"Source {ref_num} was not in the context (only {len(retrieved_chunks)} sources provided)",
            })
            warnings.append(f"Citation [Source {ref_num}] references a source not in context")
            continue

        chunk = retrieved_chunks[ref_num - 1]
        sources = chunk.get("sources", [])

        if ref_title:
            # Check if the title matches any source
            title_match = False
            for src in sources:
                if isinstance(src, dict):
                    src_title = src.get("title") or src.get("name") or ""
                    if ref_title.lower().strip() in src_title.lower() or src_title.lower() in ref_title.lower():
                        title_match = True
                        break

            if not title_match and sources:
                unverified.append({
                    "reference": f"[Source {ref_num}: {ref_title}]",
                    "reason": f"Title '{ref_title}' does not match any source title for chunk {ref_num}",
                    "actual_sources": sources,
                })
                warnings.append(f"Citation [Source {ref_num}: {ref_title}] title mismatch")
            else:
                verified.append({
                    "reference": f"[Source {ref_num}: {ref_title}]",
                    "chunk_index": ref_num - 1,
                    "sources": sources,
                })
        else:
            verified.append({
                "reference": f"[Source {ref_num}]",
                "chunk_index": ref_num - 1,
                "sources": sources,
            })

    return {
        "verified": verified,
        "unverified": unverified,
        "warnings": warnings,
        "total_citations": len(found_citations),
        "verified_count": len(verified),
        "unverified_count": len(unverified),
    }
```

**Explanation:** It accepts `response_text`, `retrieved_chunks` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `findall()`, `int()`, `get()`, `append()`, `len()`.

### `validate_input`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `361-381`
- **Signature:** `def validate_input(query: str) -> tuple[bool, str | None]:`
- **Purpose:** Validate user input before processing.

**Code:**
```python
def validate_input(query: str) -> tuple[bool, str | None]:
    """Validate user input before processing.

    Returns:
        (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query is empty."

    if len(query) > _MAX_QUERY_LENGTH:
        return False, f"Query exceeds maximum length of {_MAX_QUERY_LENGTH} characters."

    query_lower = query.lower()
    for keyword in _OFF_TOPIC_KEYWORDS:
        if keyword in query_lower:
            return False, (
                "Your query contains content that violates LUMI's usage policy. "
                "LUMI is a Renewable Energy Decision Support Assistant for the Philippines."
            )

    return True, None
```

**Explanation:** It accepts `query` and returns `tuple[bool, str | None]`. See the code below for the full implementation. Key calls include `strip()`, `len()`, `lower()`.

### `sanitize_output`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `384-396`
- **Signature:** `def sanitize_output(response_text: str) -> str:`
- **Purpose:** Sanitize LLM output: remove harmful content, enforce formatting.

**Code:**
```python
def sanitize_output(response_text: str) -> str:
    """Sanitize LLM output: remove harmful content, enforce formatting."""
    # Remove any HTML tags that might have been generated
    response_text = re.sub(r"<[^>]+>", "", response_text)

    # Remove any system prompt leaks
    response_text = re.sub(r"^(STEP \d+:.*?)(?:\n|$)", "", response_text, flags=re.MULTILINE)

    # Limit response length
    if len(response_text) > 4000:
        response_text = response_text[:4000] + "..."

    return response_text.strip()
```

**Explanation:** It accepts `response_text` and returns `str`. See the code below for the full implementation. Key calls include `sub()`, `len()`, `strip()`.

### `save_chat_message`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `403-444`
- **Signature:** `def save_chat_message(`
- **Purpose:** Save a chat message to Supabase.

**Code:**
```python
def save_chat_message(
    session_id: str,
    role: str,
    message: str,
    retrieved_chunks: list[dict[str, Any]] | None = None,
    citation_verification: dict[str, Any] | None = None,
) -> str | None:
    """Save a chat message to Supabase.

    Args:
        session_id: Chat session ID
        role: 'user' or 'assistant'
        message: Message text
        retrieved_chunks: RAG chunks used (for assistant messages)
        citation_verification: Citation verification result

    Returns:
        Message ID if saved, None on failure
    """
    try:
        import json as _json
        from datetime import datetime, timezone
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table("chat_messages")
            .insert({
                "session_id": session_id,
                "role": role,
                "content": message,
                "retrieved_context": _json.dumps(retrieved_chunks) if retrieved_chunks else None,
                "citation_verification": _json.dumps(citation_verification) if citation_verification else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
        if resp.data:
            return resp.data[0].get("id")
    except Exception as exc:
        logger.warning("Failed to save chat message: %s", exc)
    return None
```

**Explanation:** It accepts `session_id`, `role`, `message`, `retrieved_chunks`, `citation_verification` and returns `str | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `get()`, `warning()`, `insert()`.

### `get_chat_history`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `447-472`
- **Signature:** `def get_chat_history(session_id: str, limit: int = _MAX_CHAT_HISTORY) -> list[dict[str, Any]]:`
- **Purpose:** Retrieve chat history for a session.

**Code:**
```python
def get_chat_history(session_id: str, limit: int = _MAX_CHAT_HISTORY) -> list[dict[str, Any]]:
    """Retrieve chat history for a session.

    Args:
        session_id: Chat session ID
        limit: Maximum messages to return

    Returns:
        List of message dicts (oldest first)
    """
    try:
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table("chat_messages")
            .select("id,role,content,created_at")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception as exc:
        logger.warning("Failed to fetch chat history: %s", exc)
        return []
```

**Explanation:** It accepts `session_id`, `limit` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `warning()`, `limit()`, `order()`.

### `create_chat_session`

- **File:** `fastapi-backend/app/services/rag_hybrid.py`
- **Lines:** `475-498`
- **Signature:** `def create_chat_session(user_id: str | None = None) -> str | None:`
- **Purpose:** Create a new chat session.

**Code:**
```python
def create_chat_session(user_id: str | None = None) -> str | None:
    """Create a new chat session.

    Returns:
        Session ID if created, None on failure
    """
    try:
        from datetime import datetime, timezone
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table("chat_sessions")
            .insert({
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
        if resp.data:
            return resp.data[0].get("id")
    except Exception as exc:
        logger.warning("Failed to create chat session: %s", exc)
    return None
```

**Explanation:** It accepts `user_id` and returns `str | None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `get()`, `warning()`, `insert()`.


## `fastapi-backend/app/services/rag_knowledge_builder.py`

**File:** `fastapi-backend/app/services/rag_knowledge_builder.py`

**Summary:** Build structured renewable-energy knowledge documents from scraped product data

### `_enrich_sources`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `84-92`
- **Signature:** `def _enrich_sources(sources: list[str]) -> list[dict[str, str]]:`
- **Purpose:** Convert string source labels into structured source dicts.

**Code:**
```python
def _enrich_sources(sources: list[str]) -> list[dict[str, str]]:
    """Convert string source labels into structured source dicts."""
    enriched: list[dict[str, str]] = []
    for s in sources:
        if s in SOURCE_MAP:
            enriched.append(SOURCE_MAP[s].copy())
        else:
            enriched.append({"title": str(s), "url": "", "org": ""})
    return enriched
```

**Explanation:** It accepts `sources` and returns `list[dict[str, str]]`. See the code below for the full implementation. Key calls include `append()`, `copy()`, `str()`.

### `_normalize`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `141-142`
- **Signature:** `def _normalize(text: str) -> str:`
- **Purpose:** Handles  normalize.

**Code:**
```python
def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `sub()`, `strip()`, `lower()`.

### `classify_renewable`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `145-150`
- **Signature:** `def classify_renewable(name: str, source_file: str = "") -> str:`
- **Purpose:** Handles classify renewable.

**Code:**
```python
def classify_renewable(name: str, source_file: str = "") -> str:
    text = _normalize(name + " " + source_file)
    for rtype, keywords in RENEWABLE_RULES:
        if any(kw in text for kw in keywords):
            return rtype
    return ""
```

**Explanation:** It accepts `name`, `source_file` and returns `str`. See the code below for the full implementation. Key calls include `_normalize()`, `any()`.

### `classify_product_type`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `153-158`
- **Signature:** `def classify_product_type(name: str) -> str:`
- **Purpose:** Handles classify product type.

**Code:**
```python
def classify_product_type(name: str) -> str:
    text = _normalize(name)
    for ptype, keywords in PRODUCT_TYPE_RULES:
        if any(kw in text for kw in keywords):
            return ptype
    return ""
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `_normalize()`, `any()`.

### `to_php`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `161-162`
- **Signature:** `def to_php(price: float, currency: str) -> float:`
- **Purpose:** Handles to php.

**Code:**
```python
def to_php(price: float, currency: str) -> float:
    return price * CURRENCY_TO_PHP.get(currency.upper(), 1.0)
```

**Explanation:** It accepts `price`, `currency` and returns `float`. See the code below for the full implementation. Key calls include `get()`, `upper()`.

### `_currency_note`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `165-170`
- **Signature:** `def _currency_note(currency: str) -> str:`
- **Purpose:** Handles  currency note.

**Code:**
```python
def _currency_note(currency: str) -> str:
    if currency.upper() == "USD":
        return "converted from USD to PHP at approximate rate 1 USD = 60 PHP"
    if currency.upper() == "CNY":
        return "converted from CNY to PHP at approximate rate 1 CNY = 8.96 PHP"
    return ""
```

**Explanation:** It accepts `currency` and returns `str`. See the code below for the full implementation. Key calls include `upper()`.

### `load_and_fix_csv`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `177-208`
- **Signature:** `def load_and_fix_csv(csv_path: Path = DEFAULT_CSV) -> pd.DataFrame:`
- **Purpose:** Loads and fix csv.

**Code:**
```python
def load_and_fix_csv(csv_path: Path = DEFAULT_CSV) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})

    # Keep only rows that have a parseable price
    df["price_value_num"] = pd.to_numeric(df.get("price_value", pd.Series()), errors="coerce")
    df = df.dropna(subset=["price_value_num"])
    df["price_value_num"] = df["price_value_num"].astype(float)

    # Re-classify renewable type using name + source file
    df["renewable_type"] = df.apply(
        lambda r: classify_renewable(
            str(r.get("product_name", "")),
            str(r.get("source_file", "")),
        ),
        axis=1,
    )

    # Re-classify product type using product name
    df["product_type"] = df["product_name"].astype(str).apply(classify_product_type)

    # Drop rows we cannot classify at all
    df = df[df["renewable_type"] != ""].copy()

    # Convert prices to PHP
    df["currency"] = df.get("currency", "PHP").fillna("PHP")
    df["price_php"] = df.apply(lambda r: to_php(r["price_value_num"], r["currency"]), axis=1)

    return df
```

**Explanation:** It accepts `csv_path` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `exists()`, `FileNotFoundError()`, `read_csv()`, `rename()`, `lower()`.

### `_price_range_text`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `215-226`
- **Signature:** `def _price_range_text(values: list[float]) -> str:`
- **Purpose:** Handles  price range text.

**Code:**
```python
def _price_range_text(values: list[float]) -> str:
    if not values:
        return "No price data available."
    mn = min(values)
    mx = max(values)
    med = statistics.median(values)
    mean = statistics.mean(values)
    return (
        f"Prices range from PHP {mn:,.0f} to PHP {mx:,.0f}. "
        f"Median PHP {med:,.0f}, average PHP {mean:,.0f}. "
        f"Based on {len(values)} product listings."
    )
```

**Explanation:** It accepts `values` and returns `str`. See the code below for the full implementation. Key calls include `min()`, `max()`, `median()`, `mean()`, `len()`.

### `build_equipment_cost_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `229-257`
- **Signature:** `def build_equipment_cost_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:`
- **Purpose:** Aggregate price knowledge per renewable_type + product_type.

**Code:**
```python
def build_equipment_cost_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Aggregate price knowledge per renewable_type + product_type."""
    docs: list[dict[str, Any]] = []

    for rtype, group in df.groupby("renewable_type"):
        for ptype, subgroup in group.groupby("product_type"):
            if ptype == "":
                continue
            prices = subgroup["price_php"].dropna().tolist()
            if len(prices) < 3:
                continue

            sources = subgroup["source_site"].dropna().unique().tolist()
            note = _currency_note(subgroup["currency"].iloc[0])

            content = (
                f"{rtype.title()} {ptype.replace('_', ' ')} equipment cost: {_price_range_text(prices)} "
                f"Sources: {', '.join(sources)}. {note}"
            ).strip()

            docs.append({
                "renewable_type": rtype,
                "category": "equipment_cost",
                "product_type": ptype,
                "content": content,
                "sources": sources,
            })

    return docs
```

**Explanation:** It accepts `df` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `groupby()`, `tolist()`, `_currency_note()`, `strip()`, `append()`.

### `build_installation_cost_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `260-316`
- **Signature:** `def build_installation_cost_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:`
- **Purpose:** Derive rough installation-cost knowledge from equipment totals.

**Code:**
```python
def build_installation_cost_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Derive rough installation-cost knowledge from equipment totals.
    Industry rule-of-thumb:
        solar  -> installation ~30-50 % of equipment cost
        wind   -> installation ~20-40 % of equipment cost (tower + labour)
        hydro  -> installation ~40-70 % of equipment cost (civil works)
    """
    docs: list[dict[str, Any]] = []

    for rtype, group in df.groupby("renewable_type"):
        prices = group["price_php"].dropna().tolist()
        if len(prices) < 5:
            continue

        total_equip = sum(prices)
        avg_equip = statistics.mean(prices)
        med_equip = statistics.median(prices)

        if rtype == "solar":
            ratio_low, ratio_high = 0.30, 0.50
            details = (
                "Residential solar installation typically includes mounting structures, wiring, "
                "inverter installation, labour, permits, and net-metering setup. "
                "Small residential systems (1-2 kWp) may have higher per-watt installation costs."
            )
        elif rtype == "wind":
            ratio_low, ratio_high = 0.20, 0.40
            details = (
                "Wind system installation includes tower erection, foundation, wiring, controller setup, "
                "and safety equipment. Off-grid or hybrid setups may require additional battery integration labour."
            )
        else:  # hydro
            ratio_low, ratio_high = 0.40, 0.70
            details = (
                "Micro-hydro installation involves intake design, penstock laying, civil works for the powerhouse, "
                "electrical connection, and regulatory permits. Head and flow measurements are required beforehand."
            )

        content = (
            f"{rtype.title()} installation cost estimate: "
            f"Based on scraped equipment data, average equipment cost per major component is around PHP {avg_equip:,.0f} "
            f"(median PHP {med_equip:,.0f}). "
            f"Installation is estimated at {int(ratio_low*100)}-{int(ratio_high*100)}% of equipment cost. "
            f"Therefore a typical system installation may add PHP {avg_equip*ratio_low:,.0f} - PHP {avg_equip*ratio_high:,.0f} "
            f"on top of equipment prices. {details}"
        )

        docs.append({
            "renewable_type": rtype,
            "category": "installation_cost",
            "product_type": "system",
            "content": content,
            "sources": ["aggregated_scraped_data"],
        })

    return docs
```

**Explanation:** It accepts `df` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `groupby()`, `tolist()`, `sum()`, `mean()`, `median()`.

### `build_maintenance_cost_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `319-358`
- **Signature:** `def build_maintenance_cost_knowledge() -> list[dict[str, Any]]:`
- **Purpose:** Explicit knowledge documents for maintenance schedules and costs.

**Code:**
```python
def build_maintenance_cost_knowledge() -> list[dict[str, Any]]:
    """Explicit knowledge documents for maintenance schedules and costs."""
    return [
        {
            "renewable_type": "solar",
            "category": "maintenance_cost",
            "product_type": "system",
            "content": (
                "Solar maintenance cost: Annual maintenance for residential solar is typically 0.5-1% of "
                "total system cost per year. Key tasks include panel cleaning (2-4 times/year), inverter health checks, "
                "and visual inspection of mounting hardware. Panel lifespan is 20-25 years; inverters usually last 10-15 years "
                "and may need replacement once during system life. Batteries (if off-grid) last 5-10 years depending on cycle depth."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "wind",
            "category": "maintenance_cost",
            "product_type": "system",
            "content": (
                "Wind maintenance cost: Small wind turbines require annual inspection of blades, tower bolts, "
                "and controller electronics. Maintenance is roughly 1-3% of initial system cost per year. "
                "Turbine lifespan is 15-20 years; blades may need replacement or repair after 10 years. "
                "Grease bearings every 6-12 months. Off-grid systems also need battery bank monitoring."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "hydro",
            "category": "maintenance_cost",
            "product_type": "system",
            "content": (
                "Hydro maintenance cost: Micro-hydro systems have low ongoing maintenance if the intake screen is kept clear. "
                "Annual maintenance is roughly 1-2% of system cost. Key tasks: trash-rack cleaning, penstock inspection, "
                "turbine runner checks for cavitation or debris damage, and generator brush replacement. "
                "Turbine lifespan can exceed 25 years; electronic controllers may need replacement after 10-15 years."
            ),
            "sources": ["industry_standard"],
        },
    ]
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation.

### `build_components_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `361-401`
- **Signature:** `def build_components_knowledge() -> list[dict[str, Any]]:`
- **Purpose:** Builds components knowledge.

**Code:**
```python
def build_components_knowledge() -> list[dict[str, Any]]:
    return [
        {
            "renewable_type": "solar",
            "category": "components",
            "product_type": "system",
            "content": (
                "Solar system required components: photovoltaic (PV) panels, DC/AC inverter (string or micro), "
                "mounting structure (roof or ground), DC combiner box, AC disconnect, electrical wiring, "
                "net-metering equipment (if grid-tied), optional battery bank with charge controller (if off-grid). "
                "Residential systems in the Philippines are typically 1-5 kWp."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "wind",
            "category": "components",
            "product_type": "system",
            "content": (
                "Wind system required components: rotor blades, permanent-magnet generator or alternator, "
                "tower (guyed or freestanding), charge controller or grid-tie inverter, dump load (off-grid), "
                "battery bank (off-grid), deep-cycle batteries, wind-direction tail or yaw mechanism, "
                "guy wires and foundation anchors, electrical wiring and disconnects. "
                "Small residential turbines are typically 0.5-10 kW rated."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "hydro",
            "category": "components",
            "product_type": "system",
            "content": (
                "Hydro system required components: intake/weir structure, trash rack, penstock (PVC or steel pipe), "
                "forebay tank with overflow, turbine (Pelton, Francis, or Kaplan depending on head/flow), "
                "generator/alternator, governor or load controller, electrical wiring, powerhouse structure, "
                "tailrace channel, grid-tie inverter or battery charge controller (off-grid). "
                "Micro-hydro systems are typically 0.5-100 kW."
            ),
            "sources": ["industry_standard"],
        },
    ]
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation.

### `build_capacity_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `404-442`
- **Signature:** `def build_capacity_knowledge() -> list[dict[str, Any]]:`
- **Purpose:** Builds capacity knowledge.

**Code:**
```python
def build_capacity_knowledge() -> list[dict[str, Any]]:
    return [
        {
            "renewable_type": "solar",
            "category": "capacity_info",
            "product_type": "system",
            "content": (
                "Solar capacity assumptions: A typical 550 W mono PERC panel produces ~2.0-2.5 kWh/day in the Philippines "
                "depending on location and season. A 2-panel (1.1 kWp) system can generate ~60-80 kWh/month. "
                "Residential installs range from 1-5 kWp. Grid-tied systems can be larger; off-grid sizing depends on battery storage."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "wind",
            "category": "capacity_info",
            "product_type": "system",
            "content": (
                "Wind capacity assumptions: Small wind turbines (0.5-5 kW) need average wind speeds above 4-5 m/s to be viable. "
                "A 1 kW turbine at 5 m/s average generates roughly 100-150 kWh/month depending on capacity factor (15-25%). "
                "Tower height is critical; every doubling of height can increase wind speed by ~10-15%. "
                "Philippine wind resources are strongest in northern Luzon and some coastal areas."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "hydro",
            "category": "capacity_info",
            "product_type": "system",
            "content": (
                "Hydro capacity assumptions: Micro-hydro output depends on head (vertical drop) and flow rate. "
                "Power (kW) ≈ 9.81 × flow (m³/s) × head (m) × system efficiency (0.50-0.70). "
                "A typical micro-hydro site with 10 m head and 0.05 m³/s flow yields ~3-5 kW. "
                "Run-of-river designs are preferred for minimal environmental impact. "
                "Philippine highland municipalities with steep terrain and perennial streams are best suited."
            ),
            "sources": ["industry_standard"],
        },
    ]
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation.

### `build_comparison_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `445-463`
- **Signature:** `def build_comparison_knowledge() -> list[dict[str, Any]]:`
- **Purpose:** Builds comparison knowledge.

**Code:**
```python
def build_comparison_knowledge() -> list[dict[str, Any]]:
    return [
        {
            "renewable_type": "all",
            "category": "comparison",
            "product_type": "system",
            "content": (
                "Solar vs Wind vs Hydro cost comparison (Philippines context): "
                "Solar has the lowest upfront cost per kW installed (PHP ~60,000-80,000/kW) and the widest availability, "
                "but output is reduced during cloudy months (June-October). "
                "Wind requires higher tower costs and good wind resource; upfront cost is PHP ~80,000-120,000/kW; "
                "maintenance is moderate but wind is intermittent. "
                "Hydro has the highest civil-works cost (PHP ~100,000-150,000/kW) but the longest lifespan and most stable output, "
                "provided a suitable stream exists. Solar is usually the safest default for Philippine households; "
                "hydro is best for remote off-grid sites with perennial water; wind is niche and site-specific."
            ),
            "sources": ["industry_standard"],
        },
    ]
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation.

### `build_pricing_assumptions_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `466-485`
- **Signature:** `def build_pricing_assumptions_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:`
- **Purpose:** Builds pricing assumptions knowledge.

**Code:**
```python
def build_pricing_assumptions_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for rtype, group in df.groupby("renewable_type"):
        sources = group["source_site"].dropna().unique().tolist()
        currencies = group["currency"].dropna().unique().tolist()
        content = (
            f"{rtype.title()} pricing assumptions: Prices were scraped from {', '.join(sources)}. "
            f"Original currencies: {', '.join(currencies)}. "
            f"Non-PHP prices were converted using approximate rates and may differ from current market rates. "
            f"Prices reflect individual component listings, not complete turn-key systems. "
            f"Shipping, import duties, and local taxes are not included."
        )
        docs.append({
            "renewable_type": rtype,
            "category": "pricing_assumptions",
            "product_type": "system",
            "content": content,
            "sources": sources,
        })
    return docs
```

**Explanation:** It accepts `df` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `groupby()`, `tolist()`, `append()`, `unique()`, `title()`.

### `build_raw_product_chunks`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `492-517`
- **Signature:** `def build_raw_product_chunks(df: pd.DataFrame, max_per_group: int = 30) -> list[dict[str, Any]]:`
- **Purpose:** Keep a subset of individual product listings so the RAG can answer

**Code:**
```python
def build_raw_product_chunks(df: pd.DataFrame, max_per_group: int = 30) -> list[dict[str, Any]]:
    """
    Keep a subset of individual product listings so the RAG can answer
    'What is the cheapest solar panel?' style questions.
    """
    docs: list[dict[str, Any]] = []
    for (rtype, ptype), group in df.groupby(["renewable_type", "product_type"]):
        if ptype == "":
            continue
        subset = group.nsmallest(max_per_group, "price_php")
        for _, row in subset.iterrows():
            content = (
                f"Product: {row['product_name']}. "
                f"Type: {rtype} {ptype}. "
                f"Price: PHP {row['price_php']:,.0f} (original {row['currency']} {row['price_value_num']}). "
                f"Source: {row.get('source_site', '')}. "
                f"URL: {row.get('url', '')}."
            )
            docs.append({
                "renewable_type": rtype,
                "category": "equipment_cost",
                "product_type": ptype,
                "content": content,
                "sources": [str(row.get("source_site", ""))],
            })
    return docs
```

**Explanation:** It accepts `df`, `max_per_group` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `groupby()`, `nsmallest()`, `iterrows()`, `append()`, `get()`.

### `build_national_energy_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `524-629`
- **Signature:** `def build_national_energy_knowledge() -> list[dict[str, Any]]:`
- **Purpose:** Build knowledge documents from DOE national energy annual data.

**Code:**
```python
def build_national_energy_knowledge() -> list[dict[str, Any]]:
    """Build knowledge documents from DOE national energy annual data."""
    docs: list[dict[str, Any]] = []
    if not NATIONAL_ENERGY_CSV.exists():
        logger.warning("National energy CSV not found: %s", NATIONAL_ENERGY_CSV)
        return docs

    df = pd.read_csv(NATIONAL_ENERGY_CSV)
    df = df.sort_values("year")

    # Per-year detailed documents
    for _, row in df.iterrows():
        year = int(row["year"])
        content = (
            f"In {year}, the Philippines total electricity consumption was {row['total_consumption_gwh']:,.2f} GWh. "
            f"Residential sector consumed {row['residential_consumption_gwh']:,.2f} GWh, "
            f"commercial {row['commercial_consumption_gwh']:,.2f} GWh, "
            f"industrial {row['industrial_consumption_gwh']:,.2f} GWh, "
            f"others {row['others_consumption_gwh']:,.2f} GWh. "
            f"Total electricity sales were {row['electricity_sales_gwh']:,.2f} GWh with system losses of {row['system_losses_gwh']:,.2f} GWh "
            f"and utilities own use of {row['utilities_own_use_gwh']:,.2f} GWh. "
            f"Peak demand reached {row['total_peak_demand_mw']:,.2f} MW nationally: "
            f"{row['luzon_peak_demand_mw']:,.2f} MW in Luzon, "
            f"{row['visayas_peak_demand_mw']:,.2f} MW in Visayas, "
            f"{row['mindanao_peak_demand_mw']:,.2f} MW in Mindanao. "
            f"Gross generation totaled {row['luzon_generation_gwh'] + row['visayas_generation_gwh'] + row['mindanao_generation_gwh']:,.2f} GWh: "
            f"{row['luzon_generation_gwh']:,.2f} GWh in Luzon, "
            f"{row['visayas_generation_gwh']:,.2f} GWh in Visayas, "
            f"{row['mindanao_generation_gwh']:,.2f} GWh in Mindanao. "
            f"By fuel type: coal {row['coal_generation_gwh']:,.2f} GWh, "
            f"oil-based {row['oil_based_generation_gwh']:,.2f} GWh, "
            f"natural gas {row['natural_gas_generation_gwh']:,.2f} GWh, "
            f"renewable {row['renewable_generation_gwh']:,.2f} GWh. "
            f"Renewable breakdown: geothermal {row['geothermal_generation_gwh']:,.2f} GWh, "
            f"hydro {row['hydro_generation_gwh']:,.2f} GWh, "
            f"biomass {row['biomass_generation_gwh']:,.2f} GWh, "
            f"solar {row['solar_generation_gwh']:,.2f} GWh, "
            f"wind {row['wind_generation_gwh']:,.2f} GWh. "
            f"Installed capacity was {row['total_installed_capacity_mw']:,.2f} MW and dependable capacity {row['total_dependable_capacity_mw']:,.2f} MW."
        )
        docs.append({
            "renewable_type": "general",
            "category": "national_energy_statistics",
            "product_type": "annual_report",
            "content": content,
            "sources": ["DOE national_energy_annual_ready.csv"],
        })

    # Trend documents: year-over-year changes
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        year = int(curr["year"])
        prev_year = int(prev["year"])
        total_change = ((curr["total_consumption_gwh"] - prev["total_consumption_gwh"]) / prev["total_consumption_gwh"] * 100) if prev["total_consumption_gwh"] else 0
        solar_change = ((curr["solar_generation_gwh"] - prev["solar_generation_gwh"]) / prev["solar_generation_gwh"] * 100) if prev["solar_generation_gwh"] else 0
        wind_change = ((curr["wind_generation_gwh"] - prev["wind_generation_gwh"]) / prev["wind_generation_gwh"] * 100) if prev["wind_generation_gwh"] else 0
        peak_change = ((curr["total_peak_demand_mw"] - prev["total_peak_demand_mw"]) / prev["total_peak_demand_mw"] * 100) if prev["total_peak_demand_mw"] else 0
        content = (
            f"From {prev_year} to {year}, total electricity consumption changed by {total_change:+.1f}% "
            f"from {prev['total_consumption_gwh']:,.2f} to {curr['total_consumption_gwh']:,.2f} GWh. "
            f"Peak demand changed by {peak_change:+.1f}% from {prev['total_peak_demand_mw']:,.2f} to {curr['total_peak_demand_mw']:,.2f} MW. "
            f"Solar generation changed by {solar_change:+.1f}% from {prev['solar_generation_gwh']:,.2f} to {curr['solar_generation_gwh']:,.2f} GWh. "
            f"Wind generation changed by {wind_change:+.1f}% from {prev['wind_generation_gwh']:,.2f} to {curr['wind_generation_gwh']:,.2f} GWh. "
            f"Coal generation was {curr['coal_generation_gwh']:,.2f} GWh vs {prev['coal_generation_gwh']:,.2f} GWh previously. "
            f"Renewable generation was {curr['renewable_generation_gwh']:,.2f} GWh vs {prev['renewable_generation_gwh']:,.2f} GWh previously."
        )
        docs.append({
            "renewable_type": "general",
            "category": "national_energy_statistics",
            "product_type": "trend",
            "content": content,
            "sources": ["DOE national_energy_annual_ready.csv"],
        })

    # Long-term summary
    first = df.iloc[0]
    last = df.iloc[-1]
    first_year = int(first["year"])
    last_year = int(last["year"])
    total_growth = ((last["total_consumption_gwh"] - first["total_consumption_gwh"]) / first["total_consumption_gwh"] * 100)
    solar_growth = ((last["solar_generation_gwh"] - first["solar_generation_gwh"]) / first["solar_generation_gwh"] * 100) if first["solar_generation_gwh"] else 0
    wind_growth = ((last["wind_generation_gwh"] - first["wind_generation_gwh"]) / first["wind_generation_gwh"] * 100) if first["wind_generation_gwh"] else 0
    peak_growth = ((last["total_peak_demand_mw"] - first["total_peak_demand_mw"]) / first["total_peak_demand_mw"] * 100)
    content = (
        f"Long-term Philippine energy trends from {first_year} to {last_year}: "
        f"Total electricity consumption grew by {total_growth:.1f}% from {first['total_consumption_gwh']:,.2f} to {last['total_consumption_gwh']:,.2f} GWh. "
        f"Peak demand grew by {peak_growth:.1f}% from {first['total_peak_demand_mw']:,.2f} to {last['total_peak_demand_mw']:,.2f} MW. "
        f"Coal generation grew from {first['coal_generation_gwh']:,.2f} to {last['coal_generation_gwh']:,.2f} GWh. "
        f"Natural gas generation changed from {first['natural_gas_generation_gwh']:,.2f} to {last['natural_gas_generation_gwh']:,.2f} GWh. "
        f"Oil-based generation declined from {first['oil_based_generation_gwh']:,.2f} to {last['oil_based_generation_gwh']:,.2f} GWh. "
        f"Renewable generation grew from {first['renewable_generation_gwh']:,.2f} to {last['renewable_generation_gwh']:,.2f} GWh. "
        f"Solar generation grew by {solar_growth:.1f}% from {first['solar_generation_gwh']:,.2f} to {last['solar_generation_gwh']:,.2f} GWh. "
        f"Wind generation grew by {wind_growth:.1f}% from {first['wind_generation_gwh']:,.2f} to {last['wind_generation_gwh']:,.2f} GWh. "
        f"Installed capacity expanded from {first['total_installed_capacity_mw']:,.2f} to {last['total_installed_capacity_mw']:,.2f} MW."
    )
    docs.append({
        "renewable_type": "general",
        "category": "national_energy_statistics",
        "product_type": "summary",
        "content": content,
        "sources": ["DOE national_energy_annual_ready.csv"],
    })

    logger.info("Built %s national energy knowledge documents", len(docs))
    return docs
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `exists()`, `warning()`, `read_csv()`, `sort_values()`, `iterrows()`.

### `_load_municipality_names`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `636-645`
- **Signature:** `def _load_municipality_names() -> dict[int, str]:`
- **Purpose:** Load municipality_id -> name mapping.

**Code:**
```python
def _load_municipality_names() -> dict[int, str]:
    """Load municipality_id -> name mapping."""
    name_map: dict[int, str] = {}
    if not MUNICIPALITIES_CSV.exists():
        return name_map
    df = pd.read_csv(MUNICIPALITIES_CSV)
    for _, row in df.iterrows():
        mid = int(row["municipality_id"])
        name_map[mid] = str(row["name"]).strip()
    return name_map
```

**Explanation:** It accepts zero arguments and returns `dict[int, str]`. See the code below for the full implementation. Key calls include `exists()`, `read_csv()`, `iterrows()`, `int()`, `strip()`.

### `build_municipality_climate_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `648-716`
- **Signature:** `def build_municipality_climate_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:`
- **Purpose:** Build knowledge documents from NASA POWER climate averages per municipality.

**Code:**
```python
def build_municipality_climate_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from NASA POWER climate averages per municipality."""
    docs: list[dict[str, Any]] = []
    if not CLIMATE_CSV.exists():
        logger.warning("Climate CSV not found: %s", CLIMATE_CSV)
        return docs

    name_map = _load_municipality_names()
    df = pd.read_csv(CLIMATE_CSV)

    # Sort by municipality_id and limit to avoid overwhelming the index
    df = df.sort_values("municipality_id")
    if len(df) > max_docs:
        # Prioritize diverse climates: sample across wind speed and solar irradiance quartiles
        df["ws_q"] = pd.qcut(df["avg_ws10m"], q=4, labels=False, duplicates="drop")
        df["sol_q"] = pd.qcut(df["avg_allsky_sfc_sw_dwn"], q=4, labels=False, duplicates="drop")
        sampled = df.groupby(["ws_q", "sol_q"]).head(max_docs // 16)
        remaining = max_docs - len(sampled)
        if remaining > 0:
            remaining_ids = df[~df["municipality_id"].isin(sampled["municipality_id"])]["municipality_id"].head(remaining)
            df = pd.concat([sampled, df[df["municipality_id"].isin(remaining_ids)]])
        else:
            df = sampled

    for _, row in df.iterrows():
        mid = int(row["municipality_id"])
        name = name_map.get(mid, f"Municipality {mid}")
        content = (
            f"{name} has an average temperature of {row['avg_t2m']:.1f}°C "
            f"(max {row['avg_t2m_max']:.1f}°C, min {row['avg_t2m_min']:.1f}°C), "
            f"relative humidity of {row['avg_rh2m']:.1f}%, "
            f"average wind speed of {row['avg_ws10m']:.2f} m/s, "
            f"solar irradiance of {row['avg_allsky_sfc_sw_dwn']:.2f} kWh/m²/day, "
            f"and elevation of {row['elevation']:.0f} meters. "
            f"Annual precipitation averages {row['avg_prectotcorr']:.2f} mm/day. "
            f"Surface pressure is {row['avg_surface_pressure']:.2f} kPa and air density {row['avg_rhoa']:.3f} kg/m³. "
            f"Cloud amount averages {row['avg_cloud_amt']:.1f}%."
        )
        docs.append({
            "renewable_type": "general",
            "category": "municipality_climate",
            "product_type": "climate_profile",
            "content": content,
            "sources": ["NASA POWER municipality_climate_averages.csv"],
        })

    # Add a few high-wind and high-solar highlights for better retrieval
    df_all = pd.read_csv(CLIMATE_CSV)
    for label, col, threshold in [("high wind", "avg_ws10m", 5.0), ("high solar", "avg_allsky_sfc_sw_dwn", 5.5)]:
        top = df_all.nlargest(20, col)
        for _, row in top.iterrows():
            mid = int(row["municipality_id"])
            name = name_map.get(mid, f"Municipality {mid}")
            content = (
                f"{name} is a {label} municipality with {col.replace('avg_', '').replace('_', ' ')} "
                f"of {row[col]:.2f}. "
                f"Temperature {row['avg_t2m']:.1f}°C, wind {row['avg_ws10m']:.2f} m/s, "
                f"solar {row['avg_allsky_sfc_sw_dwn']:.2f} kWh/m²/day, elevation {row['elevation']:.0f}m."
            )
            docs.append({
                "renewable_type": "general",
                "category": "municipality_climate",
                "product_type": f"{label}_highlight",
                "content": content,
                "sources": ["NASA POWER municipality_climate_averages.csv"],
            })

    logger.info("Built %s municipality climate knowledge documents", len(docs))
    return docs
```

**Explanation:** It accepts `max_docs` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `exists()`, `warning()`, `_load_municipality_names()`, `read_csv()`, `sort_values()`.

### `build_terrain_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `723-786`
- **Signature:** `def build_terrain_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:`
- **Purpose:** Build knowledge documents from municipality terrain metrics.

**Code:**
```python
def build_terrain_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from municipality terrain metrics."""
    docs: list[dict[str, Any]] = []
    if not TERRAIN_CSV.exists():
        logger.warning("Terrain CSV not found: %s", TERRAIN_CSV)
        return docs

    df = pd.read_csv(TERRAIN_CSV)
    df = df.sort_values("municipality_id")
    if len(df) > max_docs:
        # Prioritize high-hydropower-potential and high-terrain-diversity municipalities
        df["hydro_q"] = pd.qcut(df["hydro_suitability_score"], q=4, labels=False, duplicates="drop")
        sampled = df.groupby("hydro_q").head(max_docs // 4)
        remaining = max_docs - len(sampled)
        if remaining > 0:
            remaining_ids = df[~df["municipality_id"].isin(sampled["municipality_id"])]["municipality_id"].head(remaining)
            df = pd.concat([sampled, df[df["municipality_id"].isin(remaining_ids)]])
        else:
            df = sampled

    for _, row in df.iterrows():
        name = str(row["municipality_name"]).strip()
        province = str(row["province"]).strip()
        content = (
            f"{name} in {province} has terrain characteristics: "
            f"elevation {row['elevation_m']:.0f} m (mean {row['mean_elevation_m']:.1f} m, range {row['elevation_range_m']:.0f} m), "
            f"mean slope {row['mean_slope_deg']:.1f}°, hydraulic head {row['hydraulic_head_m']:.0f} m, "
            f"terrain ruggedness {row['terrain_ruggedness']:.1f}, watershed gradient {row['watershed_gradient']:.4f}, "
            f"runoff potential {row['runoff_potential']:.4f}, gravity flow potential {row['gravity_flow_potential']:.4f}. "
            f"Hydropower suitability score is {row['hydro_suitability_score']:.3f}. "
            f"Estimated hydropower potential is {row['estimated_hydropower_potential_kw']:.2f} kW. "
            f"Slope classification: {row['slope_classification']}. Elevation classification: {row['elevation_classification']}."
        )
        docs.append({
            "renewable_type": "hydro",
            "category": "terrain_metrics",
            "product_type": "terrain_profile",
            "content": content,
            "sources": ["municipality_terrain_metrics.csv"],
        })

    # Add high-hydropower highlights
    df_all = pd.read_csv(TERRAIN_CSV)
    top_hydro = df_all.nlargest(20, "estimated_hydropower_potential_kw")
    for _, row in top_hydro.iterrows():
        name = str(row["municipality_name"]).strip()
        province = str(row["province"]).strip()
        content = (
            f"{name} in {province} is a high-hydropower-potential site with "
            f"estimated capacity of {row['estimated_hydropower_potential_kw']:.2f} kW, "
            f"hydraulic head {row['hydraulic_head_m']:.0f} m, "
            f"mean slope {row['mean_slope_deg']:.1f}°, "
            f"and hydro suitability score {row['hydro_suitability_score']:.3f}."
        )
        docs.append({
            "renewable_type": "hydro",
            "category": "terrain_metrics",
            "product_type": "hydro_highlight",
            "content": content,
            "sources": ["municipality_terrain_metrics.csv"],
        })

    logger.info("Built %s terrain knowledge documents", len(docs))
    return docs
```

**Explanation:** It accepts `max_docs` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `exists()`, `warning()`, `read_csv()`, `sort_values()`, `len()`.

### `build_geothermal_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `793-899`
- **Signature:** `def build_geothermal_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:`
- **Purpose:** Build knowledge documents from geothermal_suitability table in Supabase.

**Code:**
```python
def build_geothermal_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from geothermal_suitability table in Supabase."""
    docs: list[dict[str, Any]] = []
    try:
        client = get_supabase_client()
        resp = client.table("geothermal_suitability").select("*").limit(10000).execute()
        rows = resp.data or []
        if not rows:
            logger.warning("No geothermal suitability data found in Supabase")
            return docs

        # Load name maps
        name_map = _load_municipality_names()
        muni_resp = client.table("municipalities").select("municipality_id,province_id,name").limit(10000).execute()
        muni_rows = muni_resp.data or []
        muni_map = {m["municipality_id"]: m for m in muni_rows}

        prov_resp = client.table("provinces").select("province_id,name").limit(10000).execute()
        prov_rows = prov_resp.data or []
        prov_map = {p["province_id"]: p["name"] for p in prov_rows}

        # Sort and limit
        rows = sorted(rows, key=lambda r: r.get("municipality_id", 0))
        if len(rows) > max_docs:
            # Prioritize high-suitability and diverse classifications
            high = [r for r in rows if (r.get("geothermal_score") or 0) > 0.15]
            moderate = [r for r in rows if 0.08 < (r.get("geothermal_score") or 0) <= 0.15]
            low = [r for r in rows if (r.get("geothermal_score") or 0) <= 0.08]
            per_bucket = max_docs // 3
            rows = (high[:per_bucket] + moderate[:per_bucket] + low[:per_bucket])

        for row in rows:
            mid = row.get("municipality_id")
            muni = muni_map.get(mid, {})
            muni_name = muni.get("name") or name_map.get(mid, f"Municipality {mid}")
            prov_name = prov_map.get(muni.get("province_id"), "")

            score = row.get("geothermal_score") or 0
            classification = row.get("classification") or "unknown"
            fault_dist = row.get("fault_distance_km")
            fault_density = row.get("fault_density")
            volcano_dist = row.get("volcano_distance_km")
            heat_flow = row.get("heat_flow_score")
            temp_score = row.get("temperature_score")
            aquifer = row.get("aquifer_score")

            content = (
                f"{muni_name}{' in ' + prov_name if prov_name else ''} has a geothermal suitability score of {score:.3f} "
                f"(classification: {classification}). "
            )
            details = []
            if fault_dist is not None:
                details.append(f"fault distance {fault_dist:.1f} km")
            if fault_density is not None:
                details.append(f"fault density {fault_density:.2f}")
            if volcano_dist is not None:
                details.append(f"volcano distance {volcano_dist:.1f} km")
            if heat_flow is not None:
                details.append(f"heat flow score {heat_flow:.3f}")
            if temp_score is not None:
                details.append(f"temperature score {temp_score:.3f}")
            if aquifer is not None:
                details.append(f"aquifer score {aquifer:.3f}")
            if details:
                content += "Key factors: " + ", ".join(details) + ". "
            content += (
                f"This indicates {'strong' if score > 0.15 else 'moderate' if score > 0.08 else 'limited'} "
                f"potential for geothermal energy development."
            )

            docs.append({
                "renewable_type": "geothermal",
                "category": "geothermal_suitability",
                "product_type": "municipality_profile",
                "content": content,
                "sources": ["Supabase geothermal_suitability"],
            })

        # Add province-level aggregate summaries
        prov_scores: dict[str, list[float]] = {}
        for row in resp.data or []:
            mid = row.get("municipality_id")
            muni = muni_map.get(mid, {})
            prov = prov_map.get(muni.get("province_id"), "")
            if prov:
                prov_scores.setdefault(prov, []).append(row.get("geothermal_score") or 0)

        for prov, scores in prov_scores.items():
            avg = sum(scores) / len(scores)
            content = (
                f"{prov} has an average geothermal suitability score of {avg:.3f} across {len(scores)} municipalities. "
                f"This suggests {'strong' if avg > 0.15 else 'moderate' if avg > 0.08 else 'limited'} "
                f"province-wide geothermal energy potential."
            )
            docs.append({
                "renewable_type": "geothermal",
                "category": "geothermal_suitability",
                "product_type": "province_summary",
                "content": content,
                "sources": ["Supabase geothermal_suitability"],
            })

        logger.info("Built %s geothermal knowledge documents", len(docs))
    except Exception as exc:
        logger.warning("Failed to build geothermal knowledge: %s", exc)

    return docs
```

**Explanation:** It accepts `max_docs` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `_load_municipality_names()`, `sorted()`, `items()`.

### `build_hydropower_suitability_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `906-1000`
- **Signature:** `def build_hydropower_suitability_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:`
- **Purpose:** Build knowledge documents from hydropower_suitability table in Supabase.

**Code:**
```python
def build_hydropower_suitability_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from hydropower_suitability table in Supabase."""
    docs: list[dict[str, Any]] = []
    try:
        client = get_supabase_client()
        resp = client.table("hydropower_suitability").select("*").limit(10000).execute()
        rows = resp.data or []
        if not rows:
            logger.warning("No hydropower suitability data found in Supabase")
            return docs

        # Load name maps
        name_map = _load_municipality_names()

        # Sort and limit
        rows = sorted(rows, key=lambda r: r.get("municipality_id", 0))
        if len(rows) > max_docs:
            # Prioritize high-hydro-potential municipalities
            rows.sort(key=lambda r: r.get("hydro_suitability_score") or 0, reverse=True)
            rows = rows[:max_docs]

        for row in rows:
            mid = row.get("municipality_id")
            muni_name = row.get("municipality_name") or name_map.get(mid, f"Municipality {mid}")
            prov_name = row.get("province", "")
            score = row.get("hydro_suitability_score") or 0
            head = row.get("hydraulic_head_m")
            slope = row.get("mean_slope_deg")
            runoff = row.get("runoff_potential")
            gravity = row.get("gravity_flow_potential")
            est_kw = row.get("estimated_hydropower_potential_kw")

            content = (
                f"{muni_name}{' in ' + prov_name if prov_name else ''} has a hydropower suitability score of {score:.3f}. "
            )
            details = []
            if head is not None:
                details.append(f"hydraulic head {head:.0f} m")
            if slope is not None:
                details.append(f"mean slope {slope:.1f}°")
            if runoff is not None:
                details.append(f"runoff potential {runoff:.3f}")
            if gravity is not None:
                details.append(f"gravity flow potential {gravity:.3f}")
            if est_kw is not None:
                details.append(f"estimated capacity {est_kw:.2f} kW")
            if details:
                content += "Terrain characteristics: " + ", ".join(details) + ". "
            content += (
                f"This indicates {'excellent' if score > 0.6 else 'good' if score > 0.4 else 'moderate' if score > 0.2 else 'limited'} "
                f"potential for small-scale hydropower development."
            )

            docs.append({
                "renewable_type": "hydro",
                "category": "hydropower_suitability",
                "product_type": "municipality_profile",
                "content": content,
                "sources": ["Supabase hydropower_suitability"],
            })

        # Add province-level aggregate summaries
        prov_rows: dict[str, list[dict]] = {}
        for row in resp.data or []:
            prov = row.get("province", "").strip()
            if prov:
                prov_rows.setdefault(prov, []).append(row)

        for prov, prov_data in prov_rows.items():
            scores = [r.get("hydro_suitability_score") or 0 for r in prov_data]
            avg = sum(scores) / len(scores)
            capacities = [r.get("estimated_hydropower_potential_kw") or 0 for r in prov_data if r.get("estimated_hydropower_potential_kw")]
            total_cap = sum(capacities)
            content = (
                f"{prov} has an average hydropower suitability score of {avg:.3f} across {len(prov_data)} municipalities. "
            )
            if capacities:
                content += f"Aggregate estimated hydropower capacity is {total_cap:.2f} kW. "
            content += (
                f"This suggests {'excellent' if avg > 0.6 else 'good' if avg > 0.4 else 'moderate' if avg > 0.2 else 'limited'} "
                f"province-wide small-scale hydropower potential."
            )
            docs.append({
                "renewable_type": "hydro",
                "category": "hydropower_suitability",
                "product_type": "province_summary",
                "content": content,
                "sources": ["Supabase hydropower_suitability"],
            })

        logger.info("Built %s hydropower suitability knowledge documents", len(docs))
    except Exception as exc:
        logger.warning("Failed to build hydropower suitability knowledge: %s", exc)

    return docs
```

**Explanation:** It accepts `max_docs` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `_load_municipality_names()`, `sorted()`, `items()`.

### `_extract_pdf_text`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `1010-1019`
- **Signature:** `def _extract_pdf_text(pdf_path: Path, max_pages: int = 10) -> str:`
- **Purpose:** Extract text from first N pages of a PDF.

**Code:**
```python
def _extract_pdf_text(pdf_path: Path, max_pages: int = 10) -> str:
    """Extract text from first N pages of a PDF."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pages = pdf.pages[:max_pages]
            return "\n".join(p.extract_text() or "" for p in pages)
    except Exception as exc:
        logger.warning("Failed to extract %s: %s", pdf_path.name, exc)
        return ""
```

**Explanation:** It accepts `pdf_path`, `max_pages` and returns `str`. See the code below for the full implementation. Key calls include `open()`, `join()`, `warning()`, `extract_text()`.

### `_chunk_text`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `1022-1032`
- **Signature:** `def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:`
- **Purpose:** Simple sliding-window chunking for long text.

**Code:**
```python
def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Simple sliding-window chunking for long text."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 100:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
```

**Explanation:** It accepts `text`, `chunk_size`, `overlap` and returns `list[str]`. See the code below for the full implementation. Key calls include `len()`, `strip()`, `append()`.

### `build_thesis_paper_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `1035-1069`
- **Signature:** `def build_thesis_paper_knowledge(max_papers: int = 20, pages_per_paper: int = 8) -> list[dict[str, Any]]:`
- **Purpose:** Build knowledge documents from thesis research PDFs.

**Code:**
```python
def build_thesis_paper_knowledge(max_papers: int = 20, pages_per_paper: int = 8) -> list[dict[str, Any]]:
    """Build knowledge documents from thesis research PDFs."""
    docs: list[dict[str, Any]] = []
    if not THESIS_DIR.exists():
        return docs

    pdf_files = sorted([p for p in THESIS_DIR.rglob("*.pdf") if p.is_file()])[:max_papers]
    for pdf_path in pdf_files:
        title = pdf_path.stem.replace("_", " ").replace("-", " ")[:120]
        text = _extract_pdf_text(pdf_path, max_pages=pages_per_paper)
        if not text or len(text) < 200:
            continue

        # Create a summary chunk
        first_para = text[:600].strip()
        docs.append({
            "renewable_type": "general",
            "category": "research_literature",
            "product_type": "thesis_paper",
            "content": f"Research Paper: {title}. {first_para}",
            "sources": [{"title": title, "url": "", "org": "LUMI Thesis Research"}],
        })

        # Add content chunks
        for chunk in _chunk_text(text, chunk_size=600, overlap=80):
            docs.append({
                "renewable_type": "general",
                "category": "research_literature",
                "product_type": "thesis_paper",
                "content": f"From research paper '{title}': {chunk}",
                "sources": [{"title": title, "url": "", "org": "LUMI Thesis Research"}],
            })

    logger.info("Built %s thesis paper knowledge documents", len(docs))
    return docs
```

**Explanation:** It accepts `max_papers`, `pages_per_paper` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `exists()`, `sorted()`, `rglob()`, `is_file()`, `_extract_pdf_text()`.

### `build_web_article_knowledge`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `1090-1140`
- **Signature:** `def build_web_article_knowledge() -> list[dict[str, Any]]:`
- **Purpose:** Fetch and chunk web articles for RAG.

**Code:**
```python
def build_web_article_knowledge() -> list[dict[str, Any]]:
    """Fetch and chunk web articles for RAG."""
    docs: list[dict[str, Any]] = []
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("requests/bs4 not installed; skipping web articles")
        return docs

    for article in WEB_ARTICLES:
        try:
            resp = requests.get(article["url"], timeout=15, headers={"User-Agent": "LUMI-RAG/1.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract main text
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 60]
            text = "\n\n".join(paragraphs[:30])  # first 30 meaningful paragraphs

            if len(text) < 300:
                continue

            source_dict = {"title": article["title"], "url": article["url"], "org": article["org"]}

            # Summary chunk
            docs.append({
                "renewable_type": "general",
                "category": "web_article",
                "product_type": "article",
                "content": f"Article: {article['title']} by {article['org']}. {text[:800]}",
                "sources": [source_dict],
            })

            # Content chunks
            for chunk in _chunk_text(text, chunk_size=700, overlap=100):
                docs.append({
                    "renewable_type": "general",
                    "category": "web_article",
                    "product_type": "article",
                    "content": f"From article '{article['title']}': {chunk}",
                    "sources": [source_dict],
                })

        except Exception as exc:
            logger.warning("Failed to fetch article %s: %s", article["url"], exc)

    logger.info("Built %s web article knowledge documents", len(docs))
    return docs
```

**Explanation:** It accepts zero arguments and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `warning()`, `get()`, `raise_for_status()`, `BeautifulSoup()`, `soup()`.

### `build_knowledge_base`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `1147-1189`
- **Signature:** `def build_knowledge_base(csv_path: Path = DEFAULT_CSV) -> list[dict[str, Any]]:`
- **Purpose:** Builds knowledge base.

**Code:**
```python
def build_knowledge_base(csv_path: Path = DEFAULT_CSV) -> list[dict[str, Any]]:
    df = load_and_fix_csv(csv_path)
    logger.info("Loaded %s rows after cleaning/fixes", len(df))

    docs: list[dict[str, Any]] = []
    # Product / scraped data
    docs.extend(build_equipment_cost_knowledge(df))
    docs.extend(build_installation_cost_knowledge(df))
    docs.extend(build_maintenance_cost_knowledge())
    docs.extend(build_components_knowledge())
    docs.extend(build_capacity_knowledge())
    docs.extend(build_comparison_knowledge())
    docs.extend(build_pricing_assumptions_knowledge(df))
    docs.extend(build_raw_product_chunks(df))

    # LUMI data sources
    docs.extend(build_national_energy_knowledge())
    docs.extend(build_municipality_climate_knowledge())
    docs.extend(build_terrain_knowledge())
    docs.extend(build_geothermal_knowledge())
    docs.extend(build_hydropower_suitability_knowledge())

    # External sources
    docs.extend(build_thesis_paper_knowledge())
    docs.extend(build_web_article_knowledge())

    # Deduplicate by content hash
    seen: set[str] = set()
    unique_docs: list[dict[str, Any]] = []
    for d in docs:
        h = hash(d["content"])
        if h not in seen:
            seen.add(h)
            unique_docs.append(d)

    # Enrich all source strings into structured dicts
    for d in unique_docs:
        raw_sources = d.get("sources", [])
        if raw_sources and isinstance(raw_sources[0], str):
            d["sources"] = _enrich_sources(raw_sources)

    logger.info("Built %s knowledge documents", len(unique_docs))
    return unique_docs
```

**Explanation:** It accepts `csv_path` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `load_and_fix_csv()`, `info()`, `len()`, `extend()`, `build_equipment_cost_knowledge()`.

### `save_knowledge_base`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `1192-1196`
- **Signature:** `def save_knowledge_base(docs: list[dict[str, Any]], path: Path = KNOWLEDGE_JSON_PATH) -> Path:`
- **Purpose:** Saves knowledge base.

**Code:**
```python
def save_knowledge_base(docs: list[dict[str, Any]], path: Path = KNOWLEDGE_JSON_PATH) -> Path:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    logger.info("Saved knowledge base to %s", path)
    return path
```

**Explanation:** It accepts `docs`, `path` and returns `Path`. See the code below for the full implementation. Key calls include `open()`, `dump()`, `info()`.

### `load_knowledge_base`

- **File:** `fastapi-backend/app/services/rag_knowledge_builder.py`
- **Lines:** `1199-1205`
- **Signature:** `def load_knowledge_base(path: Path = KNOWLEDGE_JSON_PATH) -> list[dict[str, Any]]:`
- **Purpose:** Loads knowledge base.

**Code:**
```python
def load_knowledge_base(path: Path = KNOWLEDGE_JSON_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge base not found at {path}. Run build_knowledge_base() first."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
```

**Explanation:** It accepts `path` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `exists()`, `FileNotFoundError()`, `open()`, `load()`.


## `fastapi-backend/app/services/rag_pgvector_store.py`

**File:** `fastapi-backend/app/services/rag_pgvector_store.py`

**Summary:** Source file `fastapi-backend/app/services/rag_pgvector_store.py`.

### `_vector_literal`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `16-18`
- **Signature:** `def _vector_literal(embedding: list[float]) -> str:`
- **Purpose:** Format an embedding as a pgvector literal string.

**Code:**
```python
def _vector_literal(embedding: list[float]) -> str:
    '''Format an embedding as a pgvector literal string.'''
    return '[' + ','.join(f'{x:.8f}' for x in embedding) + ']'
```

**Explanation:** It accepts `embedding` and returns `str`. See the code below for the full implementation. Key calls include `join()`.

### `_row_to_result`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `21-29`
- **Signature:** `def _row_to_result(row: dict[str, Any]) -> dict[str, Any]:`
- **Purpose:** Handles  row to result.

**Code:**
```python
def _row_to_result(row: dict[str, Any]) -> dict[str, Any]:
    return {
        'text': row.get('chunk_text', ''),
        'score': round(float(row.get('similarity', 0.0)), 4),
        'renewable_type': row.get('renewable_type', '') or '',
        'category': row.get('category', '') or '',
        'product_type': row.get('product_type', '') or '',
        'sources': row.get('sources') or [],
    }
```

**Explanation:** It accepts `row` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get()`, `round()`, `float()`.

### `_count_rows`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `32-41`
- **Signature:** `def _count_rows(client) -> int:`
- **Purpose:** Handles  count rows.

**Code:**
```python
def _count_rows(client) -> int:
    try:
        resp = client.table(_RAG_TABLE).select('id', count='exact').limit(1).execute()
        if hasattr(resp, 'count') and resp.count is not None:
            return int(resp.count)
        # Fallback: exact count may not be available in all clients.
        count_resp = client.table(_RAG_TABLE).select('id').execute()
        return len(count_resp.data) if count_resp.data else 0
    except Exception:
        return 0
```

**Explanation:** It accepts `client` and returns `int`. See the code below for the full implementation. Key calls include `execute()`, `hasattr()`, `int()`, `len()`, `limit()`.

### `ensure_index_built`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `44-55`
- **Signature:** `def ensure_index_built() -> bool:`
- **Purpose:** Check whether the pgvector table has been seeded.

**Code:**
```python
def ensure_index_built() -> bool:
    '''Check whether the pgvector table has been seeded.'''
    try:
        client = get_supabase_client()
        resp = client.table(_RAG_TABLE).select('id').limit(1).execute()
        has_rows = bool(resp.data)
        if not has_rows:
            logger.warning('RAG chunks table is empty; seeding is required.')
        return has_rows
    except Exception as exc:
        logger.warning('Could not verify pgvector RAG store: %s', exc)
        return False
```

**Explanation:** It accepts zero arguments and returns `bool`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `bool()`, `warning()`, `limit()`.

### `index_stats`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `58-69`
- **Signature:** `def index_stats() -> dict[str, Any]:`
- **Purpose:** Handles index stats.

**Code:**
```python
def index_stats() -> dict[str, Any]:
    try:
        client = get_supabase_client()
        count = _count_rows(client)
        return {
            'chunks_loaded': count,
            'pgvector_enabled': True,
            'index_present': count > 0,
        }
    except Exception as exc:
        logger.warning('Could not get pgvector RAG stats: %s', exc)
        return {'chunks_loaded': 0, 'pgvector_enabled': False, 'index_present': False}
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `_count_rows()`, `warning()`.

### `_retrieve`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `72-110`
- **Signature:** `def _retrieve(`
- **Purpose:** Handles  retrieve.

**Code:**
```python
def _retrieve(
    query: str,
    top_k: int,
    renewable_type: str | None,
    category: str | None,
    score_threshold: float,
) -> list[dict[str, Any]]:
    settings = get_settings()
    embedding_model = settings.embedding_model or 'sentence-transformers/all-MiniLM-L6-v2'
    expected_model = 'sentence-transformers/all-MiniLM-L6-v2'
    if embedding_model != expected_model:
        logger.warning(
            'RAG_BACKEND=pgvector expects 384-d %s embeddings; using %s may fail.',
            expected_model,
            embedding_model,
        )

    embeddings = encode(query)
    if not embeddings or not embeddings[0]:
        raise RuntimeError('Failed to encode query for RAG retrieval')

    vector = _vector_literal(embeddings[0])
    client = get_supabase_client()
    params = {
        'query_embedding': vector,
        'match_count': top_k,
        'similarity_threshold': score_threshold,
        'filter_renewable_type': renewable_type,
        'filter_category': category,
    }

    try:
        resp = client.rpc(_RAG_RPC, params).execute()
    except Exception as exc:
        logger.exception('match_rag_chunks RPC failed')
        raise RuntimeError(f'pgvector RAG retrieval failed: {exc}') from exc

    rows = resp.data or []
    return [_row_to_result(row) for row in rows]
```

**Explanation:** It accepts `query`, `top_k`, `renewable_type`, `category`, `score_threshold` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_settings()`, `warning()`, `encode()`, `RuntimeError()`, `_vector_literal()`.

### `retrieve_context`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `113-120`
- **Signature:** `def retrieve_context(`
- **Purpose:** Retrieves context.

**Code:**
```python
def retrieve_context(
    query: str,
    top_k: int = 5,
    model_name: str = 'all-MiniLM-L6-v2',
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    return _retrieve(query, top_k, None, None, score_threshold)
```

**Explanation:** It accepts `query`, `top_k`, `model_name`, `score_threshold`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_retrieve()`.

### `retrieve_with_filter`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `123-132`
- **Signature:** `def retrieve_with_filter(`
- **Purpose:** Retrieves with filter.

**Code:**
```python
def retrieve_with_filter(
    query: str,
    top_k: int = 5,
    renewable_type: str | None = None,
    category: str | None = None,
    model_name: str = 'all-MiniLM-L6-v2',
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    return _retrieve(query, top_k, renewable_type, category, score_threshold)
```

**Explanation:** It accepts `query`, `top_k`, `renewable_type`, `category`, `model_name`, `score_threshold`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_retrieve()`.

### `sample_chunks`

- **File:** `fastapi-backend/app/services/rag_pgvector_store.py`
- **Lines:** `135-144`
- **Signature:** `def sample_chunks(n: int = 3) -> list[dict[str, Any]]:`
- **Purpose:** Return a sample of stored chunks for debugging.

**Code:**
```python
def sample_chunks(n: int = 3) -> list[dict[str, Any]]:
    '''Return a sample of stored chunks for debugging.'''
    try:
        client = get_supabase_client()
        resp = client.table(_RAG_TABLE).select('*').limit(n).execute()
        rows = resp.data or []
        return [_row_to_result(row) for row in rows]
    except Exception as exc:
        logger.warning('Could not sample chunks: %s', exc)
        return []
```

**Explanation:** It accepts `n` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `execute()`, `_row_to_result()`, `warning()`, `limit()`.


## `fastapi-backend/app/services/rag_pipeline.py`

**File:** `fastapi-backend/app/services/rag_pipeline.py`

**Summary:** RAG pipeline dispatcher.

### `_rag_faiss`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `17-21`
- **Signature:** `def _rag_faiss():`
- **Purpose:** Lazy import the FAISS backend so Vercel does not load it by default.

**Code:**
```python
def _rag_faiss():
    '''Lazy import the FAISS backend so Vercel does not load it by default.'''
    from app.services import rag_faiss

    return rag_faiss
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation.

### `_rag_backend`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `34-35`
- **Signature:** `def _rag_backend() -> str:`
- **Purpose:** Handles  rag backend.

**Code:**
```python
def _rag_backend() -> str:
    return (get_settings().rag_backend or 'faiss').lower()
```

**Explanation:** It accepts zero arguments and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `get_settings()`.

### `build_faiss_index`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `38-43`
- **Signature:** `def build_faiss_index(`
- **Purpose:** Builds faiss index.

**Code:**
```python
def build_faiss_index(
    docs: list[dict[str, Any]],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    save: bool = True,
) -> dict[str, Any]:
    return _rag_faiss().build_faiss_index(docs, model_name=model_name, save=save)
```

**Explanation:** It accepts `docs`, `model_name`, `save` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `build_faiss_index()`, `_rag_faiss()`.

### `load_faiss_index`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `46-56`
- **Signature:** `def load_faiss_index(`
- **Purpose:** Loads faiss index.

**Code:**
```python
def load_faiss_index(
    index_path=None,
    chunks_path=None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> bool:
    if _rag_backend() == 'pgvector':
        logger.warning('load_faiss_index is not used with RAG_BACKEND=pgvector')
        return False
    return _rag_faiss().load_faiss_index(
        index_path=index_path, chunks_path=chunks_path, model_name=model_name
    )
```

**Explanation:** It accepts `index_path`, `chunks_path`, `model_name` and returns `bool`. See the code below for the full implementation. Key calls include `_rag_backend()`, `warning()`, `load_faiss_index()`, `_rag_faiss()`.

### `ensure_index_built`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `59-65`
- **Signature:** `def ensure_index_built(`
- **Purpose:** Handles ensure index built.

**Code:**
```python
def ensure_index_built(
    docs: list[dict[str, Any]] | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> bool:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.ensure_index_built()
    return _rag_faiss().ensure_index_built(docs=docs, model_name=model_name)
```

**Explanation:** It accepts `docs`, `model_name` and returns `bool`. See the code below for the full implementation. Key calls include `_rag_backend()`, `ensure_index_built()`, `_rag_faiss()`.

### `retrieve_context`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `68-89`
- **Signature:** `def retrieve_context(`
- **Purpose:** Retrieves context.

**Code:**
```python
def retrieve_context(
    query: str,
    top_k: int = 5,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.retrieve_context(
            query,
            top_k=top_k,
            model_name=model_name,
            score_threshold=score_threshold,
            use_cache=use_cache,
        )
    return _rag_faiss().retrieve_context(
        query,
        top_k=top_k,
        model_name=model_name,
        score_threshold=score_threshold,
        use_cache=use_cache,
    )
```

**Explanation:** It accepts `query`, `top_k`, `model_name`, `score_threshold`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_rag_backend()`, `retrieve_context()`, `_rag_faiss()`.

### `retrieve_with_filter`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `92-119`
- **Signature:** `def retrieve_with_filter(`
- **Purpose:** Retrieves with filter.

**Code:**
```python
def retrieve_with_filter(
    query: str,
    top_k: int = 5,
    renewable_type: str | None = None,
    category: str | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.retrieve_with_filter(
            query,
            top_k=top_k,
            renewable_type=renewable_type,
            category=category,
            model_name=model_name,
            score_threshold=score_threshold,
            use_cache=use_cache,
        )
    return _rag_faiss().retrieve_with_filter(
        query,
        top_k=top_k,
        renewable_type=renewable_type,
        category=category,
        model_name=model_name,
        score_threshold=score_threshold,
        use_cache=use_cache,
    )
```

**Explanation:** It accepts `query`, `top_k`, `renewable_type`, `category`, `model_name`, `score_threshold`, `use_cache` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_rag_backend()`, `retrieve_with_filter()`, `_rag_faiss()`.

### `index_stats`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `122-125`
- **Signature:** `def index_stats() -> dict[str, Any]:`
- **Purpose:** Handles index stats.

**Code:**
```python
def index_stats() -> dict[str, Any]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.index_stats()
    return _rag_faiss().index_stats()
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_rag_backend()`, `index_stats()`, `_rag_faiss()`.

### `sample_chunks`

- **File:** `fastapi-backend/app/services/rag_pipeline.py`
- **Lines:** `128-131`
- **Signature:** `def sample_chunks(n: int = 3) -> list[dict[str, Any]]:`
- **Purpose:** Handles sample chunks.

**Code:**
```python
def sample_chunks(n: int = 3) -> list[dict[str, Any]]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.sample_chunks(n=n)
    return _rag_faiss().sample_chunks(n=n)
```

**Explanation:** It accepts `n` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `_rag_backend()`, `sample_chunks()`, `_rag_faiss()`.


## `fastapi-backend/app/services/redis_client.py`

**File:** `fastapi-backend/app/services/redis_client.py`

**Summary:** Source file `fastapi-backend/app/services/redis_client.py`.

### `NullRedis.get`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `24-25`
- **Signature:** `async def get(self, key: str) -> None:`
- **Purpose:** Method of `NullRedis` that handles get.

**Code:**
```python
async def get(self, key: str) -> None:
        return None
```

**Explanation:** It accepts `key` and returns `None`. See the code below for the full implementation.

### `NullRedis.setex`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `27-28`
- **Signature:** `async def setex(self, key: str, ttl: int, value: str) -> None:`
- **Purpose:** Method of `NullRedis` that handles setex.

**Code:**
```python
async def setex(self, key: str, ttl: int, value: str) -> None:
        return None
```

**Explanation:** It accepts `key`, `ttl`, `value` and returns `None`. See the code below for the full implementation.

### `NullRedis.keys`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `30-31`
- **Signature:** `async def keys(self, pattern: str) -> list[str]:`
- **Purpose:** Method of `NullRedis` that handles keys.

**Code:**
```python
async def keys(self, pattern: str) -> list[str]:
        return []
```

**Explanation:** It accepts `pattern` and returns `list[str]`. See the code below for the full implementation.

### `NullRedis.delete`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `33-34`
- **Signature:** `async def delete(self, *keys: str) -> int:`
- **Purpose:** Method of `NullRedis` that handles delete.

**Code:**
```python
async def delete(self, *keys: str) -> int:
        return 0
```

**Explanation:** It accepts `*keys` and returns `int`. See the code below for the full implementation.

### `NullRedisSync.get`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `40-41`
- **Signature:** `def get(self, key: str) -> None:`
- **Purpose:** Method of `NullRedisSync` that handles get.

**Code:**
```python
def get(self, key: str) -> None:
        return None
```

**Explanation:** It accepts `key` and returns `None`. See the code below for the full implementation.

### `NullRedisSync.setex`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `43-44`
- **Signature:** `def setex(self, key: str, ttl: int, value: str) -> None:`
- **Purpose:** Method of `NullRedisSync` that handles setex.

**Code:**
```python
def setex(self, key: str, ttl: int, value: str) -> None:
        return None
```

**Explanation:** It accepts `key`, `ttl`, `value` and returns `None`. See the code below for the full implementation.

### `NullRedisSync.keys`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `46-47`
- **Signature:** `def keys(self, pattern: str) -> list[str]:`
- **Purpose:** Method of `NullRedisSync` that handles keys.

**Code:**
```python
def keys(self, pattern: str) -> list[str]:
        return []
```

**Explanation:** It accepts `pattern` and returns `list[str]`. See the code below for the full implementation.

### `NullRedisSync.delete`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `49-50`
- **Signature:** `def delete(self, *keys: str) -> int:`
- **Purpose:** Method of `NullRedisSync` that handles delete.

**Code:**
```python
def delete(self, *keys: str) -> int:
        return 0
```

**Explanation:** It accepts `*keys` and returns `int`. See the code below for the full implementation.

### `_redis_url`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `53-55`
- **Signature:** `def _redis_url() -> str | None:`
- **Purpose:** Handles  redis url.

**Code:**
```python
def _redis_url() -> str | None:
    settings = get_settings()
    return settings.upstash_redis_url if settings.use_redis_cache else None
```

**Explanation:** It accepts zero arguments and returns `str | None`. See the code below for the full implementation. Key calls include `get_settings()`.

### `get_redis`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `58-71`
- **Signature:** `def get_redis() -> Redis | NullRedis:`
- **Purpose:** Retrieves redis.

**Code:**
```python
def get_redis() -> Redis | NullRedis:
    global _redis_async
    if _redis_async is None:
        redis_url = _redis_url()
        if not redis_url:
            logger.warning("UPSTASH_REDIS_URL is not configured; using null Redis cache.")
            _redis_async = NullRedis()
        else:
            try:
                _redis_async = Redis.from_url(redis_url, decode_responses=True)
            except Exception as exc:
                logger.warning("Failed to initialize async Redis: %s; using null cache.", exc)
                _redis_async = NullRedis()
    return _redis_async
```

**Explanation:** It accepts zero arguments and returns `Redis | NullRedis`. See the code below for the full implementation. Key calls include `_redis_url()`, `warning()`, `NullRedis()`, `from_url()`.

### `get_redis_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `74-87`
- **Signature:** `def get_redis_sync() -> redis_sync.Redis | NullRedisSync:`
- **Purpose:** Retrieves redis sync.

**Code:**
```python
def get_redis_sync() -> redis_sync.Redis | NullRedisSync:
    global _redis_sync
    if _redis_sync is None:
        redis_url = _redis_url()
        if not redis_url:
            logger.warning("UPSTASH_REDIS_URL is not configured; using null Redis sync cache.")
            _redis_sync = NullRedisSync()
        else:
            try:
                _redis_sync = redis_sync.Redis.from_url(redis_url, decode_responses=True)
            except Exception as exc:
                logger.warning("Failed to initialize sync Redis: %s; using null cache.", exc)
                _redis_sync = NullRedisSync()
    return _redis_sync
```

**Explanation:** It accepts zero arguments and returns `redis_sync.Redis | NullRedisSync`. See the code below for the full implementation. Key calls include `_redis_url()`, `warning()`, `NullRedisSync()`, `from_url()`.

### `is_redis_available`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `90-103`
- **Signature:** `def is_redis_available() -> bool:`
- **Purpose:** Return True if a real Redis connection is configured and healthy.

**Code:**
```python
def is_redis_available() -> bool:
    """Return True if a real Redis connection is configured and healthy."""
    settings = get_settings()
    if not settings.use_redis_cache or not settings.upstash_redis_url:
        return False
    redis = get_redis_sync()
    if isinstance(redis, NullRedisSync):
        return False
    try:
        redis.ping()
        return True
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        return False
```

**Explanation:** It accepts zero arguments and returns `bool`. See the code below for the full implementation. Key calls include `get_settings()`, `get_redis_sync()`, `isinstance()`, `ping()`, `warning()`.

### `_cache_key`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `110-111`
- **Signature:** `def _cache_key(renewable_type: str, level: str) -> str:`
- **Purpose:** Handles  cache key.

**Code:**
```python
def _cache_key(renewable_type: str, level: str) -> str:
    return f"lumi:suitability:{renewable_type}:{level}"
```

**Explanation:** It accepts `renewable_type`, `level` and returns `str`. See the code below for the full implementation.

### `get_suitability_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `114-123`
- **Signature:** `async def get_suitability_cache(renewable_type: str, level: str) -> list[dict[str, Any]] | None:`
- **Purpose:** Fetch cached municipality/province suitability data (async).

**Code:**
```python
async def get_suitability_cache(renewable_type: str, level: str) -> list[dict[str, Any]] | None:
    """Fetch cached municipality/province suitability data (async)."""
    try:
        redis = get_redis()
        raw = await redis.get(_cache_key(renewable_type, level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis suitability cache read failed: %s", exc)
    return None
```

**Explanation:** It accepts `renewable_type`, `level` and returns `list[dict[str, Any]] | None`. See the code below for the full implementation. Key calls include `get_redis()`, `get()`, `loads()`, `debug()`, `_cache_key()`.

### `set_suitability_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `126-141`
- **Signature:** `async def set_suitability_cache(`
- **Purpose:** Store suitability map data in Redis with TTL (async).

**Code:**
```python
async def set_suitability_cache(
    renewable_type: str,
    level: str,
    data: list[dict[str, Any]],
    ttl: int = _DEFAULT_TTL,
) -> None:
    """Store suitability map data in Redis with TTL (async)."""
    try:
        redis = get_redis()
        await redis.setex(
            _cache_key(renewable_type, level),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis suitability cache write failed: %s", exc)
```

**Explanation:** It accepts `renewable_type`, `level`, `data`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `setex()`, `debug()`, `_cache_key()`, `dumps()`.

### `invalidate_suitability_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `144-153`
- **Signature:** `async def invalidate_suitability_cache() -> None:`
- **Purpose:** Delete all suitability-related cache keys (async).

**Code:**
```python
async def invalidate_suitability_cache() -> None:
    """Delete all suitability-related cache keys (async)."""
    try:
        redis = get_redis()
        keys = await redis.keys("lumi:suitability:*")
        if keys:
            await redis.delete(*keys)
            logger.info("Invalidated %s suitability cache keys", len(keys))
    except Exception as exc:
        logger.warning("Redis suitability cache invalidation failed: %s", exc)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `keys()`, `info()`, `warning()`, `delete()`.

### `get_suitability_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `160-169`
- **Signature:** `def get_suitability_cache_sync(renewable_type: str, level: str) -> list[dict[str, Any]] | None:`
- **Purpose:** Fetch cached municipality/province suitability data (sync).

**Code:**
```python
def get_suitability_cache_sync(renewable_type: str, level: str) -> list[dict[str, Any]] | None:
    """Fetch cached municipality/province suitability data (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_cache_key(renewable_type, level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync suitability cache read failed: %s", exc)
    return None
```

**Explanation:** It accepts `renewable_type`, `level` and returns `list[dict[str, Any]] | None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `get()`, `_cache_key()`, `loads()`, `debug()`.

### `set_suitability_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `172-187`
- **Signature:** `def set_suitability_cache_sync(`
- **Purpose:** Store suitability map data in Redis with TTL (sync).

**Code:**
```python
def set_suitability_cache_sync(
    renewable_type: str,
    level: str,
    data: list[dict[str, Any]],
    ttl: int = _DEFAULT_TTL,
) -> None:
    """Store suitability map data in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _cache_key(renewable_type, level),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync suitability cache write failed: %s", exc)
```

**Explanation:** It accepts `renewable_type`, `level`, `data`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `setex()`, `_cache_key()`, `dumps()`, `debug()`.

### `invalidate_suitability_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `190-199`
- **Signature:** `def invalidate_suitability_cache_sync() -> None:`
- **Purpose:** Delete all suitability-related cache keys (sync).

**Code:**
```python
def invalidate_suitability_cache_sync() -> None:
    """Delete all suitability-related cache keys (sync)."""
    try:
        redis = get_redis_sync()
        keys = redis.keys("lumi:suitability:*")
        if keys:
            redis.delete(*keys)
            logger.info("Invalidated %s sync suitability cache keys", len(keys))
    except Exception as exc:
        logger.warning("Redis sync suitability cache invalidation failed: %s", exc)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `keys()`, `delete()`, `info()`, `warning()`.

### `_climate_cache_key`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `206-207`
- **Signature:** `def _climate_cache_key(level: str, geo_id: int | str, year: int | str) -> str:`
- **Purpose:** Handles  climate cache key.

**Code:**
```python
def _climate_cache_key(level: str, geo_id: int | str, year: int | str) -> str:
    return f"lumi:climate:{level}:{geo_id}:{year}"
```

**Explanation:** It accepts `level`, `geo_id`, `year` and returns `str`. See the code below for the full implementation.

### `get_climate_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `210-219`
- **Signature:** `def get_climate_cache_sync(level: str, geo_id: int | str, year: int | str) -> list[dict[str, Any]] | None:`
- **Purpose:** Fetch cached climate data for a geo unit and year (sync).

**Code:**
```python
def get_climate_cache_sync(level: str, geo_id: int | str, year: int | str) -> list[dict[str, Any]] | None:
    """Fetch cached climate data for a geo unit and year (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_climate_cache_key(level, geo_id, year))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync climate cache read failed: %s", exc)
    return None
```

**Explanation:** It accepts `level`, `geo_id`, `year` and returns `list[dict[str, Any]] | None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `get()`, `_climate_cache_key()`, `loads()`, `debug()`.

### `set_climate_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `222-238`
- **Signature:** `def set_climate_cache_sync(`
- **Purpose:** Store climate data in Redis with TTL (sync).

**Code:**
```python
def set_climate_cache_sync(
    level: str,
    geo_id: int | str,
    year: int | str,
    data: list[dict[str, Any]],
    ttl: int = _CLIMATE_TTL,
) -> None:
    """Store climate data in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _climate_cache_key(level, geo_id, year),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync climate cache write failed: %s", exc)
```

**Explanation:** It accepts `level`, `geo_id`, `year`, `data`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `setex()`, `_climate_cache_key()`, `dumps()`, `debug()`.

### `invalidate_climate_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `241-253`
- **Signature:** `def invalidate_climate_cache_sync(level: str | None = None, geo_id: int | str | None = None) -> None:`
- **Purpose:** Delete climate cache keys. If level/geo_id given, scoped; otherwise all.

**Code:**
```python
def invalidate_climate_cache_sync(level: str | None = None, geo_id: int | str | None = None) -> None:
    """Delete climate cache keys. If level/geo_id given, scoped; otherwise all."""
    try:
        redis = get_redis_sync()
        if level and geo_id is not None:
            keys = redis.keys(f"lumi:climate:{level}:{geo_id}:*")
        else:
            keys = redis.keys("lumi:climate:*")
        if keys:
            redis.delete(*keys)
            logger.info("Invalidated %s climate cache keys", len(keys))
    except Exception as exc:
        logger.warning("Redis sync climate cache invalidation failed: %s", exc)
```

**Explanation:** It accepts `level`, `geo_id` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `keys()`, `delete()`, `info()`, `warning()`.

### `_centroid_cache_key`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `260-261`
- **Signature:** `def _centroid_cache_key(level: str) -> str:`
- **Purpose:** Handles  centroid cache key.

**Code:**
```python
def _centroid_cache_key(level: str) -> str:
    return f"lumi:centroids:{level}"
```

**Explanation:** It accepts `level` and returns `str`. See the code below for the full implementation.

### `get_centroid_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `264-273`
- **Signature:** `def get_centroid_cache_sync(level: str) -> list[dict[str, Any]] | None:`
- **Purpose:** Fetch cached centroid data for a geographic level (sync).

**Code:**
```python
def get_centroid_cache_sync(level: str) -> list[dict[str, Any]] | None:
    """Fetch cached centroid data for a geographic level (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_centroid_cache_key(level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync centroid cache read failed: %s", exc)
    return None
```

**Explanation:** It accepts `level` and returns `list[dict[str, Any]] | None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `get()`, `_centroid_cache_key()`, `loads()`, `debug()`.

### `set_centroid_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `276-290`
- **Signature:** `def set_centroid_cache_sync(`
- **Purpose:** Store centroid data in Redis with TTL (sync).

**Code:**
```python
def set_centroid_cache_sync(
    level: str,
    data: list[dict[str, Any]],
    ttl: int = _CENTROID_TTL,
) -> None:
    """Store centroid data in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _centroid_cache_key(level),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync centroid cache write failed: %s", exc)
```

**Explanation:** It accepts `level`, `data`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `setex()`, `_centroid_cache_key()`, `dumps()`, `debug()`.

### `_ecosim_cache_key`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `297-298`
- **Signature:** `def _ecosim_cache_key(level: str, geo_id: int | str, params_hash: str) -> str:`
- **Purpose:** Handles  ecosim cache key.

**Code:**
```python
def _ecosim_cache_key(level: str, geo_id: int | str, params_hash: str) -> str:
    return f"lumi:ecosim:{level}:{geo_id}:{params_hash}"
```

**Explanation:** It accepts `level`, `geo_id`, `params_hash` and returns `str`. See the code below for the full implementation.

### `get_ecosim_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `301-310`
- **Signature:** `def get_ecosim_cache_sync(level: str, geo_id: int | str, params_hash: str) -> dict[str, Any] | None:`
- **Purpose:** Fetch cached EcoSim simulation result (sync).

**Code:**
```python
def get_ecosim_cache_sync(level: str, geo_id: int | str, params_hash: str) -> dict[str, Any] | None:
    """Fetch cached EcoSim simulation result (sync)."""
    try:
        redis = get_redis_sync()
        raw = redis.get(_ecosim_cache_key(level, geo_id, params_hash))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis sync ecosim cache read failed: %s", exc)
    return None
```

**Explanation:** It accepts `level`, `geo_id`, `params_hash` and returns `dict[str, Any] | None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `get()`, `_ecosim_cache_key()`, `loads()`, `debug()`.

### `set_ecosim_cache_sync`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `313-329`
- **Signature:** `def set_ecosim_cache_sync(`
- **Purpose:** Store EcoSim simulation result in Redis with TTL (sync).

**Code:**
```python
def set_ecosim_cache_sync(
    level: str,
    geo_id: int | str,
    params_hash: str,
    data: dict[str, Any],
    ttl: int = _ECOSIM_TTL,
) -> None:
    """Store EcoSim simulation result in Redis with TTL (sync)."""
    try:
        redis = get_redis_sync()
        redis.setex(
            _ecosim_cache_key(level, geo_id, params_hash),
            ttl,
            json.dumps(data, default=str),
        )
    except Exception as exc:
        logger.debug("Redis sync ecosim cache write failed: %s", exc)
```

**Explanation:** It accepts `level`, `geo_id`, `params_hash`, `data`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis_sync()`, `setex()`, `_ecosim_cache_key()`, `dumps()`, `debug()`.

### `get_climate_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `336-344`
- **Signature:** `async def get_climate_cache(level: str, geo_id: int | str, year: int | str) -> list[dict[str, Any]] | None:`
- **Purpose:** Retrieves climate cache.

**Code:**
```python
async def get_climate_cache(level: str, geo_id: int | str, year: int | str) -> list[dict[str, Any]] | None:
    try:
        redis = get_redis()
        raw = await redis.get(_climate_cache_key(level, geo_id, year))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis climate cache read failed: %s", exc)
    return None
```

**Explanation:** It accepts `level`, `geo_id`, `year` and returns `list[dict[str, Any]] | None`. See the code below for the full implementation. Key calls include `get_redis()`, `get()`, `loads()`, `debug()`, `_climate_cache_key()`.

### `set_climate_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `347-354`
- **Signature:** `async def set_climate_cache(`
- **Purpose:** Sets climate cache.

**Code:**
```python
async def set_climate_cache(
    level: str, geo_id: int | str, year: int | str, data: list[dict[str, Any]], ttl: int = _CLIMATE_TTL,
) -> None:
    try:
        redis = get_redis()
        await redis.setex(_climate_cache_key(level, geo_id, year), ttl, json.dumps(data, default=str))
    except Exception as exc:
        logger.debug("Redis climate cache write failed: %s", exc)
```

**Explanation:** It accepts `level`, `geo_id`, `year`, `data`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `setex()`, `debug()`, `_climate_cache_key()`, `dumps()`.

### `get_centroid_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `357-365`
- **Signature:** `async def get_centroid_cache(level: str) -> list[dict[str, Any]] | None:`
- **Purpose:** Retrieves centroid cache.

**Code:**
```python
async def get_centroid_cache(level: str) -> list[dict[str, Any]] | None:
    try:
        redis = get_redis()
        raw = await redis.get(_centroid_cache_key(level))
        if raw:
            return json.loads(raw)  # type: ignore[return-value]
    except Exception as exc:
        logger.debug("Redis centroid cache read failed: %s", exc)
    return None
```

**Explanation:** It accepts `level` and returns `list[dict[str, Any]] | None`. See the code below for the full implementation. Key calls include `get_redis()`, `get()`, `loads()`, `debug()`, `_centroid_cache_key()`.

### `set_centroid_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `368-373`
- **Signature:** `async def set_centroid_cache(level: str, data: list[dict[str, Any]], ttl: int = _CENTROID_TTL) -> None:`
- **Purpose:** Sets centroid cache.

**Code:**
```python
async def set_centroid_cache(level: str, data: list[dict[str, Any]], ttl: int = _CENTROID_TTL) -> None:
    try:
        redis = get_redis()
        await redis.setex(_centroid_cache_key(level), ttl, json.dumps(data, default=str))
    except Exception as exc:
        logger.debug("Redis centroid cache write failed: %s", exc)
```

**Explanation:** It accepts `level`, `data`, `ttl` and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `setex()`, `debug()`, `_centroid_cache_key()`, `dumps()`.

### `invalidate_all_geospatial_cache`

- **File:** `fastapi-backend/app/services/redis_client.py`
- **Lines:** `376-390`
- **Signature:** `async def invalidate_all_geospatial_cache() -> None:`
- **Purpose:** Delete all geospatial-related cache keys (async).

**Code:**
```python
async def invalidate_all_geospatial_cache() -> None:
    """Delete all geospatial-related cache keys (async)."""
    try:
        redis = get_redis()
        patterns = ["lumi:suitability:*", "lumi:climate:*", "lumi:centroids:*", "lumi:ecosim:*"]
        total = 0
        for pattern in patterns:
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
                total += len(keys)
        if total:
            logger.info("Invalidated %s total geospatial cache keys", total)
    except Exception as exc:
        logger.warning("Redis geospatial cache invalidation failed: %s", exc)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_redis()`, `info()`, `warning()`, `keys()`, `len()`.


## `fastapi-backend/app/services/solar_output_calc.py`

**File:** `fastapi-backend/app/services/solar_output_calc.py`

**Summary:** Solar output calculation module for LUMI EcoSim.

### `calculate_noct_cell_temp`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `15-42`
- **Signature:** `def calculate_noct_cell_temp(`
- **Purpose:** Estimate cell temperature using NOCT model.

**Code:**
```python
def calculate_noct_cell_temp(
    avg_temp_c: float,
    irradiance_w_m2: float,
    noct_c: float = 45.0,
    wind_speed_ms: float = 1.0,
) -> float:
    """Estimate cell temperature using NOCT model.

    T_cell = T_amb + (NOCT - 20) * (G / 800) / (1 + wind_factor)

    Based on IEC 61853 and King et al. (2004).

    Args:
        avg_temp_c: Ambient temperature in °C
        irradiance_w_m2: Plane-of-array irradiance in W/m²
        noct_c: Nominal Operating Cell Temperature (default 45°C for standard modules)
        wind_speed_ms: Wind speed at 10m in m/s

    Returns:
        Estimated cell temperature in °C
    """
    if irradiance_w_m2 <= 0:
        return avg_temp_c

    wind_factor = max(0.5, 1.0 + 0.1 * wind_speed_ms)

    t_cell = avg_temp_c + (noct_c - 20.0) * (irradiance_w_m2 / 800.0) / wind_factor
    return t_cell
```

**Explanation:** It accepts `avg_temp_c`, `irradiance_w_m2`, `noct_c`, `wind_speed_ms` and returns `float`. See the code below for the full implementation. Key calls include `max()`.

### `calculate_temperature_factor_noct`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `45-67`
- **Signature:** `def calculate_temperature_factor_noct(`
- **Purpose:** Temperature derating factor using NOCT cell temperature model.

**Code:**
```python
def calculate_temperature_factor_noct(
    avg_temp_c: float,
    irradiance_w_m2: float,
    temp_coeff_per_c: float = -0.004,
    noct_c: float = 45.0,
    wind_speed_ms: float = 1.0,
) -> float:
    """Temperature derating factor using NOCT cell temperature model.

    Args:
        avg_temp_c: Ambient temperature
        irradiance_w_m2: Solar irradiance in W/m²
        temp_coeff_per_c: Module temperature coefficient (default -0.4%/°C)
        noct_c: NOCT rating of module
        wind_speed_ms: Wind speed for cooling

    Returns:
        Temperature derating factor (0-1)
    """
    t_cell = calculate_noct_cell_temp(avg_temp_c, irradiance_w_m2, noct_c, wind_speed_ms)
    reference_temp = 25.0
    factor = 1.0 + temp_coeff_per_c * (t_cell - reference_temp)
    return max(factor, 0.0)
```

**Explanation:** It accepts `avg_temp_c`, `irradiance_w_m2`, `temp_coeff_per_c`, `noct_c`, `wind_speed_ms` and returns `float`. See the code below for the full implementation. Key calls include `calculate_noct_cell_temp()`, `max()`.

### `calculate_temperature_factor`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `70-76`
- **Signature:** `def calculate_temperature_factor(avg_temp_c: float | None, temp_coeff_per_c: float = -0.004) -> float:`
- **Purpose:** Legacy simple temperature factor (kept for backward compatibility).

**Code:**
```python
def calculate_temperature_factor(avg_temp_c: float | None, temp_coeff_per_c: float = -0.004) -> float:
    """Legacy simple temperature factor (kept for backward compatibility)."""
    if avg_temp_c is None:
        return 1.0
    reference_temp_c = 25.0
    factor = 1 + (temp_coeff_per_c * (avg_temp_c - reference_temp_c))
    return max(factor, 0.0)
```

**Explanation:** It accepts `avg_temp_c`, `temp_coeff_per_c` and returns `float`. See the code below for the full implementation. Key calls include `max()`.

### `calculate_soiling_loss`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `79-109`
- **Signature:** `def calculate_soiling_loss(`
- **Purpose:** Estimate soiling loss ratio from environmental factors.

**Code:**
```python
def calculate_soiling_loss(
    ws10m: float | None = None,
    rh2m: float | None = None,
    prectotcorr_mm: float | None = None,
    days_since_cleaning: int = 30,
) -> float:
    """Estimate soiling loss ratio from environmental factors.

    Soiling model considers:
    - Dust accumulation (wind-driven, increases with dry windy conditions)
    - Humidity (high humidity can both bind dust and cause fungal growth)
    - Rainfall (natural cleaning effect)

    Returns:
        Soiling loss ratio (0-1, where 1.0 = no loss, 0.85 = 15% loss)
    """
    base_soiling = 0.97

    if ws10m is not None and prectotcorr_mm is not None:
        if prectotcorr_mm < 10:  # Dry conditions
            dust_factor = 1.0 + 0.003 * max(ws10m - 2.0, 0) * (days_since_cleaning / 30)
            base_soiling = base_soiling / dust_factor

    if prectotcorr_mm is not None and prectotcorr_mm > 50:
        rain_cleaning = 1.0 + 0.001 * min(prectotcorr_mm - 50, 100)
        base_soiling = min(base_soiling * rain_cleaning, 0.99)

    if rh2m is not None and rh2m > 80:
        base_soiling *= 0.995

    return max(min(base_soiling, 1.0), 0.80)
```

**Explanation:** It accepts `ws10m`, `rh2m`, `prectotcorr_mm`, `days_since_cleaning` and returns `float`. See the code below for the full implementation. Key calls include `max()`, `min()`.

### `calculate_dust_loss_from_wind`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `112-117`
- **Signature:** `def calculate_dust_loss_from_wind(ws10m: float | None, base_dust_loss: float = 0.97) -> float:`
- **Purpose:** Legacy dust loss calculation (kept for backward compatibility).

**Code:**
```python
def calculate_dust_loss_from_wind(ws10m: float | None, base_dust_loss: float = 0.97) -> float:
    """Legacy dust loss calculation (kept for backward compatibility)."""
    if ws10m is None:
        return base_dust_loss
    wind_factor = 1 + 0.02 * (ws10m - 3.0)
    return max(min(base_dust_loss / wind_factor, 1.0), 0.80)
```

**Explanation:** It accepts `ws10m`, `base_dust_loss` and returns `float`. See the code below for the full implementation. Key calls include `max()`, `min()`.

### `calculate_degradation_from_humidity`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `120-126`
- **Signature:** `def calculate_degradation_from_humidity(rh2m: float | None, base_degradation: float = 0.99) -> float:`
- **Purpose:** Legacy humidity degradation (kept for backward compatibility).

**Code:**
```python
def calculate_degradation_from_humidity(rh2m: float | None, base_degradation: float = 0.99) -> float:
    """Legacy humidity degradation (kept for backward compatibility)."""
    if rh2m is None:
        return base_degradation
    if rh2m > 70:
        return base_degradation * 0.995
    return base_degradation
```

**Explanation:** It accepts `rh2m`, `base_degradation` and returns `float`. See the code below for the full implementation.

### `calculate_air_density_correction`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `129-146`
- **Signature:** `def calculate_air_density_correction(`
- **Purpose:** Air density correction factor for solar panel output.

**Code:**
```python
def calculate_air_density_correction(
    surface_pressure_pa: float | None,
    avg_temp_c: float | None,
) -> float:
    """Air density correction factor for solar panel output.

    Returns:
        Correction factor (typically 0.98-1.02)
    """
    if surface_pressure_pa is None or avg_temp_c is None:
        return 1.0

    p0 = 101325.0
    temp_k = avg_temp_c + 273.15
    rho_ratio = (surface_pressure_pa / p0) * (288.15 / temp_k)

    correction = 1.0 + 0.01 * (rho_ratio - 1.0)
    return max(min(correction, 1.02), 0.98)
```

**Explanation:** It accepts `surface_pressure_pa`, `avg_temp_c` and returns `float`. See the code below for the full implementation. Key calls include `max()`, `min()`.

### `calculate_performance_ratio`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `149-172`
- **Signature:** `def calculate_performance_ratio(`
- **Purpose:** Calculate overall performance ratio with optional advanced factors.

**Code:**
```python
def calculate_performance_ratio(
    system_efficiency: float = 0.80,
    temperature_factor: float = 1.0,
    dust_loss: float = 0.97,
    inverter_efficiency: float = 0.96,
    mismatch_loss: float = 0.98,
    wiring_loss: float = 0.98,
    degradation_loss: float = 0.99,
    soiling_loss: float | None = None,
    air_density_correction: float | None = None,
) -> float:
    """Calculate overall performance ratio with optional advanced factors."""
    pr = (
        system_efficiency
        * temperature_factor
        * (soiling_loss if soiling_loss is not None else dust_loss)
        * inverter_efficiency
        * mismatch_loss
        * wiring_loss
        * degradation_loss
    )
    if air_density_correction is not None:
        pr *= air_density_correction
    return max(pr, 0.0)
```

**Explanation:** It accepts `system_efficiency`, `temperature_factor`, `dust_loss`, `inverter_efficiency`, `mismatch_loss`, `wiring_loss`, `degradation_loss`, `soiling_loss`, `air_density_correction` and returns `float`. See the code below for the full implementation. Key calls include `max()`.

### `solar_calc`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `175-192`
- **Signature:** `def solar_calc(`
- **Purpose:** Legacy solar calculation (kept for backward compatibility).

**Code:**
```python
def solar_calc(
    panel_wattage: float,
    number_of_panels: int,
    solar_irradiance: float,
    performance_ratio: float,
    days_in_month: int,
) -> dict[str, Any]:
    """Legacy solar calculation (kept for backward compatibility)."""
    system_kwp = (panel_wattage * number_of_panels) / 1000.0
    daily_solar_output = system_kwp * solar_irradiance * performance_ratio
    monthly_solar_output = daily_solar_output * days_in_month
    solar_score = min((solar_irradiance / 6.0) * 100, 100)
    return {
        "system_kwp": system_kwp,
        "daily_solar_output": daily_solar_output,
        "monthly_solar_output": monthly_solar_output,
        "solar_score": solar_score,
    }
```

**Explanation:** It accepts `panel_wattage`, `number_of_panels`, `solar_irradiance`, `performance_ratio`, `days_in_month` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `min()`.

### `solar_calc_advanced`

- **File:** `fastapi-backend/app/services/solar_output_calc.py`
- **Lines:** `195-309`
- **Signature:** `def solar_calc_advanced(`
- **Purpose:** Advanced solar output calculation with NOCT, soiling, and transposition.

**Code:**
```python
def solar_calc_advanced(
    panel_wattage: float,
    number_of_panels: int,
    ghi_kwh_m2_day: float,
    dni_kwh_m2_day: float | None = None,
    dhi_kwh_m2_day: float | None = None,
    avg_temp_c: float | None = None,
    rh2m: float | None = None,
    ws10m: float | None = None,
    prectotcorr_mm: float | None = None,
    surface_pressure_pa: float | None = None,
    panel_tilt_deg: float = 15.0,
    panel_azimuth_deg: float = 180.0,
    latitude_deg: float = 14.0,
    noct_c: float = 45.0,
    temp_coeff_per_c: float = -0.004,
    inverter_efficiency: float = 0.96,
    mismatch_loss: float = 0.98,
    wiring_loss: float = 0.98,
    degradation_loss: float = 0.99,
    days_in_month: int = 30,
    days_since_cleaning: int = 30,
) -> dict[str, Any]:
    """Advanced solar output calculation with NOCT, soiling, and transposition.

    Uses GHI as primary input. If DNI and DHI are available, uses
    transposition model for tilted surface irradiance. Otherwise,
    applies a tilt correction factor to GHI.

    Args:
        ghi_kwh_m2_day: Global Horizontal Irradiance in kWh/m²/day
        dni_kwh_m2_day: Direct Normal Irradiance (optional)
        dhi_kwh_m2_day: Diffuse Horizontal Irradiance (optional)
        panel_tilt_deg: Panel tilt angle (default 15° for PH latitude)
        panel_azimuth_deg: Panel azimuth (180° = south)
        latitude_deg: Site latitude
        noct_c: Module NOCT rating

    Returns:
        Dict with detailed solar output and loss breakdown
    """
    system_kwp = (panel_wattage * number_of_panels) / 1000.0

    # Transposition: calculate plane-of-array (POA) irradiance
    if dni_kwh_m2_day is not None and dhi_kwh_m2_day is not None:
        tilt_rad = math.radians(panel_tilt_deg)
        aoi_cos = max(0.0, math.cos(tilt_rad) * 0.95)
        poa = (
            dhi_kwh_m2_day * (1 + math.cos(tilt_rad)) / 2
            + dni_kwh_m2_day * aoi_cos
            + ghi_kwh_m2_day * 0.2 * (1 - math.cos(tilt_rad)) / 2
        )
        poa = max(poa, ghi_kwh_m2_day * 0.9)
        transposition_source = "hay_davies"
    else:
        tilt_gain = 1.0 + 0.05 * math.cos(math.radians(panel_tilt_deg - latitude_deg))
        poa = ghi_kwh_m2_day * tilt_gain
        transposition_source = "ghi_tilt_correction"

    poa_w_m2 = poa * 1000 / 24

    if avg_temp_c is not None:
        temp_factor = calculate_temperature_factor_noct(
            avg_temp_c=avg_temp_c,
            irradiance_w_m2=poa_w_m2,
            temp_coeff_per_c=temp_coeff_per_c,
            noct_c=noct_c,
            wind_speed_ms=ws10m or 1.0,
        )
    else:
        temp_factor = 1.0

    soiling = calculate_soiling_loss(
        ws10m=ws10m,
        rh2m=rh2m,
        prectotcorr_mm=prectotcorr_mm,
        days_since_cleaning=days_since_cleaning,
    )

    air_density = calculate_air_density_correction(surface_pressure_pa, avg_temp_c)

    pr = calculate_performance_ratio(
        temperature_factor=temp_factor,
        soiling_loss=soiling,
        air_density_correction=air_density,
        inverter_efficiency=inverter_efficiency,
        mismatch_loss=mismatch_loss,
        wiring_loss=wiring_loss,
        degradation_loss=degradation_loss,
    )

    daily_solar_output = system_kwp * poa * pr
    monthly_solar_output = daily_solar_output * days_in_month

    solar_score = min((ghi_kwh_m2_day / 6.0) * 100, 100)

    return {
        "system_kwp": round(system_kwp, 4),
        "poa_irradiance_kwh_m2_day": round(poa, 4),
        "transposition_source": transposition_source,
        "daily_solar_output": round(daily_solar_output, 4),
        "monthly_solar_output": round(monthly_solar_output, 4),
        "solar_score": round(solar_score, 2),
        "performance_ratio": round(pr, 4),
        "loss_breakdown": {
            "temperature_factor": round(temp_factor, 4),
            "soiling_loss": round(soiling, 4),
            "air_density_correction": round(air_density, 4),
            "inverter_efficiency": inverter_efficiency,
            "mismatch_loss": mismatch_loss,
            "wiring_loss": wiring_loss,
            "degradation_loss": degradation_loss,
        },
        "cell_temp_c": round(calculate_noct_cell_temp(avg_temp_c or 25, poa_w_m2, noct_c, ws10m or 1.0), 2) if avg_temp_c else None,
    }
```

**Explanation:** It accepts `panel_wattage`, `number_of_panels`, `ghi_kwh_m2_day`, `dni_kwh_m2_day`, `dhi_kwh_m2_day`, `avg_temp_c`, `rh2m`, `ws10m`, `prectotcorr_mm`, `surface_pressure_pa`, `panel_tilt_deg`, `panel_azimuth_deg`, `latitude_deg`, `noct_c`, `temp_coeff_per_c`, `inverter_efficiency`, `mismatch_loss`, `wiring_loss`, `degradation_loss`, `days_in_month`, `days_since_cleaning` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `radians()`, `max()`, `cos()`, `calculate_temperature_factor_noct()`, `calculate_soiling_loss()`.


## `fastapi-backend/app/services/supabase_service.py`

**File:** `fastapi-backend/app/services/supabase_service.py`

**Summary:** Source file `fastapi-backend/app/services/supabase_service.py`.

### `_is_jwt_key`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `22-23`
- **Signature:** `def _is_jwt_key(key: str | None) -> bool:`
- **Purpose:** Handles  is jwt key.

**Code:**
```python
def _is_jwt_key(key: str | None) -> bool:
    return bool(key) and _JWT_PATTERN.match(key) is not None
```

**Explanation:** It accepts `key` and returns `bool`. See the code below for the full implementation. Key calls include `bool()`, `match()`.

### `_reset_supabase_client`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `26-30`
- **Signature:** `def _reset_supabase_client() -> None:`
- **Purpose:** Reset singletons (useful for testing or after settings change).

**Code:**
```python
def _reset_supabase_client() -> None:
    """Reset singletons (useful for testing or after settings change)."""
    global _supabase_client, _supabase_public_client
    _supabase_client = None
    _supabase_public_client = None
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation.

### `SupabaseResponse.__init__`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `34-35`
- **Signature:** `def __init__(self, data: Any):`
- **Purpose:** Method of `SupabaseResponse` that handles   init  .

**Code:**
```python
def __init__(self, data: Any):
        self.data = data
```

**Explanation:** It accepts `data`. See the code below for the full implementation.

### `SupabaseRestQuery.__init__`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `39-45`
- **Signature:** `def __init__(self, client: "SupabaseRestClient", table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []
        self._single = False
        self._limit: int | None = None
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `47-49`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.eq`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `51-53`
- **Signature:** `def eq(self, column: str, value: str) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles eq.

**Code:**
```python
def eq(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, urllib.parse.quote(str(value), safe="")))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`, `quote()`, `str()`.

### `SupabaseRestQuery.limit`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `55-57`
- **Signature:** `def limit(self, n: int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles limit.

**Code:**
```python
def limit(self, n: int) -> "SupabaseRestQuery":
        self._limit = n
        return self
```

**Explanation:** It accepts `n` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.offset`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `59-61`
- **Signature:** `def offset(self, n: int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles offset.

**Code:**
```python
def offset(self, n: int) -> "SupabaseRestQuery":
        self._offset = n
        return self
```

**Explanation:** It accepts `n` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.single`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `63-65`
- **Signature:** `def single(self) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles single.

**Code:**
```python
def single(self) -> "SupabaseRestQuery":
        self._single = True
        return self
```

**Explanation:** It accepts zero arguments and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `67-84`
- **Signature:** `def execute(self) -> SupabaseResponse:`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
def execute(self) -> SupabaseResponse:
        params: dict[str, str] = {"select": self._select}
        for column, value in self._filters:
            params[column] = f"eq.{value}"
        if self._single:
            params["limit"] = "1"
        elif self._limit is not None:
            params["limit"] = str(self._limit)
        if getattr(self, "_offset", None) is not None:
            params["offset"] = str(self._offset)

        url = f"{self._client.base_url}/rest/v1/{self._table}"
        response = self._client.http.get(url, params=params, headers=self._client.headers)
        response.raise_for_status()
        data = response.json()
        if self._single:
            data = data[0] if data else None
        return SupabaseResponse(data)
```

**Explanation:** It accepts zero arguments and returns `SupabaseResponse`. See the code below for the full implementation. Key calls include `str()`, `getattr()`, `get()`, `raise_for_status()`, `json()`.

### `SupabaseRestClient.__init__`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `88-94`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=10.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.__del__`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `96-100`
- **Signature:** `def __del__(self):`
- **Purpose:** Method of `SupabaseRestClient` that handles   del  .

**Code:**
```python
def __del__(self):
        try:
            self.http.close()
        except Exception:
            pass
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `close()`.

### `SupabaseRestClient.table`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `102-103`
- **Signature:** `def table(self, table_name: str) -> SupabaseRestQuery:`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name` and returns `SupabaseRestQuery`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `_create_client`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `106-110`
- **Signature:** `def _create_client(url: str, key: str) -> Client | SupabaseRestClient:`
- **Purpose:** Handles  create client.

**Code:**
```python
def _create_client(url: str, key: str) -> Client | SupabaseRestClient:
    if _is_jwt_key(key):
        return create_client(url, key)
    logger.warning("Supabase key is not JWT; using REST client fallback for table queries only.")
    return SupabaseRestClient(url, key)
```

**Explanation:** It accepts `url`, `key` and returns `Client | SupabaseRestClient`. See the code below for the full implementation. Key calls include `_is_jwt_key()`, `create_client()`, `warning()`, `SupabaseRestClient()`.

### `get_supabase_client`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `113-127`
- **Signature:** `def get_supabase_client() -> Client | SupabaseRestClient:`
- **Purpose:** Retrieves supabase client.

**Code:**
```python
def get_supabase_client() -> Client | SupabaseRestClient:
    global _supabase_client
    if _supabase_client is None:
        settings = get_settings()
        key = settings.supabase_service_role_key or settings.supabase_anon_key
        if not key:
            raise ValueError("Supabase key is missing. Check your .env and environment overrides.")
        _supabase_client = _create_client(settings.supabase_url, key)
        logger.debug(
            "Supabase client initialized: url=%s key_source=%s key_present=%s",
            settings.supabase_url,
            "service_role" if settings.supabase_service_role_key else "anon",
            bool(key),
        )
    return _supabase_client
```

**Explanation:** It accepts zero arguments and returns `Client | SupabaseRestClient`. See the code below for the full implementation. Key calls include `get_settings()`, `_create_client()`, `debug()`, `ValueError()`, `bool()`.

### `get_supabase_public_client`

- **File:** `fastapi-backend/app/services/supabase_service.py`
- **Lines:** `130-142`
- **Signature:** `def get_supabase_public_client() -> Client | SupabaseRestClient:`
- **Purpose:** Retrieves supabase public client.

**Code:**
```python
def get_supabase_public_client() -> Client | SupabaseRestClient:
    global _supabase_public_client
    if _supabase_public_client is None:
        settings = get_settings()
        if not settings.supabase_anon_key:
            raise ValueError("Supabase anon key is missing. Check your .env and environment overrides.")
        _supabase_public_client = _create_client(settings.supabase_url, settings.supabase_anon_key)
        logger.debug(
            "Supabase public client initialized: url=%s key_present=%s",
            settings.supabase_url,
            bool(settings.supabase_anon_key),
        )
    return _supabase_public_client
```

**Explanation:** It accepts zero arguments and returns `Client | SupabaseRestClient`. See the code below for the full implementation. Key calls include `get_settings()`, `_create_client()`, `debug()`, `ValueError()`, `bool()`.


## `fastapi-backend/app/services/test_full_pipeline.py`

**File:** `fastapi-backend/app/services/test_full_pipeline.py`

**Summary:** Full pipeline test — RAG + Groq + Gemini fallback.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/test_gemini_mock.py`

**File:** `fastapi-backend/app/services/test_gemini_mock.py`

**Summary:** Source file `fastapi-backend/app/services/test_gemini_mock.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/test_prompt_inspection.py`

**File:** `fastapi-backend/app/services/test_prompt_inspection.py`

**Summary:** Source file `fastapi-backend/app/services/test_prompt_inspection.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/test_rag_normalize.py`

**File:** `fastapi-backend/app/services/test_rag_normalize.py`

**Summary:** Source file `fastapi-backend/app/services/test_rag_normalize.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/test_rag_pipeline.py`

**File:** `fastapi-backend/app/services/test_rag_pipeline.py`

**Summary:** Test script for the LUMI RAG pipeline.

### `_build_index`

- **File:** `fastapi-backend/app/services/test_rag_pipeline.py`
- **Lines:** `28-35`
- **Signature:** `def _build_index() -> None:`
- **Purpose:** Handles  build index.

**Code:**
```python
def _build_index() -> None:
    logger.info("=== Building knowledge base ===")
    docs = build_knowledge_base()
    save_knowledge_base(docs)

    logger.info("=== Building FAISS index ===")
    meta = rag_pipeline.build_faiss_index(docs)
    logger.info("Index metadata: %s", meta)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `info()`, `build_knowledge_base()`, `save_knowledge_base()`, `build_faiss_index()`.

### `_test_retrieval`

- **File:** `fastapi-backend/app/services/test_rag_pipeline.py`
- **Lines:** `38-61`
- **Signature:** `def _test_retrieval() -> None:`
- **Purpose:** Handles  test retrieval.

**Code:**
```python
def _test_retrieval() -> None:
    queries = [
        "How much would solar installation cost for this municipality?",
        "Which renewable source is cheaper?",
        "How much does a small hydro system usually require?",
        "Compare solar vs wind vs hydro costs.",
        "What equipment is needed for a wind system?",
        "Solar panel price range",
        "Hydro turbine equipment cost",
    ]

    logger.info("\n=== Retrieval tests ===")
    for q in queries:
        results = rag_pipeline.retrieve_context(q, top_k=3)
        logger.info("\nQuery: %s", q)
        for i, r in enumerate(results, 1):
            logger.info(
                "  %s. [score=%s] [%s/%s] %s",
                i,
                r["score"],
                r.get("renewable_type", "?"),
                r.get("category", "?"),
                r["text"][:200].replace("\n", " "),
            )
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `info()`, `retrieve_context()`, `enumerate()`, `get()`, `replace()`.

### `_test_end_to_end`

- **File:** `fastapi-backend/app/services/test_rag_pipeline.py`
- **Lines:** `64-136`
- **Signature:** `def _test_end_to_end() -> None:`
- **Purpose:** Handles  test end to end.

**Code:**
```python
def _test_end_to_end() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set — skipping end-to-end Gemini tests.")
        return

    # Minimal ecosim payload for testing
    analysis_payload = {
        "municipality_data": [
            {
                "municipality_id": 1,
                "avg_t2m": 27.5,
                "avg_t2m_max": 32.0,
                "avg_t2m_min": 23.0,
                "avg_rh2m": 78.0,
                "avg_rhoa": 1.18,
                "avg_prectotcorr": 180.0,
                "avg_ws10m": 3.2,
                "avg_allsky_sfc_sw_dwn": 5.2,
                "avg_cloud_amt": 65.0,
                "avg_surface_pressure": 1010.0,
            }
        ],
        "consumption_results": {
            "monthly_consumption_kwh": 300.0,
            "daily_consumption_kwh": 10.0,
            "target_monthly_consumption_kwh": 150.0,
        },
        "renewable_energy_results": {
            "municipality": "TEST_MUNICIPALITY",
            "climate": {
                "avg_t2m": 27.5,
                "avg_ws10m": 3.2,
                "avg_prectotcorr": 180.0,
                "avg_allsky_sfc_sw_dwn": 5.2,
            },
            "solar_output": {
                "system_kwp": 1.1,
                "daily_solar_output": 3.5,
                "monthly_solar_output": 105.0,
            },
            "hydro_output": {
                "system_kwp": 0.5,
                "daily_hydro_output": 2.0,
                "monthly_hydro_output": 60.0,
                "hydro_score": 0.3,
            },
            "wind_output": {
                "swept_area_m2": 2.5,
                "rated_power_kw": 1.0,
                "capacity_factor": 0.12,
                "daily_energy_kwh": 2.9,
                "monthly_energy_kwh": 87.0,
            },
            "consumption_results": {
                "monthly_consumption_kwh": 300.0,
                "daily_consumption_kwh": 10.0,
                "target_monthly_consumption_kwh": 150.0,
            },
        },
    }

    test_cases = [
        ("Test 1 — Solar budget", "Estimate my solar installation budget."),
        ("Test 2 — Hydro equipment", "What equipment is needed for a small hydro system?"),
        ("Test 3 — Solar vs Wind", "Should I choose solar or wind for my home?"),
    ]

    logger.info("\n=== End-to-end Gemini RAG tests ===")
    for name, query in test_cases:
        logger.info("\n%s", name)
        result = analyze_with_rag(analysis_payload, query, top_k=5)
        logger.info("Result:\n%s", json.dumps(result, indent=2, ensure_ascii=False))
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `getenv()`, `warning()`, `info()`, `analyze_with_rag()`, `dumps()`.

### `main`

- **File:** `fastapi-backend/app/services/test_rag_pipeline.py`
- **Lines:** `139-142`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    _build_index()
    _test_retrieval()
    _test_end_to_end()
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `_build_index()`, `_test_retrieval()`, `_test_end_to_end()`.


## `fastapi-backend/app/services/test_retrieval_only.py`

**File:** `fastapi-backend/app/services/test_retrieval_only.py`

**Summary:** Source file `fastapi-backend/app/services/test_retrieval_only.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/app/services/wind_output_calc.py`

**File:** `fastapi-backend/app/services/wind_output_calc.py`

**Summary:** Source file `fastapi-backend/app/services/wind_output_calc.py`.

### `_compute_wind_averages`

- **File:** `fastapi-backend/app/services/wind_output_calc.py`
- **Lines:** `24-53`
- **Signature:** `def _compute_wind_averages(csv_path: str) -> dict:`
- **Purpose:** Handles  compute wind averages.

**Code:**
```python
def _compute_wind_averages(csv_path: str) -> dict:
	df = pd.read_csv(csv_path)
	df["rotor_radius_m"] = pd.to_numeric(df["rotor_radius_m"], errors="coerce")
	df["power_coefficient"] = pd.to_numeric(df["power_coefficient"], errors="coerce")

	rotor_series = df["rotor_radius_m"].dropna()
	cp_series = df["power_coefficient"].dropna()

	avg_rotor_radius_m = float(rotor_series.mean()) if not rotor_series.empty else 0.0
	avg_power_coefficient = float(cp_series.mean()) if not cp_series.empty else 0.0

	summary_rotor = (
		"Average rotor radius (m): "
		f"{avg_rotor_radius_m:.3f} from {len(rotor_series)} rows where a blade diameter was parsed "
		"from text (m/cm/mm/in/ft), then divided by 2."
	)
	summary_cp = (
		"Average power coefficient: "
		f"{avg_power_coefficient:.3f} from {len(cp_series)} rows with both parsed power (W/kW/MW) and diameter; "
		"uses Cp = P / (0.5 * 1.225 * A * V^3) with V=12.0 m/s unless a m/s value is present."
	)

	return {
		"avg_rotor_radius_m": avg_rotor_radius_m,
		"avg_power_coefficient": avg_power_coefficient * 100,
		"rotor_count": len(rotor_series),
		"cp_count": len(cp_series),
		"summary_rotor": summary_rotor,
		"summary_cp": summary_cp,
	}
```

**Explanation:** It accepts `csv_path` and returns `dict`. See the code below for the full implementation. Key calls include `read_csv()`, `to_numeric()`, `dropna()`, `float()`, `mean()`.

### `load_wind_averages`

- **File:** `fastapi-backend/app/services/wind_output_calc.py`
- **Lines:** `56-89`
- **Signature:** `def load_wind_averages(csv_path: str | None = None) -> dict:`
- **Purpose:** Loads wind averages.

**Code:**
```python
def load_wind_averages(csv_path: str | None = None) -> dict:
	global _wind_summary
	if _wind_summary is not None:
		return _wind_summary

	cache_key = "wind:summary:betz"
	cached = cache_get_sync(cache_key)
	if cached is not None:
		_wind_summary = cached
		return _wind_summary

	try:
		client = get_supabase_client()
		resp = (
			client.table("wind_products_summary")
			.select("*")
			.eq("variant", "betz")
			.single()
			.execute()
		)
		if resp.data:
			_wind_summary = resp.data
			cache_set_sync(cache_key, resp.data, ttl=86400)
			return _wind_summary
	except Exception as exc:
		logger.warning("Failed to load wind summary from Supabase: %s", exc)

	if os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true":
		path = csv_path or DATA_PATH
		if os.path.exists(path):
			_wind_summary = _compute_wind_averages(path)
			return _wind_summary

	raise RuntimeError("Wind summary unavailable and local fallback disabled")
```

**Explanation:** It accepts `csv_path` and returns `dict`. See the code below for the full implementation. Key calls include `cache_get_sync()`, `get_supabase_client()`, `execute()`, `cache_set_sync()`, `warning()`.

### `calculate_wind_output`

- **File:** `fastapi-backend/app/services/wind_output_calc.py`
- **Lines:** `98-180`
- **Signature:** `def calculate_wind_output(`
- **Purpose:** Calculate wind turbine power output and energy production.

**Code:**
```python
def calculate_wind_output(
    wind_speed_mps: float,
    days_in_month: int,
    air_density: float,
    rotor_radius_m: float | None = None,
    cp: float | None = None,
    efficiency: float = 0.90,
    capacity_factor: float = 0.30,  # NEW: 30% typical for small turbines [Baker et al., 2023]
    operating_hours_per_day: int = 24,
) -> dict:
    """
    Calculate wind turbine power output and energy production.
    
    Based on the fundamental wind power equation:
    P = 0.5 × ρ × A × V³ × Cp × η 
    - Fahim, A., Al-Mamun, A., & Hassan, M. A. (2024). 
    Toward a physics-based model of power coefficient in horizontal-axis wind turbines. 
    Wind Engineering, 48(3), 245–262. https://doi.org/10.1177/0309524X241263600
    
    Args:
        rotor_radius_m: Rotor radius in meters
        wind_speed_mps: Wind speed in m/s (from ws10m in schema)
        air_density: Air density in kg/m³ (from rhoa in schema, default 1.225) [Kumar et al., 2022]
        cp: Power coefficient (0.40 typical for HAWT, 0.10-0.25 for VAWT) [Alam & Jin, 2023]
        efficiency: Mechanical/electrical efficiency (0.85-0.95 typical) [Andersen & Jonassen, 2025]
        capacity_factor: Fraction of time turbine produces at rated power (0.20-0.40 typical) [Baker et al., 2023]
        operating_hours_per_day: Hours per day (typically 24)
        days_in_month: Days in month (typically 30)
    
    Returns:
        Dictionary with swept area, power, and energy estimates
    """
    if rotor_radius_m is None or cp is None:
        summary = load_wind_averages()
        if rotor_radius_m is None:
            rotor_radius_m = float(summary["avg_rotor_radius_m"])
        if cp is None:
            cp = float(summary["avg_power_coefficient"]) / 100

    # Validate inputs
    if rotor_radius_m <= 0 or wind_speed_mps <= 0:
        raise ValueError("Rotor radius and wind speed must be positive values")
    
    if not 0.9 <= air_density <= 1.3:
        raise ValueError("Air density should be in realistic range (0.9-1.3 kg/m³)")
    
    if cp > 0.593:
        raise ValueError(f"Cp ({cp}) exceeds Betz limit (0.593) [González-Hernández & Salas-Cabrera, 2021]")
    
    if not 0 <= capacity_factor <= 1:
        raise ValueError("Capacity factor must be between 0 and 1")
    
    # Calculate swept area: A = π × r² [Fahim et al., 2024]
    swept_area = math.pi * (rotor_radius_m ** 2)
    
    # Calculate rated power: P = 0.5 × ρ × A × V³ × Cp × η [Fahim et al., 2024]
    power_watts = (
        0.5 *
        air_density *
        swept_area *
        (wind_speed_mps ** 3) *
        cp *
        efficiency
    )
    
    power_kw = power_watts / 1000.0
    
    # Apply capacity factor for realistic energy production [Baker et al., 2023]
    # Without capacity factor: assumes 100% operation at rated power (unrealistic)
    # With capacity factor: accounts for variable wind, maintenance, cut-in/out speeds
    effective_hours_per_day = operating_hours_per_day * capacity_factor
    
    daily_energy_kwh = power_kw * effective_hours_per_day
    monthly_energy_kwh = daily_energy_kwh * days_in_month
    
    return {
        "swept_area_m2": round(swept_area, 4),
        "rated_power_kw": round(power_kw, 4),
        "capacity_factor": capacity_factor,
        "effective_operating_hours_per_day": round(effective_hours_per_day, 2),
        "daily_energy_kwh": round(daily_energy_kwh, 4),
        "monthly_energy_kwh": round(monthly_energy_kwh, 4),
    }
```

**Explanation:** It accepts `wind_speed_mps`, `days_in_month`, `air_density`, `rotor_radius_m`, `cp`, `efficiency`, `capacity_factor`, `operating_hours_per_day` and returns `dict`. See the code below for the full implementation. Key calls include `load_wind_averages()`, `float()`, `ValueError()`, `round()`.


## `fastapi-backend/app/utils/__init__.py`

**File:** `fastapi-backend/app/utils/__init__.py`

**Summary:** Source file `fastapi-backend/app/utils/__init__.py`.

_No module-level or class-level functions in this file._

## `fastapi-backend/scripts/extract_ecostress_lst.py`

**File:** `fastapi-backend/scripts/extract_ecostress_lst.py`

**Summary:** Extract ECOSTRESS L2G LSTE surface temperature for Philippine municipalities.

### `read_lst_array`

- **File:** `fastapi-backend/scripts/extract_ecostress_lst.py`
- **Lines:** `49-83`
- **Signature:** `def read_lst_array(h5_path: Path) -> tuple[np.ndarray, dict] | None:`
- **Purpose:** Read raw LST uint16 array and metadata from ECOSTRESS L2G HDF5.

**Code:**
```python
def read_lst_array(h5_path: Path) -> tuple[np.ndarray, dict] | None:
    """Read raw LST uint16 array and metadata from ECOSTRESS L2G HDF5.

    Returns:
        (raw_lst_array, meta_dict) or None on error.
    """
    if not h5_path.exists():
        logger.error("HDF5 file not found: %s", h5_path)
        return None

    try:
        with h5py.File(h5_path, "r") as f:
            lst_ds = f["HDFEOS"]["GRIDS"]["ECO_L2G_LSTE_70m"]["Data Fields"]["LST"]
            raw = lst_ds[()]

            meta = {
                "scale_factor": float(lst_ds.attrs["scale_factor"][0]),
                "add_offset": float(lst_ds.attrs["add_offset"][0]),
                "units": lst_ds.attrs["units"].decode("utf-8"),
                "fill_value": int(lst_ds.attrs["_FillValue"][0]),
                "valid_min": int(lst_ds.attrs["valid_range"][0]),
                "valid_max": int(lst_ds.attrs["valid_range"][1]),
                "shape": raw.shape,
            }
            logger.info("LST array shape: %s | dtype: %s", raw.shape, raw.dtype)
            logger.info(
                "Scale factor: %s | Offset: %s | Units: %s",
                meta["scale_factor"],
                meta["add_offset"],
                meta["units"],
            )
            return raw, meta
    except Exception as exc:
        logger.error("Failed to read LST from HDF5: %s", exc)
        return None
```

**Explanation:** It accepts `h5_path` and returns `tuple[np.ndarray, dict] | None`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `File()`, `info()`, `float()`.

### `extract_spatial_extent`

- **File:** `fastapi-backend/scripts/extract_ecostress_lst.py`
- **Lines:** `86-127`
- **Signature:** `def extract_spatial_extent(h5_path: Path) -> dict | None:`
- **Purpose:** Parse HDF-EOS StructMetadata to get corner coordinates.

**Code:**
```python
def extract_spatial_extent(h5_path: Path) -> dict | None:
    """Parse HDF-EOS StructMetadata to get corner coordinates.

    NOTE: ECOSTRESS L2G metadata projection interpretation can be
    ambiguous. This function extracts raw values for manual review.
    """
    try:
        with h5py.File(h5_path, "r") as f:
            meta_bytes = f["HDFEOS INFORMATION"]["StructMetadata.0"][()]
            meta = meta_bytes.decode("utf-8")
    except Exception as exc:
        logger.error("Failed to read metadata: %s", exc)
        return None

    import re

    extent = {}
    # UpperLeft
    m = re.search(r"UpperLeftPointMtrs=\(([-\d.]+),\s*([-\d.]+)\)", meta)
    if m:
        extent["upper_left_x"] = float(m.group(1))
        extent["upper_left_y"] = float(m.group(2))

    # LowerRight
    m = re.search(r"LowerRightMtrs=\(([-\d.]+),\s*([-\d.]+)\)", meta)
    if m:
        extent["lower_right_x"] = float(m.group(1))
        extent["lower_right_y"] = float(m.group(2))

    # Projection
    m = re.search(r'Projection=(\w+)', meta)
    if m:
        extent["projection"] = m.group(1)

    # Pixel size (if available)
    m = re.search(r"PixelSize=\(([-\d.]+),\s*([-\d.]+)\)", meta)
    if m:
        extent["pixel_size_x"] = float(m.group(1))
        extent["pixel_size_y"] = float(m.group(2))

    logger.info("Spatial extent from metadata: %s", extent)
    return extent
```

**Explanation:** It accepts `h5_path` and returns `dict | None`. See the code below for the full implementation. Key calls include `File()`, `decode()`, `error()`, `search()`, `float()`.

### `build_affine_transform`

- **File:** `fastapi-backend/scripts/extract_ecostress_lst.py`
- **Lines:** `130-165`
- **Signature:** `def build_affine_transform(extent: dict, shape: tuple) -> dict | None:`
- **Purpose:** Build a simple affine transform assuming geographic coverage.

**Code:**
```python
def build_affine_transform(extent: dict, shape: tuple) -> dict | None:
    """Build a simple affine transform assuming geographic coverage.

    WARNING: ECOSTRESS L2G metadata projection values can be misleading.
    This is a best-effort linear transform for Philippine coverage.
    For production use, verify against NASA AppEEARS or official tools.
    """
    if not extent or "upper_left_x" not in extent:
        return None

    rows, cols = shape
    ul_x = extent["upper_left_x"]
    ul_y = extent["upper_left_y"]
    lr_x = extent["lower_right_x"]
    lr_y = extent["lower_right_y"]

    # Some ECOSTRESS L2G files have metadata in units of 1E-6 degrees
    # when projection says GEO. Detect and rescale if needed.
    if abs(ul_x) > 180 or abs(lr_x) > 180:
        logger.warning("Coordinates exceed +/-180; rescaling by 1e-6")
        ul_x *= 1e-6
        lr_x *= 1e-6
        ul_y *= 1e-6
        lr_y *= 1e-6

    pixel_width = (lr_x - ul_x) / cols
    pixel_height = (lr_y - ul_y) / rows  # usually negative

    return {
        "ul_x": ul_x,
        "ul_y": ul_y,
        "pixel_width": pixel_width,
        "pixel_height": pixel_height,
        "rows": rows,
        "cols": cols,
    }
```

**Explanation:** It accepts `extent`, `shape` and returns `dict | None`. See the code below for the full implementation. Key calls include `warning()`, `abs()`.

### `extract_temperature_at`

- **File:** `fastapi-backend/scripts/extract_ecostress_lst.py`
- **Lines:** `168-225`
- **Signature:** `def extract_temperature_at(`
- **Purpose:** Extract scaled LST (°C) at a given lat/lon using bilinear lookup.

**Code:**
```python
def extract_temperature_at(
    lat: float,
    lon: float,
    raw_lst: np.ndarray,
    transform: dict,
    meta: dict,
) -> float | None:
    """Extract scaled LST (°C) at a given lat/lon using bilinear lookup.

    Returns:
        Surface temperature in °C, or None if out of bounds / invalid.
    """
    ul_x = transform["ul_x"]
    ul_y = transform["ul_y"]
    pw = transform["pixel_width"]
    ph = transform["pixel_height"]
    rows = transform["rows"]
    cols = transform["cols"]

    # Map lat/lon to array indices (approximate)
    col_f = (lon - ul_x) / pw
    row_f = (lat - ul_y) / ph

    c0 = int(np.floor(col_f))
    r0 = int(np.floor(row_f))

    if not (0 <= c0 < cols - 1 and 0 <= r0 < rows - 1):
        return None

    # Simple bilinear interpolation
    dc = col_f - c0
    dr = row_f - r0
    vals = raw_lst[r0 : r0 + 2, c0 : c0 + 2].astype(float)

    fill = meta["fill_value"]
    valid_min = meta["valid_min"]
    valid_max = meta["valid_max"]
    scale = meta["scale_factor"]
    offset = meta["add_offset"]

    # Mask invalid values
    vals[(vals == fill) | (vals < valid_min) | (vals > valid_max)] = np.nan

    if np.all(np.isnan(vals)):
        return None

    # Bilinear interpolation (handling NaNs gracefully)
    top = np.nansum([vals[0, 0] * (1 - dc), vals[0, 1] * dc])
    bot = np.nansum([vals[1, 0] * (1 - dc), vals[1, 1] * dc])
    raw = top * (1 - dr) + bot * dr

    if np.isnan(raw):
        return None

    # Convert to Celsius
    temp_k = raw * scale + offset
    temp_c = temp_k - 273.15
    return round(float(temp_c), 2)
```

**Explanation:** It accepts `lat`, `lon`, `raw_lst`, `transform`, `meta` and returns `float | None`. See the code below for the full implementation. Key calls include `int()`, `floor()`, `astype()`, `all()`, `isnan()`.

### `main`

- **File:** `fastapi-backend/scripts/extract_ecostress_lst.py`
- **Lines:** `228-302`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    raw_lst, meta = read_lst_array(INPUT_H5)
    if raw_lst is None:
        return 1

    extent = extract_spatial_extent(INPUT_H5)
    transform = build_affine_transform(extent, meta["shape"]) if extent else None

    if transform is None:
        logger.error("Could not build spatial transform; aborting sample extraction")
        return 1

    # Check if scene actually covers the Philippines
    scene_lon_min = min(transform["ul_x"], transform["ul_x"] + transform["pixel_width"] * transform["cols"])
    scene_lon_max = max(transform["ul_x"], transform["ul_x"] + transform["pixel_width"] * transform["cols"])
    scene_lat_min = min(transform["ul_y"], transform["ul_y"] + transform["pixel_height"] * transform["rows"])
    scene_lat_max = max(transform["ul_y"], transform["ul_y"] + transform["pixel_height"] * transform["rows"])

    logger.info(
        "Scene coverage: lon %.3f-%.3f, lat %.3f-%.3f",
        scene_lon_min, scene_lon_max, scene_lat_min, scene_lat_max,
    )

    # Philippine bounds
    ph_lon = (PH_BOUNDS["lon_min"], PH_BOUNDS["lon_max"])
    ph_lat = (PH_BOUNDS["lat_min"], PH_BOUNDS["lat_max"])

    overlaps = not (
        scene_lon_max < ph_lon[0]
        or scene_lon_min > ph_lon[1]
        or scene_lat_max < ph_lat[0]
        or scene_lat_min > ph_lat[1]
    )

    if not overlaps:
        logger.warning(
            "This ECOSTRESS scene does NOT overlap the Philippines. "
            "Scene: lon %.1f-%.1f, lat %.1f-%.1f | PH: lon %.1f-%.1f, lat %.1f-%.1f",
            scene_lon_min, scene_lon_max, scene_lat_min, scene_lat_max,
            ph_lon[0], ph_lon[1], ph_lat[0], ph_lat[1],
        )
        logger.info("Skipping extraction. Obtain a scene covering 116-127°E, 4-21°N for Philippine use.")
        return 0

    # Extract a grid of sample points within PH bounds (intersecting scene only)
    lat_min = max(PH_BOUNDS["lat_min"], scene_lat_min)
    lat_max = min(PH_BOUNDS["lat_max"], scene_lat_max)
    lon_min = max(PH_BOUNDS["lon_min"], scene_lon_min)
    lon_max = min(PH_BOUNDS["lon_max"], scene_lon_max)

    lats = np.linspace(lat_min, lat_max, 20)
    lons = np.linspace(lon_min, lon_max, 20)

    samples = []
    for lat in lats:
        for lon in lons:
            temp_c = extract_temperature_at(lat, lon, raw_lst, transform, meta)
            if temp_c is not None:
                samples.append({"lat": round(lat, 4), "lon": round(lon, 4), "surface_temp_c": temp_c})

    if not samples:
        logger.warning("No valid ECOSTRESS samples extracted for Philippine bounds")
        return 0

    df = pd.DataFrame(samples)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    logger.info(
        "Wrote %d ECOSTRESS LST samples to %s (range: %.1f - %.1f °C)",
        len(df),
        OUTPUT_CSV,
        df["surface_temp_c"].min(),
        df["surface_temp_c"].max(),
    )
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `read_lst_array()`, `extract_spatial_extent()`, `build_affine_transform()`, `error()`, `min()`.


## `fastapi-backend/scripts/extract_kmz_to_geojson.py`

**File:** `fastapi-backend/scripts/extract_kmz_to_geojson.py`

**Summary:** Extract volcano and fault KMZ raster overlays for EnergyHub map.

### `extract_overlay_manifest`

- **File:** `fastapi-backend/scripts/extract_kmz_to_geojson.py`
- **Lines:** `39-122`
- **Signature:** `def extract_overlay_manifest(kmz_path: Path, kind: str) -> dict | None:`
- **Purpose:** Extract PNG + bounds from a raster GroundOverlay KMZ.

**Code:**
```python
def extract_overlay_manifest(kmz_path: Path, kind: str) -> dict | None:
    """Extract PNG + bounds from a raster GroundOverlay KMZ.

    Returns a dict with:
        png_filename: str
        bounds: {"north", "south", "east", "west"}
    """
    if not kmz_path.exists():
        logger.error("KMZ file not found: %s", kmz_path)
        return None

    try:
        with zipfile.ZipFile(kmz_path, "r") as zf:
            kml_names = [n for n in zf.namelist() if n.lower().endswith(".kml")]
            if not kml_names:
                logger.error("No .kml file inside %s", kmz_path)
                return None

            # Parse KML for LatLonBox bounds
            with zf.open(kml_names[0]) as kml_file:
                kml_text = kml_file.read().decode("utf-8")
                root = ET.fromstring(kml_text.encode("utf-8"))

            # Find the first LatLonBox (GroundOverlay bounds)
            latlonbox = root.find(f".//{{{KML_NS}}}LatLonBox")
            if latlonbox is None:
                # Fallback: try LatLonAltBox
                latlonbox = root.find(f".//{{{KML_NS}}}LatLonAltBox")
            if latlonbox is None:
                logger.error("No LatLonBox found in %s", kmz_path)
                return None

            def _text(tag: str) -> str | None:
                el = latlonbox.find(f"{{{KML_NS}}}{tag}") if latlonbox is not None else None
                return el.text if el is not None else None

            north = _text("north")
            south = _text("south")
            east = _text("east")
            west = _text("west")
            if not all([north, south, east, west]):
                logger.error("Incomplete LatLonBox in %s", kmz_path)
                return None

            bounds = {
                "north": float(north),
                "south": float(south),
                "east": float(east),
                "west": float(west),
            }

            # Find the PNG href in the first GroundOverlay
            icon_href = None
            for overlay in root.iter(f"{{{KML_NS}}}GroundOverlay"):
                icon = overlay.find(f".//{{{KML_NS}}}Icon/{{{KML_NS}}}href")
                if icon is not None and icon.text:
                    icon_href = icon.text
                    break

            if not icon_href:
                logger.error("No GroundOverlay icon href found in %s", kmz_path)
                return None

            # Extract PNG to public dir
            png_members = [n for n in zf.namelist() if n.lower().endswith(".png")]
            if not png_members:
                logger.error("No PNG found inside %s", kmz_path)
                return None

            # Use the first PNG that matches or just the first PNG
            png_name = png_members[0]
            out_png = OUTPUT_DIR / f"geothermal_{kind}.png"
            with zf.open(png_name) as src, open(out_png, "wb") as dst:
                shutil.copyfileobj(src, dst)
            logger.info("Extracted %s -> %s", png_name, out_png)

            return {
                "png_filename": out_png.name,
                "bounds": bounds,
                "kind": kind,
            }
    except Exception as exc:
        logger.error("Failed to process %s: %s", kmz_path, exc)
        return None
```

**Explanation:** It accepts `kmz_path`, `kind` and returns `dict | None`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `ZipFile()`, `find()`, `_text()`.

### `main`

- **File:** `fastapi-backend/scripts/extract_kmz_to_geojson.py`
- **Lines:** `125-146`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {}

    # --- Volcanoes ---
    vol = extract_overlay_manifest(INPUT_DIR / "VOL_2016_000000000_02.kmz", "volcanoes")
    if vol:
        manifest["volcanoes"] = vol

    # --- Faults ---
    fault = extract_overlay_manifest(INPUT_DIR / "aft_2025_000000000_02.kmz", "faults")
    if fault:
        manifest["faults"] = fault

    # Write manifest JSON
    manifest_path = OUTPUT_DIR / "geothermal_overlays.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Wrote overlay manifest to %s", manifest_path)

    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `mkdir()`, `extract_overlay_manifest()`, `open()`, `dump()`, `info()`.


## `fastapi-backend/scripts/ingest_geothermal_plants.py`

**File:** `fastapi-backend/scripts/ingest_geothermal_plants.py`

**Summary:** Source file `fastapi-backend/scripts/ingest_geothermal_plants.py`.

### `main`

- **File:** `fastapi-backend/scripts/ingest_geothermal_plants.py`
- **Lines:** `7-68`
- **Signature:** `def main():`
- **Purpose:** Handles main.

**Code:**
```python
def main():
    repo_root = Path(__file__).resolve().parents[2]
    xl = repo_root / "GeothermalDatasets" / "Geothermal-Power-Tracker-March-2026-Final.xlsx"
    df = pd.read_excel(xl, sheet_name="Data", header=0, skiprows=[1])
    ph = df[df["Country/Area"] == "Philippines"].copy()

    ph["Latitude"] = pd.to_numeric(ph["Latitude"], errors="coerce")
    ph["Longitude"] = pd.to_numeric(ph["Longitude"], errors="coerce")
    ph["Unit Capacity (MW)"] = pd.to_numeric(ph["Unit Capacity (MW)"], errors="coerce")

    clean = ph[ph["Latitude"].notna() & ph["Longitude"].notna()].copy()

    status_map = {
        "operating": "operating",
        "pre-construction": "pre-construction",
        "construction": "construction",
        "announced": "announced",
        "retired": "retired",
        "mothballed / idle": "mothballed",
        " mothballed / idle": "mothballed",
    }
    clean["status_norm"] = (
        clean["Status"]
        .astype(str)
        .str.lower()
        .str.strip()
        .map(status_map)
        .fillna("unknown")
    )

    plants = []
    for _, row in clean.iterrows():
        plants.append(
            {
                "project_name": str(row["Project Name"]) if pd.notna(row["Project Name"]) else None,
                "unit_name": str(row["Unit Name"]) if pd.notna(row["Unit Name"]) else None,
                "capacity_mw": float(row["Unit Capacity (MW)"]) if pd.notna(row["Unit Capacity (MW)"]) else None,
                "technology": str(row["Technology"]) if pd.notna(row["Technology"]) else None,
                "status": row["status_norm"],
                "raw_status": str(row["Status"]) if pd.notna(row["Status"]) else None,
                "latitude": float(row["Latitude"]),
                "longitude": float(row["Longitude"]),
                "province": str(row["State/Province"]) if pd.notna(row["State/Province"]) else None,
                "city": str(row["City"]) if pd.notna(row["City"]) else None,
                "start_year": int(row["Start Year"]) if pd.notna(row["Start Year"]) else None,
                "wiki_url": str(row["Wiki URL"]) if pd.notna(row["Wiki URL"]) else None,
            }
        )

    out_path = repo_root / "fastapi-backend" / "app" / "services" / "local_data" / "ph_geothermal_plants.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plants, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(plants)} plants to {out_path}")
    operating = sum(1 for p in plants if p["status"] == "operating")
    print(f"Operating: {operating}")
    from collections import Counter
    c = Counter(p["province"] for p in plants if p["province"])
    print("By province (top 5):")
    for prov, cnt in c.most_common(5):
        print(f"  {prov}: {cnt}")
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `resolve()`, `Path()`, `read_excel()`, `copy()`, `to_numeric()`.


## `fastapi-backend/scripts/ingest_ihfc.py`

**File:** `fastapi-backend/scripts/ingest_ihfc.py`

**Summary:** Parse IHFC Global Heat Flow Database and extract Philippines-relevant data.

### `parse_ihfc`

- **File:** `fastapi-backend/scripts/ingest_ihfc.py`
- **Lines:** `48-78`
- **Signature:** `def parse_ihfc(path: Path) -> pd.DataFrame | None:`
- **Purpose:** Read IHFC text file and return a cleaned DataFrame.

**Code:**
```python
def parse_ihfc(path: Path) -> pd.DataFrame | None:
    """Read IHFC text file and return a cleaned DataFrame."""
    if not path.exists():
        logger.error("IHFC file not found: %s", path)
        return None

    logger.info("Reading IHFC data from %s ...", path)
    # The first 12 lines are comments / unit headers; line 12 is the column header.
    df = pd.read_csv(
        path,
        sep="\t",
        encoding="latin-1",
        skiprows=12,
        low_memory=False,
    )

    # Keep only columns we need
    needed = {"q", "lat_NS", "long_EW", "elevation", "environment", "Quality_Score_Parent"}
    cols = [c for c in needed if c in df.columns]
    df = df[cols].copy()

    # Coerce numeric columns
    for col in ("q", "lat_NS", "long_EW", "elevation"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing coords or heat flow
    df = df.dropna(subset=["lat_NS", "long_EW", "q"])

    logger.info("Total measurements after basic cleaning: %d", len(df))
    return df
```

**Explanation:** It accepts `path` and returns `pd.DataFrame | None`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `info()`, `read_csv()`, `copy()`.

### `filter_bounds`

- **File:** `fastapi-backend/scripts/ingest_ihfc.py`
- **Lines:** `81-107`
- **Signature:** `def filter_bounds(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Keep only rows within the Philippines + buffer bounding box.

**Code:**
```python
def filter_bounds(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows within the Philippines + buffer bounding box.

    NOTE: IHFC 2024 release uses 'U' (unclassified) quality codes
    for all entries, so we skip quality filtering and rely on
    physical bounds and the IDW interpolation radius instead.
    """
    mask = (
        (df["lat_NS"] >= MIN_LAT)
        & (df["lat_NS"] <= MAX_LAT)
        & (df["long_EW"] >= MIN_LON)
        & (df["long_EW"] <= MAX_LON)
        & (df["q"] >= Q_MIN)
        & (df["q"] <= Q_MAX)
    )
    filtered = df[mask].copy()
    logger.info(
        "Bounds filter (%0.1f-%0.1fN, %0.1f-%0.1fE, q %d-%d): %d rows kept",
        MIN_LAT,
        MAX_LAT,
        MIN_LON,
        MAX_LON,
        Q_MIN,
        Q_MAX,
        len(filtered),
    )
    return filtered
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `copy()`, `info()`, `len()`.

### `main`

- **File:** `fastapi-backend/scripts/ingest_ihfc.py`
- **Lines:** `110-152`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    if not IHFC_PATH.exists():
        logger.error("Cannot find IHFC source file: %s", IHFC_PATH)
        return 1

    df = parse_ihfc(IHFC_PATH)
    if df is None or df.empty:
        logger.error("No data parsed from IHFC file")
        return 1

    df = filter_bounds(df)

    if df.empty:
        logger.error("No measurements passed bounds filters")
        return 1

    # Rename columns for downstream compatibility
    df = df.rename(
        columns={
            "lat_NS": "lat",
            "long_EW": "lon",
            "q": "heat_flow_mw_m2",
        }
    )

    # Reorder columns
    out_cols = ["lat", "lon", "heat_flow_mw_m2", "elevation", "environment"]
    out_cols = [c for c in out_cols if c in df.columns]
    df = df[out_cols].copy()

    # Sort by lat/lon for readability
    df = df.sort_values(["lat", "lon"]).reset_index(drop=True)

    # Ensure output directory exists
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    logger.info("Wrote %d heat-flow measurements to %s", len(df), OUTPUT_CSV)
    logger.info("Lat range: %0.3f - %0.3f", df["lat"].min(), df["lat"].max())
    logger.info("Lon range: %0.3f - %0.3f", df["lon"].min(), df["lon"].max())
    logger.info("Heat-flow range: %0.1f - %0.1f mW/m²", df["heat_flow_mw_m2"].min(), df["heat_flow_mw_m2"].max())

    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `parse_ihfc()`, `filter_bounds()`, `rename()`.


## `fastapi-backend/scripts/prepare_aquifer_spatial.py`

**File:** `fastapi-backend/scripts/prepare_aquifer_spatial.py`

**Summary:** Pre-process aquifer shapefile for fast point-in-polygon queries.

### `main`

- **File:** `fastapi-backend/scripts/prepare_aquifer_spatial.py`
- **Lines:** `40-89`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    if not INPUT_SHP.exists():
        logger.error("Shapefile not found: %s", INPUT_SHP)
        return 1

    logger.info("Reading aquifer shapefile...")
    gdf = gpd.read_file(INPUT_SHP)
    logger.info("Total polygons: %d | CRS: %s", len(gdf), gdf.crs)

    # Filter Philippines
    ph = gdf[gdf["COUNTRY"].str.contains("Philippines", case=False, na=False)].copy()
    logger.info("Philippines polygons: %d", len(ph))

    if ph.empty:
        logger.error("No Philippines polygons found")
        return 1

    # Reproject to WGS84 for lat/lon queries
    if ph.crs is not None and ph.crs.to_epsg() != 4326:
        logger.info("Reprojecting from %s to EPSG:4326...", ph.crs)
        ph = ph.to_crs(epsg=4326)

    # Keep only columns we need to reduce file size
    keep_cols = [
        "OBJECTID",
        "MEAN_Poros",
        "MEAN_Perme",
        "MEAN_thk_m",
        "MEAN_Depth",
        "COUNTRY",
        "Basin_na_2",
        "geometry",
    ]
    ph = ph[[c for c in keep_cols if c in ph.columns]].copy()

    # Rename columns to snake_case for consistency
    rename = {
        "MEAN_Poros": "porosity",
        "MEAN_Perme": "permeability_log10",
        "MEAN_thk_m": "thickness_m",
        "MEAN_Depth": "depth_m",
        "Basin_na_2": "basin_name",
    }
    ph = ph.rename(columns=rename)

    OUTPUT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    ph.to_file(OUTPUT_GEOJSON, driver="GeoJSON")
    logger.info("Wrote %s (%d polygons)", OUTPUT_GEOJSON, len(ph))

    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `info()`, `read_file()`, `len()`.


## `fastapi-backend/scripts/seed_rag_pgvector.py`

**File:** `fastapi-backend/scripts/seed_rag_pgvector.py`

**Summary:** Source file `fastapi-backend/scripts/seed_rag_pgvector.py`.

### `_chunk_documents`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `20-24`
- **Signature:** `def _chunk_documents(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:`
- **Purpose:** Reuse the existing chunking logic from the FAISS backend.

**Code:**
```python
def _chunk_documents(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    '''Reuse the existing chunking logic from the FAISS backend.'''
    from app.services.rag_faiss import _chunk_documents as chunker

    return chunker(docs)
```

**Explanation:** It accepts `docs` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `chunker()`.

### `_vector_literal`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `27-29`
- **Signature:** `def _vector_literal(embedding: list[float]) -> str:`
- **Purpose:** Format an embedding as a pgvector literal string.

**Code:**
```python
def _vector_literal(embedding: list[float]) -> str:
    '''Format an embedding as a pgvector literal string.'''
    return '[' + ','.join(f'{x:.8f}' for x in embedding) + ']'
```

**Explanation:** It accepts `embedding` and returns `str`. See the code below for the full implementation. Key calls include `join()`.

### `_truncate`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `32-38`
- **Signature:** `def _truncate(client) -> None:`
- **Purpose:** Remove existing chunks so the seeder is idempotent.

**Code:**
```python
def _truncate(client) -> None:
    '''Remove existing chunks so the seeder is idempotent.'''
    try:
        client.table('rag_chunks').delete().neq('id', 0).execute()
        logger.info('Cleared existing rag_chunks.')
    except Exception as exc:
        logger.warning('Could not clear rag_chunks before seeding: %s', exc)
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `execute()`, `info()`, `warning()`, `neq()`, `delete()`.

### `_build_records`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `41-52`
- **Signature:** `def _build_records(chunks: list[dict[str, Any]], embeddings: list[list[float]]) -> list[dict[str, Any]]:`
- **Purpose:** Handles  build records.

**Code:**
```python
def _build_records(chunks: list[dict[str, Any]], embeddings: list[list[float]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for chunk, emb in zip(chunks, embeddings):
        records.append({
            'chunk_text': chunk.get('text', ''),
            'renewable_type': chunk.get('renewable_type', '') or '',
            'category': chunk.get('category', '') or '',
            'product_type': chunk.get('product_type', '') or '',
            'sources': chunk.get('sources', []),
            'embedding': _vector_literal(emb),
        })
    return records
```

**Explanation:** It accepts `chunks`, `embeddings` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `zip()`, `append()`, `get()`, `_vector_literal()`.

### `_seed`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `55-61`
- **Signature:** `def _seed(client, records: list[dict[str, Any]]) -> int:`
- **Purpose:** Handles  seed.

**Code:**
```python
def _seed(client, records: list[dict[str, Any]]) -> int:
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        client.table('rag_chunks').insert(batch).execute()
        logger.info('Inserted chunk batch %s-%s', i, min(i + batch_size, len(records)))
    return len(records)
```

**Explanation:** It accepts `client`, `records` and returns `int`. See the code below for the full implementation. Key calls include `range()`, `len()`, `execute()`, `info()`, `min()`.

### `_encode_local`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `64-74`
- **Signature:** `def _encode_local(texts: list[str]) -> list[list[float]]:`
- **Purpose:** Handles  encode local.

**Code:**
```python
def _encode_local(texts: list[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('all-MiniLM-L6-v2')
    arrays = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return arrays.astype('float32').tolist()
```

**Explanation:** It accepts `texts` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `SentenceTransformer()`, `encode()`, `tolist()`, `astype()`.

### `_encode_external`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `77-80`
- **Signature:** `def _encode_external(texts: list[str]) -> list[list[float]]:`
- **Purpose:** Handles  encode external.

**Code:**
```python
def _encode_external(texts: list[str]) -> list[list[float]]:
    from app.services.rag_embeddings_client import encode

    return encode(texts)
```

**Explanation:** It accepts `texts` and returns `list[list[float]]`. See the code below for the full implementation. Key calls include `encode()`.

### `main`

- **File:** `fastapi-backend/scripts/seed_rag_pgvector.py`
- **Lines:** `83-115`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()
    _truncate(client)

    logger.info('Loading knowledge base from %s', KNOWLEDGE_JSON)
    with open(KNOWLEDGE_JSON, 'r', encoding='utf-8') as f:
        docs = json.load(f)

    chunks = _chunk_documents(docs)
    logger.info('Generated %s chunks from %s documents', len(chunks), len(docs))

    texts = [c.get('text', '') for c in chunks]
    try:
        embeddings = _encode_local(texts)
        logger.info('Computed %s embeddings locally', len(embeddings))
    except ImportError:
        logger.warning(
            'sentence-transformers not installed; falling back to the external embedding API. '
            'This is slower and may hit rate limits.'
        )
        embeddings = _encode_external(texts)

    records = _build_records(chunks, embeddings)
    count = _seed(client, records)
    logger.info('Seeded %s chunks into Supabase.', count)

    # Quick sanity check.
    from app.services import rag_pgvector_store

    stats = rag_pgvector_store.index_stats()
    logger.info('pgvector stats: %s', stats)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `_truncate()`, `info()`, `open()`, `load()`.

