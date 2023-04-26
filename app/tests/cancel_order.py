import requests
import json

ENDPOINT = "http://localhost:8000"

def cancel_order(roll_no, access_token):
    response = requests.post(ENDPOINT + "/orders/inprogress/cancel", headers={"Authorization": f"Bearer {access_token}"})
    return response