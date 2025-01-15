import math
from datetime import datetime

from araiko_challenge.models.coupon import Coupon
from araiko_challenge.models.product import Product


class CouponApplicabilityService:
    """A service class to handle coupon-related business logic, such as
    validating coupon applicability and applying discounts.

    This service encapsulates logic for:
    - Determining if a coupon is applicable to a given product based on
      conditions like category, price thresholds, and validity periods.
    - Calculating the final price of a product after applying a coupon,
      whether the discount is percentage-based or fixed.
    """

    def _apply_percent_discount(self, discount: int, price: int) -> int:
        # I choose arbitrarly to round down the result as i don't want to handle float for now.
        # Even if it would work
        return math.floor((1 - discount / 100) * price)

    def _apply_fixed_discount(self, discount: int, price: int) -> int:
        # We handle the case where the fixed discount is greater than the price by
        return max(price - discount, 0)

    def apply_discount(self, coupon: Coupon, product: Product) -> int:
        if coupon.is_percent:
            return self._apply_percent_discount(coupon.discount, product.price)

        return self._apply_fixed_discount(coupon.discount, product.price)

    def coupon_is_valid(self, coupon: Coupon) -> bool:
        # If coupon has no validity period, it means it is always valid
        if not coupon.validity:
            return True

        # I do not handle TZ
        return coupon.validity.start <= datetime.now() <= coupon.validity.end

    def coupon_is_applicable(self, coupon: Coupon, product: Product) -> bool:
        if not self.coupon_is_valid(coupon):
            return False

        if not coupon.condition:
            return True

        if coupon.condition.category and product.category != coupon.condition.category:
            return False

        if (
            coupon.condition.price_above
            and product.price <= coupon.condition.price_above
        ):
            return False

        return True
