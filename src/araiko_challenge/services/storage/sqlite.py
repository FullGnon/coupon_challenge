import json
import sqlite3
from typing import ClassVar

from araiko_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from araiko_challenge.services.storage import CouponStorage


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
        self.conn = sqlite3.connect(db_path)
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
            "name": row[0],
            "discount": row[1],
        }
        if row[2]:
            coupon_raw["condition"] = json.loads(row[2])
        if row[3]:
            coupon_raw["validity"] = json.loads(row[3])

        return Coupon.model_validate(coupon_raw)

    # @catch_sqlite_error_and_rollback
    async def get_all(self) -> list[Coupon]:
        query = f"SELECT * FROM {self.table_name}"
        cursor = self.conn.execute(query)
        return [self._from_rowdict_to_coupon(dict(row)) for row in cursor]

    # @catch_sqlite_error_and_rollback
    async def get(self, name: str) -> Coupon | None:
        cursor = self.conn.execute(
            f"SELECT * FROM {self.table_name} WHERE name = '{name}';"
        )
        self.conn.commit()
        response = cursor.fetchone()

        return self._from_rowdict_to_coupon(response) if response else None

    # @catch_sqlite_error_and_rollback
    async def create(self, coupon: CouponCreate) -> Coupon:
        existing_coupon = await self.get(coupon.name)
        if existing_coupon:
            # TODO: This exception should be specific to this app in order to properly handle error on API side and CLI side
            raise IndexError

        query = f"""
        INSERT INTO {self.table_name} (name, discount, validity, condition)
        VALUES (?, ?, ?, ?)
        """
        self.conn.execute(
            query,
            (
                coupon.name,
                coupon.discount,
                coupon.validity.to_json_string() if coupon.validity else "",
                coupon.condition.model_dump_json() if coupon.condition else "",
            ),
        )
        self.conn.commit()

        return Coupon.model_validate(coupon.model_dump())

    # @catch_sqlite_error_and_rollback
    async def update(self, coupon: CouponUpdate) -> Coupon:
        existing_coupon = await self.get(coupon.name)
        if not existing_coupon:
            # TODO: This exception should be specific to this app in order to properly handle error on API side and CLI side
            raise IndexError

        query = f"""
        UPDATE {self.table_name}
        SET
            discount = ?,
            validity = ?,
            condition = ?,
        WHERE name = ?;
        """
        self.conn.execute(
            query,
            (
                coupon.discount,
                coupon.validity.to_json_string() if coupon.validity else "",
                coupon.condition.model_dump_json() if coupon.condition else "",
                coupon.name,
            ),
        )
        self.conn.commit()

        return existing_coupon.model_copy(update=coupon.model_dump())

    # @catch_sqlite_error_and_rollback
    async def delete(self, name: str) -> None:
        existing_coupon = await self.get(name)

        if not existing_coupon:
            # TODO: This exception should be specific to this app in order to properly handle error on API side and CLI side
            raise IndexError

        self.conn.execute(f"DELETE FROM {self.table_name} WHERE name = '{name}';")
        self.conn.commit()
