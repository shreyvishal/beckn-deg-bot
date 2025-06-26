from pydantic import BaseModel
from typing import List, Optional


class ProviderInfo(BaseModel):
    id: str
    name: str


class ProductItem(BaseModel):
    id: str
    name: str
    price: str
    currency: str
    rating: str
    provider: ProviderInfo


class SearchProductResponse(BaseModel):
    message: str
    products: List[ProductItem]


class SelectProductResponse(BaseModel):
    success: bool
    message: str
    context: Optional[dict] = None

class ConfirmOrderResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[str] = None
    product_id: Optional[str] = None
