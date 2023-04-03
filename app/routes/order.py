from fastapi import APIRouter, Depends, HTTPException, status
from ..config.deps import get_current_user
from ..config.database import db

from ..models.order import CustomerOrder, DriverOrder

order_router = APIRouter()


# Create global variable for bids
bids = {} # key: customer_roll_no, value: dict of bids (key: driver_roll_no, value: bid)

# Post Order
@order_router.post("/customer/order/create/")
async def create_order(customer_order: CustomerOrder, user = Depends(get_current_user)):
    '''
    Create an order by a Customer
    When a customer creates an order, the order is inserted into the database
    Initially the information is incomplete, as the driver has not accepted the order yet
    The driver will accept the order and update the order with the driver's roll number
    '''
    
    customer_roll_num = user.roll_no

    # Check if the customer made a previous order
    if customer_roll_num in bids:
        print("This customer already has an order in progress!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already has an order in progress",
        )
    
    # Update bids global variable
    bids[customer_roll_num] = {}

    # Insert the order into the orders array for the Customer object
    db.update_one(
        {"roll_no": customer_roll_num},
        {"$push": {"orders": customer_order.dict()}},
    )

    return {"detail": "Order created successfully"}

# Bid on Job
@order_router.post("/driver/order/bid")
async def bid_on_order(customer_roll_num: int, driver_roll_num: int, amount: int):
    '''
    Appends a bid to the bids global variable
    The final chosen bid will only be pushed to the database in the accept_bid function
    '''

    # Check if the customer exists by roll number
    customer = db.find_one({"roll_no": customer_roll_num})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    # Check if the driver exists by roll number
    driver = db.find_one({"roll_no": driver_roll_num})
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )
    
    # Check if this driver has already bid on this order
    if driver_roll_num in bids[customer_roll_num]:
        print("This driver has already bid on this order!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver already bid on this order",
        )

    bids[customer_roll_num][driver_roll_num] = amount # one driver can only bid once
    print(f"Bid placed in customer {customer_roll_num}: {bids[customer_roll_num]}")

    return {"detail": f"Bid of {amount} placed successfully by driver {driver_roll_num}"}


# # View all Bids
@order_router.get("/customer/order/viewbids/{customer_roll_num}")
async def view_bids(customer_roll_num):
    '''
    Uses the global bids variable to view all bids for a customer
    Returns a dictionary of bids (key: driver_roll_no, value: bid)
    '''

    # Check if the customer exists by roll number
    customer = db.find_one({"roll_no": customer_roll_num})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    return bids[customer_roll_num]

# # Accept Bid (remove bids global var key)
# @order_router.post("/customer/order/acceptbid/{driver_roll_num}")
# async def accept_bid(customer_roll_num: int, driver_roll_num: int):
#     '''
#     Fetch the bidding price from the bids global variable
#     Update the order in the database with the driver_roll_no and delivery_price
#     Remove the bids global variable key
    # Later, the following information will be added to the order:
    # - driver_roll_no
    # - delivery_price
    # - status
    # - delivered_at
#     '''

#     # Check if the customer exists by roll number
#     customer = db.find_one({"roll_no": customer_roll_num})
#     if not customer:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Customer not found",
#         )
    
#     # Check if the driver exists by roll number
#     driver = db.find_one({"roll_no": driver_roll_num})
#     if not driver:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Driver not found",
#         )
    
#     # Fetch the bidding price from the bids global variable
#     delivery_price = bids[customer_roll_num][driver_roll_num]

#     # Update the order in the database with the driver_roll_no and delivery_price
#     # Go inside the orders array of the Customer object
#     # Find the order with the driver_roll_no and delivery_price
#     # Update the order with the driver_roll_no and delivery_price
#     db.update_one(
#         # Find the Customer object
#         {"roll_no": customer_roll_num},
#         # Update the order with the driver_roll_no and delivery_price
#         {
#             "$set": {
#                 "orders.$[order].driver_roll_no": driver_roll_num, 
#                 "orders.$[order].delivery_price": delivery_price
#             }
#         }
#     )

#     # Remove the bids global variable key
#     del bids[customer_roll_num]

#     return {"detail": "Bid accepted successfully"}