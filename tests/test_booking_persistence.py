from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from services.booking.app.dependencies import get_session
from services.booking.app.main import app
from services.booking.app.models import BookingRecord

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


def test_create_booking_persists_record() -> None:
    client = TestClient(app)
    payload = {
        "event_id": "session-1",
        "guest_id": "guest-1",
        "seats": 2
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 201
    booking = response.json()

    with Session(TEST_ENGINE) as session:
        record = session.get(BookingRecord, booking["booking_id"])
        assert record is not None
        assert record.status == "pending"
        assert record.seats == 2


def test_update_booking_changes_status() -> None:
    client = TestClient(app)
    payload = {
        "event_id": "session-2",
        "guest_id": "guest-2",
        "seats": 1
    }
    response = client.post("/bookings", json=payload)
    booking = response.json()

    patch = client.patch(
        f"/bookings/{booking['booking_id']}", json={"status": "confirmed"}
    )
    assert patch.status_code == 200
    updated = patch.json()
    assert updated["status"] == "confirmed"

    with Session(TEST_ENGINE) as session:
        record = session.get(BookingRecord, booking["booking_id"])
        assert record is not None
        assert record.status == "confirmed"
