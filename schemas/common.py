from datetime import datetime

from pydantic import BaseModel, Field


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool
