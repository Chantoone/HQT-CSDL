from sqlalchemy import Boolean, Column, Integer, String, text, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from configs.database import Base


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(255), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    film_genres = relationship("FilmGenre", back_populates="genre")