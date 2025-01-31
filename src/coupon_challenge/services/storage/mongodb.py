from typing import ClassVar

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import MongoDsn
from pymongo.server_api import ServerApi

from coupon_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from coupon_challenge.services.storage import (
    CouponStorage,
    CouponStorageAlreadyExistsError,
    CouponStorageCreateError,
    CouponStorageDeleteError,
    CouponStorageNotFoundError,
)


def catch_mongodb_error_and_rollback():
    """This function should be a decorator and applied to every methods that connect and perform operation on database.
    If error occurs, it will rollback to the previous state and raise it
    """
    raise NotImplementedError()


class MongoDBCouponStorage(CouponStorage):
    collection_name: ClassVar[str] = "coupons"

    # FIXME: use settings to get db_uri
    def __init__(self, db_uri: str | MongoDsn):
        self.client = AsyncIOMotorClient(str(db_uri), server_api=ServerApi("1"))
        self.collection = self.client["challenge"][self.collection_name]

    # @catch_mongodb_error_and_rollback
    async def get_all(self) -> list[Coupon]:
        # We should handle limit properly by doing bulk operation, and maybe add pagination options
        cursor = self.collection.find({})
        coupons = await cursor.to_list()
        return [Coupon.model_validate(coupon) for coupon in coupons]

    # @catch_mongodb_error_and_rollback
    async def get(self, name: str) -> Coupon:
        coupon_data = await self.collection.find_one({"name": name})

        if not coupon_data:
            raise CouponStorageNotFoundError()

        # Remove id to build Coupon
        if "_id" in coupon_data:
            del coupon_data["_id"]

        return Coupon.model_validate(coupon_data)

    # @catch_mongodb_error_and_rollback
    async def create(self, coupon_create: CouponCreate) -> Coupon:
        try:
            # FIXME: We may not need to get first, see if somehow insert_one can return an error
            #        if the name is already taken in database
            await self.get(coupon_create.name)
        except CouponStorageNotFoundError:
            # FIXME: thinking about it, running nominal code in a except is quite unsual (Tech Debt)
            result = await self.collection.insert_one(coupon_create.model_dump())

            if not result.inserted_id:
                raise CouponStorageCreateError()

            # FIXME: we may use returned object from db instead of input data
            return Coupon.model_validate(coupon_create.model_dump())
        else:
            raise CouponStorageAlreadyExistsError()

    # @catch_mongodb_error_and_rollback
    async def update(self, coupon_update: CouponUpdate) -> Coupon:
        coupon = await self.get(coupon_update.name)
        update_data = coupon_update.model_dump(exclude_unset=True)

        await self.collection.update_one(
            {"name": coupon_update.name}, {"$set": update_data}
        )

        # warning: we do not return the db object :/
        return Coupon.model_validate(
            {**coupon.model_dump(), **coupon_update.model_dump(exclude_unset=True)}
        )

    # @catch_mongodb_error_and_rollback
    async def delete(self, name: str) -> None:
        await self.get(name)

        result = await self.collection.delete_one({"name": name})

        if result.deleted_count != 1:
            raise CouponStorageDeleteError()

    def close(self) -> None:
        self.client.close()
