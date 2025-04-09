from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from cinema.schemas.cinema import CinemaBase


class RoomBase(BaseModel):
    name: Optional[str] = None
    detail: Optional[str] = None
    capacity: Optional[int] = None

    class Config:
        from_attributes = True


class RoomCreate(RoomBase):
    name: str
    capacity: int
    cinema_id: int


class RoomUpdate(RoomBase):
    cinema_id: int


class RoomResponse(RoomBase):
    id: int
    is_active: Optional[bool] = None
    cinema: CinemaBase
    created_at: datetime

    class Config:
        from_attributes = True


class ListRoomResponse(BaseModel):
    rooms: list[RoomResponse]
    total_data: int

    class Config:
        from_attributes = True


class RoomPageableResponse(BaseModel):
    rooms: list[RoomResponse]
    total_data: int
    total_page: int

    class Config:
        from_attributes = True


class RoomSearch(RoomBase):
    cinema_id: Optional[int] = None 
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True