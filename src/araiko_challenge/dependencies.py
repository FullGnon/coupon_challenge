from araiko_challenge.services.coupons import CouponApplicabilityService
from araiko_challenge.services.storage import CouponStorage
from araiko_challenge.services.storage.sqlite import SQLiteCouponStorage


async def get_coupon_storage() -> CouponStorage:
    return SQLiteCouponStorage(db_path="coupon.db")


async def get_coupon_service() -> CouponApplicabilityService:
    return CouponApplicabilityService()
