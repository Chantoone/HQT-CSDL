import schedule
import time
import logging
from datetime import datetime
from warehouse.hourly_etl_email import run_hourly_etl

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("warehouse/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("etl_scheduler")

def job():
    """
    Công việc chạy ETL hàng giờ
    """
    logger.info(f"Đã bắt đầu chạy ETL theo lịch trình ({datetime.now()})")
    try:
        success = run_hourly_etl()
        status = "thành công" if success else "thất bại"
        logger.info(f"ETL hàng giờ đã hoàn thành với trạng thái: {status}")
    except Exception as e:
        logger.error(f"Lỗi không mong muốn khi chạy ETL: {e}")

def run_scheduler():
    """
    Khởi động và duy trì lịch trình ETL
    """
    # Lên lịch chạy ETL mỗi giờ
    schedule.every().hour.do(job)
    
    # Hiển thị thông tin ban đầu
    logger.info("Lịch trình ETL đã được khởi tạo")
    logger.info("ETL sẽ chạy mỗi giờ một lần")
    
    # Có thể chạy ETL ngay lập tức khi khởi động
    logger.info("Chạy ETL lần đầu...")
    job()
    
    # Vòng lặp vô hạn để duy trì lịch trình
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Kiểm tra mỗi phút
        except KeyboardInterrupt:
            logger.info("Lịch trình ETL đã bị dừng bởi người dùng")
            break
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp lịch trình: {e}")
            # Tiếp tục vòng lặp bất chấp lỗi
            time.sleep(300)  # Nghỉ 5 phút nếu có lỗi

if __name__ == "__main__":
    run_scheduler()