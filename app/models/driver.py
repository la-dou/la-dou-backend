from typing import List
from pydantic import BaseModel
from .rating import Rating
from .order import DriverOrder


class Driver(BaseModel):
    deactivated: bool = False
    rating: Rating = Rating()
    orders: List[DriverOrder] = []
