from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from bill.models.bill import Bill
from configs.authentication import get_current_user
from configs.database import get_db
from user.models.user import User
from user_bill.models.user_bill import UserBill
from user_bill.schemas.user_bill import *
import math


router = APIRouter(
    prefix="/user-bill",
    tags=["User Bill"]
)


@router.get("/all", 
            response_model=ListUserBillResponse, 
            status_code=status.HTTP_200_OK)
def get_all_user_bills(
        db: Session = Depends(get_db),
    ):
    try:
        user_bills = db.query(UserBill).all()
        
        return ListUserBillResponse(
            user_bills=user_bills,
            total_data=len(user_bills)
        )

    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.get("/pageable",
            response_model=UserBillPageableResponse, 
            status_code=status.HTTP_200_OK)
def get_all_bill_proms_pageable(
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
    ):
    try:
        user_bills = db.query(UserBill).all()
        total_data = len(user_bills)
        total_page = math.ceil(total_data / page_size)
        
        return UserBillPageableResponse(
            user_bills=user_bills[(page - 1) * page_size: page * page_size],
            total_data=total_data,
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.get("/user_bill/{user_id}",
            response_model=ListUserBillResponse, 
            status_code=status.HTTP_200_OK)
def get_user_bill_by_user_id(
        user_id: int,
        db: Session = Depends(get_db),
    ):
    try:
        user_bills = db.query(UserBill).filter(UserBill.user_id == user_id).all()
        
        return ListUserBillResponse(
            user_bills=user_bills,
            total_data=len(user_bills)
        )

    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.post("/create")
def create_user_bill(
        request: UserBillCreate,
        db: Session = Depends(get_db),
    ):
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            return JSONResponse(
                content={"message": "User not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        bill = db.query(Bill).filter(Bill.id == request.bill_id).first()
        if not bill:
            return JSONResponse(
                content={"message": "Bill not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        user_bill = UserBill(
            user_id=request.user_id,
            bill_id=request.bill_id
        )
        
        db.add(user_bill)
        db.commit()
        
        return JSONResponse(
            content={"message": "User Bill created successfully"},
            status_code=status.HTTP_201_CREATED
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.put("/update/{id}")
def update_user_bill(
        id: int,
        request: UserBillCreate,
        db: Session = Depends(get_db),
    ):
    try:
        user_bill = db.query(UserBill).filter(UserBill.id == id).first()
        if not user_bill:
            return JSONResponse(
                content={"message": "User Bill not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            return JSONResponse(
                content={"message": "User not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        bill = db.query(Bill).filter(Bill.id == request.bill_id).first()
        if not bill:
            return JSONResponse(
                content={"message": "Bill not found"},
                status_code=status.HTTP_404_NOT_FOUND)
        
        user_bill.user_id = request.user_id
        user_bill.bill_id = request.bill_id
        
        db.commit()
        
        return JSONResponse(
            content={"message": "User Bill updated successfully"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.delete("/delete/{id}")
def delete_user_bill(
        id: int,
        db: Session = Depends(get_db),
    ):
    try:
        user_bill = db.query(UserBill).filter(UserBill.id == id).first()
        if not user_bill:
            return JSONResponse(
                content={"message": "User Bill not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        db.delete(user_bill)
        db.commit()
        
        return JSONResponse(
            content={"message": "User Bill deleted successfully"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.delete("/delete-many")
def delete_many_user_bill(
        ids: list[int],
        db: Session = Depends(get_db),
    ):
    try:
        user_bills = db.query(UserBill).filter(UserBill.id.in_(ids)).all()
        if not user_bills:
            return JSONResponse(
                content={"message": "User Bill not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        for user_bill in user_bills:
            db.delete(user_bill)
        db.commit()
        
        return JSONResponse(
            content={"message": "User Bill deleted successfully"},
            status_code=status.HTTP_200_OK
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )