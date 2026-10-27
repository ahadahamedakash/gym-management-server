from pydantic import Field, BaseModel

from enum import Enum

from typing import Optional


class Roles(str, Enum):
    ADMIN = "admin"
    USER = "user"


class CreateUser(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    password: str
    role: Roles


class UpdateUser(BaseModel):
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    firstname: Optional[str] = Field(default=None)
    lastname: Optional[str] = Field(default=None)


class UpdatePassword(BaseModel):
    current_password: str
    new_password: str
