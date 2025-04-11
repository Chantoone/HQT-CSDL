from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    bill_id = Column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)
    showtime_seat_id = Column(Integer, ForeignKey("showtime_seats.id", ondelete="CASCADE"), nullable=False)
    
    showtime_seat = relationship("ShowtimeSeat", back_populates="ticket", passive_deletes=True)
    bill = relationship("Bill", back_populates="ticket", passive_deletes=True)
