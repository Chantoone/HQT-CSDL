import math
from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.database import get_db
from configs.authentication import get_current_user
from seat.models.seat import Seat
from seat.schemas.seat import *

router = APIRouter(
    prefix="/seats",
    tags=["Seats"],
)


@router.get("/all", 
            response_model=ListSeatResponse,
            status_code=status.HTTP_200_OK)
def get_all_seats(
        db: Session = Depends(get_db)
    ):
    try:
        seats = db.query(Seat).all()

        return ListSeatResponse(
            seats=seats,
            total_data=len(seats)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.get("/pagealbe", 
            response_model=SeatPageableResponse, 
            status_code=status.HTTP_200_OK)
def get_seats_pageable(
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
    ):
    try:
        total_data = db.query(func.count(Seat.id)).scalar()
        total_page = math.ceil(total_data / size)
        offset = (page - 1) * size

        seats = db.query(Seat).limit(size).offset(offset).all()

        return SeatPageableResponse(
            seats=seats,
            total_data=total_data, 
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )


@router.get("/{seat_id}", 
            response_model=SeatResponse, 
            status_code=status.HTTP_200_OK)
def get_seat_by_id(
        seat_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).first()

        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found"
            )

        return seat
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.post("/search",
            response_model=ListSeatResponse,
            status_code=status.HTTP_200_OK)
def search_seats(
        seat: SeatSearch,
        db: Session = Depends(get_db)
    ):
    try:
        seats = db.query(Seat)
        if seat.seat_number:
            seats = seats.filter(Seat.seat_number.ilike(f"%{seat.seat_number}%"))
        if seat.detail:
            seats = seats.filter(Seat.detail.ilike(f"%{seat.detail}%"))
        if seat.is_active:
            seats = seats.filter(Seat.is_active == seat.is_active)

        seats = seats.all()

        return ListSeatResponse(
            seats=seats,
            total_data=len(seats)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.post("/create", 
             response_model=SeatResponse)
def create_seat(
        seat: SeatCreate,
        db: Session = Depends(get_db)
    ):
    try:
        db_seat = db.query(Seat).filter(Seat.seat_number == seat.seat_number).first()
        if db_seat:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Seat already exists"
            )
        
        new_seat = Seat(**seat.dict())
        db.add(new_seat)
        db.commit()
        db.refresh(new_seat)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Seat created successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.put("/update/{seat_id}")
def update_seat(
        seat_id: int,
        seat: SeatUpdate,
        db: Session = Depends(get_db)
    ):
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).first()

        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found"
            )

        db.query(Seat).filter(Seat.id == seat_id).update(seat.dict())
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Seat updated successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.delete("/delete/{seat_id}")
def delete_seat(
        seat_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).first()

        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found"
            )

        db.query(Seat).filter(Seat.id == seat_id).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Seat deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.delete("/delete-many")
def delete_seats(
        seat_ids: List[int],
        db: Session = Depends(get_db)
    ):
    try:
        seats = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()

        if not seats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seats not found"
            )

        db.query(Seat).filter(Seat.id.in_(seat_ids)).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Seats deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    