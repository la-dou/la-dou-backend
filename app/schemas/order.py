def orderEntity(item) -> dict:
    
    orderDict = {}
    
    try:
        orderDict = {
            "order_id": item["order_id"],
            "deliver_to": item["deliver_to"],
            "deliver_from": item["deliver_from"],
            "notes": item["notes"],
            "delivery_price": item["delivery_price"],
            "order_amount": item["order_amount"],
            "placed_at": item["placed_at"],
            "delivered_at": item["delivered_at"],
            "status": item["status"],
            "driver_roll_no": item["driver_roll_no"],
        }
    except:
        pass
    
    return orderDict
    
def ordersEntity(items) -> list:
    return [orderEntity(item) for item in items]

def listOrdersEntity(items) -> list:
    return [ordersEntity(item) for item in items]
    
    
