from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    detail = Column(String, nullable=True)
    capacity = Column(Integer, nullable=False)
    cinema_id = Column(Integer, ForeignKey("cinemas.id"), ondelete="CASCADE", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    cinema = relationship("Cinema", back_populates="room", passive_deletes=True)