import pytest
import requests
import json

ENDPOINT = "http://localhost:8000"

def remove_order(roll_no, access_token):
    response = requests.delete(ENDPOINT + "/customer/orders/removeAllOrders", headers={"Authorization": f"Bearer {access_token}"})
    return response