from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.database import get_db
from configs.authentication import get_current_user
from film.models.film import Film
from rate.models.rate import Rate
from rate.schemas.rate import *
import math

from user.models.user import User


router = APIRouter(
    prefix="/rate",
    tags=["Rate"],
)


@router.get("/", 
            response_model=ListRateResponse, 
            status_code=status.HTTP_200_OK)
def get_all_rate(
        db: Session = Depends(get_db),
    ):
        try:
            rates = db.query(Rate).all()

            return ListRateResponse(
                rates=rates,
                total_data=len(rates)
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )
        

@router.get("/pageable",
            response_model=RatePageableResponse, 
            status_code=status.HTTP_200_OK)
def get_rate_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db),
    ):
        try:
            total_count = db.query(Rate).count()
            total_pages = math.ceil(total_count / page_size)
            offset = (page - 1) * page_size
            rates = db.query(Rate).offset(offset).limit(page_size).all()

            rates_pageable_res = RatePageableResponse(
                rates=rates,
                total_pages=total_pages,
                total_data=total_count
            )

            return rates_pageable_res

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )
        

@router.get("/{rate_id}",
            response_model=RateResponse, 
            status_code=status.HTTP_200_OK)
def get_rate_by_id(
        rate_id: int,
        db: Session = Depends(get_db),
    ):
        try:
            rate = db.query(Rate).filter(Rate.id == rate_id).first()

            if rate is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rate not found",
                )

            return rate
        
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )
        

@router.post("/search",
            response_model=ListRateResponse, 
            status_code=status.HTTP_200_OK)
def search_rate(
        rate: RateSearch,
        db: Session = Depends(get_db),
    ):
        try:
            query = db.query(Rate)

            if rate.point:
                query = query.filter(Rate.point == rate.point)
            if rate.detail:
                query = query.filter(Rate.detail.ilike(f"%{rate.detail}%"))
            if rate.user_id:
                query = query.filter(Rate.user_id == rate.user_id)
            if rate.film_id:
                query = query.filter(Rate.film_id == rate.film_id)

            rates = query.all()

            return ListRateResponse(
                rates=rates,
                total_data=len(rates)
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )


@router.post("/create")
def create_rate(
        rate: RateCreate,
        db: Session = Depends(get_db),
    ):
        try:
            film = db.query(Film).filter(Film.id == rate.film_id).first()
            if film is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Film not found",
                )
            
            user = db.query(User).filter(User.id == rate.user_id).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            new_rate = Rate(**rate.dict())
            db.add(new_rate)
            db.commit()

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Rate created successfully"},
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )


@router.put("/{rate_id}")
def update_rate(
        rate_id: int,
        rate: RateUpdate,
        db: Session = Depends(get_db),
    ):
        try:
            film = db.query(Film).filter(Film.id == rate.film_id).first()
            if film is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Film not found",
                )

            db.query(Rate).filter(Rate.id == rate_id).update(rate.dict())
            db.commit()

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Rate updated successfully"},
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )
        

@router.delete("/{rate_id}")
def delete_rate(
        rate_id: int,
        db: Session = Depends(get_db),
    ):
        try:
            db.query(Rate).filter(Rate.id == rate_id).delete()
            db.commit()

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Rate deleted successfully"},
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )
        

@router.delete("/delete-many")
def delete_many_rate(
        rate_ids: List[int],
        db: Session = Depends(get_db),
    ):
        try:
            db.query(Rate).filter(Rate.id.in_(rate_ids)).delete(synchronize_session=False)
            db.commit()

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Rates deleted successfully"},
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database error: {str(e)}",
            )
        