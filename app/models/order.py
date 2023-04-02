from pydantic import BaseModel

class BaseOrder(BaseModel):
    deliver_to: str # where to deliver the order
    deliver_from: str # where to pick up the order
    notes: str # any additional notes
    delivery_price: int # final accepted bid
    order_amount: int # total amount of the order
    placed_at: str # time when the order was placed
    delivered_at: str # time when the order was delivered
    status: str # status of the order
    
class CustomerOrder(BaseOrder):
    driver_roll_no: int # roll no of the driver who accepted the order
    
class DriverOrder(BaseOrder):
    customer_roll_no: int # roll no of the customer who placed the order