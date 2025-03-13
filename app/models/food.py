from sqlalchemy import Boolean, Column, Integer, String, text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))