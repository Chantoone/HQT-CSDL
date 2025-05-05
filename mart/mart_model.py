from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class MartRevenueByMonth(Base):
    __tablename__ = "mart_revenue_by_month"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_revenue = Column(Integer, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class MartTopFilmRevenue(Base):
    __tablename__ = "mart_top_film_revenue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    film_id = Column(Integer, nullable=False)
    film_title = Column(String, nullable=False)
    total_revenue = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
class MartFilmRatingSummary(Base):
    __tablename__ = "mart_film_rating_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    film_id = Column(Integer, nullable=False)
    film_title = Column(String, nullable=False)
    avg_rating = Column(Float, nullable=False)
    total_reviews = Column(Integer, nullable=False)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
class MartShowtimeFillRate(Base):
    __tablename__ = "mart_showtime_fill_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    showtime_id = Column(Integer, nullable=False)
    showtime_name = Column(String, nullable=False)
    avg_fill_rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
class MartRevenueByCinema(Base):
    __tablename__ = "mart_revenue_by_cinema"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cinema_id = Column(Integer, nullable=False)
    cinema_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_revenue = Column(Integer, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
class MartPaymentMethodMonthly(Base):
    __tablename__ = "mart_payment_method_monthly"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method_id = Column(Integer, nullable=False)
    payment_method_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    total_revenue = Column(Integer, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
