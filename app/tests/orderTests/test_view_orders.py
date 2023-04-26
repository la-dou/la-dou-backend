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
    
    create_order_responses, create_order_datas = [], []

    for i in range(len(customer_roll_nos)):
        create_order_responses.append(create_order(customer_roll_nos[i], access_tokens[i], "Khoka", "M6", "pending"))
        create_order_datas.append(create_order_responses[i].json())
        # print("CREATE ORDER DATA", i, ":", create_order_datas[i])
        
    response = requests.get(ENDPOINT + "/orders/pending", headers=headers)
    data = response.json()
    assert response.status_code == 200
    # print(data)

    for i in range(len(customer_roll_nos)):
        response = remove_order(customer_roll_nos[i], access_tokens[i])
        data = response.json()
        # print("REMOVE ORDER DATA", i, ":", data)


    # for i in range(len(customer_roll_nos)):
    response = cancel_order(driver_roll_no, access_token_driver)
    data = response.json()
    # print("CANCEL ORDER DATA", i, ":", data)
    
    
    print("Working")
    # customer_roll_no = 24100101
    # login_cust_response, login_cust_data = login(customer_roll_no)
    # access_token_customer = login_cust_data["access_token"]
    # print("CUST ACC TOKEN", access_token_customer)
    # remove_order_response = remove_order(customer_roll_no, access_token_customer)
    # remove_order_data = remove_order_response.json()
    # print("REMOVE ORDER DATA", remove_order_data)
    # create_order_response = create_order(customer_roll_no, access_token_customer, "Khoka", "M6", "ongoing")
    # create_order_data = create_order_response.json()
    # print("CREATE ORDER DATA", create_order_data)
    # login_driver_response, login_driver_data = login(24100300)
    # access_token_driver = login_driver_data["access_token"]
    # print("DRIVER ACC TOKEN", access_token_driver)