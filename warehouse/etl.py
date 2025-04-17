from datetime import datetime
def etl_dim_film(session_src, session_dest, FilmSrc, DimFilm):
    films = session_src.query(FilmSrc).all()
    for f in films:
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
    session_dest.commit()

def etl_dim_ticket(session_src, session_dest, TicketSrc, DimTicket):
    tickets = session_src.query(TicketSrc).all()
    for t in tickets:
        dim = DimTicket(
            ticket_id=t.id,
            title=t.title,
            description=t.description,
            price=t.price
        )
        session_dest.merge(dim)
    session_dest.commit()

def etl_dim_genre(session_src, session_dest, GenreSrc, DimGenre):
    genres = session_src.query(GenreSrc).all()
    for g in genres:
        dim = DimGenre(
            genre_id=g.id,
            name=g.name,
            description=g.description
        )
        session_dest.merge(dim)
    session_dest.commit()

def etl_dim_cinema(session_src, session_dest, CinemaSrc, DimCinema):
    cinemas = session_src.query(CinemaSrc).all()
    for c in cinemas:
        dim = DimCinema(
            cinema_id=c.id,
            name=c.name,
            address=c.address,
            phone_number=c.phone_number
        )
        session_dest.merge(dim)
    session_dest.commit()

def etl_dim_showtime(session_src, session_dest, ShowtimeSrc, DimShowtime):
    showtimes = session_src.query(ShowtimeSrc).all()
    for s in showtimes:
        dim = DimShowtime(
            showtime_id=s.id,
            name=s.name,
            start_time=s.start_time,
            film_id=s.film_id,
            room_id=s.room_id
        )
        session_dest.merge(dim)
    session_dest.commit()
def etl_dim_promotion(session_src, session_dest, PromotionSrc, DimPromotion):
    promotions = session_src.query(PromotionSrc).all()
    for p in promotions:
        dim = DimPromotion(
            promotion_id=p.id,
            name=p.name,
            description=p.description,
            duration=p.duration
        )
        session_dest.merge(dim)
    session_dest.commit()
def get_time_id(dt: datetime):
    return dt.hour * 60 + dt.minute

def get_purchase_type_id(staff_id):
    return 1 if staff_id else 2
def map_payment_method_to_id(method_text: str) -> int:
    mapping = {
        "Thanh toán bằng tiền mặt": 1,
        "Thanh toán bằng thẻ tín dụng": 2,
        "Thanh toán bằng ví điện tử": 3
    }
    return mapping.get(method_text.strip(), None)

def etl_fact_ticket_analysis(session_src, session_dest, TicketSrc, BillSrc, FactTicketAnalysis):
    tickets = session_src.query(TicketSrc).join(BillSrc).all()
    for t in tickets:
        bill = t.bill
        fact = FactTicketAnalysis(
            ticket_id=t.id,
            bill_id=bill.id,
            price=t.price,
            date_id=t.created_at.date(),
            time_id=get_time_id(t.created_at),
            payment_method_id=map_payment_method_to_id(bill.payment_method),
            purchase_type_id=get_purchase_type_id(bill.staff_id)
        )
        session_dest.merge(fact)
    session_dest.commit()
def etl_fact_film_rating(session_src, session_dest, RateSrc, FactFilmRating):
    rates = session_src.query(RateSrc).all()
    for r in rates:
        fact = FactFilmRating(
            user_id=r.user_id,
            film_id=r.film_id,
            date_id=r.created_at.date(),
            point=r.point,
            detail=r.detail
        )
        session_dest.merge(fact)
    session_dest.commit()

def etl_fact_revenue(session_src, session_dest, BillSrc, FactRevenue):
    for b in session_src.query(BillSrc).all():
        st_seat = b.ticket.showtime_seat
        showtime = st_seat.showtime
        fact = FactRevenue(
            bill_id=b.id,
            date_id=b.payment_time.date(),
            time_id=get_time_id(b.payment_time),
            film_id=showtime.film_id,
            cinema_id=showtime.room.cinema_id,
            value=b.value,
            payment_method_id=map_payment_method_to_id(b.payment_method),
            purchase_type_id=get_purchase_type_id(b.staff_id)
        )
        session_dest.merge(fact)
    session_dest.commit()

def etl_fact_showtime_fillrate(session_src, session_dest, ShowtimeSrc, FactShowtimeFillRate):
    showtimes = session_src.query(ShowtimeSrc).all()
    for s in showtimes:
        total = len(s.showtime_seat)
        booked = sum(1 for ss in s.showtime_seat if ss.ticket is not None)
        if total == 0:
            continue
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
    session_dest.commit()

def etl_fact_promotion_analysis(session_src, session_dest, BillSrc, BillPromSrc, FactPromotionAnalysis):
    for b in session_src.query(BillSrc).all():
        used = session_src.query(BillPromSrc).filter(BillPromSrc.bill_id == b.id).count() > 0
        fact = FactPromotionAnalysis(
            bill_id=b.id,
            date_id=b.payment_time.date(),
            promotion_used=used
        )
        session_dest.merge(fact)
    session_dest.commit()