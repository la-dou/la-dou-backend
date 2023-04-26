import requests
import json

ENDPOINT = "http://localhost:8000"

def delete_user(roll_no):
    delete_response = requests.get(ENDPOINT + f"/delete/user/{roll_no}")
    delete_data = delete_response.json()