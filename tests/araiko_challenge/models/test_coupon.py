from contextlib import AbstractContextManager, nullcontext
from datetime import datetime

import pytest
from pydantic import (
    ValidationError,
)

from araiko_challenge.models.coupon import Coupon, CouponCondition, CouponValidity


@pytest.mark.parametrize(
    ("expected_context", "coupon_raw", "expected_coupon"),
    [
        pytest.param(
            nullcontext(),
            {
                "name": "coupon",
                "discount": 1,
            },
            Coupon(name="coupon", discount=1),
            id="The minimal coupon, without condition, should be ok",
        ),
        pytest.param(
            nullcontext(),
            {
                "name": "coupon",
                "discount": "1",
            },
            Coupon(name="coupon", discount=1),
            id="A fixed discount value could also be a string",
        ),
        pytest.param(
            nullcontext(),
            {"name": "coupon", "discount": 1, "condition": {"category": "food"}},
            Coupon(
                name="coupon", discount=1, condition=CouponCondition(category="food")
            ),
            id="A coupon with a category condition should be ok",
        ),
        pytest.param(
            nullcontext(),
            {"name": "coupon", "discount": 1, "condition": {"price_above": 10}},
            Coupon(
                name="coupon", discount=1, condition=CouponCondition(price_above=10)
            ),
            id="A coupon with a price above condition should be ok",
        ),
        pytest.param(
            nullcontext(),
            {
                "name": "coupon",
                "discount": 1,
                "validity": {"start": "2025-01-01", "end": "2026-01-01"},
            },
            Coupon(
                name="coupon",
                discount=1,
                validity=CouponValidity(
                    start=datetime.fromisoformat("2025-01-01"),
                    end=datetime.fromisoformat("2026-01-01"),
                ),
            ),
            id="A coupon with a date period should be ok",
        ),
        pytest.param(
            nullcontext(),
            {
                "name": "coupon",
                "discount": 1,
                "condition": {"price_above": 10, "category": "food"},
            },
            Coupon(
                name="coupon",
                discount=1,
                condition=CouponCondition(price_above=10, category="food"),
            ),
            id="A coupon can have many condition",
        ),
        pytest.param(
            nullcontext(),
            {
                "name": "coupon",
                "discount": "1%",
            },
            Coupon(name="coupon", discount=1, is_percent=True),
            id="The discount value must allow percentage",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {
                "discount": 1,
            },
            None,
            id="A coupon must have a name",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {
                "name": "coupon",
            },
            None,
            id="A coupon must have a discount",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "coupon", "discount": -1},
            None,
            id="A discount must be non negative",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "coupon", "discount": 0.1},
            None,
            id="A discount must be an integer, float are not yet implemented",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "coupon", "discount": 1, "condition": {"category": "cloth"}},
            None,
            id="Unknown category lead to wrong coupon",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "coupon", "discount": 1, "condition": {"vip": True}},
            None,
            id="Unknown condition lead to wrong coupon",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {
                "name": "coupon",
                "discount": 1,
                "validity": {"start": "2026-01-01", "end": "2025-01-01"},
            },
            None,
            id="Invalid validity period lead to wrong coupon",
        ),
    ],
)
def test_coupon(
    expected_context: AbstractContextManager, coupon_raw: dict, expected_coupon: Coupon
) -> None:
    with expected_context:
        assert Coupon.model_validate(coupon_raw) == expected_coupon
