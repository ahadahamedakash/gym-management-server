from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db

from models.users import Users
from models.enrollments import Enrollments
from models.subscriptions import Subscriptions

from schemas.subscriptions import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionListResponse,
)
from .auth import get_current_admin

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

DbDependency = Annotated[Session, Depends(get_db)]
AdminDependency = Annotated[Users, Depends(get_current_admin)]


@router.get("/", response_model=SubscriptionListResponse)
def get_subscriptions(
    db: DbDependency,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    query = db.query(Subscriptions).filter(Subscriptions.is_active == True)

    total = query.count()

    items = (
        query.order_by(Subscriptions.id.desc())
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


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: DbDependency,
):
    subscription = (
        db.query(Subscriptions)
        .filter(
            Subscriptions.id == subscription_id,
            Subscriptions.is_active.is_(True),
        )
        .first()
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    return subscription


@router.post(
    "/",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subscription(
    data: SubscriptionCreate,
    db: DbDependency,
    admin: AdminDependency,
):
    existing = db.query(Subscriptions).filter(Subscriptions.name == data.name).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Subscription name already exists",
        )

    subscription = Subscriptions(**data.model_dump())

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@router.patch(
    "/{subscription_id}",
    response_model=SubscriptionResponse,
)
def update_subscription(
    subscription_id: int,
    data: SubscriptionUpdate,
    db: DbDependency,
    admin: AdminDependency,
):
    subscription = (
        db.query(Subscriptions).filter(Subscriptions.id == subscription_id).first()
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    if "name" in update_data and update_data["name"] is not None:
        existing = (
            db.query(Subscriptions)
            .filter(
                Subscriptions.name == update_data["name"],
                Subscriptions.id != subscription_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Subscription name already exists",
            )

    for key, value in update_data.items():
        setattr(subscription, key, value)

    db.commit()
    db.refresh(subscription)

    return subscription


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: DbDependency,
    admin: AdminDependency,
):
    subscription = (
        db.query(Subscriptions).filter(Subscriptions.id == subscription_id).first()
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    enrollment_exists = (
        db.query(Enrollments.id)
        .filter(Enrollments.subscription_id == subscription_id)
        .first()
    )

    if enrollment_exists:
        raise HTTPException(
            status_code=409,
            detail="Subscription has enrollments and cannot be deleted",
        )

    db.delete(subscription)
    db.commit()

    return None
