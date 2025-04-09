from sqlalchemy import Boolean, Column, Integer, String, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    seat_number = Column(String, nullable=False)
    detail = Column(String, nullable=True)
    is_booked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    room = relationship("Room", back_populates="seat", passive_deletes=True)
