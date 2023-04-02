from fastapi import APIRouter, status, HTTPException
from ..config.database import db

ratings_router = APIRouter()

# get the rating of a driver
@ratings_router.get("/driver_rating/{roll_no}")
async def get_rating_driver(roll_no: str):

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

    return {"rating": rating}




# @otp_router.post("/email/generate")
# async def generate_email_otp(roll_no: int):
#     otp = generate_OTP(roll_no)
#     # send otp to the user
#     await send_email(f"{roll_no}@lums.edu.pk", otp)

#     return {"message": "OTP sent to your email"}


# @otp_router.post("/email/verify", response_model=dict())
# async def verify_email_otp(data: VerifyOTP):
#     verification_result, message = verify_OTP(data.roll_no, data.otp)

#     if verification_result:
#         # update the db to set the email_verified field to True
#         db.update_one({"roll_no": data.roll_no}, {"$set": {"email_verified": True}})
#         return {
#             "message": "success",
#             "token": message
#         }

#     elif message == "OTP expired":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="OTP expired",
#         )
#     elif message == "Invalid OTP":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid OTP",
#         )
#     elif message == "Invalid client id":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid client id",
#         )

#     return False

# @otp_router.post("/phone/generate")
# async def generate_phone_otp(roll_no: str):
#     '''
#     Generate OTP and send it to the user's phone number
#     This will fetch the phone number from the database
#     '''
#     pass #TODO: Implement this

# @otp_router.post("/phone/verify", response_model=bool)
# async def verify_phone_otp(roll_no: str, otp: int):
#     '''
#     Generate OTP and send it to the user's phone number
#     Fetch the phone number from the database
#     '''
#     pass #TODO: Implement this
