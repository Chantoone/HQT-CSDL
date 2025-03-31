from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

from film.schemas.film import FilmResponse
from genre.schemas.genre import GenreResponse


class FilmGenreBase(BaseModel):
    genre_id: int
    film_id: int

    class Config:
        from_attributes = True


class FilmGenreCreate(FilmGenreBase):
    pass


class FilmGenreUpdate(FilmGenreBase):
    genre_id: Optional[int] = None
    film_id: Optional[int] = None


class FilmGenreResponse(BaseModel):
    id: int
    created_at: datetime
    genre: GenreResponse
    film: FilmResponse

    class Config:
        from_attributes = True


class ListFilmGenreResponse(BaseModel):
    film_genres: List[FilmGenreResponse]
    total_data: int

    class Config:
        from_attributes = True


class FilmGenrePageableResponse(BaseModel):
    film_genres: List[FilmGenreResponse]
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class FilmGenreSearch(BaseModel):
    genre_id: Optional[int] = None
    film_id: Optional[int] = None


class ListFilmResponse(BaseModel):
    films: List[FilmResponse]
    total_data: int

    class Config:
        from_attributes = True