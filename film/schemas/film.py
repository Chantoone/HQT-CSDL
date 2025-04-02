from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Optional


class FilmBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    release_date: Optional[date] = None
    author: Optional[str] = None
    poster_path: Optional[str] = None
    status: Optional[str] = None
    actors: Optional[str] = None
    director: Optional[str] = None


class FilmCreate(FilmBase):
    title: str
    status: str


class FilmUpdate(FilmBase):
    pass


class FilmResponse(FilmBase):
    id: int
    is_active: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ListFilmResponse(BaseModel):
    films: List[FilmResponse]
    total_data: int

    class Config:
        from_attributes = True


class FilmPageableResponse(ListFilmResponse):
    total_pages: int

    class Config:
        from_attributes = True


class FilmSearch(FilmBase):
    pass
