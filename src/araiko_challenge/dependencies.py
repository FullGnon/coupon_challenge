from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from fastapi import HTTPException

from araiko_challenge.services.coupons import CouponApplicabilityService
from araiko_challenge.services.storage import (
    CouponStorage,
    CouponStorageAlreadyExistsError,
    CouponStorageError,
    CouponStorageNotFoundError,
    CouponStorageProductNotApplicableError,
)
from araiko_challenge.services.storage.mongodb import MongoDBCouponStorage
from araiko_challenge.services.storage.sqlite import SQLiteCouponStorage


def get_coupon_storage() -> Generator[CouponStorage, None]:
    # TODO: Use app settings
    coupon_storage = MongoDBCouponStorage()
    # coupon_storage = SQLiteCouponStorage()

    try:
        yield coupon_storage
    except CouponStorageAlreadyExistsError:
        raise HTTPException(
            status_code=409, detail="Coupon with this name already exists"
        )
    except CouponStorageNotFoundError:
        raise HTTPException(status_code=404, detail="Coupon not found")
    except CouponStorageProductNotApplicableError:
        raise HTTPException(
            status_code=422, detail="The coupon is not applicable to this product"
        )
    except CouponStorageError:
        raise HTTPException(
            status_code=500, detail="An internal storage error occurred"
        )
    finally:
        # We properly close the connection
        coupon_storage.close()


async def get_coupon_service() -> CouponApplicabilityService:
    return CouponApplicabilityService()
