from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from bill.schemas.bill import BillResponse
from user.schemas.user import UserBase



class UserBillCreate(BaseModel):
    bill_id: int
    user_id: int


class UserBillResponse(BaseModel):
    id: int
    bill: BillResponse
    user: UserBase
    created_at: datetime

    class Config:
        from_attributes = True

    
class ListUserBillResponse(BaseModel):
    user_bills: List[UserBillResponse]
    total_data: int

    class Config:
        from_attributes = True


class UserBillPageableResponse(UserBillResponse):
    total_page: int

    class Config:
        from_attributes = True