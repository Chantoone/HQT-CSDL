from typing import List
from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from cinema.models.cinema import Cinema
from configs.database import get_db
from configs.authentication import get_current_user
from film.models.film import Film
from room.models.room import Room
from showtime.models.showtime import Showtime
from showtime.schemas.showtime import *
import math
from datetime import date,datetime
from babel.dates import format_date
from seat.models.seat import Seat
from showtime_seat.models.showtime_seat import ShowtimeSeat

router = APIRouter(
    prefix="/showtimes",
    tags=["Showtime"],
)


@router.get("/all", 
            response_model=ListShowtimeResponse,
            status_code=status.HTTP_200_OK)
def get_all_showtimes(
        db: Session = Depends(get_db)
    ):
    try:
        showtimes = db.query(Showtime).all()
        
        return ListShowtimeResponse(
            showtimes=showtimes,
            total_data=len(showtimes)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.get("/pageable", 
            response_model=ShowtimePageableResponse, 
            status_code=status.HTTP_200_OK)
def get_showtimes_pageable(
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
    ):
    try:
        total_data = db.query(func.count(Showtime.id)).scalar()
        total_page = math.ceil(total_data / size)
        offset = (page - 1) * size

        showtimes = db.query(Showtime).offset(offset).limit(size).all()

        return ShowtimePageableResponse(
            showtimes=showtimes,
            total_data=total_data,
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.get("/dates-by-cinema-and-film", response_model=List[ShowtimeByDateResponse])
def get_dates_by_cinema_and_film(
    cinema_id: int,
    film_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all available dates for a specific cinema and film, along with showtimes.
    """
    try:
        # Truy vấn Cinema và đảm bảo rằng Cinema tồn tại
        cinema = db.query(Cinema).filter(Cinema.id == cinema_id).first()
        if not cinema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Cinema with id {cinema_id} not found"
            )
        
        # Truy vấn Film và đảm bảo rằng Film tồn tại
        film = db.query(Film).filter(Film.id == film_id).first()
        if not film:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Film with id {film_id} not found"
            )
        
        # Truy vấn các Showtimes liên kết với Cinema và Film
        showtimes = db.query(Showtime).join(Room).filter(
            Showtime.film_id == film_id,
            Room.cinema_id == cinema_id
        ).all()

        if not showtimes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No showtimes available for film {film_id} in cinema {cinema_id}"
            )

        # Tạo dictionary chứa thông tin về các ngày chiếu
        date_dict = {}
        for showtime in showtimes:
            show_date = showtime.start_time.date()
            # Skip dates in the past (optional)
            if show_date < date.today():
                continue
                
            if show_date not in date_dict:
                date_dict[show_date] = {'showtimes': [], 'showtime_count': 0}

            date_dict[show_date]['showtimes'].append(showtime)
            date_dict[show_date]['showtime_count'] += 1
        
        # Convert dictionary to list of ShowtimeByDateResponse objects
        available_dates = [
            ShowtimeByDateResponse(
                date=date_key,
                date_formatted=format_date(date_key, format='full', locale='vi_VN'),
                showtime_count=date_info['showtime_count'],
            )
            for date_key, date_info in sorted(date_dict.items())
        ]
        
        return available_dates

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "/showtimes-by-date", 
    response_model=List[ShowtimeWithTimeResponse]
)
def get_showtimes_by_date(
    cinema_id: int,
    film_id: int,
    target_date: date,  # yyyy-mm-dd
    db: Session = Depends(get_db)
):
    """
    Get all showtimes for a specific film and cinema on a given date
    """
    try:
        # Truy vấn để lấy danh sách showtimes theo cinema_id, film_id, và target_date
        showtimes = db.query(Showtime).join(Room).filter(
            Showtime.film_id == film_id,
            Room.cinema_id == cinema_id,
            func.date(Showtime.start_time) == target_date
        ).order_by(Showtime.start_time).all()

        if not showtimes:
            raise HTTPException(
                status_code=404,
                detail=f"No showtimes found for the selected date"
            )

        # Chuyển đổi dữ liệu showtimes thành danh sách các ShowtimeWithTimeResponse
        results = [
            ShowtimeWithTimeResponse(
                showtime=showtime,
                time_only=showtime.start_time.strftime("%H:%M")
            )
            for showtime in showtimes
        ]

        return results

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )

@router.get(
    "/times-by-cinema-film-date", 
    response_model=List[dict], 
    status_code=status.HTTP_200_OK
)
def get_times_by_cinema_film_date(
    cinema_id: int,
    film_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    """
    Get all showtimes (time and id) for a specific cinema, film, and date,
    where the time is greater than the current time.
    """
    try:
        current_time = datetime.now()
        # Query showtimes based on cinema_id, film_id, and target_date
        showtimes = db.query(Showtime).join(Room).filter(
            Showtime.film_id == film_id,
            Room.cinema_id == cinema_id,
            func.date(Showtime.start_time) == date,
            Showtime.start_time > current_time
        ).order_by(Showtime.start_time).all()

        if not showtimes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No showtimes found for the selected cinema, film, and date"
            )

        # Return a list of dictionaries with id_showtime and time
        results = [
            {"id_showtime": showtime.id, "time": showtime.start_time.strftime("%H:%M")}
            for showtime in showtimes
        ]
        return results

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )



@router.get("/{showtime_id}", 
            response_model=ShowtimeResponse, 
            status_code=status.HTTP_200_OK)
def get_showtime_by_id(
        showtime_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        
        if showtime is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Showtime not found"}
            )
        
        return ShowtimeResponse(
            showtime=showtime
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/search", 
             response_model=ListShowtimeResponse, 
             status_code=status.HTTP_200_OK)
def search_showtime(
        search: ShowtimeSearch,
        db: Session = Depends(get_db)
    ):
    try:
        showtimes = db.query(Showtime)
        if search.name:
            showtimes = showtimes.filter(Showtime.name.ilike(f"%{search.name}%"))
        if search.start_time:
            showtimes = showtimes.filter(Showtime.start_time == search.start_time)
        if search.film_id:
            showtimes = showtimes.filter(Showtime.film_id == search.film_id)
        if search.room_id:
            showtimes = showtimes.filter(Showtime.room_id == search.room_id)
        
        return ListShowtimeResponse(
            showtimes=showtimes,
            total_data=len(showtimes)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/create")
def create_showtime(
        showtime: ShowtimeCreate,
        db: Session = Depends(get_db)
    ):
    try:
        db_showtime = db.query(Showtime).filter(
            Showtime.name == showtime.name
        ).first()

        # if db_showtime:
        #     return JSONResponse(
        #         status_code=status.HTTP_409_CONFLICT,
        #         content={"message": "Showtime already exists"}
        #     )
        
        film = db.query(Film).filter(Film.id == showtime.film_id).first()
        if not film:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Film not found"}
            )
        
        room = db.query(Room).filter(Room.id == showtime.room_id).first()
        if not room:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Room not found"}
            )

        new_showtime = Showtime(
            name=showtime.name,
            start_time=showtime.start_time, 
            film_id=showtime.film_id,
            room_id=showtime.room_id
        )
        
        db.add(new_showtime)
        db.commit()
        db.refresh(new_showtime)

        # Automatically create showtime_seat entries for the room
        seats = db.query(Seat).filter(Seat.room_id == room.id).all()
        for seat in seats:
            new_showtime_seat = ShowtimeSeat(
                seat_id=seat.id,
                showtime_id=new_showtime.id,
                seat_status=True
            )
            db.add(new_showtime_seat)

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Showtime and associated seats created successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.put("/{showtime_id}", 
            response_model=ShowtimeResponse)
def update_showtime(
        showtime_id: int,
        showtime: ShowtimeUpdate,
        db: Session = Depends(get_db)
    ):
    try:
        showtime_data = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        
        if showtime_data is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Showtime not found"}
            )
        
        if showtime.name:
            showtime_data.name = showtime.name
        if showtime.start_time:
            showtime_data.start_time = showtime.start_time
        if showtime.film_id:
            film = db.query(Film).filter(Film.id == showtime.film_id).first()
            if not film:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"message": "Film not found"}
                )
            showtime_data.film_id = showtime.film_id
        if showtime.room_id:
            room = db.query(Room).filter(Room.id == showtime.room_id).first()
            if not room:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"message": "Room not found"}
                )
            showtime_data.room_id = showtime.room_id
        
        db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Showtime updated successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete-many")
def delete_many_showtimes(
        showtimes: List[int],
        db: Session = Depends(get_db)
    ):
    try:
        db.query(Showtime).filter(Showtime.id.in_(showtimes)).delete(synchronize_session=False)
        db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Showtimes deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete-all")
def delete_many_showtimes(
        db: Session = Depends(get_db)
    ):
    try:
        db.query(Showtime).delete(synchronize_session=False)
        db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Showtimes deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/{showtime_id}")
def delete_showtime(
        showtime_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        
        if showtime is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Showtime not found"}
            )
        
        db.delete(showtime)
        db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Showtime deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

