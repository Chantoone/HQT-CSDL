from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    point = Column(Integer, nullable=False, default=0)
    detail = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), ondelete="CASCADE", nullable=False)
    film_id = Column(Integer, ForeignKey("films.id"), ondelete="CASCADE", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    rate = relationship("Rate", back_populates="user", passive_deletes=True)