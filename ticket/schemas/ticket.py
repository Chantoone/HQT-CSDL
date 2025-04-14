from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from seat.schemas.seat import SeatResponse
from showtime.schemas.showtime import ShowtimeResponse
from showtime_seat.schemas.showtime_seat import ShowtimeSeatResponse


class TicketBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None

    class Config:
        from_attributes = True


class TicketCreate(TicketBase):
    bill_id: int
    description: str
    title: str
    price: int
    showtime_seat_id: int


class TicketUpdate(TicketBase):
    showtime_seat_id: Optional[int] = None


class TicketResponse(TicketBase):
    id: int
    showtime_seat: ShowtimeSeatResponse
    created_at: datetime

    class Config:
        from_attributes = True


class ListTicketResponse(BaseModel):
    total_data: int
    tickets: list[TicketResponse]

    class Config:
        from_attributes = True


class TicketPageableResponse(BaseModel):
    total_data: int
    total_page: int
    tickets: list[TicketResponse]

    class Config:
        from_attributes = True


class TicketSearch(TicketUpdate):
    pass
