from araiko_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate


class CouponStorageError(Exception):
    pass


class CouponStorageCreateError(CouponStorageError):
    pass


class CouponStorageUpdateError(CouponStorageError):
    pass


class CouponStorageDeleteError(CouponStorageError):
    pass


class CouponStorageNotFoundError(CouponStorageError):
    pass


class CouponStorageProductNotApplicableError(CouponStorageError):
    pass


class CouponStorageAlreadyExistsError(CouponStorageError):
    pass


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

    def close(self) -> None:
        raise NotImplementedError()
