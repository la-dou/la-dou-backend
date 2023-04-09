from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from ..config.deps import get_current_user
from ..config.database import db


from ..models.order import CustomerOrder, DriverOrder
from ..schemas.order import orderEntity, ordersEntity, listOrdersEntity

order_router = APIRouter()


# Create global variable for bids
# key: customer_roll_no, value: dict of bids (key: driver_roll_no, value: bid)
bids = {}


# Post Order
@order_router.post("/customer/order/create")
async def create_order(customer_order: CustomerOrder, user=Depends(get_current_user)):
    '''
    Create an order by a Customer
    When a customer creates an order, the order is inserted into the database
    Initially the information is incomplete, as the driver has not accepted the order yet
    The driver will accept the order and update the order with the driver's roll number
    '''

    print(f"Customer order: {customer_order}")

    customer_roll_no = user.roll_no

    # Check if the customer made a previous order
    if customer_roll_no in bids:
        print("This customer already has an order in progress!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already has an order in progress",
        )

    # Update bids global variable
    bids[customer_roll_no] = {}

    # Insert the order to the customer's orders array
    db.update_one(
        {"roll_no": customer_roll_no},
        {"$push": {"customer.orders": customer_order.dict()}},
    )

    return {"detail": "Order created successfully"}


# Retrieve All Pending Orders From The Database
@order_router.get("/driver/order/viewall")
async def view_all_orders(user=Depends(get_current_user)):
    '''
        Retrieve all pending orders from the database
    '''

    # Query the database for all orders where status is pending
    users = db.find({"customer.orders.status": "pending"})

    # Get the orders from the cursor object
    orders = [user["customer"]["orders"] for user in users]

    # Convert the cursor object to a list of dictionaries
    orders = list(orders)

    orders = listOrdersEntity(orders)

    # Orders is a list of lists of dictionaries, so flatten it
    orders = [order for sublist in orders for order in sublist]

    # Remove all the orders that are not pending
    orders = [order for order in orders if order["status"] == "pending"]

    # Query the database for all orders where status is pending
    users = db.find({"customer.orders.status": "pending"})

    # If users roll number is not in bids, add it
    for user in users:
        if user["roll_no"] not in bids:
            bids[user["roll_no"]] = {}

    print(f"Bids: {bids}")

    return orders


# Bid on Job
@order_router.post("/driver/order/bid")
async def bid_on_order(order_id: str, amount: int, driver=Depends(get_current_user)):
    '''
    Appends a bid to the bids global variable
    The final chosen bid will only be pushed to the database in the accept_bid function
    '''

    # Find the customer who placed the order
    customer = db.find_one({"customer.orders.order_id": order_id})

    # If Customer not found, raise an error
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # Get the customer's roll number
    customer_roll_no = customer["roll_no"]

    # Get the driver's roll number
    driver_roll_no = driver.roll_no

    # Update bids global variable
    bids[customer_roll_no][driver_roll_no] = amount

    print(f"Bids: {bids}")

   # Return 200 OK
    return {"detail": "Bid placed successfully"}


# # View all Bids
@order_router.get("/customer/order/viewbids")
async def view_bids(customer=Depends(get_current_user)):
    '''
    Uses the global bids variable to view all bids for a customer
    Returns a dictionary of bids (key: driver_roll_no, value: bid)
    '''
    customer_roll_no = customer.roll_no

    print(f"Bids: {bids}")

    if not bids[customer_roll_no]:
        return []

    bids_list = []
    for driver_roll_no, amount in bids[customer_roll_no].items():
        bids_list.append({
            "driver_roll_no": driver_roll_no,
            "name": db.find_one({"roll_no": driver_roll_no})["name"],
            "bid": amount
        })

    return bids_list


# # Accept Bid (remove bids global var key)
@order_router.post("/customer/order/acceptbid")
async def accept_bid(driver_roll_no: int, customer=Depends(get_current_user)):
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

    customer_roll_no = customer.roll_no

    # Fetch the bidding price from the bids global variable
    delivery_price = bids[customer_roll_no][driver_roll_no]

    # Update the customer's pending order with the driver_roll_no and delivery_price
    db.update_one(
        {
            "roll_no": customer_roll_no,
            "customer.orders.status": "pending"
        },
        {
            "$set": {
                "customer.orders.$.driver_roll_no": driver_roll_no,
                "customer.orders.$.delivery_price": delivery_price,
                "customer.orders.$.status": "picking"
            }
        }
    )

    # Remove the bids global variable key now that the bid has been accepted
    # del bids[customer_roll_no]

    return {
        "customer_roll_no": customer_roll_no,
        "driver_roll_no": driver_roll_no,
        "delivery_price": delivery_price
    }


# # Update Job Status
@ order_router.post("/driver/order/updatestatus/{order_status}")
async def update_job_status(order_status: str, user=Depends(get_current_user)):
    '''
    Update the status of the order in the database
    Updates the status of the order in the database for the customer
    '''

    customer_roll_no = user.roll_no

    # Update the last order in the orders list of the customer with the order_status. match the customer_roll_no, and from customer.orders, find the last order with status not done or cancelled and update that order's status

    response = db.find_one({"roll_no": customer_roll_no})

    for order in response["customer"]["orders"]:
        if order["status"] != "done" or order["status"] != "cancelled":
            order["status"] = order_status

            if order_status == "done":
                order["delivered_at"] = datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S")
                del bids[customer_roll_no]

            if order_status == "cancelled":
                # Remove the customer from the bids global variable
                del bids[customer_roll_no]

            break

    response = db.update_one({"roll_no": customer_roll_no}, {
        "$set": {"customer": response["customer"]}})

    if response.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found",
        )

    return {"status": order_status}


# # Get Job Status
@ order_router.get("/customer/order/getStatus")
async def getOrderStatus(user=Depends(get_current_user)):
    """ 
    Get the status of the order for the customer    
    """

    customer_roll_no = user.roll_no

    # find the recent order of the customer
    try:

        orders = db.find_one({"roll_no": customer_roll_no})[
            "customer"]["orders"]
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
        response = db.find_one({"roll_no": driver})
        driver_name = response["name"]
    except:
        driver_name = "null"

    return {
        "order_status": order_status,
        "driver_name": driver_name,
        "driver_roll_no": driver
    }


# get all orders of a customer
@ order_router.get("/customer/order/getAllOrders")
async def getAllOrders(user=Depends(get_current_user)):
    """ 
    Get all orders of the customer
    """

    customer_roll_no = user.roll_no

    orders = db.find_one({"roll_no": customer_roll_no})
    orders = orders["customer"]["orders"]

    # Make an OrderHistory object for each order
    orders_list = []

    for order in orders:
        orderHistory = {
            "order_id": order["order_id"],
            "deliver_to": order["deliver_to"],
            "order_amount": order["order_amount"],
            "placed_at": order["placed_at"],
            "driver_name": "No Driver Yet" if order["driver_roll_no"] == -1 else db.find_one({"roll_no": order["driver_roll_no"]})["name"],
        }

        orders_list.append(orderHistory)

    return orders_list


# remove all orders of a customer
@ order_router.delete("/customer/order/removeAllOrders")
async def removeAllOrders(user=Depends(get_current_user)):
    """ 
    Remove all orders of the customer
    """

    customer_roll_no = user.roll_no

    response = db.find_one({"roll_no": customer_roll_no})

    response["customer"]["orders"] = []

    response = db.update_one({"roll_no": customer_roll_no}, {
        "$set": {"customer": response["customer"]}})

    if response.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found",
        )

    return {"detail": "All orders removed"}


# endpoint to update the driver of the recent order
@order_router.post("/customer/order/updateDriver/{driver_roll_no}")
async def updateDriver(driver_roll_no: int, user=Depends(get_current_user)):
    customer_roll_num = user.roll_no

    # Update the last order in the orders list of the customer with the order_status. match the customer_roll_no, and from customer.orders, find the last order with status not done or cancelled and update that order's status

    response = db.find_one({"roll_no": customer_roll_num})

    for order in response["customer"]["orders"]:
        if order["status"] != "done" or order["status"] != "cancelled":
            order["driver_roll_no"] = driver_roll_no
            break

    response = db.update_one({"roll_no": customer_roll_num}, {
                             "$set": {"customer": response["customer"]}})

    if response.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found",
        )

    return {"status": "success"}


# An endpoint to get the job status for the driver
@order_router.get("/driver/order/getStatus")
async def getDriverOrderStatus(order_id: str, user=Depends(get_current_user)):
    """ 
    Get the status of the order for the driver    
    """

    # Get the customer of the order from the database
    customer = db.find_one({"customer.orders.order_id": order_id})

    order_status = "null"
    temp_order = {}

    # Extract the order status with the order_id
    for order in customer["customer"]["orders"]:
        if order["order_id"] == order_id:
            temp_order = order
            order_status = order["status"]
            break

    # If the order status is picking and the driver is the driver of the order, then return the status as picking
    if order_status == "picking" and temp_order["driver_roll_no"] == user.roll_no:
        return {"status": "picking"}

    elif order_status == "picking" and temp_order["driver_roll_no"] != user.roll_no:
        return {"status": "denied"}
    elif order_status == "cancelled":
        return {"status": "cancelled"}
    else:
        return {"status": "null"}


# An EndPoint To Get Status Of An Order
@order_router.get("/customer/order/getStatus/{order_id}")
async def getCustomerOrderStatus(order_id: str, user=Depends(get_current_user)):
    """ 
    Get the status of the order for the customer    
    """

    # Get the customer of the order from the database
    customer = db.find_one({"customer.orders.order_id": order_id})

    order_status = "null"
    temp_order = {}

    # Extract the order status with the order_id
    for order in customer["customer"]["orders"]:
        if order["order_id"] == order_id:
            temp_order = order
            order_status = order["status"]
            break

    return {
        "customerRollNo": customer["roll_no"],
        "orderFrom": temp_order["deliver_from"],
        "orderTo": temp_order["deliver_to"],
        "orderStatus": order_status,
    }


# An Order Status Update Endpoint For Driver
@order_router.post("/driver/order/updateStatus/{order_id}/{order_status}")
async def updateOrderStatus(order_id: str, order_status: str, user=Depends(get_current_user)):
    """ 
    Update the status of the order for the driver    
    """

    print(f"Order ID: {order_id}")
    print(f"Order Status: {order_status}")

    # Get the customer of the order from the database
    customer = db.find_one({"customer.orders.order_id": order_id})

    print(f"Customer: {customer}")

    # Extract the order status with the order_id
    for order in customer["customer"]["orders"]:
        if order["order_id"] == order_id:
            order["status"] = order_status
            break

    response = db.update_one({"roll_no": customer["roll_no"]}, {
                             "$set": {"customer": customer["customer"]}})

    if response.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found",
        )

    return {"status": "success"}
