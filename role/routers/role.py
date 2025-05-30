from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from role.models.role import Role
from role.schemas.role import *
import math


router = APIRouter(
    prefix="/role",
    tags=["Role"],
)


@router.get("/all", 
            response_model=ListRoleResponse, 
            status_code=status.HTTP_200_OK)
async def get_roles(
        db: Session = Depends(get_db),
    ):

    try:
        roles = db.query(Role).all()

        return ListRoleResponse(
            roles=roles, 
            total_data=len(roles)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=RolePageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_roles_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
    ):
     
    try:
        total_count = db.query(Role).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        roles = db.query(Role).offset(offset).limit(page_size).all()

        roles_pageable_res = RolePageableResponse(
            roles=roles,
            total_pages=total_pages,
            total_data=total_count
        )

        return roles_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{id}", 
            response_model=RoleResponse, 
            status_code=status.HTTP_200_OK)
async def get_role_by_id(
        id: int,
        db: Session = Depends(get_db), 
    ):
    
    try:
        role = db.query(Role).filter(Role.id == id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Quyền không tồn tại"
            )

        return role
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/search",
            response_model=RolePageableResponse)
async def search_roles_by_name(
        search: RoleSearch,
        page: int,
        page_size: int,
        db: Session = Depends(get_db), 
    ):

    try:
        roles = db.query(Role)
        if search.name:
            roles = roles.filter(Role.name.like(f"%{search.name}%"))
        if search.detail:
            roles = roles.filter(Role.detail.like(f"%{search.detail}%"))

        total_count = roles.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        roles = roles.offset(offset).limit(page_size).all()

        return RolePageableResponse(
            roles=roles,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create", 
             response_model=RoleResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_role(
        new_role: RoleCreate,
        db: Session = Depends(get_db), 
    ):

    role = db.query(Role).filter(Role.name == new_role.name).first()
    if role:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền đã tôn tại"
        )

    role = Role(**new_role.dict())
    db.add(role)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Tạo quyền thành công"}
    )




@router.put("/update/{id}", 
            response_model=RoleResponse, 
            status_code=status.HTTP_200_OK)
async def update_role(
        id: int,
        new_role: RoleUpdate,
        db: Session = Depends(get_db), 
    ):

    try:
        role = db.query(Role).filter(Role.id == id)
        if not role.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )

        role.update(new_role.dict())
        db.commit()

        return role.first()
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete/{id}", 
            status_code=status.HTTP_200_OK)
async def delete_role(
        id: int,
        db: Session = Depends(get_db), 
    ):

    try:
        role = db.query(Role).filter(Role.id == id)
        if not role.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )
        role.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa quyền thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-many",
            status_code=status.HTTP_200_OK)
async def delete_roles(
        ids: list[int],
        db: Session = Depends(get_db), 
    ):

    try:
        roles = db.query(Role).filter(Role.id.in_(ids))
        if not roles.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )
        roles.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa quyền thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all",
            status_code=status.HTTP_200_OK)
async def delete_all_roles(
        db: Session = Depends(get_db), 
    ):

    try:
        db.query(Role).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả quyền thành công"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    