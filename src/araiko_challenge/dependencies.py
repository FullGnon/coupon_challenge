from araiko_challenge.services.storage import CouponStorage
from araiko_challenge.services.storage.sqlite import SQLiteCouponStorage


async def get_coupon_storage() -> CouponStorage:
    return SQLiteCouponStorage(db_path="coupon.db")
