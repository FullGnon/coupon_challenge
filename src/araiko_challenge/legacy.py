import argparse
import json
import math
import sqlite3
from datetime import datetime

from araiko_challenge.models.coupon import Coupon
from araiko_challenge.models.product import Product

connection = sqlite3.connect("coupon.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS coupon (
    name TEXT UNIQUE PRIMARY KEY,
    discount TEXT,
    condition TEXT
);               
""")
connection.commit()


def add_coupon(args):
    coupon_data = {"name": args.name, "discount": args.discount}
    if args.condition:
        coupon_data["condition"] = json.loads(args.condition)

    coupon = Coupon.model_validate(coupon_data)

    condition = coupon.condition.model_dump_json() if coupon.condition else ""
    cursor.execute(
        "INSERT INTO coupon VALUES ('%s', '%s', '%s')"
        % (coupon.name, coupon.discount_raw, condition)
    )
    connection.commit()

    print(f"Coupon added: {coupon}")


def get_coupon(name: str) -> Coupon:
    cursor.execute(f'SELECT * FROM coupon WHERE name = "{name}"')
    connection.commit()
    coupon = cursor.fetchone()

    coupon_raw = {
        "name": coupon[0],
        "discount": coupon[1],
    }
    if coupon[2]:
        coupon_raw["condition"] = json.loads(coupon[2])

    return Coupon.model_validate(coupon_raw)


def _apply_percent_discount(discount: int, price: int) -> int:
    # I choose arbitrarly to round down the result as i don't want to handle float for now.
    # Even if it would work
    return math.floor((1 - discount / 100) * price)


def _apply_fixed_discount(discount: int, price: int) -> int:
    # We handle the case where the fixed discount is greater than the price by
    return max(price - discount, 0)


def apply_discount(coupon: Coupon, product: Product) -> int:
    if coupon.is_percent:
        return _apply_percent_discount(coupon.discount, product.price)

    return _apply_fixed_discount(coupon.discount, product.price)


def coupon_is_valid(coupon: Coupon) -> bool:
    # If coupon has no validity period, it means it is always valid
    if not coupon.validity:
        return True

    # I do not handle TZ
    return coupon.validity.start <= datetime.now() <= coupon.validity.end


def coupon_is_applicable(coupon: Coupon, product: Product) -> bool:
    if not coupon_is_valid(coupon):
        return False

    if not coupon.condition:
        return True

    if coupon.condition.category and product.category != coupon.condition.category:
        return False

    if coupon.condition.price_above and product.price <= coupon.condition.price_above:
        return False

    return True


def test_product(args):
    coupon_name = args.coupon_name

    product = Product.model_validate_json(args.product)

    try:
        coupon = get_coupon(coupon_name)
    except Exception:  # FIXME: separate db errors from not found error
        print(f"Coupon '{coupon_name}' not found")
        return

    print(f"Test coupon {coupon.name} against product: {product}")

    if coupon_is_applicable(coupon, product):
        new_price = apply_discount(coupon, product)
        print(f"Applicable, new price is {new_price}$")
    else:
        print("Not Applicable")


def cli():
    parser = argparse.ArgumentParser(description="Coupon Management System")
    subparsers = parser.add_subparsers(help="commands")

    add_coupon_parser = subparsers.add_parser("add_coupon")
    add_coupon_parser.add_argument("name", type=str)
    add_coupon_parser.add_argument("discount", type=str)
    add_coupon_parser.add_argument("condition", type=str)
    add_coupon_parser.set_defaults(func=add_coupon)

    test_product_parser = subparsers.add_parser("test_product")
    test_product_parser.add_argument("coupon_name", type=str)
    test_product_parser.add_argument("product", type=str)
    test_product_parser.set_defaults(func=test_product)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli()
