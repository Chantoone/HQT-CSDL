from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.role import Role
from configs.database import get_db
from configs.authentication import get_current_user, hash_password
from app.models.auth_credential import AuthCredential
from app.models.user import User
from app.schemas.user import *
from os import getenv
import math


router = APIRouter(
    prefix= "/user",
    tags=["User"]
)
    

@router.get("/all",
            response_model=ListUserResponse,
            status_code=status.HTTP_200_OK)
async def get_all_users(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User).all()

        return ListUserResponse(
            users=users, 
            tolal_data=len(users)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/pageable", 
            response_model=UserPageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_user_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
     
    try:
        total_count = db.query(User).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        
        users = db.query(User).offset(offset).limit(page_size).all()

        user_pageable_res = UserPageableResponse(
            users=users,
            total_pages=total_pages,
            total_data=total_count
        )

        return user_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.get("/{user_id}", 
            status_code=status.HTTP_200_OK,  
            response_model=UserResponse)
async def get_user_by_id(
        user_id: int, 
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )

        return user
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/create-account")
async def create_account(
        account: UserCreate,
        db: Session = Depends(get_db)
    ):
    
    try:
        username = db.query(User).filter(User.username == account.username).first()
        if username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tên đăng nhập đã tồn tại"
            )
        
        default_password = getenv("DEFAULT_PASSWORD")
        if not default_password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chưa cấu hình mật khẩu mặc định"
            )

        new_info = User(
            username=account.username, 
            full_name=account.full_name,
            email=account.email,
            phone_number=account.phone_number,
            birthdate=account.birthdate,
            address=account.address
        )
        db.add(new_info)
        db.flush()

        new_auth = AuthCredential(
            user_id=new_info.id,
            hashed_password=hash_password(default_password)
        )
        db.add(new_auth)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Tạo tài khoản thành công"
            }
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put("/update/{user_id}")
async def update_user(
        user_id: int, 
        newUser: UserUpdate, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
 
    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )

        user.update(
            newUser.dict(), 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Cập nhật người dùng thành công"
            }
        )
    
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/delete/{user_id}")
async def delete_user(
        user_id: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )

        user.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Xóa người dùng thành công"
            }
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/delete_many")
async def delete_many_user(
        ids: UserDelete, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User).filter(User.id.in_(ids.list_id))
        if not users.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )

        users.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Xóa người dùng thành công"
            }
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.delete("/delete-all")
async def delete_all_user(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        db.query(User).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Xóa tất cả người dùng thành công"
            }
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
