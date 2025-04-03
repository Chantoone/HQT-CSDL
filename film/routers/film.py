from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from film.models.film import Film
from film.schemas.film import *
import math


router = APIRouter(
    prefix="/film",
    tags=["Film"],
)


@router.get("/all",
            response_model=ListFilmResponse,
            status_code=status.HTTP_200_OK)
async def get_films(
        db: Session = Depends(get_db),
    ):

    try:
        films = db.query(Film).all()

        return ListFilmResponse(
            films=films,
            total_data=len(films)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/pageable",
            response_model=FilmPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_films_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db),
    ):
     
    try:
        total_count = db.query(Film).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        films = db.query(Film).offset(offset).limit(page_size).all()

        films_pageable_res = FilmPageableResponse(
            films=films,
            total_pages=total_pages,
            total_data=total_count
        )

        return films_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{film_id}",
            response_model=FilmResponse,
            status_code=status.HTTP_200_OK)
async def get_film(
        film_id: int,
        db: Session = Depends(get_db),
    ):
    
    try:
        film = db.query(Film).filter(Film.id == film_id).first()

        if film is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phim"
            )

        return film
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    


@router.post("/search",
            response_model=ListFilmResponse,
            status_code=status.HTTP_200_OK)
async def search_film(
        search: FilmSearch,
        db: Session = Depends(get_db),
    ):
    
    try:
        films = db.query(Film)
        if search.title:
            films = films.filter(Film.title.ilike(f"%{search.title}%"))
        if search.description:
            films = films.filter(Film.description.ilike(f"%{search.description}%"))
        if search.duration:
            films = films.filter(Film.duration == search.duration)
        if search.release_date:
            films = films.filter(Film.release_date == search.release_date)
        if search.author:
            films = films.filter(Film.author.ilike(f"%{search.author}%"))
        if search.status:
            films = films.filter(Film.status == search.status)
        if search.actors:
            films = films.filter(Film.actors.ilike(f"%{search.actors}%"))
        if search.director:
            films = films.filter(Film.director.ilike(f"%{search.director}%"))

        return ListFilmResponse(
            films=films,
            total_data=len(films)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/create",
             response_model=FilmResponse,
             status_code=status.HTTP_201_CREATED)
async def create_film(
        film: FilmCreate,
        db: Session = Depends(get_db),
    ):
    
    try:
        film = Film(
            title=film.title,
            description=film.description,
            duration=film.duration,
            release_date=film.release_date,
            author=film.author,
            poster_path=film.poster_path, 
            status=film.status,
        )
        
        db.add(film)
        db.commit()
        db.refresh(film)

        return film
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/update/{film_id}",
            response_model=FilmResponse,
            status_code=status.HTTP_200_OK)
async def update_film(
        film_id: int,
        film: FilmUpdate,
        db: Session = Depends(get_db),
    ):
    
    try:
        db_film = db.query(Film).filter(Film.id == film_id).first()

        if db_film is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phim không tồn tại"
            )

        update_data = film.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_film, key, value)

        db.commit()
        db.refresh(db_film)

        return db_film
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete/{film_id}",
               status_code=status.HTTP_200_OK)
async def delete_film(
        film_id: int,
        db: Session = Depends(get_db),
    ):
    
    try:
        film = db.query(Film).filter(Film.id == film_id).first()

        if film is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phim không tồn tại"
            )

        db.delete(film)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete-many",
               status_code=status.HTTP_200_OK)
async def delete_films(
        film_ids: List[int],
        db: Session = Depends(get_db),
    ):
    
    try:
        films = db.query(Film).filter(Film.id.in_(film_ids)).all()

        if len(films) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phim"
            )

        for film in films:
            db.delete(film)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all",
               status_code=status.HTTP_200_OK)
async def delete_all_films(
        db: Session = Depends(get_db),
    ):
    
    try:
        db.query(Film).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )