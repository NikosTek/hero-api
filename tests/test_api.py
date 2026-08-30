import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, username="user1", password="password123"):
    client.post("/auth/register", json={"username": username, "password": password})
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def make_admin(session: Session, username="user1"):
    from app.models import User

    user = session.exec(
        __import__("sqlmodel").select(User).where(User.username == username)
    ).first()
    user.is_admin = True
    session.add(user)
    session.commit()


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register", json={"username": "hero_fan", "password": "secret123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "hero_fan"
    assert "hashed_password" not in data


def test_login_returns_token(client: TestClient):
    client.post("/auth/register", json={"username": "hero_fan", "password": "secret123"})
    response = client.post(
        "/auth/login", data={"username": "hero_fan", "password": "secret123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_hero_requires_authentication(client: TestClient):
    response = client.post(
        "/heroes", json={"name": "Ironclad", "power": "Super strength"}
    )
    assert response.status_code == 401


def test_create_hero_with_token(client: TestClient):
    headers = register_and_login(client)
    response = client.post(
        "/heroes",
        json={"name": "Ironclad", "power": "Super strength", "level": 10},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ironclad"
    assert data["level"] == 10


def test_create_mission_for_missing_hero_returns_404(client: TestClient):
    headers = register_and_login(client)
    response = client.post(
        "/missions",
        json={"title": "Save the city", "difficulty": 5, "hero_id": 9999},
        headers=headers,
    )
    assert response.status_code == 404


def test_normal_user_cannot_delete_hero(client: TestClient):
    headers = register_and_login(client)
    hero_resp = client.post(
        "/heroes",
        json={"name": "Ironclad", "power": "Super strength"},
        headers=headers,
    )
    hero_id = hero_resp.json()["id"]

    response = client.delete(f"/heroes/{hero_id}", headers=headers)
    assert response.status_code == 403


def test_admin_can_delete_mission(client: TestClient, session: Session):
    headers = register_and_login(client)
    make_admin(session)
    
    hero_resp = client.post(
        "/heroes",
        json={"name": "Ironclad", "power": "Super strength"},
        headers=headers,
    )
    hero_id = hero_resp.json()["id"]

    mission_resp = client.post(
        "/missions",
        json={"title": "Save the city", "difficulty": 5, "hero_id": hero_id},
        headers=headers,
    )
    mission_id = mission_resp.json()["id"]

    response = client.delete(f"/missions/{mission_id}", headers=headers)
    assert response.status_code == 204

    get_resp = client.get(f"/missions/{mission_id}")
    assert get_resp.status_code == 404
