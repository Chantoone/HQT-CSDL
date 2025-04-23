from sqlalchemy import Column, String, DateTime
from configs.database import Base


class ETLMetadata(Base):
    __tablename__ = "etl_metadata"

    table_name = Column(String, primary_key=True)
    last_loaded_time = Column(DateTime)
