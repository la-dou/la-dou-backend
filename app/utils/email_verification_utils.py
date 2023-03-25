import random
from datetime import datetime

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ..config.config import settings

import os

OTP_DICTIONARY = {}

def generate_OTP(client_id):
    otp = random.randint(1000, 9999)

    # get the time stamp
    time_stamp = datetime.now()

    # store the otp and time stamp in the dictionary
    OTP_DICTIONARY[client_id] = (otp, time_stamp)

    return otp

def verify_OTP(client_id, otp):
    # check if the client id is present in the dictionary
    if client_id in OTP_DICTIONARY:
        stored_otp, stored_time_stamp = OTP_DICTIONARY[client_id]
        # check if the otp is correct
        if stored_otp == otp:
            # check if the otp is not expired
            if (datetime.now() - stored_time_stamp).total_seconds() < 300:
                # delete the otp from the dictionary
                del OTP_DICTIONARY[client_id]
                return (True,"success")
            else:
                return (False,"OTP expired")
        else:
            return (False,"Invalid OTP")
    else:
        return (False,"Invalid client id")
    
async def send_email(email: str, otp):
    message = Mail(
        from_email=settings.SENDER_EMAIL,
        to_emails=email,
        subject='La-Dou: OTP for email verification (DO NOT REPLY)',
        html_content=f'<strong>Your OTP is : {otp}</strong>')

    try:
        sg =SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response
    except Exception as e:
        print("Error encountered:")
        print(e)