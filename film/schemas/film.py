from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Optional


class GenreBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


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

    @property
    def genres(self):
        return [fg.genre for fg in self.film_genres]
    

class FilmCreate(FilmBase):
    title: str
    status: str
    genre_ids: List[int] = []


class FilmUpdate(FilmBase):
    genre_ids: Optional[List[int]] = None


class FilmResponse(FilmBase):
    id: int
    is_active: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FILMRESPONSE(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration: Optional[int]
    release_date: Optional[date]
    author: Optional[str]
    poster_path: Optional[str]
    status: Optional[str]
    actors: Optional[str]
    director: Optional[str]
    created_at: datetime
    is_active: Optional[bool] = True
    genres: Optional[List[GenreBase]] = []  # Explicitly define genres as a field

    class Config:
        from_attributes = True


class ListFilmResponse(BaseModel):
    films: List[FILMRESPONSE]
    total_data: int

    class Config:
        from_attributes = True


class FilmPageableResponse(ListFilmResponse):
    total_pages: int

    class Config:
        from_attributes = True


class FilmSearch(FilmBase):
    pass






