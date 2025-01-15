import pytest
from fastapi.testclient import TestClient

from araiko_challenge.models.coupon import Coupon
from araiko_challenge.routers.coupons import COUPONS_ROUTE_PREFIX
from araiko_challenge.services.storage import CouponStorage


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_storage",
    [
        pytest.param([], id="Empty db should return empty response"),
        pytest.param(
            [Coupon(name="coupon_1", discount=1), Coupon(name="coupon_2", discount=1)],
            id=f"{COUPONS_ROUTE_PREFIX}/ should returns all coupons",
        ),
    ],
    indirect=True,
)
async def test_read_coupons_should_returns_all_coupons(
    mock_storage: CouponStorage, fake_api: TestClient
) -> None:
    response = fake_api.get(f"{COUPONS_ROUTE_PREFIX}/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(await mock_storage.get_all())


@pytest.mark.parametrize(
    "mock_storage",
    [[Coupon(name="coupon_1", discount=1)]],
    indirect=True,
)
def test_read_coupon_should_return_the_proper_coupon(fake_api: TestClient) -> None:
    response = fake_api.get(f"{COUPONS_ROUTE_PREFIX}/coupon_1")
    assert response.status_code == 200
    assert Coupon.model_validate(response.json()) == Coupon(name="coupon_1", discount=1)


def test_read_coupon_should_return_404_if_no_coupon_exists(
    fake_api: TestClient,
) -> None:
    response = fake_api.get(f"{COUPONS_ROUTE_PREFIX}/coupon_1")
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("coupon"),
    [
        pytest.param(
            {"name": "coupon_1", "discount": 10}, id="Simple coupon should be created"
        ),
        pytest.param(
            {"name": "coupon_1", "discount": "10%"},
            id="coupon with percent discount should be created",
        ),
        pytest.param(
            {
                "name": "coupon_1",
                "discount": 10,
                "validity": {"start": "2025-01-01", "end": "2026-01-01"},
            },
            id="coupon with validity period should be created",
        ),
        pytest.param(
            {"name": "coupon_1", "discount": 10, "condition": {"category": "food"}},
            id="coupon with condition should be created",
        ),
    ],
)
def test_create_coupon_should_return_201_with_valid_coupon(
    fake_api: TestClient, coupon: dict
) -> None:
    response = fake_api.post(f"{COUPONS_ROUTE_PREFIX}/", json=coupon)
    assert response.status_code == 201
    assert Coupon.model_validate(response.json()) == Coupon.model_validate(coupon)


@pytest.mark.parametrize(
    "mock_storage",
    [
        pytest.param(
            [Coupon(name="coupon_1", discount=1)],
            id=f"{COUPONS_ROUTE_PREFIX}/ should returns all coupons",
        ),
    ],
    indirect=True,
)
def test_create_coupon_should_return_409_with_existing_coupon(
    fake_api: TestClient,
) -> None:
    response = fake_api.post(
        f"{COUPONS_ROUTE_PREFIX}/", json={"name": "coupon_1", "discount": "10%"}
    )
    assert response.status_code == 409


@pytest.mark.parametrize(
    ("coupon"),
    [
        pytest.param({"name": "coupon_1"}, id="Invalid coupon definition"),
        pytest.param(
            {"name": "coupon_1", "discount": "10%", "vip": True},
            id="Extra parameters are not allowed",
        ),
    ],
)
def test_create_coupon_should_return_422_with_invalid_input(
    fake_api: TestClient, coupon: dict
) -> None:
    response = fake_api.post(f"{COUPONS_ROUTE_PREFIX}/", json=coupon)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "mock_storage",
    [
        pytest.param([Coupon(name="coupon_1", discount=1)]),
    ],
    indirect=True,
)
def test_update_coupon_should_return_202_with_updated_coupon(
    fake_api: TestClient,
) -> None:
    data = {"name": "coupon_1", "discount": "10%"}
    response = fake_api.put(f"{COUPONS_ROUTE_PREFIX}/", json=data)
    assert response.status_code == 202
    assert Coupon.model_validate(data) == Coupon.model_validate(response.json())


@pytest.mark.parametrize(
    "mock_storage",
    [
        pytest.param([Coupon(name="coupon_1", discount=1)]),
    ],
    indirect=True,
)
def test_update_coupon_should_return_422_with_invalid_input(
    fake_api: TestClient,
) -> None:
    data = {"name": "coupon_1", "discount": "10%", "vip": True}
    response = fake_api.put(f"{COUPONS_ROUTE_PREFIX}/", json=data)
    assert response.status_code == 422


def test_update_coupon_should_return_404_with_missing_coupon(
    fake_api: TestClient,
) -> None:
    data = {"name": "coupon_1", "discount": "10%"}
    response = fake_api.put(f"{COUPONS_ROUTE_PREFIX}/", json=data)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "mock_storage",
    [
        pytest.param([Coupon(name="coupon_1", discount=1)]),
    ],
    indirect=True,
)
def test_delete_coupon_should_return_200(
    fake_api: TestClient,
) -> None:
    response = fake_api.delete(f"{COUPONS_ROUTE_PREFIX}/coupon_1")
    assert response.status_code == 200


def test_delete_coupon_should_return_404_with_missing_coupon(
    fake_api: TestClient,
) -> None:
    response = fake_api.delete(f"{COUPONS_ROUTE_PREFIX}/coupon_1")
    assert response.status_code == 404
