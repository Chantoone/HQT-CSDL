from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from cinema.schemas.cinema import CinemaBase


class UserBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None
    cinema: Optional[CinemaBase] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    username: str
    password: str


class UserUpdate(UserBase):
    full_name: Optional[str] = None
    cinema_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    full_name: str
    username: str
    is_active: bool
    created_at: datetime

    roles: list[str]
    
    class Config:
        from_attributes = True


class ListUserResponse(BaseModel):
    users: list[UserResponse]
    tolal_data: int

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    id: int
    full_name: str
    is_active: bool
    created_at: datetime
    roles: list[str]

    class Config:
        from_attributes = True


class UserPageableResponse(BaseModel):
    users: list[UserResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class UserSearch(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True

    
class UserDelete(BaseModel):
    list_id: list[int]

    class Config:
        from_attributes = True


class UserCreateAccount(BaseModel):
    full_name: str
    username: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class UserFullNameResponse(BaseModel):
    id: int
    full_name: str

    class Config:
        from_attributes = True


class ListUserFullNameResponse(BaseModel):
    users: list[UserFullNameResponse]

    class Config:
        from_attributes = True