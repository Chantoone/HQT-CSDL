from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from cinema.models.cinema import Cinema
from cinema.schemas.cinema import *
import math

from room.models.room import Room
from showtime.models.showtime import Showtime


router = APIRouter(
    prefix="/cinema",
    tags=["Cinema"],
)


@router.get("/all",
            response_model=ListCinemaResponse,
            status_code=status.HTTP_200_OK)
async def get_cinemas(
        db: Session = Depends(get_db),
    ):

    try:
        cinemas = db.query(Cinema).all()

        return ListCinemaResponse(
            cinemas=cinemas,
            total_data=len(cinemas)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/pageable",
            response_model=CinemaPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_cinemas_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db),
    ):
     
    try:
        total_count = db.query(Cinema).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        cinemas = db.query(Cinema).offset(offset).limit(page_size).all()

        cinemas_pageable_res = CinemaPageableResponse(
            cinemas=cinemas,
            total_pages=total_pages,
            total_data=total_count
        )

        return cinemas_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{id}",
            response_model=CinemaResponse,
            status_code=status.HTTP_200_OK)
async def get_cinema(
        id: int,
        db: Session = Depends(get_db),
    ):

    try:
        cinema = db.query(Cinema).filter(Cinema.id == id).first()

        if cinema is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rạp chiếu phim không tồn tại"
            )

        return cinema
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/search",
            response_model=ListCinemaResponse,
            status_code=status.HTTP_200_OK)
async def search_cinemas(
        cinema_data: CinemaSearch,
        db: Session = Depends(get_db),
    ):

    try:
        cinemas = db.query(Cinema)
        if cinema_data.name:
            cinemas = cinemas.filter(Cinema.name.ilike(f"%{cinema_data.name}%"))
        if cinema_data.address:
            cinemas = cinemas.filter(Cinema.address.ilike(f"%{cinema_data.address}%"))
        if cinema_data.phone_number:
            cinemas = cinemas.filter(Cinema.phone_number.ilike(f"%{cinema_data.phone_number}%"))
        if cinema_data.is_active:
            cinemas = cinemas.filter(Cinema.is_active == cinema_data.is_active)
        cinemas = cinemas.all()

        return ListCinemaResponse(
            cinemas=cinemas,
            total_data=len(cinemas)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/create",
             response_model=CinemaResponse,
             status_code=status.HTTP_201_CREATED)
async def create_cinema(
        cinema_data: CinemaCreate,
        db: Session = Depends(get_db),
    ):

    try:
        cinema = Cinema(
            name=cinema_data.name,
            address=cinema_data.address,
            phone_number=cinema_data.phone_number,
            is_active=True
        )

        db.add(cinema)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Tạo rạp chiếu phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/update/{id}",
            response_model=CinemaResponse,
            status_code=status.HTTP_200_OK)
async def update_cinema(
        id: int,
        cinema_data: CinemaUpdate,
        db: Session = Depends(get_db),
    ):

    try:
        cinema = db.query(Cinema).filter(Cinema.id == id).first()

        if cinema is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rạp chiếu phim không tồn tại"
            )

        cinema.name = cinema_data.name
        cinema.address = cinema_data.address
        cinema.phone_number = cinema_data.phone_number

        db.commit()
        db.refresh(cinema)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Cập nhật rạp chiếu phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete/{id}",
               status_code=status.HTTP_200_OK)
async def delete_cinema(
        id: int,
        db: Session = Depends(get_db),
    ):

    try:
        cinema = db.query(Cinema).filter(Cinema.id == id).first()

        if cinema is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rạp chiếu phim không tồn tại"
            )

        db.delete(cinema)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa rạp chiếu phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete-many",
            status_code=status.HTTP_200_OK)
async def delete_cinemas(
        ids: list[int],
        db: Session = Depends(get_db),
    ):

    try:
        cinemas = db.query(Cinema).filter(Cinema.id.in_(ids))
        if not cinemas.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Rạp chiếu phim không tồn tại"
            )
        cinemas.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa rạp chiếu phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete-all",
            status_code=status.HTTP_200_OK)
async def delete_all_cinemas(
        db: Session = Depends(get_db),
    ):

    try:
        db.query(Cinema).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả rạp chiếu phim thành công"}
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/by-film/{film_id}", 
            response_model=List[CinemaResponse])
def get_cinemas_by_film_id(
    film_id: int, 
    db: Session = Depends(get_db)
):
    film_exists = db.query(Showtime).filter(Showtime.film_id == film_id).first()
    if not film_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No showtimes found for film with id: {film_id}")

    cinemas = db.query(Cinema).join(
        Room, Room.cinema_id == Cinema.id
    ).join(
        Showtime, Showtime.room_id == Room.id
    ).filter(
        Showtime.film_id == film_id
    ).distinct().all()
    
    if not cinemas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No cinemas showing film with id: {film_id}")
    
    return cinemas