from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class BillProm(Base):
    __tablename__ = "bill_proms"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)
    prom_id = Column(Integer, ForeignKey("promotions.id", ondelete="CASCADE"), nullable=False)

    bill = relationship("Bill", back_populates="bill_prom", passive_deletes=True)
    prom = relationship("Promotion", back_populates="bill_prom", passive_deletes=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))