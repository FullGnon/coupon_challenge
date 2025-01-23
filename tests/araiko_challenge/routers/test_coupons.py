import pytest
from coupon_challenge.models.coupon import Coupon
from coupon_challenge.models.product import Product
from coupon_challenge.routers.coupons import COUPONS_ROUTE_PREFIX
from coupon_challenge.services.storage import CouponStorage
from fastapi.testclient import TestClient


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


@pytest.mark.parametrize(
    "mock_storage",
    [
        pytest.param([Coupon(name="coupon_1", discount=10)], id="Fixed discount"),
        pytest.param([Coupon(name="coupon_1", discount="10%")], id="Percent discount"),
        pytest.param(
            [
                Coupon(
                    name="coupon_1",
                    discount=10,
                    validity={"start": "2015-01-01", "end": "2036-01-01"},
                )
            ],
            id="Coupon with validity period",
        ),
        pytest.param(
            [Coupon(name="coupon_1", discount=10, condition={"price_above": 80})],
            id="Coupon with price threshold condition",
        ),
        pytest.param(
            [Coupon(name="coupon_1", discount=10, condition={"category": "food"})],
            id="Coupon with category condition",
        ),
    ],
    indirect=True,
)
def test_apply_product_should_apply_discount_on_valid_product(
    fake_api: TestClient,
) -> None:
    product = Product(name="product", price=100, category="food")
    response = fake_api.post(
        f"{COUPONS_ROUTE_PREFIX}/coupon_1/apply_product", json=product.model_dump()
    )
    assert response.status_code == 200
    assert Product.model_validate(response.json()) == product.model_copy(
        update={"price": 90}
    )


def test_apply_product_should_return_404_with_missing_coupon(
    fake_api: TestClient,
) -> None:
    product = Product(name="product", price=100, category="food")
    response = fake_api.post(
        f"{COUPONS_ROUTE_PREFIX}/coupon_1/apply_product", json=product.model_dump()
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    "mock_storage",
    [
        pytest.param(
            [
                Coupon(
                    name="coupon_1",
                    discount=10,
                    validity={"start": "2015-01-01", "end": "2016-01-01"},
                )
            ],
            id="Coupon with invalid period",
        ),
        pytest.param(
            [Coupon(name="coupon_1", discount=10, condition={"price_above": 120})],
            id="Coupon with invalid price threshold condition",
        ),
        pytest.param(
            [
                Coupon(
                    name="coupon_1", discount=10, condition={"category": "electronics"}
                )
            ],
            id="Coupon with wrong category condition",
        ),
    ],
    indirect=True,
)
def test_apply_product_should_return_422_if_coupon_is_not_applicable(
    fake_api: TestClient,
) -> None:
    product = Product(name="product", price=100, category="food")
    response = fake_api.post(
        f"{COUPONS_ROUTE_PREFIX}/coupon_1/apply_product", json=product.model_dump()
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("product"),
    [
        pytest.param({"name": "product"}, id="Incomplete product"),
        pytest.param(
            {"name": "product", "price": 10, "category": "cloth"}, id="Unknown category"
        ),
        pytest.param(
            {"name": "product", "price": 10, "category": "food", "vip": True},
            id="Extra parameter are forbidden",
        ),
    ],
)
def test_apply_product_should_return_422_with_invalid_product(
    product: dict,
    fake_api: TestClient,
) -> None:
    response = fake_api.post(
        f"{COUPONS_ROUTE_PREFIX}/coupon_1/apply_product", json=product
    )
    assert response.status_code == 422
