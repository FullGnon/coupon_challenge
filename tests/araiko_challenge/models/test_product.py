from contextlib import AbstractContextManager, nullcontext

import pytest
from pydantic import ValidationError

from coupon_challenge.models.product import Product


@pytest.mark.parametrize(
    ("expected_context", "product_raw", "expected_product"),
    [
        pytest.param(
            nullcontext(),
            {"name": "product", "price": 100, "category": "food"},
            Product(name="product", price=100, category="food"),
            id="A valid product should be ok",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"price": 100, "category": "food"},
            None,
            id="A product must have a name",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "product", "category": "food"},
            None,
            id="A product must have a price",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "product", "price": 100},
            None,
            id="A product must have a category",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "product", "price": 100, "category": "cloth"},
            None,
            id="A product must have a known category",
        ),
        pytest.param(
            pytest.raises(ValidationError),
            {"name": "product", "price": -100, "category": "cloth"},
            None,
            id="A product must have positive price",
        ),
    ],
)
def test_product(
    expected_context: AbstractContextManager,
    product_raw: dict,
    expected_product: Product | None,
) -> None:
    with expected_context:
        assert Product.model_validate(product_raw) == expected_product
