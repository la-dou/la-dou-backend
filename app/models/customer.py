from typing import List
from pydantic import BaseModel
from .rating import Rating
from .order import CustomerOrder

class Customer(BaseModel):
    deactivated: bool = False
    rating: Rating = Rating()
    orders: List[CustomerOrder] = []