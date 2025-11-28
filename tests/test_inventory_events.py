from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from services.inventory.app.dependencies import get_session
from services.inventory.app.main import app
from services.inventory.app.models import ViewingSession

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_session():
    with Session(TEST_ENGINE) as session:
        yield session


app.dependency_overrides[get_session] = override_session


def setup_module(_: object) -> None:  # pragma: no cover
    SQLModel.metadata.create_all(TEST_ENGINE)


def teardown_function(_: object) -> None:  # pragma: no cover
    SQLModel.metadata.drop_all(TEST_ENGINE)
    SQLModel.metadata.create_all(TEST_ENGINE)


def seed_event() -> None:
    with Session(TEST_ENGINE) as session:
        event = ViewingSession(
            title="Test Derby",
            starts_at=datetime.utcnow() + timedelta(hours=5),
            slots_total=5,
            slots_available=5,
            location="Łódź",
            host_id="host-test",
            price_pln=99,
        )
        session.add(event)
        session.commit()


def test_events_listing_returns_seeded_rows() -> None:
    seed_event()
    client = TestClient(app)
    response = client.get("/events")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["title"] == "Test Derby"
