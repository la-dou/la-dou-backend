import requests
import json

ENDPOINT = "http://localhost:8000"

def create_order(roll_no, access_token, deliver_to, deliver_from, status):
    payload = {
        "deliver_to": deliver_to,
        "deliver_from": deliver_from,
        "notes": "Fresh and hot pls",
        "delivery_price": 30,
        "order_amount": 450,
        "placed_at": "smthsmth",
        "delivered_at": "smthsmth2",
        "status": status,
        "bids": [],
        "assigned_to": 0
    }
    response = requests.post(ENDPOINT + f"/orders/customer/create", json=payload, headers={"Authorization": f"Bearer {access_token}"})
    return response