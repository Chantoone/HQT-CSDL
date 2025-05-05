from sqlalchemy import create_engine
from mart.mart_model import Base

# Khởi tạo engine
engine = create_engine("postgresql://postgres:123456@localhost:5432/mart")

#
# Base.metadata.create_all(engine)
