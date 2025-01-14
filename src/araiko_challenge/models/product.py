from enum import StrEnum

from pydantic import BaseModel, NonNegativeInt


class ProductCategory(StrEnum):
    FOOD = "food"
    FURNITURE = "furniture"
    ELECTRONICS = "electronics"


class Product(BaseModel):
    name: str
    price: NonNegativeInt
    category: ProductCategory
