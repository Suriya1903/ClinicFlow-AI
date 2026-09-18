from redis import Redis

from backend.app.core.config import settings


TOKEN_REVOCATION_KEY_PREFIX = (
    "clinicflow:revoked-token:"
)


class TokenRevocationStore:
    """
    Redis-backed JWT token revocation store.

    Revoked JWT IDs are stored using their `jti` value.

    Each revoked token receives a TTL matching the remaining
    lifetime of the JWT. Redis therefore automatically removes
    revocation entries after the token would have expired anyway.
    """

    def __init__(
        self,
        redis_url: str | None = None,
    ):
        self.redis = Redis.from_url(
            redis_url or settings.redis_url,
            decode_responses=True,
        )

    def _get_key(
        self,
        token_id: str,
    ) -> str:
        """
        Build the Redis key for a JWT ID.
        """

        return (
            f"{TOKEN_REVOCATION_KEY_PREFIX}"
            f"{token_id}"
        )

    def revoke(
        self,
        token_id: str,
        expires_in_seconds: int,
    ) -> None:
        """
        Mark a JWT ID as revoked.

        The revocation entry automatically expires after the
        remaining lifetime of the original JWT.
        """

        if not token_id:
            return

        if expires_in_seconds <= 0:
            return

        key = self._get_key(token_id)

        try:
            self.redis.set(
                key,
                "revoked",
                ex=expires_in_seconds,
            )

        except Exception:
            # Logout should not crash because Redis is
            # temporarily unavailable.
            #
            # In a production deployment, this behavior can
            # be changed to fail closed depending on security
            # requirements.
            return

    def is_revoked(
        self,
        token_id: str,
    ) -> bool:
        """
        Check whether a JWT ID has been revoked.
        """

        if not token_id:
            return False

        key = self._get_key(token_id)

        try:
            return bool(
                self.redis.exists(key)
            )

        except Exception:
            # Fail closed for token revocation checks.
            #
            # If Redis cannot be reached, an existing token
            # cannot be confirmed as non-revoked.
            return True

    def clear(self) -> None:
        """
        Clear all ClinicFlow token-revocation keys.

        Primarily useful for automated tests.
        """

        try:
            pattern = (
                f"{TOKEN_REVOCATION_KEY_PREFIX}*"
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
        """

        try:
            return bool(self.redis.ping())

        except Exception:
            return False


token_revocation_store = TokenRevocationStore()