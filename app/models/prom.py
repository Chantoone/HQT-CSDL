from sqlalchemy import Boolean, Column, Integer, String, text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Prom(Base):
    __tablename__ = "proms"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    staff_id = Column(Integer, nullable=False)
    staff = relationship("User", back_populates="prom", passive_deletes=True)