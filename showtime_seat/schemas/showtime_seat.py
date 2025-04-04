from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from seat.schemas.seat import SeatResponse
from showtime.schemas.showtime import ShowtimeResponse


class ShowtimeSeatBase(BaseModel):
    seat_status: Optional[bool] = None

    class Config:
        from_attributes = True


class ShowtimeSeatCreate(ShowtimeSeatBase):
    seat_id: int
    showtime_id: int


class ShowtimeSeatUpdate(ShowtimeSeatBase):
    seat_id: Optional[int] = None
    showtime_id: Optional[int] = None
    

class ShowtimeSeatResponse(ShowtimeSeatBase):
    id: int
    seat: SeatResponse
    showtime: ShowtimeResponse
    created_at: datetime

    class Config:
        from_attributes = True


class ListShowtimeSeatResponse(BaseModel):
    total_data: int
    showtime_seats: list[ShowtimeSeatResponse]

    class Config:
        from_attributes = True


class ShowtimeSeatPageableResponse(BaseModel):
    total_data: int
    total_page: int
    showtime_seats: list[ShowtimeSeatResponse]

    class Config:
        from_attributes = True


class ShowtimeSeatSearch(ShowtimeSeatUpdate):
    pass
