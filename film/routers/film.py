from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import func
from configs.authentication import get_current_user
from configs.database import get_db
from film.models.film import Film
from film.schemas.film import *
from film_genre.models.film_genre import FilmGenre
import math
import random


router = APIRouter(
    prefix="/film",
    tags=["Film"],
)
    
    
@router.get("/allID",status_code=status.HTTP_200_OK)
def get_allID(db: Session = Depends(get_db)):
    try:
        films = db.query(Film.id).all()
        film_ids = [film.id for film in films]
        return {"film_ids": film_ids, "total": len(film_ids)}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/all", response_model=ListFilmResponse)
async def get_all_films(db: Session = Depends(get_db)):
    try:
        films = (
            db.query(Film)
            .options(joinedload(Film.film_genres).joinedload(FilmGenre.genre))
            .all()
        )

        # map genres thủ công cho từng film
        result = []
        for film in films:
            film_data = jsonable_encoder(film)
            film_data["genres"] = [
                {
                    "id": fg.genre.id,
                    "name": fg.genre.name
                } for fg in film.film_genres
            ]
            result.append(film_data)

        return ListFilmResponse(
            films=result,
            total_data=len(result)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/latest-now-showing", 
            response_model=ListFilmResponse, 
            status_code=status.HTTP_200_OK)
def get_latest_now_showing_films(db: Session = Depends(get_db)):
    try:
        films = (
            db.query(Film)
            .filter(Film.status == "NOW_SHOWING")
            .order_by(Film.created_at.desc())
            .limit(7)
            .all()
        )

        return ListFilmResponse(
            films=films,
            total_data=len(films)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/get_by_status_and_genre", response_model=ListFilmResponse, status_code=status.HTTP_200_OK)
def get_movies(state: Optional[str] = None, type_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(Film)

        # Lọc theo trạng thái nếu có
        if state:
            query = query.filter(Film.status == state)

        # Lọc theo thể loại nếu có
        if type_id:
            query = query.join(FilmGenre).filter(FilmGenre.genre_id == type_id)

        films = query.all()

        return ListFilmResponse(
            films=films,
            total_data=len(films)
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/random-now-showing", 
            response_model=ListFilmResponse, 
            status_code=status.HTTP_200_OK)
def get_random_now_showing_films(db: Session = Depends(get_db)):
    try:
        films = (
            db.query(Film)
            .filter(Film.status == "NOW_SHOWING")
            .order_by(func.random())  # chọn ngẫu nhiên
            .limit(7)
            .all()
        )

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

        films = (
            db.query(Film)
            .options(joinedload(Film.film_genres).joinedload(FilmGenre.genre))
            .offset(offset)
            .limit(page_size)
            .all()
        )

        result = []
        for film in films:
            film_data = jsonable_encoder(film)
            film_data["genres"] = [
                {
                    "id": fg.genre.id,
                    "name": fg.genre.name
                } for fg in film.film_genres
            ]
            result.append(film_data)

        films_pageable_res = FilmPageableResponse(
            films=result,
            total_pages=total_pages,
            total_data=total_count
        )

        return films_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{film_id}", response_model=FILMRESPONSE, status_code=status.HTTP_200_OK)
async def get_film(film_id: int, db: Session = Depends(get_db)):
    try:
        film = (
            db.query(Film)
            .options(joinedload(Film.film_genres).joinedload(FilmGenre.genre))
            .filter(Film.id == film_id)
            .first()
        )

        if not film:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phim"
            )

        # Trả về thủ công dưới dạng dict
        return {
            **jsonable_encoder(film),
            "genres": [GenreBase.from_orm(fg.genre) for fg in film.film_genres]
        }

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
    

@router.post("/create", response_model=FilmResponse, status_code=status.HTTP_201_CREATED)
async def create_film(
        film: FilmCreate,
        db: Session = Depends(get_db),
    ):
    try:
        # 1. Tạo film mới
        new_film = Film(
            title=film.title,
            description=film.description,
            duration=film.duration,
            release_date=film.release_date,
            author=film.author,
            poster_path=film.poster_path, 
            status=film.status,
        )

        db.add(new_film)
        db.flush()

        # 2. Tạo liên kết film - genres
        for genre_id in film.genre_ids:
            film_genre = FilmGenre(film_id=new_film.id, genre_id=genre_id)
            db.add(film_genre)

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Thêm phim thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
        

@router.put("/update-film-status", status_code=status.HTTP_200_OK)
async def update_film_status(db: Session = Depends(get_db)):
    try:
        films = db.query(Film).all()
        total_films = len(films)

        if total_films < 143:
            raise HTTPException(
                status_code=400,
                detail=f"Hiện chỉ có {total_films} film. Cần đủ 143 film để cập nhật theo yêu cầu."
            )

        # Shuffle film list để đảm bảo chọn ngẫu nhiên
        random.shuffle(films)

        # Chia ra danh sách film cần update
        end_films = films[:80]
        now_showing_films = films[80:120]
        coming_soon_films = films[120:143]

        # Cập nhật trạng thái
        for film in end_films:
            film.status = "END"

        for film in now_showing_films:
            film.status = "NOW_SHOWING"

        for film in coming_soon_films:
            film.status = "COMING_SOON"

        db.commit()

        return {
            "message": "Cập nhật trạng thái thành công cho 143 film!",
            "updated": {
                "END": len(end_films),
                "NOW_SHOWING": len(now_showing_films),
                "COMING_SOON": len(coming_soon_films)
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/update/{film_id}",
            response_model=FILMRESPONSE,
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
        
        # Cập nhật các field thông thường
        for key, value in update_data.items():
            if key != "genre_ids":
                setattr(db_film, key, value)

        # Cập nhật genres nếu có
        if "genre_ids" in update_data:
            # Xoá toàn bộ genre cũ
            db.query(FilmGenre).filter(FilmGenre.film_id == film_id).delete()

            # Thêm lại genre mới
            for genre_id in film.genre_ids:
                db.add(FilmGenre(film_id=film_id, genre_id=genre_id))

        db.commit()
        db.refresh(db_film)

        # Chuẩn bị response
        response = jsonable_encoder(db_film)
        response["genres"] = [
            {"id": fg.genre.id, "name": fg.genre.name}
            for fg in db_film.film_genres
        ]

        return response

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
    