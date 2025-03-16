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