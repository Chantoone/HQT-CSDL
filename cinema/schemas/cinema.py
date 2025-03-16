from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class CinemaBase(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None


class CinemaCreate(CinemaBase):
    name: str
    address: str
    phone_number: str


class CinemaUpdate(CinemaBase):
    pass


class CinemaResponse(CinemaBase):
    id: int
    is_active: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ListCinemaResponse(BaseModel):
    cinemas: list[CinemaResponse]
    total_data: int

    class Config:
        from_attributes = True


class CinemaPageableResponse(BaseModel):
    cinemas: list[CinemaResponse]
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class CinemaSearch(CinemaBase):
    pass

    class Config:
        from_attributes = True


