from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from promotion.schemas.promotion import *
from promotion.models.promotion import Promotion
import math

from user.models.user import User


router = APIRouter(
    prefix="/promotion",
    tags=["Promotion"]
)


@router.get("/all", 
            response_model=ListPromotionResponse)
async def get_all_promotion(
        db: Session = Depends(get_db)
    ):
    try:
        promotions = db.query(Promotion).all()

        return ListPromotionResponse(
            promotions=promotions, 
            total_data=len(promotions)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.get("/pageable",
            response_model=PromotionPageableResponse)
async def get_all_promotion_pageable(
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
    ):
    try:
        total_data = db.query(Promotion).count()
        total_page = math.ceil(total_data / size)

        promotions = db.query(Promotion).limit(size).offset((page - 1) * size).all()

        return PromotionPageableResponse(
            promotions=promotions,
            total_data=total_data,
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{promotion_id}",
            response_model=PromotionResponse)
async def get_promotion_by_id(
        promotion_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()

        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found"
            )

        return promotion
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/search",
                response_model=ListPromotionResponse)
async def search_promotion(
        promotion: PromotionSearch,
        db: Session = Depends(get_db)
    ):
    try:
        promotions = db.query(Promotion)
        if promotion.name:
            promotions = promotions.filter(Promotion.name.ilike(f"%{promotion.name}%"))
        if promotion.description:
            promotions = promotions.filter(Promotion.description.ilike(f"%{promotion.description}%"))
        if promotion.duration:
            promotions = promotions.filter(Promotion.duration == promotion.duration)
        if promotion.staff_id:
            promotions = promotions.filter(Promotion.staff_id == promotion.staff_id)

        promotions = promotions.all()

        return ListPromotionResponse(
            promotions=promotions,
            total_data=len(promotions)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/create")
def create_promotion(
        promotion: PromotionCreate,
        db: Session = Depends(get_db),
    ):
    try:
        staff = db.query(User).filter(User.id == promotion.staff_id).first()
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found"
            )

        new_promotion = Promotion(
            name=promotion.name,
            description=promotion.description,
            duration=promotion.duration,
            staff_id=promotion.staff_id
        )

        db.add(new_promotion)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Promotion created successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.put("/update/{promotion_id}")
def update_promotion(
        promotion_id: int,
        promotion: PromotionUpdate,
        db: Session = Depends(get_db)
    ):
    try:
        promotion_data = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found"
            )

        if promotion.staff_id:
            staff = db.query(User).filter(User.id == promotion.staff_id).first()
            if not staff:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Staff not found"
                )

            promotion_data.staff_id = promotion.staff_id

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Promotion updated successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete/{promotion_id}")
def delete_promotion(
        promotion_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found"
            )

        db.delete(promotion)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Promotion deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete-many")
def delete_many_promotion(
        promotion_ids: List[int],
        db: Session = Depends(get_db)
    ):
    try:
        promotions = db.query(Promotion).filter(Promotion.id.in_(promotion_ids)).all()
        if not promotions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotions not found"
            )
        
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Promotions deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )