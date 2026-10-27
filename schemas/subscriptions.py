from pydantic import Field, BaseModel

from decimal import Decimal

from .common import TimestampSchema, PaginationMeta


class SubscriptionCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=3000)
    duration_months: int = Field(gt=0, le=120)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class SubscriptionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=3000)
    duration_months: int | None = Field(default=None, gt=0, le=120)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    is_active: bool | None = None


class SubscriptionResponse(TimestampSchema):
    id: int
    name: str
    description: str | None
    duration_months: int
    price: Decimal
    is_active: bool


class SubscriptionListResponse(BaseModel):
    items: list[SubscriptionResponse]
    pagination: PaginationMeta
