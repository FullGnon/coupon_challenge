import json
from datetime import datetime
from typing import Any, NamedTuple

from pydantic import BaseModel, ConfigDict, NonNegativeInt, model_validator

from coupon_challenge.models.product import ProductCategory


class CouponCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: ProductCategory | None = None
    price_above: NonNegativeInt | None = None


class CouponValidity(NamedTuple):
    start: datetime
    end: datetime

    def to_json_string(self) -> str:
        return json.dumps(
            self._asdict(),
            default=lambda o: o.isoformat() if isinstance(o, datetime) else o,
        )


class CouponBase(BaseModel):
    name: str
    condition: CouponCondition | None = None
    validity: CouponValidity | None = None

    @model_validator(mode="after")
    def check_valid_period(self) -> "CouponBase":
        if self.validity and self.validity.start > self.validity.end:
            msg = "Invalid period, start > end"
            raise ValueError(msg)

        return self


class Coupon(CouponBase):
    discount: NonNegativeInt
    is_percent: bool = False

    @model_validator(mode="before")
    def save_discount(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "discount" not in data:
                msg = "Discount is mandatory for a coupon"
                raise ValueError(msg)

            if isinstance(data["discount"], str) and data["discount"].endswith("%"):
                data["is_percent"] = True
                data["discount"] = int(data["discount"][:-1])

            # TODO: add a check to cap percent discount below 100%

        return data

    @property
    def discount_raw(self: "Coupon") -> str:
        return f"{self.discount}%" if self.is_percent else str(self.discount)


class CouponDTO(CouponBase):
    model_config = ConfigDict(extra="forbid")


class CouponCreate(CouponDTO):
    discount: NonNegativeInt | str


class CouponUpdate(CouponDTO):
    discount: NonNegativeInt | str | None = None
