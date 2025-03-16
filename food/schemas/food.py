from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Optional

class FoodBase(BaseModel):
    name: Optional[str]
    price: Optional[int]

    class Config:
        from_attributes = True


class FoodCreate(FoodBase):
    name: str


class FoodUpdate(FoodBase):
    pass


class FoodResponse(FoodBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ListFoodResponse(BaseModel):
    foods: List[FoodResponse]
    total_data: int

    class Config:
        from_attributes = True


class FoodPageableResponse(ListFoodResponse):
    total_page: int

    class Config:
        from_attributes = True


class FoodSearch(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None

    class Config:
        from_attributes = True


