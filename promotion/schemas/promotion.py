from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from user.schemas.user import UserBase

class PromotionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    
    class Config:
        from_attributes = True


class PromotionCreate(PromotionBase):
    name: str
    duration: int
    staff_id: int


class PromotionUpdate(PromotionBase):
    staff_id: Optional[int] = None


class PromotionResponse(PromotionBase):
    id: int
    staff: UserBase
    created_at: datetime

    class Config:
        from_attributes = True


class ListPromotionResponse(BaseModel):
    promotions: List[PromotionResponse]
    total_data: int

    class Config:
        from_attributes = True


class PromotionPageableResponse(ListPromotionResponse):
    total_page: int

    class Config:
        from_attributes = True


class PromotionSearch(PromotionBase):
    staff_id: Optional[int] = None