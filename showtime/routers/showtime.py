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
from ticket.models.ticket import Ticket

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
    

@router.get("/available-dates", response_model=List[AvailableDateResponse])
def get_available_dates(
    film_id: int, 
    cinema_id: int, 
    db: Session = Depends(get_db)
):
    film = db.query(Film).filter(Film.id == film_id).first()
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Film with id {film_id} not found")
    
    rooms = db.query(Room).filter(Room.cinema_id == cinema_id).all()
    if not rooms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Theater with id {cinema_id} not found or has no rooms")
    
    room_ids = [room.id for room in rooms]
    
    date_query = db.query(
        func.date(Showtime.start_time).label("show_date")
    ).filter(
        Showtime.film_id == film_id,
        Showtime.room_id.in_(room_ids)
    ).distinct().order_by("show_date").all()

    if not date_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No showtimes available for film {film_id} at theater {cinema_id}")
    
    # Format the response
    available_dates = []
    for date_row in date_query:
        show_date = date_row.show_date
        # Skip dates in the past
        if show_date < date.today():
            continue
            
        # Get count of showtimes on this date
        showtime_count = db.query(Showtime).filter(
            Showtime.film_id == film_id,
            Showtime.room_id.in_(room_ids),
            func.date(Showtime.start_time) == show_date
        ).count()
        
        # Tạo đối tượng AvailableDateResponse thay vì dictionary
        available_dates.append(AvailableDateResponse(
            date=show_date,
            date_formatted=show_date.strftime("%A, %d %B %Y"),
            showtime_count=showtime_count
        ))
    
    return available_dates


@router.get("/available-times", response_model=List[AvailableTimeResponse])
def get_available_times(
    film_id: int,
    cinema_id: int,
    show_date: date,
    db: Session = Depends(get_db)
):
    """
    Get all available showtime hours for a specific film at a specific theater on a specific date.
    This endpoint should be called after selecting a film, theater, and date.
    """
    # Validate film exists
    film = db.query(Film).filter(Film.id == film_id).first()
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f"Film with id {film_id} not found")
    
    # Get all rooms that belong to the cinema
    rooms = db.query(Room).filter(Room.cinema_id == cinema_id).all()
    if not rooms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f"Cinema with id {cinema_id} not found or has no rooms")
    
    room_ids = [room.id for room in rooms]
    
    # Find all showtimes for this film in this cinema on this date
    showtimes = db.query(Showtime).filter(
        Showtime.film_id == film_id,
        Showtime.room_id.in_(room_ids),
        func.date(Showtime.start_time) == show_date
    ).order_by(Showtime.start_time).all()
    
    if not showtimes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f"No showtimes available for film {film_id} at cinema {cinema_id} on {show_date}")
    
    # Format the response
    available_times = []
    for showtime in showtimes:
        # Get room details
        room = db.query(Room).filter(Room.id == showtime.room_id).first()
        
        # For each showtime, collect detailed information
        available_times.append(AvailableTimeResponse(
            id=showtime.id,
            start_time=showtime.start_time,
            time_formatted=showtime.start_time.strftime("%H:%M"),
            room_name=room.name,
            room_detail=room.detail,
            room_capacity=room.capacity,
            available_seats=calculate_available_seats(showtime.id, db)  # Implement this function
        ))
    
    return available_times

def calculate_available_seats(showtime_id: int, db: Session):
    """
    Calculate how many seats are still available for a specific showtime.
    This is done by counting how many tickets have been booked for this showtime
    and subtracting from the room's capacity.
    """
    # Get the showtime
    showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
    if not showtime:
        return 0
    
    # Get the room capacity
    room = db.query(Room).filter(Room.id == showtime.room_id).first()
    room_capacity = room.capacity
    
    # Count booked tickets for this showtime
    # Assuming you have a Ticket model with a showtime_id field
    booked_tickets = db.query(func.count(Ticket.id)).filter(Ticket.showtime_id == showtime_id).scalar()
    
    # Calculate available seats
    available_seats = room_capacity - booked_tickets
    
    return available_seats


@router.get("/{showtime_id}/seats", response_model=SeatsResponse)
def get_showtime_seats(
    showtime_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all seats with their status (booked or available) for a specific showtime.
    This endpoint should be called after selecting a specific showtime.
    """
    # Validate showtime exists
    showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
    if not showtime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Showtime with id {showtime_id} not found"
        )
    
    # Get the room info
    room = db.query(Room).filter(Room.id == showtime.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {showtime.room_id} not found"
        )
    
    # Get the film info
    film = db.query(Film).filter(Film.id == showtime.film_id).first()
    
    # Get all booked tickets for this showtime
    booked_tickets = db.query(Ticket).filter(
        Ticket.showtime_id == showtime_id
    ).all()
    
    # Create a set of booked seat IDs for easier lookup
    booked_seat_ids = {ticket.seat_id for ticket in booked_tickets}
    
    # Generate all seats for the room
    total_seats = room.capacity
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]  # Adjust based on your cinema layout
    seats_per_row = math.ceil(total_seats / len(rows))
    
    # Generate all seats
    seat_rows = []
    seat_count = 1
    for row_letter in rows:
        row_seats = []
        for seat_num in range(1, seats_per_row + 1):
            if seat_count <= total_seats:
                seat_id = f"{row_letter}{seat_num}"
                is_booked = seat_id in booked_seat_ids
                
                # Calculate price based on location
                price = calculate_seat_price(row_letter, seat_num, seats_per_row)
                
                row_seats.append(SeatInfo(
                    id=seat_id,
                    row=row_letter,
                    number=seat_num,
                    is_booked=is_booked,
                    price=price
                ))
                seat_count += 1
        
        if row_seats:
            seat_rows.append(SeatRow(
                row=row_letter,
                seats=row_seats
            ))
    
    # Calculate available seats
    available_seats = total_seats - len(booked_seat_ids)
    
    return SeatsResponse(
        showtime_id=showtime_id,
        film_title=film.title if film else "Unknown Film",
        cinema_name=room.cinema.name if hasattr(room, 'cinema') else "Unknown Cinema",
        room_name=room.name,
        start_time=showtime.start_time,
        time_formatted=showtime.start_time.strftime("%H:%M, %A, %d %B %Y"),
        total_seats=total_seats,
        available_seats=available_seats,
        rows=seat_rows
    )

def calculate_seat_price(row: str, seat_num: int, seats_per_row: int):
    """
    Calculate the price for a specific seat based on its position.
    You can customize this based on your pricing strategy.
    """
    # Base price
    base_price = 100000  # 100K VND
    
    # Premium for specific rows
    row_premium = {
        "A": 0,      # Front row (may be too close to screen)
        "B": 20000,  
        "C": 30000,
        "D": 40000,  # Middle rows (premium)
        "E": 40000,
        "F": 30000,
        "G": 20000,
        "H": 10000   # Back rows
    }
    
    # Premium for center seats in a row
    middle_seat = seats_per_row // 2
    distance_from_middle = abs(seat_num - middle_seat)
    
    # The closer to the middle, the higher the premium
    center_premium = max(0, 20000 - 4000 * distance_from_middle)  # Up to 20K extra
    
    # Final price (adjust the values as needed)
    final_price = base_price + row_premium.get(row, 0) + center_premium
    
    return final_price
    

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
    

@router.post("/create", 
             response_model=ShowtimeResponse)
def create_showtime(
        showtime: ShowtimeCreate,
        db: Session = Depends(get_db)
    ):
    try:
        film = db.query(Film).filter(Film.id == showtime.film_id).first()
        if film is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Film not found"}
            )
        
        room = db.query(Room).filter(Room.id == showtime.room_id).first()
        if room is None:
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
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Showtime created successfully"}
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
            showtime_data.film_id = showtime.film_id
        if showtime.room_id:
            showtime_data.room_id = showtime.room_id
        
        db.commit()
        db.refresh(showtime_data)
        
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
    