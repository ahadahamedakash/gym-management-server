from pydantic import Field, BaseModel

from datetime import date


class EnrollmentCreate(BaseModel):
    subscription_id: int = Field(gt=0)


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    start_date: date
    end_date: date
    status: str
