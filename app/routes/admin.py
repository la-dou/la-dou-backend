from fastapi import APIRouter, Depends, HTTPException, status
from ..config.deps import get_current_user
from ..models.user import  UserSearch
from ..config.database import db
from ..schemas.user import usersEntity


admin = APIRouter()

@admin.get('/search', response_model=list[UserSearch])
async def search_user(search: str):
# search for the user
#print(search)
#print(type(search))
    if (search.isdigit()):
        #exact match for int and for string starts with match
        query =  { "$or": [ { "roll_no": int(search) }, { "name": { "$regex": '^'+search+'.*', "$options": "i" } } ] }
    else:
        
        query =  { "name": { "$regex": '^'+search+'.*', "$options": "i" } } 
    users = db.find(query)
    # limit to 5 users
    users = users[:5]

    # return the user
    resp =[]
    for user in users:
        name = user['name']
        roll_no = user['roll_no']
        

        #what if customer and driver rating object is not present #TODO

        


        if user['customer']['rating']['count']!=0:
            rating_as_customer = user['customer']['rating']['sum'] / user['customer']['rating']['count']
        else:
            rating_as_customer = "N/A"
        
        if user['driver']['rating']['count']!=0:
            rating_as_driver = user['driver']['rating']['sum'] / user['driver']['rating']['count']
        else:
            rating_as_driver = "N/A"

        user = UserSearch(name=name, roll_no=roll_no, rating_as_customer=rating_as_customer, rating_as_driver=rating_as_driver)
        resp.append(user)

        
    # EMPTY LIST WHEN NO USER FOUND
    return resp