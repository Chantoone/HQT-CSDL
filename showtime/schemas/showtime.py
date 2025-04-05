from datetime import datetime, date
from pydantic import BaseModel
from typing import List, Optional

from film.schemas.film import FilmResponse
from room.schemas.room import RoomResponse


class ShowtimeBase(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ShowtimeCreate(ShowtimeBase):
    name: str
    start_time: datetime
    film_id: int
    room_id: int


class ShowtimeUpdate(ShowtimeBase):
    film_id: Optional[int] = None
    room_id: Optional[int] = None


class ShowtimeResponse(ShowtimeBase):
    id: int
    film: FilmResponse  
    room: RoomResponse 
    created_at: datetime

    class Config:
        from_attributes = True


class ListShowtimeResponse(BaseModel):
    total_data: int
    showtimes: List[ShowtimeResponse]

    class Config:
        from_attributes = True


class ShowtimePageableResponse(BaseModel):
    total_data: int
    total_page: int
    showtimes: List[ShowtimeResponse]

    class Config:
        from_attributes = True 


class ShowtimeSearch(ShowtimeUpdate):
    pass


class ShowtimeByDateResponse(BaseModel):
    date: date
    date_formatted: str
    showtime_count: int
    # showtimes: List[ShowtimeResponse]


class ShowtimeWithTimeResponse(BaseModel):
    showtime: ShowtimeResponse
    time_only: str  # định dạng HH:MM

