from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    slug: str


class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryStats(CategoryOut):
    product_count: int


class ProductBase(BaseModel):
    name: str
    price: Decimal
    stock: int
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    category_name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
