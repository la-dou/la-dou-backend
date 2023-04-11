from typing import List
from pydantic import BaseModel
from .rating import Rating
from .order import Order
from uuid import uuid4, UUID


class Customer(BaseModel):
    deactivated: bool = False
    rating: Rating = Rating()
    orders: List[Order] = []
    order_in_progress: UUID = None
