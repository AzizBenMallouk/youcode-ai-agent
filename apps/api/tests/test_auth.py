"""Tests LOT 3 — Authentification & Autorisation."""

import pytest
from datetime import datetime, timezone, timedelta

from youcode_ai.domain.enums.auth import UserRole
from youcode_ai.domain.exceptions import AuthenticationError, AccountLockedError, AccountDisabledError
from youcode_ai.infrastructure.database.tables.user import UserTable
from youcode_ai.infrastructure.database.tables.refresh_token import RefreshTokenTable
from youcode_ai.infrastructure.security.password import hash_password, verify_password
from youcode_ai.infrastructure.security.tokens import create_access_token, decode_access_token
from youcode_ai.application.services.auth import AuthService
from youcode_ai.application.services.admin_user import AdminUserService


class TestSecurityUtilities:
    def test_password_hashing(self):
        password = "secure_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_jwt_tokens(self):
        secret = "test-secret-key-32-chars-minimum"
        token = create_access_token(
            user_id="u123",
            email="admin@test.com",
            role="admin",
            secret_key=secret,
            ttl_minutes=15
        )
        
        decoded = decode_access_token(token, secret_key=secret)
        assert decoded["sub"] == "u123"
        assert decoded["email"] == "admin@test.com"
        assert decoded["role"] == "admin"
        assert decoded["type"] == "access"

class TestAdminUserService:
    def test_create_user(self, db_session):
        service = AdminUserService(session=db_session)
        
        user = service.create_user(
            email="new@example.com",
            password="password123",
            full_name="New User",
            role=UserRole.SUPPORT
        )
        
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.role == UserRole.SUPPORT
        assert verify_password("password123", user.password_hash)

class TestAuthService:
    def test_login_success(self, db_session):
        admin_service = AdminUserService(session=db_session)
        user = admin_service.create_user(
            email="login@example.com",
            password="password123",
            full_name="Login Test",
            role=UserRole.ADMIN
        )
        
        auth_service = AuthService(session=db_session)
        result = auth_service.login(
            email="login@example.com",
            password="password123",
            user_agent="pytest",
            ip_address="127.0.0.1"
        )
        
        assert "access_token" in result
        assert "refresh_token" in result
        
        db_session.refresh(user)
        assert user.last_login_at is not None

    def test_login_invalid_password(self, db_session):
        admin_service = AdminUserService(session=db_session)
        admin_service.create_user(
            email="invalid@example.com",
            password="password123",
            full_name="Invalid Test",
            role=UserRole.ADMIN
        )
        
        auth_service = AuthService(session=db_session)
        
        with pytest.raises(AuthenticationError):
            auth_service.login(
                email="invalid@example.com",
                password="wrongpassword",
                user_agent="pytest",
                ip_address="127.0.0.1"
            )

    def test_login_disabled_account(self, db_session):
        admin_service = AdminUserService(session=db_session)
        user = admin_service.create_user(
            email="disabled@example.com",
            password="password123",
            full_name="Disabled Test",
            role=UserRole.ADMIN
        )
        user.is_active = False
        db_session.commit()
        
        auth_service = AuthService(session=db_session)
        
        with pytest.raises(AccountDisabledError):
            auth_service.login(
                email="disabled@example.com",
                password="password123",
                user_agent="pytest",
                ip_address="127.0.0.1"
            )
