from datetime import datetime
from typing import Any, NamedTuple

from pydantic import BaseModel, ConfigDict, NonNegativeInt, model_validator

from araiko_challenge.models.product import ProductCategory


class CouponCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: ProductCategory | None = None
    price_above: NonNegativeInt | None = None


class CouponValidity(NamedTuple):
    start: datetime
    end: datetime


class Coupon(BaseModel):
    name: str
    discount: NonNegativeInt
    condition: CouponCondition | None = None
    validity: CouponValidity | None = None
    is_percent: bool = False

    @model_validator(mode="before")
    def save_discount(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "discount" not in data:
                msg = "Discount is mandatory for a coupon"
                raise ValueError(msg)

            if isinstance(data["discount"], str) and data["discount"].endswith("%"):
                data["is_percent"] = True
                data["discount"] = data["discount"][:-1]

            # TODO: add a check to cap percent discount below 100%

        return data

    @property
    def discount_raw(self: "Coupon") -> str:
        return f"{self.discount}%" if self.is_percent else self.discount

    @model_validator(mode="after")
    def check_valid_period(self) -> "Coupon":
        if self.validity and self.validity.start > self.validity.end:
            msg = "Invalid period, start > end"
            raise ValueError(msg)

        return self
