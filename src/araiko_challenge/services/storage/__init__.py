from araiko_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate


class CouponStorage:
    async def get_all(self) -> list[Coupon]:
        raise NotImplementedError()

    async def get(self, name: str) -> Coupon | None:
        raise NotImplementedError()

    async def create(self, coupon: CouponCreate) -> Coupon:
        raise NotImplementedError()

    async def update(self, coupon: CouponUpdate) -> Coupon:
        raise NotImplementedError()

    async def delete(self, name: str) -> None:
        raise NotImplementedError()
