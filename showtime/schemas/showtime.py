from datetime import datetime, date
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


class AvailableDateResponse(BaseModel):
    date: date
    date_formatted: str
    showtime_count: int

    class Config:
        from_attributes = True


# Thêm class này

class AvailableTimeResponse(BaseModel):
    id: int
    start_time: datetime
    time_formatted: str
    room_name: str
    room_detail: Optional[str] = None
    room_capacity: int
    available_seats: int
    
    class Config:
        from_attributes = True


class SeatInfo(BaseModel):
    id: str               # Ví dụ: A1, B2, C3
    row: str              # Ví dụ: A, B, C
    number: int           # Ví dụ: 1, 2, 3
    is_booked: bool       # True nếu đã đặt, False nếu còn trống
    price: int            # Giá vé cho ghế này
    
    class Config:
        from_attributes = True

class SeatRow(BaseModel):
    row: str              # Ký hiệu hàng (A, B, C...)
    seats: List[SeatInfo] # Danh sách ghế trong hàng này
    
    class Config:
        from_attributes = True


class SeatsResponse(BaseModel):
    showtime_id: int
    film_title: str
    cinema_name: str
    room_name: str
    start_time: datetime
    time_formatted: str
    total_seats: int
    available_seats: int
    rows: List[SeatRow]

    class Config:
        from_attributes = True