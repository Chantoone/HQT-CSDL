from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    staff = relationship("User", back_populates="promotion", passive_deletes=True)
    bill_prom = relationship("BillProm", back_populates="prom", passive_deletes=True)