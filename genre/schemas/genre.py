from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class GenreBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class GenreCreate(GenreBase):
    pass


class GenreUpdate(GenreBase):
    name: Optional[str] = None


class GenreResponse(GenreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ListGenreResponse(BaseModel):
    genres: List[GenreResponse]

    class Config:
        from_attributes = True


class GenrePageableResponse(BaseModel):
    total_data: int
    total_pages: int
    genres: List[GenreResponse]

    class Config:
        from_attributes = True


class GenreSearch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
