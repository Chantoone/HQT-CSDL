import sys
import os

# Add the parent directory to the system path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from warehouse_models import DimFilm, DimTicket, DimGenre, DimCinema, DimShowtime, DimPromotion,FactRevenue,FactFilmRating,FactShowtimeFillRate,FactTicketAnalysis,FactPromotionAnalysis
from etl import *
from user.models.user import User
from auth_credential.models.auth_credential import AuthCredential
from role.models.role import Role
from user_role.models.user_role import UserRole
from bill.models.bill import Bill
from user_bill.models.user_bill import UserBill
from cinema.models.cinema import Cinema
from room.models.room import Room
from seat.models.seat import Seat
from film.models.film import Film
from food.models.food import Food
from ticket.models.ticket import Ticket
from genre.models.genre import Genre
from film_genre.models.film_genre import FilmGenre
from cinema.models.cinema import Cinema
from showtime.models.showtime import Showtime
from showtime_seat.models.showtime_seat import ShowtimeSeat
from promotion.models.promotion import Promotion
from rate.models.rate import Rate
from bill_prom.models.bill_prom import BillProm
src_engine = create_engine("postgresql://postgres:admin@localhost:5432/hqt_csdl")
dest_engine = create_engine("postgresql://postgres:admin@localhost:5432/warehouse")
SrcSession = sessionmaker(bind=src_engine)()
DestSession = sessionmaker(bind=dest_engine)()
print("Bắt đầu ETL DIM...")
etl_dim_film(SrcSession, DestSession, Film, DimFilm)
etl_dim_ticket(SrcSession, DestSession, Ticket, DimTicket)
etl_dim_genre(SrcSession, DestSession, Genre, DimGenre)
etl_dim_cinema(SrcSession, DestSession, Cinema, DimCinema)
etl_dim_showtime(SrcSession, DestSession, Showtime, DimShowtime)
etl_dim_promotion(SrcSession, DestSession, Promotion, DimPromotion)
print("Đã xong: dim_film")
etl_fact_ticket_analysis(SrcSession, DestSession, Ticket, Bill, FactTicketAnalysis)
print("Đã xong: fact_ticket_analysis")
etl_fact_film_rating(SrcSession, DestSession, Rate, FactFilmRating)
print("Đã xong: fact_film_rating")
etl_fact_revenue(SrcSession, DestSession, Bill, FactRevenue)
print("Đã xong: fact_revenue")
etl_fact_showtime_fillrate(SrcSession, DestSession, Showtime, FactShowtimeFillRate)
print("Đã xong: fact_showtime_fillrate")
etl_fact_promotion_analysis(SrcSession, DestSession, Bill, BillProm, FactPromotionAnalysis)