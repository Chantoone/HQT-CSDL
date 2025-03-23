from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from seat.schemas.seat import SeatResponseWithoutRoom
from showtime.schemas.showtime import ShowtimeResponse


class TicketBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None

    class Config:
        from_attributes = True


class TicketCreate(TicketBase):
    title: str
    price: int
    showtime_id: int
    seat_id: int


class TicketUpdate(TicketBase):
    showtime_id: Optional[int] = None
    seat_id: Optional[int] = None


class TicketResponse(TicketBase):
    id: int
    showtime: ShowtimeResponse
    seat: SeatResponseWithoutRoom
    created_at: datetime

    class Config:
        from_attributes = True


class ListTicketResponse(BaseModel):
    tickets: list[TicketResponse]
    total_data: int

    class Config:
        from_attributes = True


class TicketPageableResponse(BaseModel):
    tickets: list[TicketResponse]
    total_data: int
    total_page: int

    class Config:
        from_attributes = True


class TicketSearch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    showtime_id: Optional[int] = None
    seat_id: Optional[int] = None
