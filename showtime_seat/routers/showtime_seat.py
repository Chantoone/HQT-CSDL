from typing import List
from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.database import get_db
from configs.authentication import get_current_user
from seat.models.seat import Seat
from showtime.models.showtime import Showtime
from showtime_seat.models.showtime_seat import ShowtimeSeat
from showtime_seat.schemas.showtime_seat import *
import math


router = APIRouter(
    prefix="/showtime_seat",
    tags=["Showtime Seat"]
)


@router.get("/", 
            response_model=ListShowtimeSeatResponse, 
            status_code=status.HTTP_200_OK)
async def get_all_showtime_seats(
        db: Session = Depends(get_db)
    ):
    try:
        showtime_seats = db.query(ShowtimeSeat).all()

        return ListShowtimeSeatResponse(
            showtime_seats=showtime_seats,
            total_data=len(showtime_seats)
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.get("/pageable",
            response_model=ShowtimeSeatPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_all_showtime_seats_pageable(
        page: int = 1,
        limit: int = 10,
        db: Session = Depends(get_db)
    ):
    try:
        showtime_seats = db.query(ShowtimeSeat).all()

        if not showtime_seats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime seats not found"
            )

        total_data = len(showtime_seats)
        total_page = math.ceil(total_data / limit)

        showtime_seats = db.query(ShowtimeSeat).offset((page - 1) * limit).limit(limit).all()

        return ShowtimeSeatPageableResponse(
            showtime_seats=showtime_seats,
            total_data=total_data,
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.get("/seats-by-showtime/{showtime_id}", response_model=List[SeatWithStatus])
def get_seats_by_showtime(showtime_id: int, db: Session = Depends(get_db)):
    try:
        # Join ShowtimeSeat + Seat để lấy thông tin ghế và trạng thái
        results = (
            db.query(Seat, ShowtimeSeat)
            .join(ShowtimeSeat, Seat.id == ShowtimeSeat.seat_id)
            .filter(ShowtimeSeat.showtime_id == showtime_id)
            .all()
        )

        seats_with_status = [
            SeatWithStatus(
                showtime_seat_id=showtimeseat.id,
                seat_number=seat.seat_number,
                seat_status=showtimeseat.seat_status,
            )
            for seat, showtimeseat in results
        ]

        return seats_with_status

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )


@router.get("/{showtime_seat_id}",
            response_model=ShowtimeSeatResponse,
            status_code=status.HTTP_200_OK) 
async def get_showtime_seat_by_id(
        showtime_seat_id: int,
        db: Session = Depends(get_db)
    ):

    try:
        showtime_seat = db.query(ShowtimeSeat).filter(ShowtimeSeat.id == showtime_seat_id).first()

        if not showtime_seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime seat not found"
            )

        return showtime_seat
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/search",
            response_model=ListShowtimeSeatResponse,
            status_code=status.HTTP_200_OK)
async def search_showtime_seat(
        showtime_seat: ShowtimeSeatSearch,
        db: Session = Depends(get_db)
    ):

    try:
        showtime_seats = db.query(ShowtimeSeat)
        if showtime_seat.seat_id:
            showtime_seats = showtime_seats.filter(ShowtimeSeat.seat_id == showtime_seat.seat_id)
        if showtime_seat.showtime_id:
            showtime_seats = showtime_seats.filter(ShowtimeSeat.showtime_id == showtime_seat.showtime_id)
        if showtime_seat.seat_status is not None:
            showtime_seats = showtime_seats.filter(ShowtimeSeat.seat_status == showtime_seat.seat_status)

        if not showtime_seats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime seats not found"
            )

        return ListShowtimeSeatResponse(
            showtime_seats=showtime_seats,
            total_data=len(showtime_seats)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/create",
             status_code=status.HTTP_201_CREATED)
async def create_showtime_seat(
        showtime_seat: ShowtimeSeatCreate,
        db: Session = Depends(get_db)
    ):
    try:

        seat = db.query(Seat).filter(Seat.id == showtime_seat.seat_id).first()
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found"
            )
        
        showtime = db.query(Showtime).filter(Showtime.id == showtime_seat.showtime_id).first()
        if not showtime:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime not found"
            )

        new_showtime_seat = ShowtimeSeat(
            seat_status=showtime_seat.seat_status,
            seat_id=showtime_seat.seat_id,
            showtime_id=showtime_seat.showtime_id
        )

        db.add(new_showtime_seat)
        db.commit()
        db.refresh(new_showtime_seat)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Showtime seat created successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.put("/update/{showtime_seat_id}",
            response_model=ShowtimeSeatResponse,
            status_code=status.HTTP_200_OK)
async def update_showtime_seat(
        showtime_seat_id: int,
        showtime_seat: ShowtimeSeatUpdate,
        db: Session = Depends(get_db)
    ):

    try:
        showtime_seat_data = db.query(ShowtimeSeat).filter(ShowtimeSeat.id == showtime_seat_id).first()

        if not showtime_seat_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime seat not found"
            )

        if showtime_seat.seat_id:
            seat = db.query(Seat).filter(Seat.id == showtime_seat.seat_id).first()
            if not seat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Seat not found"
                )
        
        if showtime_seat.showtime_id:
            showtime = db.query(Showtime).filter(Showtime.id == showtime_seat.showtime_id).first()
            if not showtime:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Showtime not found"
                )

        for key, value in showtime_seat.dict(exclude_unset=True).items():
            setattr(showtime_seat_data, key, value)

        db.commit()
        db.refresh(showtime_seat_data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Showtime seat updated successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete/{showtime_seat_id}",
            status_code=status.HTTP_200_OK)
async def delete_showtime_seat(
        showtime_seat_id: int,
        db: Session = Depends(get_db)
    ):

    try:
        showtime_seat = db.query(ShowtimeSeat).filter(ShowtimeSeat.id == showtime_seat_id).first()

        if not showtime_seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime seat not found"
            )

        db.delete(showtime_seat)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Showtime seat deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete-many")
async def delete_many_showtime_seats(
        showtime_seat_ids: List[int],
        db: Session = Depends(get_db)
    ):
    try:
        showtime_seats = db.query(ShowtimeSeat).filter(ShowtimeSeat.id.in_(showtime_seat_ids)).all()

        if not showtime_seats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime seats not found"
            )

        for showtime_seat in showtime_seats:
            db.delete(showtime_seat)

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Showtime seats deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )