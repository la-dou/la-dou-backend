from pydantic import BaseModel
# from bson.objectid import ObjectId


class Order(BaseModel):
    id: str = None  # order id
    deliver_to: str = ""  # where to deliver the order
    deliver_from: str = ""  # where to pick up the order
    notes: str = ""  # any additional notes
    delivery_price: int = -1  # final accepted bid
    order_amount: int = -1  # total amount of the order
    placed_at: str = ""  # time when the order was placed
    delivered_at: str = ""  # time when the order was delivered
    status: str = "pending"  # status of the order
    bids: list = []  # bids for the order, rollno:bid_amount
    assigned_to: int = None  # roll no of the driver/customer assigned to the order
