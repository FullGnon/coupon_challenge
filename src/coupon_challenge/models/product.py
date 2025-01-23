from enum import StrEnum

from pydantic import BaseModel, ConfigDict, NonNegativeInt


class ProductCategory(StrEnum):
    FOOD = "food"
    FURNITURE = "furniture"
    ELECTRONICS = "electronics"


class Product(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    price: NonNegativeInt
    category: ProductCategory
