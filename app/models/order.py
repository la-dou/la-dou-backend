from pydantic import BaseModel

class BaseOrder(BaseModel):
    by: str
    to: str
    notes: str
    delivery_price: int
    order_amount: int
    placed_at: str
    delivered_at: str
    status: str
    
class CustomerOrder(BaseOrder):
    driver_roll_no: int
    
class DriverOrder(BaseOrder):
    rider_roll_no: int