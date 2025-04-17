from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class DimPaymentMethod(Base):
    __tablename__ = "dim_payment_method"

    payment_method_id = Column(Integer, primary_key=True)
    method_name = Column(String, nullable=False)


class DimDate(Base):
    __tablename__ = "dim_date"

    date_id = Column(Date, primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    weekday = Column(String, nullable=False)
    is_weekend = Column(Boolean, nullable=False)


class DimTime(Base):
    __tablename__ = "dim_time"

    time_id = Column(Integer, primary_key=True)  # hour * 60 + minute
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, nullable=False)
    period = Column(String, nullable=False)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class DimCinema(Base):
    __tablename__ = "dim_cinema"

    cinema_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class DimFilm(Base):
    __tablename__ = "dim_film"

    film_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)
    release_date = Column(Date)
    author = Column(String)
    actors = Column(String)
    director = Column(String)
    status = Column(String)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class DimGenre(Base):
    __tablename__ = "dim_genre"

    genre_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class DimTicket(Base):
    __tablename__ = "dim_ticket"

    ticket_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class DimPromotion(Base):
    __tablename__ = "dim_promotion"

    promotion_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class DimShowtime(Base):
    __tablename__ = "dim_showtime"

    showtime_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    film_id = Column(Integer)
    room_id = Column(Integer)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class DimPurchaseType(Base):
    __tablename__ = "dim_purchase_type"

    purchase_type_id = Column(Integer, primary_key=True)
    type_name = Column(String, nullable=False)
    description = Column(String)
    etl_loaded_at = Column(DateTime, server_default=func.now())


# ===== FACTS =====

class FactRevenue(Base):
    __tablename__ = "fact_revenue"

    bill_id = Column(Integer, primary_key=True)
    date_id = Column(Date, ForeignKey("dim_date.date_id"))
    time_id = Column(Integer, ForeignKey("dim_time.time_id"))
    film_id = Column(Integer, ForeignKey("dim_film.film_id"))
    cinema_id = Column(Integer, ForeignKey("dim_cinema.cinema_id"))
    value = Column(Integer, nullable=False)
    etl_loaded_at = Column(DateTime, server_default=func.now())

    payment_method_id = Column(Integer, ForeignKey("dim_payment_method.payment_method_id"))

    purchase_type_id = Column(Integer, ForeignKey("dim_purchase_type.purchase_type_id"))


class FactTicketAnalysis(Base):
    __tablename__ = "fact_ticket_analysis"

    ticket_id = Column(Integer, primary_key=True)
    bill_id = Column(Integer)
    date_id = Column(Date, ForeignKey("dim_date.date_id"))
    time_id = Column(Integer, ForeignKey("dim_time.time_id"))
    price = Column(Integer, nullable=False)
    etl_loaded_at = Column(DateTime, server_default=func.now())

    payment_method_id = Column(Integer, ForeignKey("dim_payment_method.payment_method_id"))

    purchase_type_id = Column(Integer, ForeignKey("dim_purchase_type.purchase_type_id"))


class FactFilmRating(Base):
    __tablename__ = "fact_film_rating"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    film_id = Column(Integer, ForeignKey("dim_film.film_id"))
    date_id = Column(Date, ForeignKey("dim_date.date_id"))
    point = Column(Integer, nullable=False)
    detail = Column(String)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class FactShowtimeFillRate(Base):
    __tablename__ = "fact_showtime_fillrate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_id = Column(Date, ForeignKey("dim_date.date_id"))
    film_id = Column(Integer, ForeignKey("dim_film.film_id"))
    showtime_id = Column(Integer, ForeignKey("dim_showtime.showtime_id"))
    total_seats = Column(Integer, nullable=False)
    booked_seats = Column(Integer, nullable=False)
    fill_rate = Column(Float, nullable=False)
    etl_loaded_at = Column(DateTime, server_default=func.now())


class FactPromotionAnalysis(Base):
    __tablename__ = "fact_promotion_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_id = Column(Integer)
    date_id = Column(Date, ForeignKey("dim_date.date_id"))
    promotion_used = Column(Boolean, nullable=False)
    point = Column(Integer, nullable=False)

class FactFilmGenre(Base):
    __tablename__ = "fact_film_genre"

    film_id = Column(Integer, ForeignKey("dim_film.film_id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("dim_genre.genre_id"), primary_key=True)
    point = Column(Integer, nullable=False)