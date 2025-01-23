import json
import sqlite3
from typing import ClassVar

from coupon_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from coupon_challenge.services.storage import (
    CouponStorage,
    CouponStorageAlreadyExistsError,
    CouponStorageNotFoundError,
)


def catch_sqlite_error_and_rollback():
    """This function should be a decorator and applied to every methods that connect and perform operation on database.
    If error occurs, it will rollback to the previous state
    """
    raise NotImplementedError()


# Note: I could use SQLModel (or SQLAlchemy) instead of managing sqlite engine directly
# Disclaimer: This implementation has not been updated after the improvement made in CouponStorage
#             for error handling (CouponStorageError). It should still works but it is not tested.
class SQLiteCouponStorage(CouponStorage):
    table_name: ClassVar[str] = "coupons"

    def __init__(self, db_path: str = "coupon.db"):
        # Warn Log something about this backend being deprecated
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_table()

    def _initialize_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            name TEXT UNIQUE PRIMARY KEY,
            discount TEXT NOT NULL,
            validity TEXT,
            condition TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def _from_rowdict_to_coupon(self, row: dict) -> Coupon:
        coupon_raw = {
            "name": row["name"],
            "discount": row["discount"],
        }
        if row["condition"]:
            coupon_raw["condition"] = json.loads(row["condition"])
        if row["validity"]:
            coupon_raw["validity"] = json.loads(row["validity"])

        return Coupon.model_validate(coupon_raw)

    # @catch_sqlite_error_and_rollback
    async def get_all(self) -> list[Coupon]:
        query = f"SELECT * FROM {self.table_name}"
        cursor = self.conn.execute(query)
        return [self._from_rowdict_to_coupon(dict(row)) for row in cursor]

    # @catch_sqlite_error_and_rollback
    async def get(self, name: str) -> Coupon:
        cursor = self.conn.execute(
            f"SELECT * FROM {self.table_name} WHERE name = '{name}';"
        )
        self.conn.commit()
        response = cursor.fetchone()

        if not response:
            raise CouponStorageNotFoundError()

        return self._from_rowdict_to_coupon(response)

    # @catch_sqlite_error_and_rollback
    async def create(self, coupon_create: CouponCreate) -> Coupon:
        existing_coupon = await self.get(coupon_create.name)
        if existing_coupon:
            raise CouponStorageAlreadyExistsError()

        query = f"""
        INSERT INTO {self.table_name} (name, discount, validity, condition)
        VALUES (?, ?, ?, ?)
        """
        self.conn.execute(
            query,
            (
                coupon_create.name,
                coupon_create.discount,
                coupon_create.validity.to_json_string()
                if coupon_create.validity
                else "",
                coupon_create.condition.model_dump_json()
                if coupon_create.condition
                else "",
            ),
        )
        self.conn.commit()

        return Coupon.model_validate(coupon_create.model_dump())

    # @catch_sqlite_error_and_rollback
    async def update(self, coupon_update: CouponUpdate) -> Coupon:
        existing_coupon = await self.get(coupon_update.name)
        if not existing_coupon:
            # TODO: This exception should be specific to this app in order to properly handle error on API side and CLI side
            raise IndexError

        query = f"""
        UPDATE {self.table_name}
        SET
            discount = ?,
            validity = ?,
            condition = ?
        WHERE name = ?;
        """
        self.conn.execute(
            query,
            (
                coupon_update.discount,
                coupon_update.validity.to_json_string()
                if coupon_update.validity
                else "",
                coupon_update.condition.model_dump_json()
                if coupon_update.condition
                else "",
                coupon_update.name,
            ),
        )
        self.conn.commit()

        return existing_coupon.model_copy(update=coupon_update.model_dump())

    # @catch_sqlite_error_and_rollback
    async def delete(self, name: str) -> None:
        existing_coupon = await self.get(name)

        if not existing_coupon:
            # TODO: This exception should be specific to this app in order to properly handle error on API side and CLI side
            raise IndexError

        self.conn.execute(f"DELETE FROM {self.table_name} WHERE name = '{name}';")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
