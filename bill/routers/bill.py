from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.database import get_db
from configs.authentication import get_current_user
from bill.models.bill import Bill
from bill.schemas.bill import *
import math

from food.models.food import Food
from ticket.models.ticket import Ticket
from user.models.user import User


router = APIRouter(
    prefix="/bill",
    tags=["Bill"],
)


@router.get("/", 
            response_model=ListBillResponse, 
            status_code=status.HTTP_200_OK)
def get_all_bills(
        db: Session = Depends(get_db)
    ):
    try:
        bills = db.query(Bill).all()
        
        return ListBillResponse(
            bills=bills, 
            total_data=len(bills)
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )
    

@router.get("/pageable",
            response_model=BillPageableResponse,
            status_code=status.HTTP_200_OK)
def get_all_bills_pageable(
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
    ):
    try:
        total_data = db.query(Bill).count()
        total_page = math.ceil(total_data / size)
        offset = (page - 1) * size

        bills = db.query(Bill).offset(offset).limit(size).all()

        return BillPageableResponse(
            bills=bills,
            total_data=total_data,
            total_page=total_page
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )
    

@router.get("/{bill_id}",
            response_model=BillResponse,
            status_code=status.HTTP_200_OK)
def get_bill_by_id(
        bill_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()

        if bill is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found"
            )
        
        return BillResponse(bill=bill)
    
    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )
    

@router.post("/search",
            response_model=ListBillResponse,
            status_code=status.HTTP_200_OK)
def search_bill(
        bill: BillSearch,
        db: Session = Depends(get_db)
    ):
    try:
        bills = db.query(Bill)
        if bill.payment_method:
            bills = bills.filter(Bill.payment_method == bill.payment_method)
        if bill.payment_time:
            bills = bills.filter(Bill.payment_time == bill.payment_time)
        if bill.status:
            bills = bills.filter(Bill.status == bill.status)
        if bill.value:
            bills = bills.filter(Bill.value == bill.value)
        if bill.staff_id:
            bills = bills.filter(Bill.staff_id == bill.staff_id)
        if bill.food_id:
            bills = bills.filter(Bill.food_id == bill.food_id)
        if bill.ticket_id:
            bills = bills.filter(Bill.ticket_id == bill.ticket_id)

        bills = bills.all()

        return ListBillResponse(
            bills=bills,
            total=len(bills)
        )
    
    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )
    

@router.post("/create",
             response_model=BillResponse)
def create_bill(
        bill: BillCreate,
        db: Session = Depends(get_db),
    ):
    try:
        staff = db.query(User).filter(User.id == bill.staff_id).first()
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found"
            )
        
        food = db.query(Food).filter(Food.id == bill.food_id).first()
        if not food:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found"
            )
        
        ticket = db.query(Ticket).filter(Ticket.id == bill.ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        new_bill = Bill(
            payment_method=bill.payment_method,
            payment_time=bill.payment_time,
            status=bill.status,
            value=bill.value,
            staff_id=bill.staff_id,
            food_id=bill.food_id,
            ticket_id=bill.ticket_id
        )

        db.add(new_bill)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Bill created successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )
    

@router.put("/update/{bill_id}")
def update_bill(
        bill_id: int,
        bill: BillUpdate,
        db: Session = Depends(get_db)
    ):
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()

        if bill is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found"
            )

        bill.payment_method = bill.payment_method
        bill.payment_time = bill.payment_time
        bill.status = bill.status
        bill.value = bill.value

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Bill updated successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )
    

@router.delete("/delete/{bill_id}")
def delete_bill(
        bill_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()

        if bill is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found"
            )

        db.delete(bill)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Bill deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )
    

@router.delete("/delete-many")
def delete_many_bills(
        bill_ids: List[int],
        db: Session = Depends(get_db)
    ):
    try:
        bills = db.query(Bill).filter(Bill.id.in_(bill_ids)).all()

        if not bills:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bills not found"
            )

        for bill in bills:
            db.delete(bill)
        
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Bills deleted successfully"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)}
        )