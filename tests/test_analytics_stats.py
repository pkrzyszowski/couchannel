from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from services.analytics.app.dependencies import get_session
from services.analytics.app.main import app
from services.analytics.app.models import BookingStat

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


def test_stats_list_returns_rows() -> None:
    with Session(TEST_ENGINE) as session:
        session.add(BookingStat(event_id="session-1", total_seats=3, total_bookings=1))
        session.commit()

    client = TestClient(app)
    response = client.get("/stats")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["event_id"] == "session-1"


def test_stats_detail_404() -> None:
    client = TestClient(app)
    response = client.get("/stats/unknown")
    assert response.status_code == 404
