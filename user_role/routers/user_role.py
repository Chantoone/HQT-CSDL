from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.database import get_db
from configs.authentication import get_current_user
from role.models.role import Role
from user.models.user import User
from user_role.models.user_role import UserRole
from user_role.schemas.user_role import *
import math


router = APIRouter(
    prefix="/user-role",
    tags=["User_Role"],
)


@router.get("/all", 
            response_model=ListUserRoleResponse, 
            status_code=status.HTTP_200_OK)
async def get_user_roles(
        db: Session = Depends(get_db),
    ):
    
    try:
        user_roles = db.query(UserRole).all()

        return ListUserRoleResponse(
            user_roles=user_roles,
            total_data=len(user_roles)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable", 
            response_model=UserRolePageableResponse)
async def get_user_roles_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
    ):
     
    try:
        total_count = db.query(UserRole).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        user_roles = db.query(UserRole).offset(offset).limit(page_size).all()

        user_roles_pageable_res = UserRolePageableResponse(
            user_roles=user_roles,
            total_pages=total_pages,
            total_data=total_count
        )

        return user_roles_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{user_id}",
            response_model=list[UserRoleResponse])
async def get_user_role_by_user_id(
        user_id: int,
        db: Session = Depends(get_db),
    ):
    
    try:
        user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()

        if not user_roles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Quyền người dùng không tồn tại"
            )

        return user_roles
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
             response_model=UserRoleResponse,
             status_code=status.HTTP_201_CREATED)
async def create_user_role(
        new_user_role: UserRoleCreate,
        db: Session = Depends(get_db), 
    ):
    
    try:
        user_role = db.query(UserRole).filter(
            UserRole.user_id == new_user_role.user_id, 
            UserRole.role_id == new_user_role.role_id
        ).first()
        if user_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền người dùng đã tồn tại"
            )

        user_role = UserRole(**new_user_role.dict())
        db.add(user_role)
        db.commit()    

        return user_role
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{id}",
            response_model=UserRoleResponse,
            status_code=status.HTTP_200_OK)
async def update_user_role(
        id: int,
        user_role: UserRoleUpdate,
        db: Session = Depends(get_db),
    ):
    
    try:
        user_role = db.query(UserRole).filter(UserRole.id == id)
        if not user_role.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Quyền người dùng không tồn tại"
            )

        user_role.update(user_role.dict(), synchronize_session=False)
        db.commit()

        return user_role.first()

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete/{id}",
                status_code=status.HTTP_200_OK)
async def delete_user_role(
        id: int,
        db: Session = Depends(get_db),
    ):
    
    try:
        user_role = db.query(UserRole).filter(UserRole.id == id)
        if not user_role.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Quyền người dùng không tồn tại"
            )

        user_role.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa quyền người dùng thành công"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-many",
                status_code=status.HTTP_200_OK)
async def delete_user_roles(
        user_ids: list[int],
        db: Session = Depends(get_db),
    ):
    
    try:
        user_roles = db.query(UserRole).filter(UserRole.id.in_(user_ids))
        if not user_roles.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Quyền người dùng không tồn tại"
            )

        user_roles.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa quyền người dùng thành công"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all",
                status_code=status.HTTP_200_OK)
async def delete_all_user_roles(
        db: Session = Depends(get_db),
    ):
    
    try:
        db.query(UserRole).delete()
        db.commit()

        return {"message": "Xóa tất cả quyền người dùng thành công"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )