from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from room.schemas.room import RoomResponse


class SeatBase(BaseModel):
    seat_number: Optional[str] = None
    detail: Optional[str] = None
    is_booked: Optional[bool] = False
    is_active: Optional[bool] = True
 

class SeatCreate(SeatBase):
    seat_number: str
    room_id: int


class SeatUpdate(SeatBase):
    pass


class SeatResponse(SeatBase):
    id: int
    room: RoomResponse
    created_at: datetime

    class Config:
        from_attributes = True


class SeatResponseWithoutRoom(SeatBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ListSeatResponse(BaseModel):
    seats: List[SeatResponse]
    total_data: int

    class Config:
        from_attributes = True


class SeatPageableResponse(ListSeatResponse):
    total_data: int

    class Config:
        from_attributes = True


class SeatSearch(SeatBase):
    pass