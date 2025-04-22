from fastapi import APIRouter, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime
from warehouse.etl import *
from ticket.models.ticket import Ticket
from bill.models.bill import Bill
from rate.models.rate import Rate
from showtime.models.showtime import Showtime
from bill_prom.models.bill_prom import BillProm
from warehouse.warehouse_models import *
from warehouse.etl_metadata.models.etl_metadata import ETLMetadata


router = APIRouter()

@router.post("/etl/run-incremental")
def run_incremental_etl():
    print("🔄 Running incremental ETL...")
    src_engine = create_engine("postgresql://postgres:admin@localhost:5432/hqt_csdl")
    dest_engine = create_engine("postgresql://postgres:admin@localhost:5432/warehouse")
    src_session = sessionmaker(bind=src_engine)
    dest_session = sessionmaker(bind=dest_engine)

    start_time = datetime.now()
    try:
        etl_fact_ticket_analysis_incremental(src_session, dest_session, Ticket, Bill, FactTicketAnalysis, ETLMetadata)
        etl_fact_film_rating_incremental(src_session, dest_session, Rate, FactFilmRating, ETLMetadata)
        etl_fact_revenue_incremental(src_session, dest_session, Bill, FactRevenue, ETLMetadata)
        etl_fact_showtime_fillrate_incremental(src_session, dest_session, Showtime, FactShowtimeFillRate, ETLMetadata)
        etl_fact_promotion_analysis_incremental(src_session, dest_session, Bill, BillProm, FactPromotionAnalysis, ETLMetadata)

        duration = (datetime.now() - start_time).total_seconds()
        subject = "✅ ETL Incremental - Thành công"
        body = f"ETL chạy thành công lúc {datetime.now().strftime('%H:%M:%S')}.\nThời gian chạy: {duration:.2f} giây."
        # send_email(subject, body)

    except Exception as e:
        subject = "❌ ETL Incremental - Lỗi"
        body = f"ETL lỗi lúc {datetime.now().strftime('%H:%M:%S')}!\nChi tiết lỗi:\n{str(e)}"
        # send_email(subject, body)
        print(body)
