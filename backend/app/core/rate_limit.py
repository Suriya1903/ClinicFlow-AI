from redis import Redis

from backend.app.core.config import settings


MAX_LOGIN_ATTEMPTS = 5
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 60

LOGIN_RATE_LIMIT_KEY_PREFIX = (
    "clinicflow:login-rate-limit:"
)


class LoginRateLimiter:
    """
    Redis-backed rate limiter for login attempts.

    Failed login attempts are shared across all ClinicFlow
    application instances through Redis.

    Each client identifier receives a Redis key with a TTL.
    The key automatically expires after the configured
    rate-limit window.
    """

    def __init__(
        self,
        max_attempts: int = MAX_LOGIN_ATTEMPTS,
        window_seconds: int = (
            LOGIN_RATE_LIMIT_WINDOW_SECONDS
        ),
        redis_url: str | None = None,
    ):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds

        self.redis = Redis.from_url(
            redis_url or settings.redis_url,
            decode_responses=True,
        )

    def _get_key(
        self,
        identifier: str,
    ) -> str:
        """
        Build the Redis key for a client identifier.
        """

        return (
            f"{LOGIN_RATE_LIMIT_KEY_PREFIX}"
            f"{identifier}"
        )

    def is_blocked(
        self,
        identifier: str,
    ) -> bool:
        """
        Return True when the identifier has reached
        the maximum allowed failed login attempts.
        """

        if not identifier:
            return False

        key = self._get_key(identifier)

        try:
            attempts = self.redis.get(key)

            if attempts is None:
                return False

            return int(attempts) >= self.max_attempts

        except Exception:
            # Fail open if Redis is temporarily unavailable.
            #
            # This prevents a Redis outage from locking every
            # user out of the application.
            return False

    def record_failure(
        self,
        identifier: str,
    ) -> None:
        """
        Record one failed login attempt.

        The first failure creates the Redis key and starts
        the rate-limit window.

        Subsequent failures increment the same key while
        preserving its original TTL.
        """

        if not identifier:
            return

        key = self._get_key(identifier)

        try:
            with self.redis.pipeline() as pipeline:
                pipeline.incr(key)
                pipeline.expire(
                    key,
                    self.window_seconds,
                )
                pipeline.execute()

        except Exception:
            # Login functionality should not fail solely
            # because Redis is temporarily unavailable.
            return

    def reset(
        self,
        identifier: str,
    ) -> None:
        """
        Clear failed login attempts after successful
        authentication.
        """

        if not identifier:
            return

        key = self._get_key(identifier)

        try:
            self.redis.delete(key)

        except Exception:
            return

    def get_failed_attempts(
        self,
        identifier: str,
    ) -> int:
        """
        Return the current number of failed attempts.

        Primarily useful for tests and monitoring.
        """

        if not identifier:
            return 0

        key = self._get_key(identifier)

        try:
            attempts = self.redis.get(key)

            if attempts is None:
                return 0

            return int(attempts)

        except Exception:
            return 0

    def clear(self) -> None:
        """
        Clear all ClinicFlow login-rate-limit keys.

        Primarily useful for automated tests.
        """

        try:
            pattern = (
                f"{LOGIN_RATE_LIMIT_KEY_PREFIX}*"
            )

            keys = list(
                self.redis.scan_iter(
                    match=pattern
                )
            )

            if keys:
                self.redis.delete(*keys)

        except Exception:
            return

    def ping(self) -> bool:
        """
        Check whether Redis is reachable.

        Useful for diagnostics and health checks.
        """

        try:
            return bool(self.redis.ping())

        except Exception:
            return False


login_rate_limiter = LoginRateLimiter()