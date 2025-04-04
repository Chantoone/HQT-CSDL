from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from film_genre.models.film_genre import FilmGenre
from film_genre.schemas.film_genre import *
from film.models.film import Film
import math
from genre.models.genre import Genre
import random

router = APIRouter(
    prefix="/film_genre",
    tags=["FilmGenre"],
)


@router.get("/all",
            response_model=ListFilmGenreResponse,
            status_code=status.HTTP_200_OK)
async def get_film_genres(
        db: Session = Depends(get_db),
    ):

    try:
        film_genres = db.query(FilmGenre).all()

        return ListFilmGenreResponse(
            film_genres=film_genres,
            total_data=len(film_genres)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/pageable",
            response_model=FilmGenreResponse,
            status_code=status.HTTP_200_OK)
async def get_film_genres_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db),
    ):

    try:
        total_count = db.query(FilmGenre).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        film_genres = db.query(FilmGenre).offset(offset).limit(page_size).all()

        film_genres_pageable_res = FilmGenrePageableResponse(
            film_genres=film_genres,
            total_pages=total_pages,
            total_data=total_count
        )

        return film_genres_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{film_genre_id}",
            response_model=FilmGenreResponse,
            status_code=status.HTTP_200_OK)
async def get_film_genre(
        film_genre_id: int,
        db: Session = Depends(get_db),
    ):

    try:
        film_genre = db.query(FilmGenre).filter(FilmGenre.id == film_genre_id).first()

        if film_genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thể loại phim không tồn tại"
            )

        return film_genre
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/search",
            response_model=ListFilmGenreResponse,
            status_code=status.HTTP_200_OK)
async def search_film_genre(
        film_genre: FilmGenreSearch,
        db: Session = Depends(get_db),
    ):

    try:
        query = db.query(FilmGenre)
        if film_genre.film_id:
            query = query.filter(FilmGenre.film_id == film_genre.film_id)
        if film_genre.genre_id:
            query = query.filter(FilmGenre.genre_id == film_genre.genre_id)

        film_genres = query.all()

        return ListFilmGenreResponse(
            film_genres=film_genres,
            total_data=len(film_genres)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    
@router.post("/film_genre/bulk-create", status_code=status.HTTP_201_CREATED)
async def bulk_create_film_genres(db: Session = Depends(get_db)):
    try:
        # Danh sách 143 film_id
        film_ids = list(range(148, 291))

        # Lấy tất cả genres
        genres = db.query(Genre).all()
        if not genres:
            raise HTTPException(status_code=404, detail="Không có thể loại nào trong cơ sở dữ liệu.")

        # Gán ngẫu nhiên thể loại cho từng film
        created_records = []
        for film_id in film_ids:
            selected_genres = random.sample(genres, random.randint(1, 3))
            for genre in selected_genres:
                film_genre = FilmGenre(film_id=film_id, genre_id=genre.id)
                db.add(film_genre)
                created_records.append({
                    "film_id": film_id,
                    "genre_id": genre.id
                })

        db.commit()
        return {
            "message": f"Đã tạo thành công {len(created_records)} bản ghi film-genre.",
            "data": created_records
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )

@router.post("/create",
             response_model=FilmGenreResponse,
                status_code=status.HTTP_201_CREATED)
async def create_film_genre(
        film_genre: FilmGenreCreate,
        db: Session = Depends(get_db),
    ):

    try:
        new_film_genre = FilmGenre(**film_genre.dict())
        db.add(new_film_genre)
        db.commit()
        db.refresh(new_film_genre)

        return new_film_genre
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/update/{film_genre_id}",
            response_model=FilmGenreResponse,
            status_code=status.HTTP_200_OK)
async def update_film_genre(
        film_genre_id: int,
        film_genre: FilmGenreUpdate,
        db: Session = Depends(get_db),
    ):

    try:
        existing_film_genre = db.query(FilmGenre).filter(FilmGenre.id == film_genre_id).first()

        if existing_film_genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thể loại phim không tồn tại"
            )

        for key, value in film_genre.dict().items():
            setattr(existing_film_genre, key, value)

        db.commit()
        db.refresh(existing_film_genre)

        return existing_film_genre
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete/{film_genre_id}",
               status_code=status.HTTP_200_OK)
async def delete_film_genre(
        film_genre_id: int,
        db: Session = Depends(get_db),
    ):

    try:
        film_genre = db.query(FilmGenre).filter(FilmGenre.id == film_genre_id).first()

        if film_genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thể loại phim không tồn tại"
            )

        db.delete(film_genre)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa thể loại phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete-many",
               status_code=status.HTTP_200_OK)
async def delete_film_genres(
        film_genre_ids: List[int],
        db: Session = Depends(get_db),
    ):

    try:
        film_genres = db.query(FilmGenre).filter(FilmGenre.id.in_(film_genre_ids)).all()

        if len(film_genres) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không có thể loại phim nào được tìm thấy"
            )

        for film_genre in film_genres:
            db.delete(film_genre)

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa các thể loại phim thành công"}
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all",
               status_code=status.HTTP_200_OK)
async def delete_all_film_genres(
        db: Session = Depends(get_db),
    ):

    try:
        db.query(FilmGenre).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả thể loại phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/films/by-genre/{genre_id}",
            response_model=ListFilmResponse,
            status_code=status.HTTP_200_OK)
async def get_films_by_genre(
        genre_id: int,
        db: Session = Depends(get_db),
    ):
    """
    Get all films that belong to a specific genre
    """
    try:
        # Query films through the film_genre relationship
        film_genres = db.query(FilmGenre).filter(FilmGenre.genre_id == genre_id).all()
        
        if not film_genres:
            return []
        
        # Get film_ids from the film_genres
        film_ids = [fg.film_id for fg in film_genres]
        
        # Query films with those ids
        films = db.query(Film).filter(Film.id.in_(film_ids)).all()
        
        return ListFilmResponse(
            films=films,
            total_data=len(films)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
