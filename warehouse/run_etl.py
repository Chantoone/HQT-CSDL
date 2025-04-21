import sys
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# --- Cấu hình logging cơ bản ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory to the system path to resolve module imports
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from warehouse_models import *
    from user.models.user import User
    from auth_credential.models.auth_credential import AuthCredential
    from role.models.role import Role
    from user_role.models.user_role import UserRole
    from cinema.models.cinema import Cinema
    from room.models.room import Room
    from seat.models.seat import Seat
    from film.models.film import Film
    from food.models.food import Food
    from ticket.models.ticket import Ticket
    from bill.models.bill import Bill
    from user_bill.models.user_bill import UserBill
    from genre.models.genre import Genre
    from film_genre.models.film_genre import FilmGenre
    from showtime.models.showtime import Showtime
    from showtime_seat.models.showtime_seat import ShowtimeSeat
    from promotion.models.promotion import Promotion
    from rate.models.rate import Rate
    from bill_prom.models.bill_prom import BillProm
    from etl import *

except ImportError as e:
    logging.error(f"Lỗi import module: {e}")
    sys.exit(1) 

# --- Khối chính thực thi ETL ---
if __name__ == "__main__":
    SrcSession = None
    DestSession = None
    try:
        src_engine = create_engine("postgresql://postgres:123456@localhost:5432/cinema")
        dest_engine = create_engine("postgresql://postgres:123456@localhost:5432/warehouse")

        SrcSessionMaker = sessionmaker(bind=src_engine)
        DestSessionMaker = sessionmaker(bind=dest_engine)
        SrcSession = SrcSessionMaker()
        DestSession = DestSessionMaker()

        logging.info("Kết nối cơ sở dữ liệu thành công.")
        logging.info("Bắt đầu quá trình ETL...")

        # # --- Thực thi ETL cho các bảng DIM ---
        # logging.info("--- Bắt đầu ETL DIM ---")
        # etl_dim_film(SrcSession, DestSession, Film, DimFilm)
        # etl_dim_ticket(SrcSession, DestSession, Ticket, DimTicket)
        # etl_dim_genre(SrcSession, DestSession, Genre, DimGenre)
        # etl_dim_cinema(SrcSession, DestSession, Cinema, DimCinema)
        # etl_dim_showtime(SrcSession, DestSession, Showtime, DimShowtime)
        # etl_dim_promotion(SrcSession, DestSession, Promotion, DimPromotion)
        # logging.info("--- Hoàn thành ETL DIM ---")


        # --- Thực thi ETL cho các bảng FACT ---
        logging.info("--- Bắt đầu ETL FACT ---")
        # etl_fact_ticket_analysis(SrcSession, DestSession, Ticket, Bill, FactTicketAnalysis)
        etl_fact_film_rating_optimized(SrcSession, DestSession, Rate, FactFilmRating)
        # etl_fact_revenue_optimized_v4(
        #     SrcSession, DestSession,
        #     Ticket, # Truyền TicketSrc là model chính
        #     Bill, ShowtimeSeat, Showtime, Room, # Các model phụ trợ
        #     FactRevenue
        # )
        # etl_fact_showtime_fillrate_optimized_v2(SrcSession, DestSession, Showtime, ShowtimeSeat, FactShowtimeFillRate)
        # etl_fact_promotion_analysis_optimized(SrcSession, DestSession, Bill, BillProm, FactPromotionAnalysis)
        logging.info("--- Hoàn thành ETL FACT ---")

        logging.info("Quá trình ETL hoàn tất thành công!")

    except SQLAlchemyError as db_conn_error:
        logging.error(f"Lỗi kết nối hoặc khởi tạo session SQLAlchemy: {db_conn_error}")

    except Exception as general_error:
        logging.error(f"Lỗi không xác định xảy ra trong quá trình ETL chính: {general_error}")
        if DestSession:
            try:
                DestSession.rollback()
                logging.info("Đã rollback session đích do lỗi.")
            except Exception as rollback_err:
                logging.error(f"Lỗi khi thực hiện rollback session đích: {rollback_err}")
    finally:
        if SrcSession:
            try:
                SrcSession.close()
                logging.info("Đã đóng session nguồn.")
            except Exception as close_err:
                logging.error(f"Lỗi khi đóng session nguồn: {close_err}")
        if DestSession:
            try:
                DestSession.close()
                logging.info("Đã đóng session đích.")
            except Exception as close_err:
                logging.error(f"Lỗi khi đóng session đích: {close_err}")
                