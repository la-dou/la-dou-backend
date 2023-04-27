import pytest
import requests
import json
from ..login import login
from ..create_order import create_order
from ..remove_order import remove_order

ENDPOINT = "http://localhost:8000"

def test_post_order():
    roll_no = 24100301
    response, data = login(roll_no)
    access_token = data["access_token"]
    response = create_order(roll_no, access_token, "Khoka", "M6", "pending")
    data = response.json()
    assert response.status_code == 200
    assert data["deliver_to"] == "Khoka"
    assert data["deliver_from"] == "M6"
    assert data["status"] == "pending"

    response = remove_order(roll_no, access_token)
    data = response.json()
    assert response.status_code == 200

