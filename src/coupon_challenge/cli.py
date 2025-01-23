import asyncio
from functools import wraps
from typing import Annotated

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from coupon_challenge.models.coupon import (
    Coupon,
    CouponCondition,
    CouponCreate,
    CouponUpdate,
    CouponValidity,
)
from coupon_challenge.models.product import Product
from coupon_challenge.services.coupons import CouponApplicabilityService
from coupon_challenge.services.storage import (
    CouponStorageAlreadyExistsError,
    CouponStorageError,
    CouponStorageNotFoundError,
    CouponStorageProductNotApplicableError,
)
from coupon_challenge.services.storage.mongodb import MongoDBCouponStorage
from coupon_challenge.services.storage.sqlite import SQLiteCouponStorage
from coupon_challenge.settings import (
    DBBackendEnum,
    get_app_settings,
    get_mongodb_settings,
)

app = typer.Typer()
coupons_app = typer.Typer()
app.add_typer(coupons_app, name="coupons")


@app.callback()
def main(ctx: typer.Context):
    settings = get_app_settings()
    if settings.db_backend == DBBackendEnum.mongo:
        mongo_settings = get_mongodb_settings()
        ctx.params["storage"] = MongoDBCouponStorage(mongo_settings.db_uri)
    elif settings.db_backend == DBBackendEnum.sqlite:
        ctx.params["storage"] = SQLiteCouponStorage()


def print_coupons(coupons: list[Coupon]) -> None:
    console = Console()

    table = Table("Name", "Discount", "Validity", "Condition")

    for coupon in coupons:
        table.add_row(
            coupon.name,
            str(coupon.discount_raw),
            "" if not coupon.validity else coupon.validity.to_json_string(),
            ""
            if not coupon.condition
            else coupon.condition.model_dump_json(
                exclude_unset=True, exclude_defaults=True
            ),
        )

    console.print(table)


def print_coupon(coupon: Coupon) -> None:
    print_coupons([coupon])


def print_product(product: Product) -> None:
    console = Console()

    table = Table("Name", "Price", "Category")
    table.add_row(product.name, str(product.price), product.category)

    console.print(table)


def prompt_for_coupon_update() -> CouponUpdate:
    answers = {}
    # Very simple prompting
    answers["name"] = typer.prompt("Name")
    discount = typer.prompt("Discount", default="")
    if discount:
        answers["discount"] = discount
    start = typer.prompt("Validity.start", default="")
    if start:
        end = typer.prompt("Validity.end")
        answers["validity"] = {"start": start, "end": end}
    condition = {}
    category = typer.prompt("Condition.category", default="")
    if category:
        condition["category"] = category
    price_above = typer.prompt("Condition.price_above", default="")
    if price_above:
        condition["price_above"] = price_above

    if condition:
        answers["condition"] = condition

    return CouponUpdate.model_validate(answers)


def prompt_for_coupon_create() -> CouponCreate:
    # Very simple prompting
    name = typer.prompt("Name")
    discount = typer.prompt("Discount")
    start = typer.prompt("Validity.start", default="")
    validity = None
    if start:
        end = typer.prompt("Validity.end")
        validity = CouponValidity(start=start, end=end)
    condition = {}
    category = typer.prompt("Condition.category", default="")
    if category:
        condition["category"] = category
    price_above = typer.prompt("Condition.price_above", default="")
    if price_above:
        condition["price_above"] = price_above

    condition = None if not condition else CouponCondition(**condition)

    return CouponCreate(
        name=name, discount=discount, validity=validity, condition=condition
    )


def prompt_for_product() -> Product:
    # Very simple prompting
    name = typer.prompt("Name")
    price = typer.prompt("Price")
    category = typer.prompt("Category")

    return Product(name=name, price=price, category=category)


# Decorator for async command handling
def async_command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def async_func():
            return await func(*args, **kwargs)

        return asyncio.run(async_func())

    return wrapper


# Handle every coupon storage error
def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except CouponStorageNotFoundError:
            print("Coupon not found")
        except CouponStorageAlreadyExistsError:
            print("Coupon already exists")
        except CouponStorageProductNotApplicableError:
            print("Coupon is not applicable for this product")
        except CouponStorageError:
            print("Internal storage error")

    return wrapper


@coupons_app.command()
@handle_errors
@async_command
async def list(ctx: typer.Context) -> None:
    """List all registered coupons"""
    coupons = await ctx.params["storage"].get_all()
    print_coupons(coupons)


@coupons_app.command()
@handle_errors
@async_command
async def get(ctx: typer.Context, name: str) -> None:
    """Get an existing coupon"""
    coupon = await ctx.params["storage"].get(name)
    print_coupon(coupon)


@coupons_app.command()
@handle_errors
@async_command
async def update(
    ctx: typer.Context,
    coupon_update: Annotated[
        CouponUpdate | None, typer.Argument(parser=CouponUpdate.model_validate_json)
    ] = None,
) -> None:
    """Update an existing coupon"""
    coupon_update = coupon_update or prompt_for_coupon_update()

    coupon = await ctx.params["storage"].update(coupon_update)
    print("Coupon Updated :)")
    print_coupon(coupon)


@coupons_app.command()
@handle_errors
@async_command
async def create(
    ctx: typer.Context,
    coupon_create: Annotated[
        CouponCreate | None, typer.Argument(parser=CouponCreate.model_validate_json)
    ] = None,
) -> None:
    """Create a coupon"""
    coupon_create = coupon_create or prompt_for_coupon_create()

    coupon = await ctx.params["storage"].create(coupon_create)
    print("Coupon Created :)")
    print_coupon(coupon)


@coupons_app.command()
@handle_errors
@async_command
async def delete(ctx: typer.Context, name: str) -> None:
    """Delete an existing coupon"""
    await ctx.params["storage"].delete(name)

    print(f"Coupon {name} Deleted :)")


@coupons_app.command()
@handle_errors
@async_command
async def apply(
    ctx: typer.Context,
    coupon_name: str,
    product: Annotated[
        Product | None, typer.Argument(parser=Product.model_validate_json)
    ] = None,
) -> None:
    """Test applicability of a Coupon over a Product"""
    product = product or prompt_for_product()

    service = CouponApplicabilityService()

    coupon = await ctx.params["storage"].get(coupon_name)

    print_coupon(coupon)

    if not service.coupon_is_applicable(coupon, product):
        print("Coupon not applicable for this product :(")
        return

    print("Applied to")
    print_product(product)

    new_product = service.apply_discount(coupon, product)

    print("Here your discount :)")
    print_product(new_product)
