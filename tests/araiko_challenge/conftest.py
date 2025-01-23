from typing import Generator, TypeVar

import pytest
from coupon_challenge.dependencies import get_coupon_storage
from coupon_challenge.main import app
from coupon_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from coupon_challenge.services.coupons import CouponApplicabilityService
from coupon_challenge.services.storage import (
    CouponStorage,
    CouponStorageAlreadyExistsError,
    CouponStorageError,
    CouponStorageNotFoundError,
    CouponStorageProductNotApplicableError,
)
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

T = TypeVar("T")

YieldFixture = Generator[T, None, None]


class InMemoryCouponStorage(CouponStorage):
    def __init__(self, data: list[Coupon] = None):
        super().__init__()
        self.data: dict[str, Coupon] = {c.name: c for c in data} if data else {}

    async def get_all(self) -> list[Coupon]:
        return list(self.data.values())

    async def get(self, name: str) -> Coupon:
        if name not in self.data:
            raise CouponStorageNotFoundError()

        return self.data[name]

    async def create(self, coupon: CouponCreate) -> Coupon:
        if coupon.name in self.data:
            raise CouponStorageAlreadyExistsError()

        self.data[coupon.name] = Coupon.model_validate(coupon.model_dump())

        return self.data[coupon.name]

    async def update(self, coupon: CouponUpdate) -> Coupon:
        if coupon.name not in self.data:
            raise CouponStorageNotFoundError()

        self.data[coupon.name] = Coupon.model_validate(coupon.model_dump())

        return self.data[coupon.name]

    async def delete(self, name: str) -> None:
        if name not in self.data:
            raise CouponStorageNotFoundError()

        del self.data[name]

    def close(self) -> None:
        return


def add_storage_exception_handlers(app: FastAPI):
    @app.exception_handler(CouponStorageAlreadyExistsError)
    async def handle_already_exists_error(request, exc):
        return JSONResponse(
            status_code=409, content={"detail": "Coupon with this name already exists"}
        )

    @app.exception_handler(CouponStorageNotFoundError)
    async def handle_not_found_error(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Coupon not found"})

    @app.exception_handler(CouponStorageProductNotApplicableError)
    async def handle_not_applicable_error(request, exc):
        return JSONResponse(
            status_code=422,
            content={"detail": "The coupon is not applicable to this product"},
        )

    @app.exception_handler(CouponStorageError)
    async def handle_general_storage_error(request, exc):
        return JSONResponse(
            status_code=500, content={"detail": "An internal storage error occurred"}
        )


@pytest.fixture
def mock_storage(request) -> YieldFixture[CouponStorage]:
    data = request.param if hasattr(request, "param") else None
    coupon_storage = InMemoryCouponStorage(data)
    try:
        yield coupon_storage
    finally:
        coupon_storage.close()


@pytest.fixture
def fake_api(mock_storage: CouponStorage) -> YieldFixture[TestClient]:
    app.dependency_overrides[get_coupon_storage] = lambda: mock_storage
    add_storage_exception_handlers(app)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def coupon_service() -> CouponApplicabilityService:
    return CouponApplicabilityService()
