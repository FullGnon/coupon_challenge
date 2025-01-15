from fastapi import APIRouter, Depends, HTTPException

from araiko_challenge.dependencies import get_coupon_storage
from araiko_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from araiko_challenge.services.storage import CouponStorage

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

    if not coupon:
        raise HTTPException(status_code=404, detail=f"Coupon {name} not found")

    return coupon


@router.post("/", response_model=Coupon, status_code=201)
async def create_coupon(
    coupon_create: CouponCreate,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> Coupon:
    existing_coupon = await coupon_storage.get(coupon_create.name)
    if existing_coupon:
        raise HTTPException(
            status_code=409, detail="Coupon with this name already exists"
        )

    new_coupon = await coupon_storage.create(coupon_create)

    return new_coupon


@router.put("/", response_model=Coupon, status_code=202)
async def update_coupon(
    coupon_update: CouponUpdate,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> Coupon:
    existing_coupon = await coupon_storage.get(coupon_update.name)
    if not existing_coupon:
        raise HTTPException(
            status_code=404, detail="Coupon with this name does not exists"
        )

    updated_coupon = await coupon_storage.update(coupon_update)

    return updated_coupon


@router.delete("/{name}", status_code=200)
async def delete_coupon(
    name: str,
    coupon_storage: CouponStorage = Depends(get_coupon_storage),
) -> None:
    existing_coupon = await coupon_storage.get(name)
    if not existing_coupon:
        raise HTTPException(
            status_code=404, detail="Coupon with this name does not exists"
        )

    await coupon_storage.delete(name)
