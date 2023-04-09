from pydantic import BaseModel
from uuid import uuid4, UUID

class BaseOrder(BaseModel):
    order_id: UUID = uuid4().hex # unique id of the order
    deliver_to: str = "" # where to deliver the order
    deliver_from: str = "" # where to pick up the order
    notes: str = "" # any additional notes
    delivery_price: int = -1 # final accepted bid
    order_amount: int = -1 # total amount of the order
    placed_at: str = "" # time when the order was placed
    delivered_at: str = "" # time when the order was delivered
    status: str = "pending" # status of the order
    
class CustomerOrder(BaseOrder):
    driver_roll_no: int = -1 # roll no of the driver who accepted the order
    
class DriverOrder(BaseOrder):
    customer_roll_no: int = -1 # roll no of the customer who placed the order