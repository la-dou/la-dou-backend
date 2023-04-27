import pytest
import requests
import json
from ..login import login
from ..create_order import create_order
from ..remove_order import remove_order
from ..cancel_order import cancel_order

ENDPOINT = "http://localhost:8000"

def test_view_orders():
    driver_roll_no = 24100300
    customer_roll_nos = list(range(24100301, 24100311))
    # print("CUSTOMER ROLL NOS", customer_roll_nos)

    login_driver_response, login_driver_data = login(driver_roll_no)
    access_token_driver = login_driver_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token_driver}"}

    login_cust_responses, login_cust_datas, access_tokens = [], [], []
    for roll_no in customer_roll_nos:
        login_cust_response, login_cust_data = login(roll_no)
        login_cust_responses.append(login_cust_response)
        login_cust_datas.append(login_cust_data)
        access_tokens.append(login_cust_data["access_token"])
    
    # create_order_responses, create_order_datas = [], []

    for i in range(len(customer_roll_nos)):
        create_order_responses.append(create_order(customer_roll_nos[i], access_tokens[i], "Khoka", "M6", "pending"))
        create_order_datas.append(create_order_responses[i].json())
        # print("CREATE ORDER DATA", i, ":", create_order_datas[i])
        
    response = requests.get(ENDPOINT + "/orders/pending", headers=headers)
    # print("HERE", response)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 10
    # print(data)

    for i in range(len(customer_roll_nos)):
        response = remove_order(customer_roll_nos[i], access_tokens[i])
        # print("TEST", i)
        data = response.json()
        # print(response)
        data = json.loads(response.text)


    for i in range(len(customer_roll_nos)):
        response = cancel_order(driver_roll_no, access_token_driver)
        data = response.json()
        # print(response)
        # print("CANCEL ORDER DATA", i, ":", data)