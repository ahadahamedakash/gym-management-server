from pydantic import Field, BaseModel
from datetime import date

from .common import PaginationMeta


class EnrollmentCreate(BaseModel):
    subscription_id: int = Field(gt=0)


class EnrollmentUserInfo(BaseModel):
    id: int
    name: str
    email: str


class EnrollmentSubscriptionInfo(BaseModel):
    id: int
    name: str
    price: float
    duration_months: int


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    start_date: date
    end_date: date
    status: str

    user: EnrollmentUserInfo | None = None
    subscription: EnrollmentSubscriptionInfo | None = None


class EnrollmentListResponse(BaseModel):
    items: list[EnrollmentResponse]
    pagination: PaginationMeta
