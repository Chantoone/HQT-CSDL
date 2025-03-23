from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from film.schemas.film import FilmResponse
from room.schemas.room import RoomResponse


class ShowtimeBase(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    film_id: Optional[int] = None
    room_id: Optional[int] = None

    class Config:
        from_attributes = True


class ShowtimeCreate(ShowtimeBase):
    name: str
    start_time: datetime
    film_id: int
    room_id: int


class ShowtimeUpdate(ShowtimeBase):
    pass


class ShowtimeResponse(ShowtimeBase):
    id: int
    film: Optional[FilmResponse] = None
    room: Optional[RoomResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ShowtimeResponseWithoutRoom(ShowtimeBase):
    id: int
    film: Optional[FilmResponse] = None
    room: Optional[RoomResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ListShowtimeResponse(BaseModel):
    showtimes: List[ShowtimeResponse]
    total_data: int

    class Config:
        from_attributes = True


class ShowtimePageableResponse(BaseModel):
    showtimes: List[ShowtimeResponse]
    total_data: int
    total_page: int

    class Config:
        from_attributes = True 


class ShowtimeSearch(ShowtimeBase):
    pass