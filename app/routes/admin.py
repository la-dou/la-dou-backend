from fastapi import APIRouter, Depends, HTTPException, status
from ..config.deps import get_current_user
from ..models.user import UserSearch
from ..config.database import db
from ..schemas.user import usersEntity
from ..models.user import SystemUser
from ..models.order import DriverOrder

admin = APIRouter()


@admin.get('/search', response_model=list[UserSearch])
async def search_user(search: str, sysuser: SystemUser = Depends(get_current_user)):

    if not sysuser.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin",
        )

    if (search.isdigit()):  # if search is a number
        query_for_int = query = {
            "$expr": {
                "$regexMatch": {
                    "input": {"$toString": "$roll_no"},
                    "regex": '^'+search+'.*',
                    "options": "i"
                }
            }
        }
        query_for_string = {
            "name": {"$regex": '^'+search+'.*', "$options": "i"}}

        query = {"$or": [query_for_int, query_for_string]}

    else:
        query = {"name": {"$regex": '^'+search+'.*', "$options": "i"}}

    users = db.find(query)

    # return the user
    resp = []  # no user so ret empty list
    for user in users:

        name = user['name']
        roll_no = user['roll_no']
        phone_number = user['phone_number']

        # try catch better or
        # just check if the key exists
        # if 'customer' in user and 'rating' in user['customer'] and 'count' in user['customer']['rating']:
        try:
            amount_as_customer = user['customer']['orders']['amount'].sum()
        except:
            amount_as_customer = 0
        try:
            if user['customer']['rating']['count'] != 0:
                rating_as_customer = user['customer']['rating']['sum'] / \
                    user['customer']['rating']['count']
                count_as_customer = user['customer']['rating']['count']

                # amount_as_customer = user['customer']['orders']['amount'].sum()

            else:
                rating_as_customer = "N/A"
                count_as_customer = 0
                # amount_as_customer = 0
            deactivated_customer = user['customer']['deactivated']

        except:
            rating_as_customer = "N/A"
            deactivated_customer = True

            count_as_customer = 0
            # amount_as_customer = 0

      # driver details

        try:
            amount_as_driver = user['driver']['orders']['amount'].sum()
        except:
            amount_as_driver = 0
        try:
            if user['driver']['rating']['count'] != 0:
                rating_as_driver = user['driver']['rating']['sum'] / \
                    user['driver']['rating']['count']
                count_as_driver = user['driver']['rating']['count']

                # amount_as_driver = user['driver']['orders']['amount'].sum()
            else:
                rating_as_driver = "N/A"
                count_as_driver = 0
                # amount_as_driver = 0
            deactivated_driver = user['driver']['deactivated']
        except:
            rating_as_driver = "N/A"
            deactivated_driver = True
            count_as_driver = 0
            # amount_as_driver = 0

        user = UserSearch(name=name, roll_no=roll_no, rating_as_customer=rating_as_customer, rating_as_driver=rating_as_driver, phone_number=phone_number, deactivated_customer=deactivated_customer,
                          deactivated_driver=deactivated_driver, count_as_customer=count_as_customer, count_as_driver=count_as_driver, amount_as_customer=amount_as_customer, amount_as_driver=amount_as_driver)

        resp.append(user)

    return resp


@admin.post('/toggle/customer', response_model=bool)
async def deactivate_customer(roll_no: int, sysuser: SystemUser = Depends(get_current_user)):
    if not sysuser.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin",
        )

    query = {"roll_no": roll_no}
    user = db.find_one(query)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not 'customer' in user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    prev_val = user['customer']['deactivated']
    db.update_one(query, {"$set": {"customer.deactivated": not prev_val}})

    return True


@admin.post('/toggle/driver', response_model=bool)
async def deactivate_driver(roll_no: int, sysuser: SystemUser = Depends(get_current_user)):
    if not sysuser.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin",
        )

    query = {"roll_no": roll_no}
    user = db.find_one(query)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not 'driver' in user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    prev_val = user['driver']['deactivated']
    db.update_one(query, {"$set": {"driver.deactivated": not prev_val}})

    return True
