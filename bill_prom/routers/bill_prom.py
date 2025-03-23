from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from bill.models.bill import Bill
from configs.authentication import get_current_user
from configs.database import get_db
from bill_prom.models.bill_prom import BillProm
from bill_prom.schemas.bill_prom import *
import math

from promotion.models.promotion import Promotion


router = APIRouter(
    prefix="/bill-prom",
    tags=["Bill Prom"]
)


@router.get("/all", 
            response_model=ListBillPromResponse, 
            status_code=status.HTTP_200_OK)
def get_all_bill_proms(
        db: Session = Depends(get_db),
    ):
    try:
        bill_proms = db.query(BillProm).all()
        
        return ListBillPromResponse(
            bill_proms=bill_proms,
            total_data=len(bill_proms)
        )

    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.get("/pageable",
            response_model=BillPromPageableResponse, 
            status_code=status.HTTP_200_OK)
def get_all_bill_proms_pageable(
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
    ):
    try:
        bill_proms = db.query(BillProm).all()
        total_data = len(bill_proms)
        total_page = math.ceil(total_data / page_size)
        
        return BillPromPageableResponse(
            bill_proms=bill_proms[(page - 1) * page_size: page * page_size],
            total_data=total_data,
            total_page=total_page
        )

    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.get("/{bill_prom_id}", 
            response_model=BillPromResponse, 
            status_code=status.HTTP_200_OK)
def get_bill_prom_by_id(
        bill_prom_id: int,
        db: Session = Depends(get_db),
    ):
    try:
        bill_prom = db.query(BillProm).filter(BillProm.id == bill_prom_id).first()
        
        if not bill_prom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill Prom not found"
            )

        return bill_prom

    except SQLAlchemyError as e:
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.post("/create")
def create_bill_prom(
        bill_prom: BillPromCreate,
        db: Session = Depends(get_db),
    ):
    try:
        bill = db.query(Bill).filter(Bill.id == bill_prom.bill_id).first()
        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found"
            )
        
        prom = db.query(Promotion).filter(Promotion.id == bill_prom.prom_id).first()
        if not prom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prom not found"
            )

        new_bill_prom = BillProm(
            bill_id=bill_prom.bill_id,
            prom_id=bill_prom.prom_id
        )

        db.add(new_bill_prom)
        db.commit()

        return JSONResponse(
            content={"message": "Bill Prom created successfully"},
            status_code=status.HTTP_201_CREATED
        )

    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.put("/update/{bill_prom_id}")
def update_bill_prom(
        bill_prom_id: int,
        bill_prom: BillPromCreate,
        db: Session = Depends(get_db),
    ):
    try:
        bill_prom = db.query(BillProm).filter(BillProm.id == bill_prom_id).first()
        
        if not bill_prom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill Prom not found"
            )

        bill_prom.bill_id = bill_prom.bill_id
        bill_prom.prom_id = bill_prom.prom_id

        db.commit()

        return JSONResponse(
            content={"message": "Bill Prom updated successfully"},
            status_code=status.HTTP_200_OK
        )

    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.delete("/delete/{bill_prom_id}")
def delete_bill_prom(
        bill_prom_id: int,
        db: Session = Depends(get_db),
    ):
    try:
        bill_prom = db.query(BillProm).filter(BillProm.id == bill_prom_id).first()
        
        if not bill_prom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill Prom not found"
            )

        db.delete(bill_prom)
        db.commit()

        return JSONResponse(
            content={"message": "Bill Prom deleted successfully"},
            status_code=status.HTTP_200_OK
        )

    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )
    

@router.delete("/delete-many")
def delete_many_bill_proms(
        bill_proms: List[BillPromCreate],
        db: Session = Depends(get_db),
    ):
    try:
        for bill_prom in bill_proms:
            bill_prom = db.query(BillProm).filter(BillProm.id == bill_prom.bill_prom_id).first()
            
            if not bill_prom:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Bill Prom not found"
                )

            db.delete(bill_prom)
            db.commit()

        return JSONResponse(
            content={"message": "Bill Proms deleted successfully"},
            status_code=status.HTTP_200_OK
        )

    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            content={"message": str(e)},
            status_code=status.HTTP_409_CONFLICT
        )