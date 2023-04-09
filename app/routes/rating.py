from fastapi import APIRouter, status, HTTPException, Request
from ..config.database import db

from ..models.rating import Rating

ratings_router = APIRouter()

# get the rating of a driver
@ratings_router.get("/driver")
async def get_rating_driver(roll_no: str):

    try:
        roll_no = int(roll_no)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid roll number",
        )

    # get the user from the database
    user = db.find_one({"roll_no": roll_no})

    # check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # check if the user is a driver
    if not user["driver"] or user["driver"]["deactivated"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a driver",
        )
    
    # get the rating of the driver
    try:
        rating_obj = user["driver"]["rating"]
        rating = rating_obj["sum"] / rating_obj["count"]
    except:
        rating = 0

    # return the rating of the driver with 2 decimal places
    return {"rating": round(rating, 2)}


# update the rating of a driver
@ratings_router.post("/rate/driver")
async def update_rating_driver(roll_no: str, rating: int):

    print("Rating driver", roll_no, "with rating", rating)
    # rating should be between 0 and 5
    if rating < 0 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid rating. Rating should be between 0 and 5",
        )

    try:
        roll_no = int(roll_no)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid roll number",
        )

    # get the user from the database
    user = db.find_one({"roll_no": roll_no})

    # check if the user exists
    if not user:
        print("User with roll number", roll_no, "not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # check if the user is a driver (and not deactivated)
    if not user["driver"] or user["driver"]["deactivated"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a driver",
        )

    # update the rating of the driver
    try:
        rating_obj = user["driver"]["rating"]

        # convert the rating_obj to a Rating object
        rating_obj = Rating(**rating_obj)

        # update the rating
        rating_obj.sum += rating
        rating_obj.count += 1

        # check if the rating is valid
        if rating_obj.sum < 0 or rating_obj.count < 0:
            raise Exception("Invalid rating. Can't have negative values.")
        
    except Exception as e:
        rating_obj = Rating(**{"sum": rating, "count": 1})

    # update the user in the database
    result = db.update_one(
                    {"roll_no": roll_no},
                    {"$set": {"driver.rating": rating_obj.dict()}}
                )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update rating in DB",
        )

    return {"message": "success"}

# get the rating of a customer
@ratings_router.get("/customer")
async def get_rating_customer(roll_no: str):

    try:
        roll_no = int(roll_no)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid roll number",
        )

    # get the user from the database
    user = db.find_one({"roll_no": roll_no})

    # check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # check if the user is a customer
    if not user["customer"] or user["customer"]["deactivated"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a customer",
        )
    
    # get the rating of the customer
    try:
        rating_obj = user["customer"]["rating"]
        rating = rating_obj["sum"] / rating_obj["count"]
    except:
        rating = 0

    # return the rating of the customer with 2 decimal places
    return {"rating": round(rating, 2)}


# update the rating of a customer
@ratings_router.post("/customer")
async def update_rating_customer(roll_no: str, rating: int):

    # rating should be between 0 and 5
    if rating < 0 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid rating. Rating should be between 0 and 5",
        )

    try:
        roll_no = int(roll_no)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid roll number",
        )

    # get the user from the database
    user = db.find_one({"roll_no": roll_no})

    # check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # check if the user is a customer (and not deactivated)
    if not user["customer"] or user["customer"]["deactivated"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a customer",
        )

    # update the rating of the customer
    try:
        rating_obj = user["customer"]["rating"]

        # convert the rating_obj to a Rating object
        rating_obj = Rating(**rating_obj)

        # update the rating
        rating_obj.sum += rating
        rating_obj.count += 1

        # check if the rating is valid
        if rating_obj.sum < 0 or rating_obj.count < 0:
            raise Exception("Invalid rating. Can't have negative values.")
        
    except Exception as e:
        rating_obj = Rating(**{"sum": rating, "count": 1})

    # update the user in the database
    result = db.update_one(
                    {"roll_no": roll_no},
                    {"$set": {"customer.rating": rating_obj.dict()}}
                )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update rating in DB",
        )

    return {"message": "success"}