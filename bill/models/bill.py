from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    payment_method = Column(String, nullable=False)
    payment_time = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    staff = relationship("User", back_populates="bill", passive_deletes=True)
    food = relationship("Food", back_populates="bill", passive_deletes=True)
    ticket = relationship("Ticket", back_populates="bill", passive_deletes=True)
    bill_prom = relationship("BillProm", back_populates="bill", passive_deletes=True)
    user_bill = relationship("UserBill", back_populates="bill", passive_deletes=True)