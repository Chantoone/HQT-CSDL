from sqlalchemy import Boolean, Column, Integer, String, text, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    release_date = Column(Date, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    poster_path = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))