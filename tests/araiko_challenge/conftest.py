from typing import Generator, TypeVar

import pytest
from fastapi.testclient import TestClient

from araiko_challenge.dependencies import get_coupon_storage
from araiko_challenge.main import app
from araiko_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from araiko_challenge.services.coupons import CouponApplicabilityService
from araiko_challenge.services.storage import CouponStorage

T = TypeVar("T")

YieldFixture = Generator[T, None, None]


class InMemoryCouponStorage(CouponStorage):
    def __init__(self, data: list[Coupon] = None):
        super().__init__()
        self.data: dict[str, Coupon] = {c.name: c for c in data} if data else {}

    async def get_all(self) -> list[Coupon]:
        return list(self.data.values())

    async def get(self, name: str) -> Coupon | None:
        return self.data.get(name, None)

    async def create(self, coupon: CouponCreate) -> Coupon:
        if coupon.name in self.data:
            raise IndexError

        self.data[coupon.name] = Coupon.model_validate(coupon.model_dump())

        return self.data[coupon.name]

    async def update(self, coupon: CouponUpdate) -> Coupon:
        if coupon.name not in self.data:
            raise IndexError

        self.data[coupon.name] = Coupon.model_validate(coupon.model_dump())

        return self.data[coupon.name]

    async def delete(self, name: str) -> None:
        if name not in self.data:
            raise IndexError

        del self.data[name]


@pytest.fixture
def mock_storage(request) -> CouponStorage:
    data = request.param if hasattr(request, "param") else None
    return InMemoryCouponStorage(data)


@pytest.fixture
def fake_api(mock_storage: CouponStorage) -> YieldFixture[TestClient]:
    app.dependency_overrides[get_coupon_storage] = lambda: mock_storage
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def coupon_service() -> CouponApplicabilityService:
    return CouponApplicabilityService()
