from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from bill.schemas.bill import BillResponse
from promotion.schemas.promotion import PromotionResponse



class BillPromCreate(BaseModel):
    bill_id: int
    prom_id: int


class BillPromResponse(BaseModel):
    id: int
    bill: BillResponse
    prom: PromotionResponse
    created_at: datetime

    class Config:
        from_attributes = True

    
class ListBillPromResponse(BaseModel):
    bill_proms: List[BillPromResponse]
    total_data: int

    class Config:
        from_attributes = True


class BillPromPageableResponse(ListBillPromResponse):
    total_page: int

    class Config:
        from_attributes = True