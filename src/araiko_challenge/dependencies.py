from typing import Generator

from fastapi import Depends, HTTPException

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
from araiko_challenge.settings import (
    AppChallengeSettings,
    DBBackendEnum,
    MongoDBSettings,
    get_app_settings,
    get_mongodb_settings,
)


def dep_app_settings() -> AppChallengeSettings:
    return get_app_settings()


def dep_mongo_settings() -> MongoDBSettings:
    return get_mongodb_settings()


def get_mongo_storage(settings: MongoDBSettings) -> MongoDBCouponStorage:
    return MongoDBCouponStorage(settings.db_uri)


def get_coupon_storage(
    settings: AppChallengeSettings = Depends(dep_app_settings),
) -> Generator[CouponStorage, None]:
    if settings.db_backend == DBBackendEnum.mongo:
        coupon_storage = get_mongo_storage(get_mongodb_settings())
    elif settings.db_backend == DBBackendEnum.sqlite:
        # TODO: make settings for sqlite backend
        coupon_storage = SQLiteCouponStorage()

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


def get_coupon_service() -> CouponApplicabilityService:
    return CouponApplicabilityService()
