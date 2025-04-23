from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from warehouse.etl import (
    etl_fact_ticket_analysis_incremental,
    etl_fact_film_rating_incremental,
    etl_fact_revenue_incremental,
    etl_fact_showtime_fillrate_incremental,
    etl_fact_promotion_analysis_incremental,
)
from warehouse.etl_metadata.models.etl_metadata import ETLMetadata
from warehouse.warehouse_models import *
from ticket.models.ticket import Ticket
from bill.models.bill import Bill
from rate.models.rate import Rate
from showtime.models.showtime import Showtime
from bill_prom.models.bill_prom import BillProm

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os


load_dotenv()

def send_email(subject: str, body: str):
    host = os.getenv("EMAIL_HOST")
    port = int(os.getenv("EMAIL_PORT", 587))
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    msg = MIMEMultipart()
    msg["From"] = username
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            print("✅ Email đã được gửi thành công.")
    except Exception as e:
        print(f"❌ Gửi email lỗi: {str(e)}")


# Kết nối DB
src_engine = create_engine("postgresql://postgres:123456@localhost:5432/cinema")
dest_engine = create_engine("postgresql://postgres:123456@localhost:5432/warehouse")
SrcSession = sessionmaker(bind=src_engine)
DestSession = sessionmaker(bind=dest_engine)

def run_incremental_etl():
    print("🔄 Running incremental ETL...")

    src_session = SrcSession()
    dest_session = DestSession()

    etl_fact_ticket_analysis_incremental(src_session, dest_session, Ticket, Bill, FactTicketAnalysis, ETLMetadata)
    etl_fact_film_rating_incremental(src_session, dest_session, Rate, FactFilmRating, ETLMetadata)
    etl_fact_revenue_incremental(src_session, dest_session, Bill, FactRevenue, ETLMetadata)
    etl_fact_showtime_fillrate_incremental(src_session, dest_session, Showtime, FactShowtimeFillRate, ETLMetadata)
    etl_fact_promotion_analysis_incremental(src_session, dest_session, Bill, BillProm, FactPromotionAnalysis, ETLMetadata)

    print("✅ ETL hoàn tất!")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Chạy mỗi 1 giờ (bạn có thể đổi sang minutes=30, hoặc daily, weekly...)
    scheduler.add_job(run_incremental_etl, 'interval', hours=1)
    scheduler.start()
