from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Annotated
from models import Users
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt

from schemas.auth import CreateUser, UpdatePassword, UpdateUser
from database import get_db

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "86746eeb8285ca279c6251e0bd83cdd50c88027b934a93f19d8b9af782139516"
ALGORITHM = "HS256"


def authenticate_user(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()

    if user is None:
        return False
    if bcrypt_context.verify(password, user.hash_password):
        return user

    return False


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"username": username, "id": user_id, "role": role}
    except:
        raise HTTPException(status_code=404, detail="User not found")


DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]


@router.post("/register")
def register(db: DbDependency, new_user: CreateUser):
    existing_username = (
        db.query(Users).filter(Users.username == new_user.username).first()
    )

    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = db.query(Users).filter(Users.email == new_user.email).first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_model = Users(
        email=new_user.email,
        username=new_user.username,
        firstname=new_user.firstname,
        lastname=new_user.lastname,
        hash_password=bcrypt_context.hash(new_user.password),
        is_active=True,
        role=new_user.role,
    )

    db.add(user_model)
    db.commit()

    return JSONResponse(
        status_code=201, content={"message": "User created successfully"}
    )


@router.post("/login")
def login_user(
    db: DbDependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        return "Failed authentication"

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=30)
    )

    return {"access_token": token, "tokey_type": "bearer"}


@router.put("/update-user")
def update_user(user: UserDependency, db: DbDependency, update_user: UpdateUser):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    user = db.query(Users).filter(Users.id == user.get("id")).first()

    update_data = update_user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()

    return JSONResponse(
        status_code=200, content={"message": "User updated successfully"}
    )


@router.put("/change-password")
def update_password(
    user: UserDependency, db: DbDependency, update_password: UpdatePassword
):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(update_password.current_password, user.hash_password):
        raise HTTPException(status_code=401, detail="Wrong Password")

    user.hash_password = bcrypt_context.hash(update_password.new_password)

    db.add(user)
    db.commit()
    return JSONResponse(
        status_code=200, content={"message": "Password updated successfully"}
    )


@router.get("/user-details")
def get_user_details(user: UserDependency, db: DbDependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "firstname": current_user.firstname,
        "lastname": current_user.lastname,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
