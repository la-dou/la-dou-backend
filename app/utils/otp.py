import random
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config.config import settings

import os


OTP_DICTIONARY = {} # this stores the otp and time stamp for 5 minutes
VERIFICATION_TOKENS = {} # this stores a token for 30 minutes after the otp is verified

OTP_TIMEOUT_SECONDS = 300


def generate_OTP(client_id: int):
    otp = random.randint(1000, 9999)
    # get the time stamp
    time_stamp = datetime.now()
    # store the otp and time stamp in the dictionary
    OTP_DICTIONARY[client_id] = (otp, time_stamp)

    return otp


def verify_OTP(client_id: int, otp: int):
    # check if the client id is present in the dictionary
    if client_id in OTP_DICTIONARY:
        stored_otp, stored_time_stamp = OTP_DICTIONARY[client_id]
        # check if the otp is correct
        if stored_otp == otp:
            # check if the otp is not expired
            if (datetime.now() - stored_time_stamp).total_seconds() < OTP_TIMEOUT_SECONDS:
                # delete the otp from the dictionary
                del OTP_DICTIONARY[client_id]
                # generate a token
                token: str = os.urandom(16).hex()
                # store the token in the verified token dictionary
                VERIFICATION_TOKENS[client_id] = (token, datetime.now())
                return (True, token)
            else:
                return (False, "OTP expired")
        else:
            return (False, "Invalid OTP")
    else:
        return (False, "Invalid client id")


async def send_email(email: str, otp):
    
    sender_email = settings.SENDER_EMAIL
    receiver_email = email
    password = settings.SENDER_EMAIL_PASSWORD
    subject = "OTP verification code"
    message = f"Your OTP verification code is: {otp}"
    # try:
        
    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add body to email
    msg.attach(MIMEText(message, 'plain'))

    # Create SMTP session
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to email account
    server.login(sender_email, password)

    # Send email
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()


def verify_token(client_id: int, token: str):
    # print(VERIFICATION_TOKENS, client_id, token)
    if client_id in VERIFICATION_TOKENS:
        stored_token, stored_time_stamp = VERIFICATION_TOKENS[client_id]
        # check if the token is correct
        if stored_token == token:
            # check if the token is not expired
            if (datetime.now() - stored_time_stamp).total_seconds() < 60*30:
                # delete the token from the dictionary
                del VERIFICATION_TOKENS[client_id]
                return (True, "success")
            else:
                return (False, "Token expired")
        else:
            return (False, "Invalid token")
    else:
        return (False, "Invalid client id")
        
