from fastapi import APIRouter, Depends, HTTPException, status
from ..config.deps import get_current_user
from ..config.database import db

from ..models.order import CustomerOrder, DriverOrder
from ..schemas.order import orderEntity, ordersEntity, listOrdersEntity

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
    
    print(f"Customer order: {customer_order}")
    
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

    
    # Insert the order to the customer's orders array
    db.update_one(
        {"roll_no": customer_roll_num},
        {"$push": {"customer.orders": customer_order.dict()}},
    )

    return {"detail": "Order created successfully"}

# Retrieve All Pending Orders From The Database
@order_router.get("/driver/order/viewall")
async def view_all_orders(user = Depends(get_current_user)):
    '''
        Retrieve all pending orders from the database
    '''
    
    # Query the database for all orders where status is pending
    users = db.find({"customer.orders.status": "pending"})
    
    # Get the orders from the cursor object
    orders = [user["customer"]["orders"] for user in users]
    
    # Convert the cursor object to a list of dictionaries
    orders = list(orders)
    
    return listOrdersEntity(orders)

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
async def view_bids(customer_roll_num: int):
    '''
    Uses the global bids variable to view all bids for a customer
    Returns a dictionary of bids (key: driver_roll_no, value: bid)
    '''
    
    print(f"Bids: {bids}")

    # Check if the customer exists by roll number
    customer = db.find_one({"roll_no": int(customer_roll_num)})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    if not bids[customer_roll_num]:
        return {"detail": "No bids yet"}
    
    return bids[customer_roll_num]



# # Accept Bid (remove bids global var key)
@order_router.post("/customer/order/acceptbid/{driver_roll_num}")
async def accept_bid(customer_roll_num: int, driver_roll_num: int):
    '''
    Fetch the bidding price from the bids global variable
    Update the order in the database with the driver_roll_no and delivery_price
    Remove the bids global variable key
    Later, the following information will be added to the order:
    - driver_roll_no
    - delivery_price
    - status
    - delivered_at
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
    
    # Fetch the bidding price from the bids global variable
    delivery_price = bids[customer_roll_num][driver_roll_num]

    # Update the last order in the database made by customer_roll_no with the driver_roll_no and delivery_price
    db.update_one({
        "roll_no": customer_roll_num,
        "orders": {
            "$elemMatch": {
                "driver_roll_no": -1,
                "delivery_price": -1
            }
    }
    }, {
        "$set": {
            "orders.$.driver_roll_no": driver_roll_num,
            "orders.$.delivery_price": delivery_price
        }
    })

    # Remove the bids global variable key now that the bid has been accepted
    del bids[customer_roll_num]

    return {
        "customer_roll_no": customer_roll_num,
        "driver_roll_no": driver_roll_num,
        "delivery_price": delivery_price
    }

# # Update Job Status
@order_router.post("/driver/order/updatestatus/{order_status}")
async def update_job_status(order_status: str, user=Depends(get_current_user)):
    '''
    Update the status of the order in the database
    Updates the status of the order in the database for the customer
    '''

    customer_roll_num = user.roll_no

    # Update the last order in the orders list of the customer with the order_status. match the customer_roll_no, and from customer.orders, find the last order with status not done or cancelled and update that order's status

    response = db.find_one({"roll_no": customer_roll_num})

    for order in response["customer"]["orders"]:
        if order["status"] != "done" or order["status"] != "cancelled":
            order["status"] = order_status
            break
    
    response = db.update_one({"roll_no": customer_roll_num}, {"$set": {"customer": response["customer"]}})

    if response.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found",
        )

    return {"status": order_status}

@order_router.get("/customer/order/getStatus/")
async def getOrderStatus(user = Depends(get_current_user)):

    customer_roll_num = user.roll_no

    # find the recent order of the customer
    try:

        orders = db.find_one({"roll_no": customer_roll_num})["customer"]["orders"]
        for order in orders:
            if order["status"] != "done" and order["status"] != "cancelled":
                recent_order = order
                break

        print("recent_order : ", recent_order)

    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No orders found",
        )
    
    try:
        # find the status of the recent order
        order_status = recent_order["status"]
        driver = recent_order["driver_roll_no"]
    except:
        order_status = "null"
        driver = "null"

    try:
        # find the name of the driver
        driver = db.find_one({"roll_no": driver})
        driver_name = driver["name"]
    except:
        driver_name = "null"

    return {
        "status": order_status,
        "driver": driver_name
    }
    
# get all orders of a customer
@order_router.get("/customer/order/getAllOrders/")
async def getAllOrders(user = Depends(get_current_user)):
    customer_roll_num = user.roll_no

    orders = db.find_one({"roll_no": customer_roll_num})
    orders = orders["customer"]["orders"]

    return {"orders": orders}

# remove all orders of a customer
@order_router.delete("/customer/order/removeAllOrders/")
async def removeAllOrders(user = Depends(get_current_user)):
    customer_roll_num = user.roll_no

    response = db.find_one({"roll_no": customer_roll_num})

    response["customer"]["orders"] = []

    response = db.update_one({"roll_no": customer_roll_num}, {"$set": {"customer": response["customer"]}})

    if response.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found",
        )

    return {"detail": "All orders removed"}