from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from user.schemas.user import UserBase
from film.schemas.film import FilmResponse

class RateBase(BaseModel):
    point: Optional[int] = 0
    detail: Optional[str] = None


class RateCreate(RateBase):
    user_id: int
    film_id: int
    point: int


class RateUpdate(RateBase):
    pass


class RateResponse(RateBase):
    id: int
    user: UserBase
    film: FilmResponse
    created_at: datetime

    class Config:
        from_attributes = True


class ListRateResponse(BaseModel):
    rates: List[RateResponse]
    total_data: int

    class Config:
        from_attributes = True


class RatePageableResponse(BaseModel):
    rates: List[RateResponse]
    total_data: int
    total_page: int

    class Config:
        from_attributes = True


class RateSearch(BaseModel):
    point: Optional[int] = None
    detail: Optional[str] = None
    user_id: Optional[int] = None
    film_id: Optional[int] = None

    class Config:
        from_attributes = True