from coupon_challenge.dependencies import get_coupon_service, get_coupon_storage
from coupon_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from coupon_challenge.models.product import Product
from coupon_challenge.services.coupons import CouponApplicabilityService
from coupon_challenge.services.storage import (
    CouponStorage,
    CouponStorageProductNotApplicableError,
)
from fastapi import APIRouter, Depends

COUPONS_ROUTE_PREFIX = "/coupons"

router = APIRouter(
    prefix=COUPONS_ROUTE_PREFIX,
    tags=["coupons"],
)


@router.get("/", response_model=list[Coupon])
async def read_coupons(
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> list[Coupon]:
    """Retrieve all coupons."""
    coupons = await coupon_storage.get_all()

    return coupons


@router.get("/{name}", response_model=Coupon)
async def read_coupon(
    name: str,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> Coupon:
    """Retrieve a coupon by its name."""
    coupon = await coupon_storage.get(name)

    return coupon


@router.post("/", response_model=Coupon, status_code=201)
async def create_coupon(
    coupon_create: CouponCreate,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> Coupon:
    new_coupon = await coupon_storage.create(coupon_create)

    return new_coupon


@router.put("/", response_model=Coupon, status_code=202)
async def update_coupon(
    coupon_update: CouponUpdate,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> Coupon:
    updated_coupon = await coupon_storage.update(coupon_update)

    return updated_coupon


@router.delete("/{name}", status_code=200)
async def delete_coupon(
    name: str,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> None:
    await coupon_storage.delete(name)


@router.post("/{name}/apply_product", status_code=200)
async def apply_product(
    name: str,
    product: Product,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
    coupon_service: CouponApplicabilityService = Depends(get_coupon_service),
) -> Product:
    coupon = await coupon_storage.get(name)

    if not coupon_service.coupon_is_applicable(coupon, product):
        raise CouponStorageProductNotApplicableError()

    discounted_product = coupon_service.apply_discount(coupon, product)

    return discounted_product
