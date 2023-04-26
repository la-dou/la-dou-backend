import requests
import json

ENDPOINT = "http://localhost:8000"

def login(roll_no):
    head = {"Content-Type": "application/x-www-form-urlencoded"}
    auth_info = {"username": f"{roll_no}", "password": "test_password"}
    response = requests.post(ENDPOINT + "/login", data=auth_info, headers=head)
    data = json.loads(response.text)
    return response, data