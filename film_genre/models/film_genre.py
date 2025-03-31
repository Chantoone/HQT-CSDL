from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from configs.database import Base


class FilmGenre(Base):
    __tablename__ = "film_genres"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    film_id = Column(Integer, ForeignKey("films.id"), nullable=False, index=True)
    genre = relationship("Genre", back_populates="film_genres")
    film = relationship("Film", back_populates="film_genres")