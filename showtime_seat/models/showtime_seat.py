from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base
from seat.models.seat import Seat
from showtime.models.showtime import Showtime


class ShowtimeSeat(Base):
    __tablename__ = "showtime_seats"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    seat_status = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    showtime_id = Column(Integer, ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False)
    
    seat = relationship("Seat", back_populates="showtime_seat", passive_deletes=True)
    showtime = relationship("Showtime", back_populates="showtime_seat", passive_deletes=True)
    ticket = relationship("Ticket", back_populates="showtime_seat", passive_deletes=True)
