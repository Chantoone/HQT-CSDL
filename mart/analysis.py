from mart_model import *
from warehouse.warehouse_models import *
from sqlalchemy import create_engine, func, case
from sqlalchemy.orm import sessionmaker
import logging

# Cấu hình ghi log UTF-8 có BOM để xem được tiếng Việt
logging.basicConfig(
    filename='etl_mart.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8-sig'
)

# Kết nối đến warehouse DB
warehouse_engine = create_engine("postgresql://postgres:123456@localhost:5432/warehouse")
WarehouseSession = sessionmaker(bind=warehouse_engine)
warehouse_session = WarehouseSession()

# Kết nối đến mart DB
mart_engine = create_engine("postgresql://postgres:123456@localhost:5432/mart")
MartSession = sessionmaker(bind=mart_engine)
mart_session = MartSession()

def load_to_revenue_mart(warehouse_session, mart_session):
    try:
        logging.info("Bắt đầu truy vấn dữ liệu từ warehouse...")
        results = (
            warehouse_session.query(
                DimDate.year,
                DimDate.month,
                func.sum(FactRevenue.value).label("total_revenue")
            )
            .join(FactRevenue, DimDate.date_id == FactRevenue.date_id)
            .group_by(DimDate.year, DimDate.month)
            .order_by(DimDate.year, DimDate.month)
            .all()
        )

        BATCH_SIZE = 1000
        buffer = []
        inserted = 0

        logging.info(f"Truy vấn thành công {len(results)} bản ghi. Bắt đầu load theo batch...")

        for year, month, revenue in results:
            record = MartRevenueByMonth(
                year=year,
                month=month,
                total_revenue=revenue
            )
            buffer.append(record)
            inserted += 1

            if len(buffer) >= BATCH_SIZE:
                try:
                    mart_session.bulk_save_objects(buffer)
                    mart_session.commit()
                    logging.info(f"Đã ghi batch {len(buffer)} bản ghi vào mart.")
                    buffer = []
                except Exception as e:
                    mart_session.rollback()
                    logging.error(f" Lỗi khi ghi batch: {e}")
                    buffer = []

        # Ghi phần còn lại nếu có
        if buffer:
            try:
                mart_session.bulk_save_objects(buffer)
                mart_session.commit()
                logging.info(f"Đã ghi batch cuối: {len(buffer)} bản ghi.")
            except Exception as e:
                mart_session.rollback()
                logging.error(f" Lỗi khi ghi batch cuối: {e}")

        logging.info(f" Hoàn tất ETL: tổng cộng {inserted} bản ghi đã được tải vào mart_revenue_by_month.")

    except Exception as e:
        mart_session.rollback()
        logging.error(f" Lỗi toàn cục trong ETL: {e}")

    finally:
        warehouse_session.close()
        mart_session.close()
        logging.info(" Đã đóng kết nối cơ sở dữ liệu.")

# # Chạy ETL


def load_to_promotion_ratio_mart(warehouse_session, mart_session):
    try:
        logging.info(" Bắt đầu truy vấn dữ liệu khuyến mãi từ warehouse...")

        results = (
            warehouse_session.query(
                DimDate.year,
                DimDate.month,
                func.sum(case((FactPromotionAnalysis.promotion_used == True, 1), else_=0)).label("used_count"),
                func.sum(case((FactPromotionAnalysis.promotion_used == False, 1), else_=0)).label("not_used_count")
            )
            .join(DimDate, FactPromotionAnalysis.date_id == DimDate.date_id)
            .group_by(DimDate.year, DimDate.month)
            .order_by(DimDate.year, DimDate.month)
            .all()
        )

        BATCH_SIZE = 1000
        buffer = []
        inserted = 0

        logging.info(f" Truy vấn thành công {len(results)} bản ghi. Bắt đầu load vào mart...")

        for year, month, used, not_used in results:
            total = used + not_used
            ratio = round(used / total, 4) if total > 0 else 0.0

            record = MartPromotionRatioMonthly(
                year=year,
                month=month,
                used_count=used,
                not_used_count=not_used,
                used_ratio=ratio
            )
            buffer.append(record)
            inserted += 1

            if len(buffer) >= BATCH_SIZE:
                try:
                    mart_session.bulk_save_objects(buffer)
                    mart_session.commit()
                    logging.info(f" Đã ghi batch {len(buffer)} bản ghi vào mart.")
                    buffer = []
                except Exception as e:
                    mart_session.rollback()
                    logging.error(f" Lỗi khi ghi batch: {e}")
                    buffer = []

        if buffer:
            try:
                mart_session.bulk_save_objects(buffer)
                mart_session.commit()
                logging.info(f" Đã ghi batch cuối: {len(buffer)} bản ghi.")
            except Exception as e:
                mart_session.rollback()
                logging.error(f" Lỗi khi ghi batch cuối: {e}")

        logging.info(f" Hoàn tất ETL: đã tải {inserted} bản ghi vào mart_promotion_ratio_monthly.")

    except Exception as e:
        mart_session.rollback()
        logging.error(f" Lỗi toàn cục trong ETL khuyến mãi: {e}")

    finally:
        logging.info(" Đã kết thúc job ETL khuyến mãi.")

def load_to_payment_method_mart(warehouse_session, mart_session):
    try:
        logging.info(" Bắt đầu ETL mart_payment_method_monthly...")

        # Lấy dữ liệu đã join
        results = (
            warehouse_session.query(
                DimDate.year,
                DimDate.month,
                FactRevenue.payment_method_id,
                DimPaymentMethod.method_name,
                func.count(FactRevenue.bill_id),
                func.sum(FactRevenue.value)
            )
            .join(DimDate, FactRevenue.date_id == DimDate.date_id)
            .join(DimPaymentMethod, FactRevenue.payment_method_id == DimPaymentMethod.payment_method_id)
            .group_by(DimDate.year, DimDate.month, FactRevenue.payment_method_id, DimPaymentMethod.method_name)
            .order_by(DimDate.year, DimDate.month)
            .all()
        )

        BATCH_SIZE = 1000
        buffer = []
        inserted = 0

        for year, month, method_id, method_name, count, total in results:
            record = MartPaymentMethodMonthly(
                year=year,
                month=month,
                payment_method_id=method_id,
                payment_method_name=method_name,
                transaction_count=count,
                total_revenue=total
            )
            buffer.append(record)
            inserted += 1

            if len(buffer) >= BATCH_SIZE:
                try:
                    mart_session.bulk_save_objects(buffer)
                    mart_session.commit()
                    logging.info(f" Đã ghi batch {len(buffer)} bản ghi.")
                    buffer = []
                except Exception as e:
                    mart_session.rollback()
                    logging.error(f" Lỗi khi ghi batch: {e}")
                    buffer = []

        if buffer:
            try:
                mart_session.bulk_save_objects(buffer)
                mart_session.commit()
                logging.info(f" Đã ghi batch cuối: {len(buffer)} bản ghi.")
            except Exception as e:
                mart_session.rollback()
                logging.error(f" Lỗi khi ghi batch cuối: {e}")

        logging.info(f" Hoàn tất ETL: đã tải {inserted} bản ghi vào mart_payment_method_monthly.")

    except Exception as e:
        mart_session.rollback()
        logging.error(f" Lỗi toàn cục trong ETL phương thức thanh toán: {e}")

def load_to_revenue_cinema(warehouse_session, mart_session):
    try:
        logging.info("Bắt đầu load bảng CinemaRevenue")
        results = (
            warehouse_session.query(
                DimDate.year,
                DimDate.month,
                DimCinema.cinema_id,
                DimCinema.name,
                func.sum(FactRevenue.value).label('total_revenue')
            )
            .join(DimDate, DimDate.date_id == FactRevenue.date_id)
            .join(DimCinema,DimCinema.cinema_id == FactRevenue.cinema_id)
            .group_by(DimDate.year, DimDate.month, DimCinema.cinema_id)
            .order_by(DimDate.year, DimDate.month)
            .all()
        )
        logging.info(f"Truy vấn thành công {len(results)}")
        inserted = 0
        buffer = []
        for year, month, cinema_id, name , total_revenue in results:
            record = MartRevenueByCinema(
                year=year,
                month=month,
                cinema_id=cinema_id,
                cinema_name=name,
                total_revenue=total_revenue
            )
            buffer.append(record)
            inserted += 1
        mart_session.add_all(buffer)
        mart_session.commit()

        logging.info(f"Đã load thành công {inserted} bản ghi vào mart_revenue_by_cinema.")

    except Exception as e:
        mart_session.rollback()
        logging.info(f"Lỗi toàn cục trong ETL: {e}")
    finally:
        warehouse_session.close()
        mart_session.close()
        logging.info("Đã đóng kết nối cơ sở dữ liệu")


def load_to_film_rating(warehouse_session, mart_session):
    try:
        logging.info("Bắt đầu load dữ liệu vào Rating")
        results = (warehouse_session.query(
            FactFilmRating.film_id,
            DimFilm.title,
            func.avg(FactFilmRating.point).label('avg_rating'),
            func.count(FactFilmRating.film_id).label('total_reviews')
        )
        .join(DimFilm ,FactFilmRating.film_id== DimFilm.film_id)
        .group_by(FactFilmRating.film_id,DimFilm.title)
        .order_by(FactFilmRating.film_id)
        .all()
        )

        buffer = []
        inserted = 0
        for id, title, avg_rating, total_reviews in results:
            inserted += 1
            record=MartFilmRatingSummary(
                film_id=id,
                film_title=title,
                avg_rating=avg_rating,
                total_reviews=total_reviews
            )
            buffer.append(record)

        logging.info(f"Đã query {inserted} bản ghi , tiếp tục tiến hành load ...")
        mart_session.add_all(buffer)
        mart_session.commit()
        logging.info(f"Dữ Liệu đã được load thành công !!")
    except Exception as e:
        mart_session.rollback()
        logging.info(f"Đã có lỗi xảy ra -> {e}")
    finally:
        warehouse_session.close()
        mart_session.close()
        logging.info("Đã đóng kết nối cơ sở dữ liệu")



from sqlalchemy import func
from sqlalchemy.orm import aliased

def load_to_top_film(warehouse_session, mart_session):
    try:
        logging.info("Bắt đầu load Top 5 phim doanh thu cao nhất")

        # Subquery để tính row_number cho từng phim trong mỗi tháng/năm
        row_number_subquery = (
            warehouse_session.query(
                FactRevenue.film_id,
                DimFilm.title,
                DimDate.year,
                DimDate.month,
                func.sum(FactRevenue.value).label('total_revenue'),
                func.row_number().over(
                    partition_by=[DimDate.year, DimDate.month],  # Phân nhóm theo tháng và năm
                    order_by=func.sum(FactRevenue.value).desc()  # Sắp xếp theo doanh thu giảm dần
                ).label('row_num')
            )
            .join(DimFilm, DimFilm.film_id == FactRevenue.film_id)
            .join(DimDate, DimDate.date_id == FactRevenue.date_id)
            .group_by(FactRevenue.film_id, DimFilm.title, DimDate.year, DimDate.month)
            .subquery()  # Chuyển thành subquery
        )

        # Truy vấn dữ liệu từ subquery và lấy chỉ top 5 phim
        results = (
            warehouse_session.query(
                row_number_subquery.c.film_id,
                row_number_subquery.c.title,
                row_number_subquery.c.total_revenue,
                row_number_subquery.c.year,
                row_number_subquery.c.month
            )
            .filter(row_number_subquery.c.row_num <= 5)  # Lọc lấy chỉ top 5
        )

        buffer = []
        inserted = 0
        for film_id, title, total_revenue, year, month in results:
            inserted += 1
            record = MartTopFilmRevenue(
                film_id=film_id,
                film_title=title,
                total_revenue=total_revenue,
                year=year,
                month=month
            )
            buffer.append(record)

        logging.info(f"Đã query {inserted} bản ghi , tiếp tục tiến hành load ...")

        # Load vào mart
        mart_session.add_all(buffer)
        mart_session.commit()
        logging.info(f"Dữ Liệu đã được load thành công !!")

    except Exception as e:
        mart_session.rollback()
        logging.error(f"Đã có lỗi xảy ra -> {e}")
    finally:
        warehouse_session.close()
        mart_session.close()
        logging.info("Đã đóng kết nối cơ sở dữ liệu")
load_to_revenue_mart(warehouse_session, mart_session)
load_to_promotion_ratio_mart(warehouse_session, mart_session)
load_to_payment_method_mart(warehouse_session,mart_session)
load_to_revenue_cinema(warehouse_session, mart_session)
load_to_film_rating(warehouse_session, mart_session)
# load_to_top_film(warehouse_session, mart_session)