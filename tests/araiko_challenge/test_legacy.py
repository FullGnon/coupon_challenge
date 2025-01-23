from datetime import datetime
from unittest.mock import patch

import pytest
from coupon_challenge.legacy import (
    apply_discount,
    coupon_is_applicable,
    coupon_is_valid,
)
from coupon_challenge.models.coupon import Coupon, CouponCondition, CouponValidity
from coupon_challenge.models.product import Product


@pytest.mark.parametrize(
    ("coupon", "product", "expected_result"),
    [
        pytest.param(
            Coupon(name="coupon", discount=10),
            Product(name="product", price=100, category="food"),
            90,
            id="Apply fixed discount",
        ),
        pytest.param(
            Coupon(name="coupon", discount="10%"),
            Product(name="product", price=100, category="food"),
            90,
            id="Apply percent discount",
        ),
        pytest.param(
            Coupon(name="coupon", discount=200),
            Product(name="product", price=100, category="food"),
            0,
            id="Apply greater fixed discount should returns 0",
        ),
    ],
)
def test_apply_discount(coupon: Coupon, product: Product, expected_result: int) -> None:
    assert apply_discount(coupon, product) == expected_result


@pytest.mark.parametrize(
    ("condition", "product", "expected_result"),
    [
        pytest.param(
            None,
            Product(name="product", price=100, category="food"),
            True,
            id="No condition should always apply to a product",
        ),
        pytest.param(
            CouponCondition(category="food"),
            Product(name="product", price=100, category="food"),
            True,
            id="Apply coupon with correct category condition",
        ),
        pytest.param(
            CouponCondition(category="food"),
            Product(name="product", price=100, category="furniture"),
            False,
            id="Coupon not applicable with incorrect category condition",
        ),
        pytest.param(
            CouponCondition(price_above=10),
            Product(name="product", price=100, category="food"),
            True,
            id="Coupon applicable with price_above condition",
        ),
        pytest.param(
            CouponCondition(price_above=100),
            Product(name="product", price=10, category="food"),
            False,
            id="Coupon not applicable with price_above condition",
        ),
        pytest.param(
            CouponCondition(category="food", price_above=100),
            Product(name="product", price=10, category="food"),
            False,
            id="A product should fulfill every condition to be applicable, wrong price_above",
        ),
        pytest.param(
            CouponCondition(category="furniture", price_above=10),
            Product(name="product", price=100, category="food"),
            False,
            id="A product should fulfill every condition to be applicable, wrong category",
        ),
        pytest.param(
            CouponCondition(category="food", price_above=10),
            Product(name="product", price=100, category="food"),
            True,
            id="A product should fulfill every condition to be applicable",
        ),
    ],
)
def test_coupon_is_applicable(
    condition: CouponCondition, product: Product, expected_result: bool
) -> None:
    coupon = Coupon(name="coupon", discount=10, condition=condition)
    assert coupon_is_applicable(coupon, product) == expected_result


@pytest.mark.parametrize(
    ("start", "end", "moment", "expected_result"),
    [
        pytest.param(
            "2025-01-01",
            "2026-01-01",
            "2025-02-01",
            True,
            id="Coupon is valid in date range",
        ),
        pytest.param(
            "2025-01-01", "2026-01-01", "2027-01-01", False, id="Coupon has expired"
        ),
        pytest.param(
            "2025-01-01",
            "2026-01-01",
            "2024-01-01",
            False,
            id="Coupon is not yet available",
        ),
        pytest.param(
            "2025-01-01",
            "2026-01-01",
            "2025-01-01",
            True,
            id="Date validation is inclusive on start",
        ),
        pytest.param(
            "2025-01-01",
            "2026-01-01",
            "2026-01-01",
            True,
            id="Date validation is inclusive on end",
        ),
    ],
)
def test_coupon_is_valid(
    start: str, end: str, moment: str, expected_result: bool
) -> None:
    coupon = Coupon(
        name="coupon", discount=10, validity=CouponValidity(start=start, end=end)
    )

    with patch("coupon_challenge.legacy.datetime") as datetime_mock:
        datetime_mock.now.return_value = datetime.fromisoformat(moment)
        assert coupon_is_valid(coupon) == expected_result
