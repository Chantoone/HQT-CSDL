from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from food.schemas.food import FoodBase
from ticket.schemas.ticket import TicketBase
from user.schemas.user import UserBase

class BillBase(BaseModel):
    payment_method: Optional[str] = None
    payment_time: Optional[datetime] = None
    status: Optional[str] = None
    value: Optional[int] = None

    class Config:
        from_attributes = True


class BillCreate(BillBase):
    payment_method: str
    payment_time: datetime
    status: str
    value: int
    staff_id: int
    food_id: int
    ticket_id: int


class BillUpdate(BillBase):
    pass


class BillResponse(BillBase):
    id: int
    created_at: datetime
    staff: UserBase
    food: FoodBase
    ticket: TicketBase

    class Config:
        from_attributes = True
    

class ListBillResponse(BaseModel):
    bills: List[BillResponse]
    total_data: int

    class Config:
        from_attributes = True


class BillPageableResponse(ListBillResponse):
    total_page: int

    class Config:
        from_attributes = True


class BillSearch(BaseModel):
    payment_method: Optional[str] = None
    payment_time: Optional[datetime] = None
    status: Optional[str] = None
    value: Optional[int] = None
    staff_id: Optional[int] = None
    food_id: Optional[int] = None
    ticket_id: Optional[int] = None

    class Config:
        from_attributes = True