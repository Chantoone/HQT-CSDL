from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from food.models.food import Food
from food.schemas.food import *
import math


router = APIRouter(
    prefix="/food",
    tags=["Food"],
)


@router.get("/all",
            response_model=ListFoodResponse,
            status_code=status.HTTP_200_OK)
async def get_foods(
        db: Session = Depends(get_db),
    ):

    try:
        foods = db.query(Food).all()

        return ListFoodResponse(
            foods=foods,
            total_data=len(foods)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/pageable",
            response_model=FoodPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_foods_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db),
    ):
     
    try:
        total_count = db.query(Food).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        foods = db.query(Food).offset(offset).limit(page_size).all()

        foods_pageable_res = FoodPageableResponse(
            foods=foods,
            total_page=total_pages,
            total_data=total_count
        )

        return foods_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{food_id}",
            response_model=FoodResponse,
            status_code=status.HTTP_200_OK)
async def get_food_by_id(
        food_id: int,
        db: Session = Depends(get_db),
    ):
    
    try:
        food = db.query(Food).filter(Food.id == food_id).first()

        if food is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thức ăn"
            )

        return food
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.post("/search",
             response_model=ListFoodResponse,
             status_code=status.HTTP_200_OK)
async def search_food(
        food_search: FoodSearch,
        db: Session = Depends(get_db),
    ):
    
    try:
        foods = db.query(Food).filter(
            Food.name.like(f"%{food_search.name}%"),
            Food.price == food_search.price
        ).all()

        return ListFoodResponse(
            foods=foods,
            total_data=len(foods)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    
    
@router.post("/create",
             response_model=FoodResponse)
async def create_food(
        food_create: FoodCreate,
        db: Session = Depends(get_db),
    ):
    
    try:
        food = Food(
            name=food_create.name,
            price=food_create.price
        )

        db.add(food)
        db.commit()
        db.refresh(food)

        return JSONResponse(
            content={"message": "Tạo thức ăn thành công"},
            status_code=status.HTTP_201_CREATED
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.put("/{food_id}",
            response_model=FoodResponse)
async def update_food(
        food_id: int,
        food_update: FoodUpdate,
        db: Session = Depends(get_db),
    ):
    
    try:
        food = db.query(Food).filter(Food.id == food_id)
        if not food.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thức ăn không tồn tại"
            )

        food.update(food_update.dict())
        db.commit()

        return JSONResponse(
            content={"message": "Cập nhật thức ăn thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/{food_id}")
async def delete_food(
        food_id: int,
        db: Session = Depends(get_db),
    ):
    
    try:
        food = db.query(Food).filter(Food.id == food_id)
        if not food.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thức ăn không tồn tại"
            )

        food.delete()
        db.commit()

        return JSONResponse(
            content={"message": "Xóa thức ăn thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.delete("/delete-many")
async def delete_many_foods(
        food_ids: List[int],
        db: Session = Depends(get_db),
    ):
    
    try:
        foods = db.query(Food).filter(Food.id.in_(food_ids)).all()
        if not foods:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thức ăn không tồn tại"
            )

        for food in foods:
            db.delete(food)
        db.commit()

        return JSONResponse(
            content={"message": "Xóa thức ăn thành công"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    