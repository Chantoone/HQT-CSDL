from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from genre.models.genre import Genre
from genre.schemas.genre import *
import math


router = APIRouter(
    prefix="/genre",
    tags=["Genre"],
)


@router.get("/all",
            response_model=ListGenreResponse,
            status_code=status.HTTP_200_OK)
async def get_genres(
        db: Session = Depends(get_db),
    ):

    try:
        genres = db.query(Genre).all()

        return ListGenreResponse(
            genres=genres,
            total_data=len(genres)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=GenrePageableResponse,
            status_code=status.HTTP_200_OK)
async def get_genres_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db),
    ):

    try:
        total_count = db.query(Genre).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        genres = db.query(Genre).offset(offset).limit(page_size).all()

        genres_pageable_res = GenrePageableResponse(
            genres=genres,
            total_pages=total_pages,
            total_data=total_count
        )

        return genres_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{genre_id}",
            response_model=GenreResponse,
            status_code=status.HTTP_200_OK)
async def get_genre(
        genre_id: int,
        db: Session = Depends(get_db),
    ):

    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()

        if genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thể loại không tồn tại"
            )

        return genre
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    


@router.post("/search",
            response_model=ListGenreResponse,
            status_code=status.HTTP_200_OK)
async def search_genres(
        genre: GenreSearch,
        db: Session = Depends(get_db),
    ):

    try:
        query = db.query(Genre)

        if genre.name:
            query = query.filter(Genre.name.ilike(f"%{genre.name}%"))
        if genre.description:
            query = query.filter(Genre.description.ilike(f"%{genre.description}%"))

        genres = query.all()

        return ListGenreResponse(
            genres=genres,
            total_data=len(genres)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/create",
             response_model=GenreResponse,
             status_code=status.HTTP_201_CREATED)
async def create_genre(
        genre: GenreCreate,
        db: Session = Depends(get_db),
    ):

    try:
        new_genre = Genre(
            name=genre.name,
            description=genre.description
        )

        db.add(new_genre)
        db.commit()
        db.refresh(new_genre)

        return new_genre
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/update/{genre_id}",
            response_model=GenreResponse,
            status_code=status.HTTP_200_OK)
async def update_genre(
        genre_id: int,
        genre: GenreUpdate,
        db: Session = Depends(get_db),
    ):

    try:
        existing_genre = db.query(Genre).filter(Genre.id == genre_id).first()

        if existing_genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thể loại không tồn tại"
            )

        existing_genre.name = genre.name
        existing_genre.description = genre.description

        db.commit()
        db.refresh(existing_genre)

        return existing_genre
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete/{genre_id}",
               status_code=status.HTTP_200_OK)
async def delete_genre(
        genre_id: int,
        db: Session = Depends(get_db),
    ):

    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()

        if genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thể loại không tồn tại"
            )

        db.delete(genre)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa thể loại thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete-many",
               status_code=status.HTTP_200_OK)
async def delete_genres(
        genre_ids: List[int],
        db: Session = Depends(get_db),
    ):

    try:
        genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()

        if len(genres) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không có thể loại nào được tìm thấy"
            )

        for genre in genres:
            db.delete(genre)

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa các thể loại thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all",
               status_code=status.HTTP_200_OK)
async def delete_all_genres(
        db: Session = Depends(get_db),
    ):

    try:
        db.query(Genre).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả thể loại thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    