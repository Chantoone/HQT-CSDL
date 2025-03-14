from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from configs.database import get_db
from configs.authentication import get_current_user, hash_password, validate_pwd
from role.models.role import Role
from user.models.user import User
from user.schemas.user import *
from auth_credential.models.auth_credential import AuthCredential
from user_role.models.user_role import UserRole
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
    ):
    
    try:
        query = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
            .order_by(func.split_part(User.full_name, ' ', -1))
        )
        users = query.all()
        
        users = [
            UserResponse(
                id=user[0].id,
                full_name=user[0].full_name,
                username=user[0].username,
                email=user[0].email,
                phone_number=user[0].phone_number,
                birthdate=user[0].birthdate,
                address=user[0].address,
                is_active=user[0].is_active,
                created_at=user[0].created_at,
                roles=user[1]
            )
            for user in users
        ]

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
    ):
     
    try:
        total_count = db.query(User).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        
        query = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
            .order_by(func.split_part(User.full_name, ' ', -1))
            .offset(offset)
            .limit(page_size)
        )
        users = query.all()
        
        users = [
            UserResponse(
                id=user[0].id,
                full_name=user[0].full_name,
                username=user[0].username,
                email=user[0].email,
                phone_number=user[0].phone_number,
                birthdate=user[0].birthdate,
                address=user[0].address,
                is_active=user[0].is_active,
                created_at=user[0].created_at,
                roles=user[1]
            )
            for user in users
        ]

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
    ):
    
    try:
        query = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
            .filter(User.id == user_id)
        )
        user = query.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )
        
        user = UserResponse(
            id=user[0].id,
            full_name=user[0].full_name,
            username=user[0].username,
            email=user[0].email,
            phone_number=user[0].phone_number,
            birthdate=user[0].birthdate,
            address=user[0].address,
            is_active=user[0].is_active,
            created_at=user[0].created_at,
            roles=user[1]
        )

        return user
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/search",
            status_code=status.HTTP_200_OK,  
            response_model=UserPageableResponse)
async def search_user(
        search: UserSearch, 
        page: int,
        page_size: int,
        db: Session = Depends(get_db), 
    ):
    
    try:
        users = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
        )

        if search.username:
            users = users.filter(User.username.ilike(f"%{search.username}%"))
        if search.full_name:
            users = users.filter(User.full_name.ilike(f"%{search.full_name}%"))
        if search.phone_number:
            users = users.filter(User.phone_number.ilike(f"%{search.phone_number}%"))
        if search.address:
            users = users.filter(User.address.ilike(f"%{search.address}%"))
        if search.role:
            users = users.join(UserRole).join(Role).filter(Role.name == search.role)

        total_count = users.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        users = users.offset(offset).limit(page_size).all()
        users = [
            UserResponse(
                id=user[0].id,
                full_name=user[0].full_name,
                username=user[0].username,
                email=user[0].email,
                phone_number=user[0].phone_number,
                birthdate=user[0].birthdate,
                address=user[0].address,
                is_active=user[0].is_active,
                created_at=user[0].created_at,
                roles=user[1]
            )
            for user in users
        ]

        return UserPageableResponse(
            users=users,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    

@router.post("/register", 
             status_code=status.HTTP_201_CREATED)
async def create_user(
        new_user: UserCreate,
        db: Session = Depends(get_db), 
    ):
    
    try:
        username = db.query(User).filter(User.username == new_user.username).first()
        if username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tên đăng nhập đã tồn tại"
            )
        
        validate_pwd(new_user.password)

        # Create all objects first without committing
        new_info = User(
            username=new_user.username, 
            full_name=new_user.full_name,
            email=new_user.email,
            phone_number=new_user.phone_number,
            birthdate=new_user.birthdate,
            address=new_user.address
        )
        db.add(new_info)
        
        # Flush to get the user ID but don't commit yet
        db.flush()

        new_auth = AuthCredential(
            user_id=new_info.id,
            hashed_password=hash_password(new_user.password),
        )        
        db.add(new_auth)

        register_role = db.query(Role).filter(Role.name == "user").first()
        new_user_role = UserRole(
            user_id=new_info.id,
            role_id=register_role.id
        )
        db.add(new_user_role)

        # Commit everything at once
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
        ) from e
    

@router.post("/create-account")
async def create_account(
        account: UserCreateAccount,
        db: Session = Depends(get_db),
    ):
    
    try:
        # Check existing username
        username = db.query(User).filter(User.username == account.username).first()
        if username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tên đăng nhập đã tồn tại"
            )
        
        # Check existing email - only if email is provided and not empty
        if account.email and account.email.strip() != '':
            email = db.query(User).filter(User.email == account.email).first()
            if email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Email đã tồn tại"
                )

        # Get default password from .env
        default_password = getenv("DEFAULT_PASSWORD")
        if not default_password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chưa cấu hình mật khẩu mặc định"
            )

        # Create and commit user first
        new_info = User(
            username=account.username,
            full_name=account.full_name,
            email=account.email if account.email and account.email.strip() != '' else None,
            phone_number=account.phone_number if account.phone_number and account.phone_number.strip() != '' else None,
            birthdate=account.birthdate if account.birthdate else None, 
            address=account.address if account.address and account.address.strip() != '' else None
        )
        db.add(new_info)
        db.flush()

        # Create auth credential with default password
        new_auth = AuthCredential(
            user_id=new_info.id,
            hashed_password=hash_password(default_password)
        )
        db.add(new_auth)

        # Assign default user role
        default_role = db.query(Role).filter(Role.name == "user").first()
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy role mặc định"
            )

        new_user_role = UserRole(
            user_id=new_info.id,
            role_id=default_role.id
        )
        db.add(new_user_role)

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


@router.post("/activate/{user_id}")
async def activate_user(
        user_id: int,
        db: Session = Depends(get_db), 
    ):

    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tài khoản không tồn tại"
            )

        user.update(
            {"is_active": True}, 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Kích hoạt tài khoản thành công"
            }
        )

    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/deactivate/{user_id}")
async def deactivate_user(
        user_id: int,
        db: Session = Depends(get_db),
    ):

    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại"
            )
        
        user.update(
            {"is_active": False}, 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Vô hiệu hóa tài khoản thành công"
            }
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{user_id}", 
            status_code=status.HTTP_200_OK,  
            response_model=UserResponse)
async def update_user(
        user_id: int, 
        newUser: UserUpdate, 
        db: Session = Depends(get_db), 
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


@router.delete("/delete/{user_id}",
                status_code=status.HTTP_200_OK)
async def delete_user(
        user_id: int, 
        db: Session = Depends(get_db), 
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


@router.delete("/delete_many",
                status_code=status.HTTP_200_OK)
async def delete_many_user(
        ids: UserDelete, 
        db: Session = Depends(get_db), 
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
    

@router.delete("/delete-all",
                status_code=status.HTTP_200_OK)
async def delete_all_user(
        db: Session = Depends(get_db), 
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
