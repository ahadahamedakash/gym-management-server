from datetime import datetime

from pydantic import BaseModel, Field


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    page: int = Field(default=1, gt=1)
    total: int = Field(default=0, ge=0)
    skip: int = Field(default=10, gt=1)
