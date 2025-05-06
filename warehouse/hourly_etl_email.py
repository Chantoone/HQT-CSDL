import logging
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import các module cần thiết của dự án
import sys
sys.path.append('d:\\WORKSPACE\\HQT-CSDL')  # Đảm bảo import được các module từ thư mục gốc
from warehouse.database import engine as warehouse_engine
from configs.database import engine as source_engine
from warehouse.etl import (
    etl_fact_ticket_analysis_incremental,
    etl_fact_film_rating_incremental,
    etl_fact_revenue_incremental,
    etl_fact_showtime_fillrate_incremental,
    etl_fact_promotion_analysis_incremental,
    get_last_loaded_time,
    update_last_loaded_time
)

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("warehouse/etl_hourly.log", encoding='utf-8'),  # Thêm encoding='utf-8'
        logging.StreamHandler(sys.stdout)  # StreamHandler mặc định dùng encoding của terminal
    ]
)
logger = logging.getLogger("hourly_etl")

load_dotenv()  # Tải biến môi trường từ file .env
# Cấu hình email
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
EMAIL_USER="danhhieu123ns@gmail.com"
EMAIL_PASSWORD="macx viyz tuwi vjzo"
EMAIL_TO="ca.trantu@gmail.com"

def get_models():
    """
    Import các model từ ứng dụng chính và warehouse để phục vụ ETL
    """
    # Import các model nguồn (source)
    from bill.models.bill import Bill as BillSrc
    from ticket.models.ticket import Ticket as TicketSrc
    from showtime_seat.models.showtime_seat import ShowtimeSeat as ShowtimeSeatSrc
    from showtime.models.showtime import Showtime as ShowtimeSrc
    from room.models.room import Room as RoomSrc
    from bill_prom.models.bill_prom import BillProm as BillPromSrc
    from film.models.film import Film as FilmSrc
    from genre.models.genre import Genre as GenreSrc
    from cinema.models.cinema import Cinema as CinemaSrc
    from promotion.models.promotion import Promotion as PromotionSrc
    from rate.models.rate import Rate as RateSrc

    # Import các model đích (warehouse)
    from warehouse.warehouse_models import (
        DimFilm, DimTicket, DimGenre, DimCinema, DimShowtime, DimPromotion,
        FactTicketAnalysis, FactFilmRating, FactRevenue, FactShowtimeFillRate, FactPromotionAnalysis
    )

    return {
        # Source models
        'BillSrc': BillSrc,
        'TicketSrc': TicketSrc,
        'ShowtimeSeatSrc': ShowtimeSeatSrc,
        'ShowtimeSrc': ShowtimeSrc,
        'RoomSrc': RoomSrc,
        'BillPromSrc': BillPromSrc,
        'FilmSrc': FilmSrc,
        'GenreSrc': GenreSrc,
        'CinemaSrc': CinemaSrc,
        'PromotionSrc': PromotionSrc,
        'RateSrc': RateSrc,

        # Warehouse models
        'DimFilm': DimFilm,
        'DimTicket': DimTicket,
        'DimGenre': DimGenre,
        'DimCinema': DimCinema,
        'DimShowtime': DimShowtime,
        'DimPromotion': DimPromotion,
        'FactTicketAnalysis': FactTicketAnalysis,
        'FactFilmRating': FactFilmRating,
        'FactRevenue': FactRevenue,
        'FactShowtimeFillRate': FactShowtimeFillRate,
        'FactPromotionAnalysis': FactPromotionAnalysis
    }

def generate_etl_report(session_dest):
    """
    Tạo báo cáo ETL với các thống kê từ kho dữ liệu
    """
    report = []
    report.append("<h2>ETL Report - Dữ liệu 1 giờ qua</h2>")
    report.append(f"<p>Thời gian chạy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")

    # Lấy thời điểm 1 giờ trước
    one_hour_ago = datetime.now() - timedelta(days=30)
    report.append(f"<p>Dữ liệu từ: {one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')}</p>")

    try:
        # Thống kê từ các bảng fact
        models = get_models()

        # 1. Số lượng vé bán ra trong 1 giờ qua
        ticket_count = session_dest.query(func.count(models['FactTicketAnalysis'].ticket_id)).filter(
            models['FactTicketAnalysis'].date_id >= one_hour_ago.date()
        ).scalar() or 0
        report.append(f"<p><b>Số vé bán ra:</b> {ticket_count}</p>")

        # 2. Doanh thu trong 1 giờ qua
        revenue = session_dest.query(func.sum(models['FactRevenue'].value)).filter(
            models['FactRevenue'].date_id >= one_hour_ago.date()
        ).scalar() or 0
        report.append(f"<p><b>Tổng doanh thu:</b> {revenue:,.0f} VND</p>")

        # 3. Số lượng đánh giá phim mới
        rating_count = session_dest.query(func.count(models['FactFilmRating'].user_id)).filter(
            models['FactFilmRating'].date_id >= one_hour_ago.date()
        ).scalar() or 0
        report.append(f"<p><b>Số đánh giá phim:</b> {rating_count}</p>")

        # 4. Tỉ lệ lấp đầy trung bình của các suất chiếu
        fill_rate_avg = session_dest.query(func.avg(models['FactShowtimeFillRate'].fill_rate)).filter(
            models['FactShowtimeFillRate'].date_id >= one_hour_ago.date()
        ).scalar() or 0
        report.append(f"<p><b>Tỉ lệ lấp đầy trung bình:</b> {fill_rate_avg:.2%}</p>")

        # 5. Số lượng hóa đơn sử dụng khuyến mãi
        promo_count = session_dest.query(func.count(models['FactPromotionAnalysis'].bill_id)).filter(
            models['FactPromotionAnalysis'].date_id >= one_hour_ago.date(),
            models['FactPromotionAnalysis'].promotion_used == True
        ).scalar() or 0
        report.append(f"<p><b>Số hóa đơn dùng khuyến mãi:</b> {promo_count}</p>")

        # 6. Top 5 phim bán chạy nhất
        top_films_query = """
        SELECT df.title, COUNT(fr.film_id) AS ticket_count
        FROM fact_revenue fr
        JOIN dim_film df ON fr.film_id = df.film_id
        WHERE fr.date_id >= :one_hour_ago
        GROUP BY df.title
        ORDER BY ticket_count DESC
        LIMIT 5
        """

        top_films = session_dest.execute(text(top_films_query), {"one_hour_ago": one_hour_ago.date()}).fetchall()

        if top_films:
            report.append("<h3>Top 5 phim bán chạy:</h3>")
            report.append("<ol>")
            for film in top_films:
                report.append(f"<li>{film[0]} - {film[1]} vé</li>")
            report.append("</ol>")
        else:
            report.append("<p>Không có dữ liệu về phim bán chạy trong 1 thang qua</p>")

    except Exception as e:
        logger.error(f"Lỗi khi tạo báo cáo ETL: {e}")
        report.append(f"<p style='color: red'>Có lỗi khi tạo báo cáo: {str(e)}</p>")

    return "<br>".join(report)

def send_email(subject, html_content):
    """
    Gửi email với nội dung HTML
    """
    try:
        # Tạo message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject

        # Thêm nội dung HTML
        msg.attach(MIMEText(html_content, 'html', 'utf-8')) # Thêm encoding='utf-8'

        # Thiết lập kết nối SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        # Gửi email
        server.send_message(msg)
        server.quit()

        logger.info(f"Đã gửi email báo cáo ETL thành công đến {EMAIL_TO}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi gửi email: {e}")
        return False

def run_hourly_etl():
    """
    Chạy ETL cho dữ liệu 1 giờ trước và gửi báo cáo qua email
    """
    # Thiết lập phiên làm việc
    Session_src = sessionmaker(bind=source_engine)
    Session_dest = sessionmaker(bind=warehouse_engine)

    session_src = Session_src()
    session_dest = Session_dest()

    start_time = datetime.now()
    logger.info(f"Bắt đầu ETL cho dữ liệu 1 giờ trước ({start_time})")

    # Tải các model
    models = get_models()

    # Biến lưu trạng thái ETL
    etl_success = True
    etl_errors = []

    try:
        # Thiết lập thời gian bắt đầu (1 giờ trước)
        one_hour_ago = datetime.now() - timedelta(hours=1)

        # Ghi đè last_loaded_time cho các bảng fact để chỉ xử lý dữ liệu 1 giờ trước
        tables = ["fact_ticket_analysis", "fact_film_rating", "fact_revenue",
                  "fact_showtime_fillrate", "fact_promotion_analysis"]

        for table in tables:
            update_last_loaded_time(session_dest, table, one_hour_ago)

        # Chạy các hàm ETL cho từng bảng fact
        logger.info("Bắt đầu ETL cho FactTicketAnalysis")
        etl_fact_ticket_analysis_incremental(
            session_src, session_dest,
            models["TicketSrc"], models["BillSrc"], models["FactTicketAnalysis"]
        )

        logger.info("Bắt đầu ETL cho FactFilmRating")
        etl_fact_film_rating_incremental(
            session_src, session_dest,
            models["RateSrc"], models["FactFilmRating"]
        )

        logger.info("Bắt đầu ETL cho FactRevenue")
        etl_fact_revenue_incremental(
            session_src, session_dest,
            models["BillSrc"], models["TicketSrc"], models["ShowtimeSeatSrc"],
            models["ShowtimeSrc"], models["RoomSrc"], models["FactRevenue"]
        )

        logger.info("Bắt đầu ETL cho FactShowtimeFillRate")
        etl_fact_showtime_fillrate_incremental(
            session_src, session_dest,
            models["ShowtimeSrc"], models["ShowtimeSeatSrc"], models["TicketSrc"],
            models["FactShowtimeFillRate"]
        )

        logger.info("Bắt đầu ETL cho FactPromotionAnalysis")
        etl_fact_promotion_analysis_incremental(
            session_src, session_dest,
            models["BillSrc"], models["BillPromSrc"], models["FactPromotionAnalysis"]
        )

    except Exception as e:
        etl_success = False
        error_msg = f"Lỗi khi thực hiện ETL: {str(e)}"
        logger.error(error_msg)
        etl_errors.append(error_msg)
    finally:
        # Tạo báo cáo
        report_html = generate_etl_report(session_dest)

        if not etl_success:
            report_html += "<h3 style='color: red'>Lỗi trong quá trình ETL:</h3>"
            report_html += "<ul>"
            for error in etl_errors:
                report_html += f"<li>{error}</li>"
            report_html += "</ul>"

        # Gửi báo cáo qua email
        subject = f"ETL Report - {datetime.now().strftime('%Y-%m-%d %H:%M')} - {'SUCCESS' if etl_success else 'ERROR'}"
        send_email(subject, report_html)

        # Đóng phiên làm việc
        session_src.close()
        session_dest.close()

        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Kết thúc ETL ({end_time}). Thời gian thực hiện: {duration}")

        return etl_success

if __name__ == "__main__":
    run_hourly_etl()