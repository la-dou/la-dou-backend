import requests
import json

ENDPOINT = "http://localhost:8000"

def admin_login():
    head = {"Content-Type": "application/x-www-form-urlencoded"}
    auth_info = {"username": "0", "password": "super_secret"}
    response = requests.post(ENDPOINT + "/login", data=auth_info, headers=head)
    response = json.loads(response.text)
    return response
