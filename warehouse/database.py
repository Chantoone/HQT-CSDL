from sqlalchemy import create_engine
from warehouse_models import Base

# Khởi tạo engine
engine = create_engine("postgresql://postgres:123456@localhost:5432/warehouse")

# Tạo tất cả bảng
# Base.metadata.create_all(engine)
