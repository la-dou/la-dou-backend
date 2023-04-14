from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from bson.objectid import ObjectId
from ..config.deps import get_current_user
from ..config.database import db
from ..models.order import Order

order_router = APIRouter()


# Post Order
@order_router.post("/orders/customer/create", response_model=Order)
async def create_order(order: Order, user=Depends(get_current_user)):
    '''
    Create an order by a Customer
    When a customer creates an order, the order is inserted into the database
    Initially the information is incomplete, as the driver has not accepted the order yet
    The driver will accept the order and update the order with the driver's roll number
    '''

    print("Order placed by:", user.roll_no, "details:", order)

    # check if the customer has an order in progress
    customer_obj = db.find_one({"roll_no": user.roll_no})["customer"]
    if customer_obj["order_in_progress"] is not None:
        print("Customer already has an order in progress!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already has an order in progress",
        )
    # Generate a unique id for the order
    order.id = str(ObjectId())
    # Insert the order to the customer's orders array
    db.update_one(
        {"roll_no": user.roll_no},
        {"$push": {"customer.orders": order.dict()}},
    )

    # Update the customer's order_in_progress field
    db.update_one(
        {"roll_no": user.roll_no},
        {"$set": {"customer.order_in_progress": order.id}},
    )

    return order


# Retrieve All Pending Orders From The Database
@order_router.get("/orders/pending")
async def view_all_orders(user=Depends(get_current_user)):
    '''
        Retrieve all pending orders from the database
    '''

    # Query the database for all orders where status is pending
    users = db.find({"customer.orders.status": "pending"})

    # Get the orders from the cursor object
    orders = [user["customer"]["orders"] for user in users]

    # Orders is a list of lists of dictionaries, so flatten it
    orders = [order for sublist in orders for order in sublist]
    # Remove all the orders that are not pending
    orders = [order for order in orders if order["status"] == "pending"]

    # Query the database for all orders where status is pending
    users = db.find({"customer.orders.status": "pending"})

    return orders


# Bid on Job
@order_router.post("/orders/bid")
async def bid_on_order(order_id: str, amount: int, driver=Depends(get_current_user)):
    '''
    Appends a bid to the bids global variable
    The final chosen bid will only be pushed to the database in the accept_bid function
    '''

    # Find the customer who placed the order
    customer = db.find_one({"customer.orders.id": order_id})

    # If order not found, raise an error
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    # add the bid in the db
    db.update_one(
        {"customer.orders.id": order_id},
        {"$push": {"customer.orders.$.bids": {
            "driver_roll_no": driver.roll_no,
            "amount": amount
        }}},
    )

   # Return 200 OK
    return {"detail": "Bid placed successfully"}


# # View all Bids
@order_router.get("/orders/inprogress/bids/view")
async def view_bids(user=Depends(get_current_user)):
    '''
    Uses the global bids variable to view all bids for a customer
    Returns a dictionary of bids (key: driver_roll_no, value: bid)
    '''
    # query the DB for order in progress
    order_in_progress = db.find_one({"roll_no": user.roll_no})[
        "customer"]["order_in_progress"]
    print(order_in_progress)
    # query the DB for bids
    bids = db.aggregate([
        {"$match": {"customer.orders.id": order_in_progress}},
        {"$unwind": "$customer.orders"},
        {"$match": {"customer.orders.id": order_in_progress}},
        {"$unwind": "$customer.orders.bids"},
        {"$project": {
            "driver_roll_no": "$customer.orders.bids.driver_roll_no",
            "amount": "$customer.orders.bids.amount"
        }}
    ])
    # extract the bids info
    bids = {bid["driver_roll_no"]: bid["amount"] for bid in bids}
    bids_list = []
    for driver_roll_no, amount in bids.items():
        bids_list.append({
            "driver_roll_no": driver_roll_no,
            "name": db.find_one({"roll_no": driver_roll_no})["name"],
            "bid": amount
        })
    print("Order in progress:", order_in_progress, "; bids:", bids_list)
    return bids_list


# # Accept Bid (remove bids global var key)
@order_router.post("/orders/inprogress/bid/accept")
async def accept_bid(driver_roll_no: int, user=Depends(get_current_user)):
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
    # check if the driver already has an order in progress
    driver_obj = db.find_one({"roll_no": driver_roll_no})["driver"]
    if driver_obj["order_in_progress"] is not None:
        print("Driver already has an order in progress!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver already has an order in progress",
        )

    # query the DB for order in progress
    order_in_progress = db.find_one({"roll_no": user.roll_no})[
        "customer"]["order_in_progress"]
    # fetch the order from the DB
    order = list(db.aggregate([
        {"$match": {"customer.orders.id": order_in_progress}},
        {"$unwind": "$customer.orders"},
        {"$match": {"customer.orders.id": order_in_progress}},
        {"$project": {
            "order": "$customer.orders"
        }}
    ]))[0]["order"]

    # get the bid
    bid = list(db.aggregate([
        {"$match": {"customer.orders.id": order_in_progress}},
        {"$unwind": "$customer.orders"},
        {"$match": {"customer.orders.id": order_in_progress}},
        {"$unwind": "$customer.orders.bids"},
        {"$match": {"customer.orders.bids.driver_roll_no": driver_roll_no}},
        {"$project": {
            "amount": "$customer.orders.bids.amount"
        }}
    ]))[0]
    # Update the customer's pending order with the driver_roll_no and delivery_price
    db.update_one(
        {
            "roll_no": user.roll_no,
            "customer.orders.id": order_in_progress
        },
        {
            "$set": {
                "customer.orders.$.assigned_to": driver_roll_no,
                "customer.orders.$.delivery_price": bid["amount"],
                "customer.orders.$.status": "assigned"
            }
        }
    )
    # Add the order to the driver's orders array
    db.update_one(
        {
            "roll_no": driver_roll_no
        },
        {
            "$push": {
                "driver.orders": {
                    **order,
                    "status": "assigned",
                    "assigned_to": user.roll_no
                }
            }
        }
    )
    # update driver's order in progress
    db.update_one(
        {
            "roll_no": driver_roll_no
        },
        {
            "$set": {
                "driver.order_in_progress": order_in_progress
            }
        }
    )

    return {
        "customer_roll_no": user.roll_no,
        "driver_roll_no": driver_roll_no,
        "delivery_price":  bid["amount"]
    }


# Update Job Status
@order_router.post("/orders/inprogress/update")
async def update_job_status(status: str, user=Depends(get_current_user)):
    '''
    Update the status of the order in the database
    Updates the status of the order in the database for the customer
    '''

    # fetch the order in progress from the DB
    order_in_progress = db.find_one({"roll_no": user.roll_no})[
        "customer"]["order_in_progress"]
    if not order_in_progress:
        order_in_progress = db.find_one({"roll_no": user.roll_no})[
            "driver"]["order_in_progress"]

    if not order_in_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No order in progress",
        )

    # Update the order in the database with the order_status, do it for both customer and driver
    # update the status of the order in the database for the customer
    db.update_one(
        {
            "customer.orders.id": order_in_progress
        },
        {
            "$set": {
                "customer.orders.$.status": status,
                "customer.orders.$.delivered_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S") if status == "delivered" else None
            }
        }
    )
    # update the status of the order in the database for the driver
    db.update_one(
        {
            "driver.orders.id": order_in_progress
        },
        {
            "$set": {
                "driver.orders.$.status": status,
                "driver.orders.$.delivered_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S") if status == "delivered" else None
            }
        }
    )
    if status == "delivered":
        # update driver's order in progress
        db.update_one(
            {
                "roll_no": user.roll_no
            },
            {
                "$set": {
                    "driver.order_in_progress": None
                }
            }
        )
        # update customer's order in progress
        db.update_one(
            {
                "customer.orders.id": order_in_progress
            },
            {
                "$set": {
                    "customer.order_in_progress": None
                }
            }
        )

    return {"status": status}


# get the status of the order in progress
@order_router.get("/orders/inprogress")
async def getOrderStatus(user=Depends(get_current_user)):
    """ 
    Get the status of the order for the customer    
    """
    # fetch the order in progress from the DB
    order_in_progress = db.find_one({"roll_no": user.roll_no})[
        "customer"]["order_in_progress"]
    if not order_in_progress:
        order_in_progress = db.find_one({"roll_no": user.roll_no})[
            "driver"]["order_in_progress"]
        # fetch the order from the DB
        if order_in_progress:
            order = list(db.aggregate([
                {"$match": {"driver.orders.id": order_in_progress}},
                {"$unwind": "$driver.orders"},
                {"$match": {"driver.orders.id": order_in_progress}},
                {"$project": {
                    "order": "$driver.orders"
                }}
            ]))[0]["order"]
        print("/orders/inprogress driver:", order_in_progress, order)
    else:
        # fetch the order from the DB
        order = list(db.aggregate([
            {"$match": {"customer.orders.id": order_in_progress}},
            {"$unwind": "$customer.orders"},
            {"$match": {"customer.orders.id": order_in_progress}},
            {"$project": {
                "order": "$customer.orders"
            }}
        ]))[0]["order"]
        print("/orders/inprogress customer:", order_in_progress, order)

    if not order_in_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No order in progress",
        )

    # get the assignee's name
    assignee_name = None if not order["assigned_to"] else db.find_one(
        {"roll_no": order["assigned_to"]})["name"]

    return {
        **order,
        "assignee_name": assignee_name
    }


# get all orders of a customer
@ order_router.get("/orders/customer/getAllOrders")
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
            "id": order["id"],
            "deliver_to": order["deliver_to"],
            "order_amount": order["order_amount"],
            "placed_at": order["placed_at"],
            "driver_name": "No Driver Yet" if order["assigned_to"] == -1 else db.find_one({"roll_no": order["assigned_to"]})["name"],
        }

        orders_list.append(orderHistory)

    return orders_list


# remove all orders of a customer
@ order_router.delete("/customer/orders/removeAllOrders")
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


# An EndPoint To Get Status Of An Order
@order_router.get("/orders/status")  # TODO: THERES A BUG FIX IT
async def getCustomerOrderStatus(id: str, user=Depends(get_current_user)):
    """
    Get the status of the order for the customer    
    """
    roll_no = user.roll_no
    # fetch the order from DB for the current user using order id
    try:
        order = list(db.aggregate([
            {"$match": {"roll_no": roll_no}},
            {"$unwind": "$customer.orders"},
            {"$match": {"customer.orders.id": id}},
            {"$project": {
                "order": "$customer.orders"
            }}
        ]))[0]["order"]
    except IndexError:
        try:
            order = list(db.aggregate([
                {"$match": {"roll_no": roll_no}},
                {"$unwind": "$driver.orders"},
                {"$match": {"driver.orders.id": id}},
                {"$project": {
                    "order": "$driver.orders"
                }}
            ]))[0]["order"]
        except IndexError:
            order = None
    print("/orders/status:", order)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No order found",
        )

    # get the assignee's name
    assignee_name = None if not order["assigned_to"] else db.find_one(
        {"roll_no": order["assigned_to"]})["name"]

    return {
        **order,
        "assignee_name": assignee_name
    }


@order_router.post("/orders/inprogress/cancel")
async def cancelOrder(user=Depends(get_current_user)):
    '''
    Cancel the order in progress
    '''

    # fetch the order in progress from the DB
    order_in_progress = db.find_one({"roll_no": user.roll_no})[
        "customer"]["order_in_progress"]
    if not order_in_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No order in progress",
        )

    # Update the order in the database with the order_status, do it for both customer and driver
    # update the status of the order in the database for the customer
    db.update_one(
        {
            "customer.orders.id": order_in_progress
        },
        {
            "$set": {
                "customer.orders.$.status": "cancelled",
                "customer.orders.$.delivered_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        }
    )
    # update the status of the order in the database for the driver
    db.update_one(
        {
            "driver.orders.id": order_in_progress
        },
        {
            "$set": {
                "driver.orders.$.status": "cancelled",
                "driver.orders.$.delivered_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        }
    )

    # update the order_in_progress field in the database for the customer
    db.update_one(
        {
            "roll_no": user.roll_no
        },
        {
            "$set": {
                "customer.order_in_progress": None
            }
        }
    )
    # update the order_in_progress field in the database for the driver
    db.update_one(
        {
            "driver.orders.id": order_in_progress
        },
        {
            "$set": {
                "driver.order_in_progress": None
            }
        }
    )

    return {"detail": "Order Cancelled"}
