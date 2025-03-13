from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    price = Column(Integer, nullable=False)
    suat_chieu_id = Column(Integer, nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), ondelete="CASCADE", nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), ondelete="CASCADE", nullable=False)
    cinema_id = Column(Integer, ForeignKey("cinemas.id"), ondelete="CASCADE", nullable=False)

    suat_chieu = relationship("SuatChieu", back_populates="tickets", passive_deletes=True)
    seat = relationship("Seat", back_populates="tickets", passive_deletes=True)
    room = relationship("Room", back_populates="tickets", passive_deletes=True)
    cinema = relationship("Cinema", back_populates="tickets", passive_deletes=True)
