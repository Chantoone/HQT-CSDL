from typing import List
from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from cinema.models.cinema import Cinema
from configs.database import get_db
from configs.authentication import get_current_user
from room.models.room import Room
from room.schemas.room import *
import math

from seat.models.seat import Seat

router = APIRouter(
    prefix='/rooms',
    tags=['Rooms']
)

@router.post("/")
def create_room(room_data: RoomCreate, db: Session = Depends(get_db)):
    # Tạo phòng
    new_room = Room(
        name=room_data.name,
        detail=room_data.detail,
        capacity=room_data.capacity,
        cinema_id=room_data.cinema_id,
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    lenrow=room_data.capacity//10
    # Tạo ghế (A1-A10 đến F1-F10)
    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    seats = []
    for row in range(lenrow):
        for num in range(1, 11):  # A1-A10
            seat_number = f"{rows[row]}{num}"
            seats.append(
                Seat(seat_number=seat_number, room_id=new_room.id)
            )

    db.add_all(seats)
    db.commit()

    return {"message": "Phòng và các ghế đã được tạo thành công", "room_id": new_room.id}
@router.get('/', 
            response_model=ListRoomResponse, 
            status_code=status.HTTP_200_OK)
def get_all_rooms(
        db: Session = Depends(get_db)
    ):
    
    try:
        rooms = db.query(Room).all()

        return ListRoomResponse(
            rooms=rooms,
            total_data=len(rooms)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.get('/pageable',
            response_model=RoomPageableResponse,
            status_code=status.HTTP_200_OK)
def get_rooms_pageable(
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
    ):
    
    try:
        total_data = db.query(func.count(Room.id)).scalar()
        total_page = math.ceil(total_data / size)
        offset = (page - 1) * size

        rooms = db.query(Room).offset(offset).limit(size).all()

        return RoomPageableResponse(
            rooms=rooms,
            total_data=total_data,
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )

@router.get('/by-cinema-id/{cinema_id}',
            response_model=ListRoomResponse,
            status_code=status.HTTP_200_OK)
def get_room_by_cinema_id(
        cinema_id: int,
        db: Session = Depends(get_db)
    ):
    
    try:
        room = db.query(Room).filter(Room.cinema_id == cinema_id).all()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Room not found'
            )

        return ListRoomResponse(
            rooms=room,
            total_data=len(room)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )



@router.get('/{room_id}',
            response_model=RoomResponse,
            status_code=status.HTTP_200_OK)
def get_room_by_id(
        room_id: int,
        db: Session = Depends(get_db)
    ):
    
    try:
        room = db.query(Room).filter(Room.id == room_id).first()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Room not found'
            )

        return room
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.post('/search',
            response_model=ListRoomResponse,
            status_code=status.HTTP_200_OK)
def search_rooms(
        room: RoomSearch,
        db: Session = Depends(get_db)
    ):
    
    try:
        query = db.query(Room)

        if room.name:
            query = query.filter(Room.name.ilike(f'%{room.name}%'))
        if room.detail:
            query = query.filter(Room.detail.ilike(f'%{room.detail}%'))
        if room.capacity:
            query = query.filter(Room.capacity == room.capacity)
        if room.is_active:
            query = query.filter(Room.is_active == room.is_active)
        if room.cinema_id:
            query = query.filter(Room.cinema_id == room.cinema_id)

        rooms = query.all()

        return ListRoomResponse(
            rooms=rooms,
            total_data=len(rooms)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.post('/create',   
            response_model=RoomResponse) 
def create_room(
        room: RoomCreate,
        db: Session = Depends(get_db),
    ):
    
    try:
        cinema = db.query(Cinema).filter(Cinema.id == room.cinema_id).first()
        if not cinema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cinema not found!"
            )

        new_room = Room(**room.dict())

        db.add(new_room)
        db.commit()

        return JSONResponse(
            content={'message': 'Room created successfully'},
            status_code=status.HTTP_201_CREATED
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.put('/update/{room_id}',
            response_model=RoomResponse)
def update_room(
        room_id: int,
        room: RoomUpdate,
        db: Session = Depends(get_db),
    ):
    
    try:
        room_up = db.query(Room).filter(Room.id == room_id)

        if not room_up.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Room not found'
            )
        
        if room.cinema_id:
            cinema = db.query(Cinema).filter(Cinema.id == room.cinema_id).first()
            if not cinema:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Cinema not found'
                )

        room_up.update(room.dict(exclude_unset=True))
        db.commit()

        return JSONResponse(
            content={'message': 'Room updated successfully'},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.delete('/delete/{room_id}')
def delete_room(
        room_id: int,
        db: Session = Depends(get_db),
    ):
    
    try:
        room = db.query(Room).filter(Room.id == room_id).first()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Room not found'
            )

        db.query(Room).filter(Room.id == room_id).delete()
        db.commit()

        return JSONResponse(
            content={'message': 'Room deleted successfully'},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    

@router.delete('/delete-many')
def delete_many_rooms(
        rooms: List[int],
        db: Session = Depends(get_db),
    ):
    
    try:
        db.query(Room).filter(Room.id.in_(rooms)).delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            content={'message': 'Rooms deleted successfully'},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )