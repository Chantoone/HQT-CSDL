from sqlalchemy import Boolean, Column, Integer, String, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Cinema(Base):
    __tablename__ = "cinemas"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
