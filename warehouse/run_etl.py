from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from warehouse_models import DimFilm, DimTicket, DimGenre, DimCinema, DimShowtime, DimPromotion,FactRevenue,FactFilmRating,FactShowtimeFillRate,FactTicketAnalysis,FactPromotionAnalysis
from etl import *
from bill.models.bill import Bill
from film.models.film import Film
from ticket.models.ticket import Ticket
from genre.models.genre import Genre
from cinema.models.cinema import Cinema
from showtime.models.showtime import Showtime
from promotion.models.promotion import Promotion
from rate.models.rate import Rate
from bill_prom.models.bill_prom import BillProm
src_engine = create_engine("postgresql://postgres:123456@localhost:5432/cinema")
dest_engine = create_engine("postgresql://postgres:123456@localhost:5432/warehouse")
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