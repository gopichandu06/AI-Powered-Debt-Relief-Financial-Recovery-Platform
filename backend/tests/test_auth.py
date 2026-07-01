"""
FinRelief AI — Authentication endpoint tests.
Tests: register, login, /me access control, logout.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.dependencies import get_db
from app.db.database import Base
from app.main import app

# ─────────────────────────────────────────────────────────────────────────────
# Test database setup (in-memory SQLite)
# ─────────────────────────────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_auth.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="module")
def setup_database():
    """Create all tables before tests, drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="module")
def client():
    """Return a TestClient with the test database injected."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Test data
# ─────────────────────────────────────────────────────────────────────────────

TEST_USER = {
    "email": "testuser@finrelief.ai",
    "password": "SecurePass123",
    "full_name": "Test User",
}


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_new_user_returns_token(self, client: TestClient) -> None:
        """A new user registration should return a Bearer token."""
        response = client.post("/api/auth/register", json=TEST_USER)
        assert response.status_code == 201, response.text
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20

    def test_register_duplicate_email_returns_409(self, client: TestClient) -> None:
        """Registering with an already-used email should fail with 409 Conflict."""
        # First registration succeeds (may already be done in previous test)
        client.post("/api/auth/register", json=TEST_USER)
        # Second attempt must fail
        response = client.post("/api/auth/register", json=TEST_USER)
        assert response.status_code == 409, response.text

    def test_register_short_password_returns_422(self, client: TestClient) -> None:
        """A password shorter than 8 characters should be rejected with 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "short@finrelief.ai",
                "password": "abc",
                "full_name": "Short Pass",
            },
        )
        assert response.status_code == 422, response.text

    def test_register_invalid_email_returns_422(self, client: TestClient) -> None:
        """An invalid email format should return 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "ValidPass123",
                "full_name": "Invalid Email",
            },
        )
        assert response.status_code == 422, response.text


class TestLogin:
    def test_login_with_valid_credentials_returns_token(
        self, client: TestClient
    ) -> None:
        """Valid credentials submitted as form data should return a token."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"],
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_wrong_password_returns_401(
        self, client: TestClient
    ) -> None:
        """Wrong password should return 401 Unauthorized."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": TEST_USER["email"],
                "password": "WrongPassword!",
            },
        )
        assert response.status_code == 401, response.text
        assert "Incorrect" in response.json()["detail"]

    def test_login_with_nonexistent_email_returns_401(
        self, client: TestClient
    ) -> None:
        """A login attempt for an unregistered email should return 401."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nobody@finrelief.ai",
                "password": "SomePass123",
            },
        )
        assert response.status_code == 401, response.text


class TestMe:
    def _get_token(self, client: TestClient) -> str:
        response = client.post(
            "/api/auth/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"],
            },
        )
        return response.json()["access_token"]

    def test_me_without_token_returns_401(self, client: TestClient) -> None:
        """GET /api/auth/me without a token should return 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401, response.text

    def test_me_with_invalid_token_returns_401(self, client: TestClient) -> None:
        """An invalid/tampered Bearer token should be rejected with 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
        )
        assert response.status_code == 401, response.text

    def test_me_with_valid_token_returns_200(self, client: TestClient) -> None:
        """A valid Bearer token should return the user's profile with 200."""
        token = self._get_token(client)
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == TEST_USER["email"]
        assert data["full_name"] == TEST_USER["full_name"]
        assert data["is_active"] is True
        assert "id" in data

    def test_me_response_does_not_contain_password(
        self, client: TestClient
    ) -> None:
        """The /me response must never expose the hashed password."""
        token = self._get_token(client)
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data


class TestLogout:
    def test_logout_returns_success_message(self, client: TestClient) -> None:
        """POST /api/auth/logout should return a success message."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 200, response.text
        data = response.json()
        assert "message" in data
        assert "logout" in data["message"].lower() or "logged" in data["message"].lower()


class TestHealthCheck:
    def test_root_health_check(self, client: TestClient) -> None:
        """GET / should return status ok."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_api_health_check(self, client: TestClient) -> None:
        """GET /api/health should return status healthy with a timestamp."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
