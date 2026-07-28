from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from shared.core.config import settings
from shared.domain.exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AuthenticationError,
)
from shared.infrastructure.database.repositories.refresh_token import (
    RefreshTokenRepository,
)
from shared.infrastructure.database.repositories.user import UserRepository
from shared.infrastructure.database.tables.refresh_token import RefreshTokenTable
from shared.infrastructure.database.tables.user import UserTable
from shared.infrastructure.security.password import verify_password
from shared.infrastructure.security.tokens import (
    create_access_token,
    generate_refresh_token,
    hash_token,
)

_login_attempts: dict[str, dict] = {}


class AuthService:
    def __init__(self, *, session: Session):
        self.session = session
        self.user_repo = UserRepository(session=session)
        self.refresh_repo = RefreshTokenRepository(session=session)

    def _check_rate_limit(self, email: str) -> None:
        now = datetime.now(timezone.utc)
        record = _login_attempts.get(email)
        if record:
            if record["locked_until"] and record["locked_until"] > now:
                raise AccountLockedError(
                    "Account temporarily locked due to too many failed attempts"
                )
            if record["locked_until"] and record["locked_until"] <= now:
                _login_attempts.pop(email)

    def _record_failed_attempt(self, email: str) -> None:
        now = datetime.now(timezone.utc)
        if email not in _login_attempts:
            _login_attempts[email] = {"count": 1, "locked_until": None}
        else:
            _login_attempts[email]["count"] += 1

        if _login_attempts[email]["count"] >= settings.auth_max_login_attempts:
            _login_attempts[email]["locked_until"] = now + timedelta(
                minutes=settings.auth_lockout_minutes
            )

    def _clear_attempts(self, email: str) -> None:
        _login_attempts.pop(email, None)

    def login(
        self,
        *,
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> dict:
        self._check_rate_limit(email)

        user = self.user_repo.find_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            self._record_failed_attempt(email)
            raise AuthenticationError("Invalid credentials")

        if not user.is_active:
            raise AccountDisabledError("Account is disabled")

        self._clear_attempts(email)

        user.last_login_at = datetime.now(timezone.utc)

        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            secret_key=settings.auth_secret_key,
            ttl_minutes=settings.access_token_ttl_minutes,
        )

        refresh_token_str = generate_refresh_token()
        refresh_token_hash = hash_token(refresh_token_str)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_ttl_days
        )

        refresh_token = RefreshTokenTable(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(refresh_token)
        self.session.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
        }

    def refresh(
        self,
        *,
        refresh_token_str: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> dict:
        token_hash = hash_token(refresh_token_str)
        token_record = self.refresh_repo.find_by_token_hash(token_hash)

        now = datetime.now(timezone.utc)

        if (
            not token_record
            or token_record.revoked_at
            or token_record.expires_at <= now
        ):
            raise AuthenticationError("Invalid refresh token")

        user = token_record.user
        if not user.is_active:
            raise AccountDisabledError("Account is disabled")

        token_record.revoked_at = now

        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            secret_key=settings.auth_secret_key,
            ttl_minutes=settings.access_token_ttl_minutes,
        )

        new_refresh_str = generate_refresh_token()
        new_refresh_hash = hash_token(new_refresh_str)
        expires_at = now + timedelta(days=settings.refresh_token_ttl_days)

        new_token_record = RefreshTokenTable(
            user_id=user.id,
            token_hash=new_refresh_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(new_token_record)
        self.session.commit()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_str,
        }

    def logout(self, *, refresh_token_str: str) -> None:
        token_hash = hash_token(refresh_token_str)
        token_record = self.refresh_repo.find_by_token_hash(token_hash)
        if token_record and not token_record.revoked_at:
            token_record.revoked_at = datetime.now(timezone.utc)
            self.session.commit()

    def get_current_user(self, *, user_id: str) -> UserTable:
        return self.user_repo.get_by_id(user_id)
