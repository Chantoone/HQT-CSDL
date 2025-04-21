import logging
from sqlalchemy.orm import sessionmaker, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from datetime import datetime

# --- Hàm trợ giúp ---
def get_time_id(dt: datetime):
    if dt is None:
        return None # Trả về None nếu datetime là None
    return dt.hour * 60 + dt.minute

def get_purchase_type_id(staff_id):
    # Trả về 1 nếu mua tại quầy (có staff_id), 2 nếu mua online (staff_id là None)
    return 1 if staff_id is not None else 2

def map_payment_method_to_id(method_text: str) -> int | None: # Cho phép trả về None
    if method_text is None:
        return None
    mapping = {
        "Thanh toán tiền mặt": 1,
        "Thanh toán bằng thẻ tín dụng": 2,
        "Thanh toán bằng ví điện tử": 3
    }
    # Dùng strip() để loại bỏ khoảng trắng thừa và get() để xử lý key không tồn tại
    return mapping.get(method_text.strip(), None)


#  --- Các hàm ETL với xử lý ngoại lệ ---

def etl_dim_film(session_src, session_dest, FilmSrc, DimFilm):
    try:
        logging.info("Bắt đầu: etl_dim_film")
        films = session_src.query(FilmSrc).all()
        count = 0
        for f in films:
            try:
                dim = DimFilm(
                    film_id=f.id,
                    title=f.title,
                    description=f.description,
                    duration=f.duration,
                    release_date=f.release_date,
                    author=f.author,
                    actors=f.actors,
                    director=f.director,
                    status=f.status
                )
                session_dest.merge(dim)
                count += 1
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý film ID {f.id}: {item_error}")
                # Có thể thêm logic bỏ qua bản ghi này hoặc xử lý khác
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_dim_film - Đã xử lý {count} bản ghi.")
    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_dim_film: {db_error}")
        session_dest.rollback()
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_dim_film: {e}")
        session_dest.rollback()
        raise # Ném lại lỗi để dừng tiến trình nếu cần

def etl_dim_ticket(session_src, session_dest, TicketSrc, DimTicket):
    try:
        logging.info("Bắt đầu: etl_dim_ticket")
        tickets = session_src.query(TicketSrc).all()
        count = 0
        for t in tickets:
            try:
                dim = DimTicket(
                    ticket_id=t.id,
                    title=t.title,
                    description=t.description,
                    price=t.price
                )
                session_dest.merge(dim)
                count += 1
            except Exception as item_error:
                 logging.error(f"Lỗi khi xử lý ticket ID {t.id}: {item_error}")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_dim_ticket - Đã xử lý {count} bản ghi.")
    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_dim_ticket: {db_error}")
        session_dest.rollback()
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_dim_ticket: {e}")
        session_dest.rollback()
        raise

def etl_dim_genre(session_src, session_dest, GenreSrc, DimGenre):
    try:
        logging.info("Bắt đầu: etl_dim_genre")
        genres = session_src.query(GenreSrc).all()
        count = 0
        for g in genres:
            try:
                dim = DimGenre(
                    genre_id=g.id,
                    name=g.name,
                    description=g.description
                )
                session_dest.merge(dim)
                count += 1
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý genre ID {g.id}: {item_error}")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_dim_genre - Đã xử lý {count} bản ghi.")
    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_dim_genre: {db_error}")
        session_dest.rollback()
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_dim_genre: {e}")
        session_dest.rollback()
        raise

def etl_dim_cinema(session_src, session_dest, CinemaSrc, DimCinema):
    try:
        logging.info("Bắt đầu: etl_dim_cinema")
        cinemas = session_src.query(CinemaSrc).all()
        count = 0
        for c in cinemas:
            try:
                dim = DimCinema(
                    cinema_id=c.id,
                    name=c.name,
                    address=c.address,
                    phone_number=c.phone_number
                )
                session_dest.merge(dim)
                count += 1
            except Exception as item_error:
                 logging.error(f"Lỗi khi xử lý cinema ID {c.id}: {item_error}")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_dim_cinema - Đã xử lý {count} bản ghi.")
    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_dim_cinema: {db_error}")
        session_dest.rollback()
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_dim_cinema: {e}")
        session_dest.rollback()
        raise

def etl_dim_showtime(session_src, session_dest, ShowtimeSrc, DimShowtime):
    try:
        logging.info("Bắt đầu: etl_dim_showtime")
        showtimes = session_src.query(ShowtimeSrc).all()
        count = 0
        for s in showtimes:
            try:
                # Kiểm tra các giá trị bắt buộc trước khi tạo DimShowtime
                if s.id is None or s.start_time is None or s.film_id is None or s.room_id is None:
                    logging.warning(f"Bỏ qua showtime ID {s.id or 'UNKNOWN'} do thiếu thông tin bắt buộc (film_id, room_id, start_time).")
                    continue

                dim = DimShowtime(
                    showtime_id=s.id,
                    name=s.name, # Có thể là None
                    start_time=s.start_time,
                    film_id=s.film_id,
                    room_id=s.room_id
                )
                session_dest.merge(dim)
                count += 1
            except AttributeError as attr_err:
                logging.error(f"Lỗi thuộc tính khi xử lý showtime ID {s.id}: {attr_err}")
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý showtime ID {s.id}: {item_error}")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_dim_showtime - Đã xử lý {count} bản ghi.")
    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_dim_showtime: {db_error}")
        session_dest.rollback()
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_dim_showtime: {e}")
        session_dest.rollback()
        raise

def etl_dim_promotion(session_src, session_dest, PromotionSrc, DimPromotion):
    try:
        logging.info("Bắt đầu: etl_dim_promotion")
        promotions = session_src.query(PromotionSrc).all()
        count = 0
        for p in promotions:
            try:
                dim = DimPromotion(
                    promotion_id=p.id,
                    name=p.name,
                    description=p.description,
                    duration=p.duration # Giả sử duration là trường phù hợp
                    # Cần xem lại warehouse_models.DimPromotion để đảm bảo các trường khớp
                )
                session_dest.merge(dim)
                count += 1
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý promotion ID {p.id}: {item_error}")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_dim_promotion - Đã xử lý {count} bản ghi.")
    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_dim_promotion: {db_error}")
        session_dest.rollback()
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_dim_promotion: {e}")
        session_dest.rollback()
        raise

def etl_fact_ticket_analysis(session_src, session_dest, TicketSrc, BillSrc, FactTicketAnalysis):
    try:
        logging.info("Bắt đầu: etl_fact_ticket_analysis")
        # Join Ticket và Bill để lấy thông tin cần thiết
        # Cần đảm bảo mối quan hệ giữa Ticket và Bill được định nghĩa đúng trong models
        # Giả sử Ticket có quan hệ trực tiếp hoặc gián tiếp tới Bill
        # Ví dụ: Ticket -> ShowtimeSeat -> Bill (cần kiểm tra lại cấu trúc model)
        # HOẶC Bill có ticket_id (phổ biến hơn)
        query = session_src.query(TicketSrc).join(BillSrc, TicketSrc.bill_id == BillSrc.id) # Giả sử Ticket có bill_id
        tickets_with_bills = query.all()
        count = 0
        for t in tickets_with_bills:
            try:
                bill = t.bill # Truy cập bill thông qua quan hệ đã join

                if bill is None:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}: không tìm thấy Bill liên kết.")
                    continue
                if t.created_at is None:
                     logging.warning(f"Bỏ qua Ticket ID {t.id}: created_at is None.")
                     continue
                if bill.payment_method is None:
                     logging.warning(f"Bỏ qua Ticket ID {t.id}, Bill ID {bill.id}: payment_method is None.")
                     continue # Hoặc gán giá trị mặc định nếu có thể

                payment_method_id = map_payment_method_to_id(bill.payment_method)
                if payment_method_id is None:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, Bill ID {bill.id}: Không thể map payment_method '{bill.payment_method}'.")
                    continue # Hoặc gán giá trị mặc định

                fact = FactTicketAnalysis(
                    # Đảm bảo các khóa ngoại tồn tại trong bảng DIM tương ứng trước khi thêm vào FACT
                    ticket_id=t.id,
                    bill_id=bill.id,
                    price=t.price,
                    date_id=t.created_at.date(), # Cần đảm bảo t.created_at không None
                    time_id=get_time_id(t.created_at), # Hàm get_time_id đã xử lý None
                    payment_method_id=payment_method_id,
                    purchase_type_id=get_purchase_type_id(bill.staff_id)
                )
                session_dest.merge(fact)
                count += 1
            except AttributeError as attr_err:
                logging.error(f"Lỗi thuộc tính khi xử lý ticket ID {t.id} / bill ID {getattr(t, 'bill', None)}: {attr_err}")
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý ticket ID {t.id}: {item_error}")

        session_dest.commit()
        logging.info(f"Hoàn thành: etl_fact_ticket_analysis - Đã xử lý {count} bản ghi.")
    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_fact_ticket_analysis: {db_error}")
        session_dest.rollback()
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_fact_ticket_analysis: {e}")
        session_dest.rollback()
        raise

BATCH_SIZE = 1000 # Có thể điều chỉnh

def etl_fact_film_rating_optimized(session_src: sessionmaker,
                                  session_dest: sessionmaker,
                                  RateSrc,
                                  FactFilmRating,
                                  # Thêm các model Dim nếu bạn muốn kiểm tra FK chủ động
                                  DimUser=None,
                                  DimFilm=None,
                                  DimDate=None,
                                  # Cờ để bật/tắt kiểm tra FK chủ động
                                  proactive_fk_check=False
                                 ):
    """
    ETL function to populate FactFilmRating, optimized with:
    1. Batch Processing (yield_per) for memory efficiency.
    2. Optional: Proactive foreign key checks before attempting merge.
    """
    try:
        logging.info("Bắt đầu: etl_fact_film_rating_optimized")

        # --- (TÙY CHỌN) Bước kiểm tra khóa ngoại chủ động ---
        valid_user_ids = set()
        valid_film_ids = set()
        # valid_date_ids = set() # Có thể không hiệu quả nếu DimDate quá lớn

        if proactive_fk_check:
            logging.info("Đang thực hiện kiểm tra khóa ngoại chủ động (có thể mất thêm thời gian)...")
            try:
                if DimUser:
                    logging.debug("Truy vấn khóa hợp lệ từ DimUser...")
                    valid_user_ids = {u.id for u in session_dest.query(DimUser.id).all()} # Cân nhắc yield_per nếu DimUser lớn
                    logging.debug(f"Tìm thấy {len(valid_user_ids)} user IDs hợp lệ.")
                else:
                     logging.warning("Không thể kiểm tra FK cho User vì DimUser model không được cung cấp.")

                if DimFilm:
                    logging.debug("Truy vấn khóa hợp lệ từ DimFilm...")
                    valid_film_ids = {f.id for f in session_dest.query(DimFilm.id).all()}
                    logging.debug(f"Tìm thấy {len(valid_film_ids)} film IDs hợp lệ.")
                else:
                     logging.warning("Không thể kiểm tra FK cho Film vì DimFilm model không được cung cấp.")

                # Việc lấy tất cả date_id có thể không hiệu quả nếu DimDate rất lớn
                # Cân nhắc bỏ qua bước này và dựa vào ETL của DimDate để đảm bảo tính đầy đủ
                # Hoặc chỉ kiểm tra các ngày trong một khoảng thời gian gần đây nếu hợp lý
                # if DimDate:
                #     logging.debug("Truy vấn khóa hợp lệ từ DimDate...")
                #     valid_date_ids = {d.id for d in session_dest.query(DimDate.id).all()}
                #     logging.debug(f"Tìm thấy {len(valid_date_ids)} date IDs hợp lệ.")
                # else:
                #      logging.warning("Không thể kiểm tra FK cho Date vì DimDate model không được cung cấp.")

            except Exception as fk_query_error:
                logging.error(f"Lỗi khi truy vấn khóa ngoại từ bảng Dimension: {fk_query_error}", exc_info=True)
                logging.warning("Tiếp tục ETL mà không kiểm tra khóa ngoại chủ động do lỗi truy vấn Dim.")
                proactive_fk_check = False # Tắt kiểm tra nếu không lấy được khóa
        # --- Kết thúc bước kiểm tra khóa ngoại chủ động ---


        # Sử dụng yield_per để xử lý RateSrc theo lô
        rates_iterable = session_src.query(RateSrc).yield_per(BATCH_SIZE)
        count = 0
        skipped_count = 0
        processed_in_batch = 0

        logging.info("Bắt đầu xử lý các bản ghi đánh giá...")
        for r in rates_iterable:
            try:
                # Kiểm tra các giá trị bắt buộc từ nguồn
                if r.user_id is None or r.film_id is None or r.created_at is None or r.point is None:
                    logging.warning(f"Bỏ qua rate ID {r.id or 'UNKNOWN'} do thiếu thông tin bắt buộc (user_id, film_id, created_at, point).")
                    skipped_count += 1
                    continue

                # Trích xuất date_id để kiểm tra (nếu cần)
                rating_date = r.created_at.date()

                # --- (TÙY CHỌN) Thực hiện kiểm tra FK chủ động ---
                if proactive_fk_check:
                    if DimUser and r.user_id not in valid_user_ids:
                        logging.warning(f"Bỏ qua rate ID {r.id}: User ID {r.user_id} không tìm thấy trong DimUser.")
                        skipped_count += 1
                        continue
                    if DimFilm and r.film_id not in valid_film_ids:
                        logging.warning(f"Bỏ qua rate ID {r.id}: Film ID {r.film_id} không tìm thấy trong DimFilm.")
                        skipped_count += 1
                        continue
                    # if DimDate and rating_date not in valid_date_ids:
                    #     logging.warning(f"Bỏ qua rate ID {r.id}: Date ID {rating_date} không tìm thấy trong DimDate.")
                    #     skipped_count += 1
                    #     continue
                # --- Kết thúc kiểm tra FK ---

                # Tạo đối tượng Fact
                fact = FactFilmRating(
                    user_id=r.user_id,
                    film_id=r.film_id,
                    # date_id=rating_date, # Sử dụng biến đã trích xuất
                    date_id="2023-01-01",
                    point=r.point,
                    detail=r.detail # detail có thể là None
                )
                session_dest.merge(fact)
                count += 1
                processed_in_batch += 1

                # Tùy chọn: Commit theo batch
                # if processed_in_batch >= BATCH_SIZE:
                #     logging.info(f"Committing batch, processed {count} records so far...")
                #     session_dest.commit()
                #     processed_in_batch = 0

            except AttributeError as attr_err:
                logging.error(f"Lỗi thuộc tính khi xử lý rate ID {r.id or 'UNKNOWN'}: {attr_err}", exc_info=True)
                skipped_count += 1
            except Exception as item_error:
                 # Lỗi ForeignKeyViolation từ DB vẫn có thể xảy ra ở đây nếu không bật kiểm tra chủ động
                 # hoặc nếu kiểm tra chủ động bị lỗi / không đầy đủ (ví dụ: không kiểm tra Date)
                logging.error(f"Lỗi khi xử lý rate ID {r.id or 'UNKNOWN'}: {item_error}", exc_info=True)
                # Nếu lỗi xảy ra ở đây, transaction có thể đã bị rollback bởi autoflush
                # Việc tiếp tục vòng lặp có thể gây lỗi "transaction rolled back" trừ khi rollback được xử lý
                # Cân nhắc thêm rollback và break/continue tùy chiến lược xử lý lỗi
                # session_dest.rollback() # Cần thiết nếu muốn tiếp tục các batch sau lỗi flush
                skipped_count += 1


        # Commit cuối cùng
        logging.info(f"Hoàn tất duyệt qua các bản ghi đánh giá. Chuẩn bị commit {count} bản ghi hợp lệ...")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_fact_film_rating_optimized - Đã xử lý {count} bản ghi. Bỏ qua {skipped_count} bản ghi.")

    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_fact_film_rating_optimized: {db_error}", exc_info=True)
        session_dest.rollback()
        raise
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_fact_film_rating_optimized: {e}", exc_info=True)
        session_dest.rollback()
        raise


BATCH_SIZE = 500 

def etl_fact_revenue_optimized_v4(session_src: sessionmaker,
                                  session_dest: sessionmaker,
                                  TicketSrc, # Model Ticket nguồn
                                  BillSrc,
                                  ShowtimeSeatSrc,
                                  ShowtimeSrc,
                                  RoomSrc,
                                  FactRevenue # Model Fact đích
                                 ):
    """
    ETL function to populate FactRevenue, optimized based on relationship:
    Ticket --> Bill
      |
      --> ShowtimeSeat ->> Showtime ->> Room ->> Cinema (lấy cinema_id)

    Starts query from TicketSrc. Uses Eager Loading and Batch Processing.
    (Corrected Room location within Showtime)
    """
    try:
        logging.info("Bắt đầu: etl_fact_revenue_optimized_v4 (Query từ Ticket, Room trong Showtime)")

        # Truy vấn từ TicketSrc và joinedload các quan hệ cần thiết
        # Đã sửa lại đường dẫn joinedload cho Room (nằm trong Showtime)
        query = session_src.query(TicketSrc).options(
            joinedload(TicketSrc.bill), # Tải Bill từ Ticket
            joinedload(TicketSrc.showtime_seat) # Tải ShowtimeSeat từ Ticket
                .joinedload(ShowtimeSeatSrc.showtime) # Tải Showtime từ ShowtimeSeat
                .joinedload(ShowtimeSrc.room) # Tải Room từ Showtime (ĐÃ SỬA)
                # Giả định RoomSrc có cinema_id
        )

        # Sử dụng yield_per để xử lý theo batch
        tickets_iterable = query.yield_per(BATCH_SIZE)

        count = 0
        processed_in_batch = 0
        # Lặp qua từng ticket (t)
        for t in tickets_iterable:
            try:
                # --- Truy cập dữ liệu đã được joinedload ---
                bill = t.bill
                if not bill:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}: Thiếu thông tin Bill liên kết.")
                    continue

                st_seat = t.showtime_seat
                if not st_seat:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}: Thiếu thông tin ShowtimeSeat liên kết.")
                    continue

                showtime = st_seat.showtime
                if not showtime:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, ShowtimeSeat ID {st_seat.id}: Thiếu thông tin Showtime.")
                    continue

                # Lấy Room từ Showtime (ĐÃ SỬA)
                room = showtime.room
                if not room:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, Showtime ID {showtime.id}: Thiếu thông tin Room.")
                    continue
                # --- Kết thúc truy cập dữ liệu ---

                # --- Kiểm tra các giá trị cần thiết ---
                if bill.payment_time is None:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, Bill ID {bill.id}: payment_time is None.")
                    continue
                if showtime.film_id is None: # Lấy từ showtime
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, Showtime ID {showtime.id}: film_id is None.")
                    continue
                if room.cinema_id is None: # Lấy từ room
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, Room ID {room.id}: cinema_id is None.")
                    continue
                if bill.payment_method is None:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, Bill ID {bill.id}: payment_method is None.")
                    continue
                # --- Kết thúc kiểm tra ---

                # --- Ánh xạ và tạo Fact ---
                payment_method_id = map_payment_method_to_id(bill.payment_method)
                if payment_method_id is None:
                    logging.warning(f"Bỏ qua Ticket ID {t.id}, Bill ID {bill.id}: Không thể map payment_method '{bill.payment_method}'.")
                    continue

                fact = FactRevenue(
                    bill_id=bill.id,
                    date_id=bill.payment_time.date(),
                    time_id=get_time_id(bill.payment_time),
                    film_id=showtime.film_id, # Lấy từ showtime
                    cinema_id=room.cinema_id, # Lấy từ room
                    value=bill.value,
                    payment_method_id=payment_method_id,
                    purchase_type_id=get_purchase_type_id(bill.staff_id)
                )
                session_dest.merge(fact)
                count += 1
                processed_in_batch += 1

                # Tùy chọn: Commit theo batch
                # if processed_in_batch >= BATCH_SIZE:
                #     logging.info(f"Committing batch, processed {count} records so far...")
                #     session_dest.commit()
                #     processed_in_batch = 0

            except AttributeError as attr_err:
                logging.error(f"Lỗi thuộc tính không mong muốn khi xử lý ticket ID {t.id}: {attr_err}")
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý ticket ID {t.id}: {item_error}")


        # Commit cuối cùng
        logging.info("Hoàn tất duyệt qua các ticket, chuẩn bị commit...")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_fact_revenue_optimized_v4 - Đã xử lý và commit {count} bản ghi.")

    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_fact_revenue_optimized_v4: {db_error}")
        session_dest.rollback()
        raise
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_fact_revenue_optimized_v4: {e}")
        session_dest.rollback()
        raise

def etl_fact_showtime_fillrate_optimized_v2(session_src: sessionmaker,
                                           session_dest: sessionmaker,
                                           ShowtimeSrc,
                                           ShowtimeSeatSrc,
                                           FactShowtimeFillRate
                                          ):
    """
    ETL function for ShowtimeFillRate, optimized with:
    1. Batch Processing (yield_per).
    2. selectinload() for the Showtime->ShowtimeSeat collection (compatible with yield_per).
    3. Nested joinedload() for ShowtimeSeat->Ticket (assuming many-to-one/one-to-one).
    """
    try:
        logging.info("Bắt đầu: etl_fact_showtime_fillrate_optimized_v2 (dùng selectinload)")

        # Sử dụng selectinload cho collection 'showtime_seat'
        # và giữ joinedload cho 'ticket' (nếu là many-to-one/one-to-one)
        query = session_src.query(ShowtimeSrc).options(
            # THAY THẾ joinedload ở đây bằng selectinload
            selectinload(ShowtimeSrc.showtime_seat)
                # Có thể giữ joinedload lồng nhau nếu ticket là quan hệ *-to-one
                .joinedload(ShowtimeSeatSrc.ticket)
                # Hoặc nếu ticket cũng là collection hoặc gây lỗi, dùng tiếp selectinload:
                # .selectinload(ShowtimeSeatSrc.ticket)
        ).yield_per(BATCH_SIZE) # Giữ yield_per

        count = 0
        processed_in_batch = 0
        for s in query:
            # --- Phần còn lại của logic xử lý bên trong vòng lặp giữ nguyên ---
            try:
                if s.start_time is None:
                    logging.warning(f"Bỏ qua Showtime ID {s.id}: start_time is None.")
                    continue
                if s.film_id is None:
                    logging.warning(f"Bỏ qua Showtime ID {s.id}: film_id is None.")
                    continue

                # Truy cập s.showtime_seat và ss.ticket giờ đây hiệu quả và tương thích yield_per
                showtime_seats = s.showtime_seat
                total = len(showtime_seats)

                if total == 0:
                    logging.warning(f"Showtime ID {s.id} không có ghế nào (total=0), bỏ qua.")
                    continue

                booked = sum(1 for ss in showtime_seats if ss.ticket is not None)
                fill_rate = booked / total

                fact = FactShowtimeFillRate(
                    date_id=s.start_time.date(),
                    film_id=s.film_id,
                    showtime_id=s.id,
                    total_seats=total,
                    booked_seats=booked,
                    fill_rate=fill_rate
                )
                session_dest.merge(fact)
                count += 1
                processed_in_batch += 1

            except AttributeError as attr_err:
                logging.error(f"Lỗi thuộc tính khi xử lý showtime ID {s.id}: {attr_err}", exc_info=True)
            except ZeroDivisionError:
                logging.error(f"Lỗi chia cho 0 không mong muốn khi xử lý showtime ID {s.id}")
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý showtime ID {s.id}: {item_error}", exc_info=True)
        # --- Hết phần logic trong vòng lặp ---

        logging.info("Hoàn tất duyệt qua các showtime, chuẩn bị commit...")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_fact_showtime_fillrate_optimized_v2 - Đã xử lý và commit {count} bản ghi.")

    except SQLAlchemyError as db_error:
        # Lỗi InvalidRequestError có thể xảy ra ở đây nếu query bị sai cú pháp
        logging.error(f"Lỗi SQLAlchemy trong etl_fact_showtime_fillrate_optimized_v2: {db_error}", exc_info=True)
        session_dest.rollback()
        raise
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_fact_showtime_fillrate_optimized_v2: {e}", exc_info=True)
        session_dest.rollback()
        raise

def etl_fact_promotion_analysis_optimized(session_src: sessionmaker,
                                         session_dest: sessionmaker,
                                         BillSrc,
                                         BillPromSrc, # Cần model này để truy vấn ID
                                         FactPromotionAnalysis
                                        ):
    """
    ETL function to populate FactPromotionAnalysis, optimized by:
    1. Pre-fetching bill_ids that used promotions into a set.
    2. Batch Processing Bills (yield_per) for memory efficiency.
    3. Avoiding N+1 query problem by checking against the pre-fetched set.
    """
    try:
        logging.info("Bắt đầu: etl_fact_promotion_analysis_optimized")

        # 1. Truy vấn trước tất cả các bill_id đã sử dụng khuyến mãi (từ BillPromSrc)
        #    Sử dụng distinct() để tránh trùng lặp và lấy chỉ cột bill_id.
        logging.info("Truy vấn các bill_id đã sử dụng khuyến mãi...")
        try:
            # Lấy tất cả bill_id duy nhất từ BillPromSrc
            promo_bills_query = session_src.query(BillPromSrc.bill_id).distinct()
            # Lưu vào một set để tra cứu O(1)
            # Nếu bảng BillPromSrc quá lớn, cân nhắc xử lý theo lô cho cả query này
            promo_bill_ids = {row.bill_id for row in promo_bills_query.all()}
            logging.info(f"Đã lấy được {len(promo_bill_ids)} bill_id duy nhất đã dùng khuyến mãi.")
        except Exception as e:
            logging.error(f"Lỗi khi truy vấn bill_id từ BillPromSrc: {e}", exc_info=True)
            raise # Ném lại lỗi để dừng tiến trình nếu không lấy được dữ liệu này

        # 2. Truy vấn BillSrc và xử lý theo lô (yield_per)
        bills_iterable = session_src.query(BillSrc).yield_per(BATCH_SIZE)
        count = 0
        processed_in_batch = 0

        logging.info("Bắt đầu xử lý các hóa đơn...")
        for b in bills_iterable:
            try:
                # Kiểm tra thông tin cần thiết của Bill
                if b.payment_time is None:
                    logging.warning(f"Bỏ qua Bill ID {b.id}: payment_time is None.")
                    continue

                # 3. Kiểm tra xem bill_id có trong tập hợp đã lấy trước không (O(1) lookup)
                #    Loại bỏ hoàn toàn truy vấn exists() bên trong vòng lặp.
                used = b.id in promo_bill_ids

                # Tạo bản ghi Fact
                fact = FactPromotionAnalysis(
                    bill_id=b.id,
                    date_id=b.payment_time.date(), # Cần DimDate
                    promotion_used=used, # Đã là boolean
                    point=0
                )
                session_dest.merge(fact)
                count += 1
                processed_in_batch += 1

                # Tùy chọn: Commit theo batch
                # if processed_in_batch >= BATCH_SIZE:
                #     logging.info(f"Committing batch, processed {count} records so far...")
                #     session_dest.commit()
                #     processed_in_batch = 0

            except AttributeError as attr_err:
                logging.error(f"Lỗi thuộc tính khi xử lý bill ID {b.id}: {attr_err}", exc_info=True)
            except Exception as item_error:
                logging.error(f"Lỗi khi xử lý bill ID {b.id}: {item_error}", exc_info=True)

        # Commit cuối cùng
        logging.info("Hoàn tất duyệt qua các hóa đơn, chuẩn bị commit...")
        session_dest.commit()
        logging.info(f"Hoàn thành: etl_fact_promotion_analysis_optimized - Đã xử lý và commit {count} bản ghi.")

    except SQLAlchemyError as db_error:
        logging.error(f"Lỗi SQLAlchemy trong etl_fact_promotion_analysis_optimized: {db_error}", exc_info=True)
        session_dest.rollback()
        raise
    except Exception as e:
        logging.error(f"Lỗi không xác định trong etl_fact_promotion_analysis_optimized: {e}", exc_info=True)
        session_dest.rollback()
        raise
