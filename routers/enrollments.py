import calendar
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from typing import Annotated
from datetime import datetime, timezone


from database import get_db
from routers.auth import UserDependency
from models.enrollments import Enrollments
from models.subscriptions import Subscriptions
from schemas.enrollments import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentListResponse,
)

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

DbDependency = Annotated[Session, Depends(get_db)]


def add_months(start_date, months: int):
    month_index = start_date.month - 1 + months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1

    day = min(
        start_date.day,
        calendar.monthrange(year, month)[1],
    )

    return start_date.replace(year=year, month=month, day=day)


@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_enrollment(
    data: EnrollmentCreate,
    db: DbDependency,
    user: UserDependency,
):
    subscription = (
        db.query(Subscriptions)
        .filter(
            Subscriptions.id == data.subscription_id,
            Subscriptions.is_active.is_(True),
        )
        .first()
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Active subscription not found",
        )

    start_date = datetime.now(timezone.utc).date()
    end_date = add_months(start_date, subscription.duration_months)

    enrollment = Enrollments(
        user_id=user["id"],
        subscription_id=subscription.id,
        start_date=start_date,
        end_date=end_date,
        status="active",
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


@router.get("/", response_model=EnrollmentListResponse)
def list_my_enrollments(
    db: DbDependency,
    user: UserDependency,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    query = db.query(Enrollments).filter(Enrollments.user_id == user["id"])

    total = query.count()

    items = (
        query.order_by(Enrollments.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_previous = page > 1

    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
        },
    }


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_my_enrollment(
    enrollment_id: int,
    db: DbDependency,
    user: UserDependency,
):
    enrollment = (
        db.query(Enrollments)
        .filter(
            Enrollments.id == enrollment_id,
            Enrollments.user_id == user["id"],
        )
        .first()
    )

    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment not found",
        )

    return enrollment
