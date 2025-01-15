from araiko_challenge.models.coupon import Coupon


class CouponStorage:
    async def get_all(self) -> list[Coupon]:
        raise NotImplementedError()

    async def get(self, name: str) -> Coupon | None:
        raise NotImplementedError()

    async def create(self, coupon: Coupon) -> None:
        raise NotImplementedError()

    async def update(self, name: str, coupon: Coupon):
        raise NotImplementedError()

    async def delete(self, name: str):
        raise NotImplementedError()
