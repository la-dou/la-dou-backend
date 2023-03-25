from typing import List
from pydantic import BaseModel
from .rating import Rating
from .order import DriverOrder


class Driver(BaseModel):
    deactivated: bool
    rating: Rating
    orders: List[DriverOrder]
