from sqlalchemy import Column, Integer, String, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Showtime(Base):
    __tablename__ = "showtimes"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    film = relationship("Film", back_populates="showtime", passive_deletes=True)
    room = relationship("Room", back_populates="showtime", passive_deletes=True)
    ticket = relationship("Ticket", back_populates="showtime", passive_deletes=True)