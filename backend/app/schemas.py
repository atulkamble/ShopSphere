from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "US"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool = False

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    description: str
    price: Decimal
    image_url: Optional[str] = None
    category_id: int
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int


class CartOut(BaseModel):
    user_id: int
    items: List[CartItemOut]
    subtotal: Decimal


class CheckoutItem(BaseModel):
    product_id: int
    quantity: int = 1


class CheckoutRequest(BaseModel):
    user_id: int
    idempotency_key: Optional[str] = None
    shipping_address: AddressBase
    items: List[CheckoutItem]


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    items: List[OrderItemOut]
    payments: List[dict]


class DashboardSummary(BaseModel):
    products: int
    orders: int
    revenue: Decimal
    low_inventory: int
