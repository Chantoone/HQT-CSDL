from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class FilmBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    release_date: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    poster_path: Optional[str] = None
    is_active: Optional[bool] = None


class FilmCreate(FilmBase):
    title: str


class FilmUpdate(FilmBase):
    pass


class FilmResponse(FilmBase):
    id: int
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
