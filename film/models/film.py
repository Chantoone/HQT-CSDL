from sqlalchemy import Boolean, Column, Integer, String, text, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from configs.database import Base


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    release_date = Column(Date, nullable=True)
    author = Column(String, nullable=True)
    poster_path = Column(String, nullable=True)
    status = Column(String, nullable=True)
    actors = Column(String, nullable=True)
    director = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    film_genres = relationship("FilmGenre", back_populates="film", passive_deletes=True)
    rates = relationship("Rate", back_populates="film", passive_deletes=True)
    showtimes = relationship("Showtime", back_populates="film", passive_deletes=True)