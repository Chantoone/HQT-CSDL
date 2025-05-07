from sqlalchemy import create_engine
from mart.mart_model import Base
from sqlalchemy.orm import sessionmaker
# Khởi tạo engine
engine = create_engine("postgresql://postgres:123456@localhost:5432/mart")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
def get_db():
    db=SessionLocal()
    try:

        yield db
    finally:
        db.close()
Base.metadata.create_all(engine)
