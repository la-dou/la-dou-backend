def userEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "roll_no": item["roll_no"],
        "name": item["name"],
        "password": item["password"],
        "phone_number": item["phone_number"],
        "gender": item["gender"],
        "email_verified": item["email_verified"],
        "phone_verified": item["phone_verified"],
        "fcm_device_token": item["fcm_device_token"],
        "customer": item["customer"],
        "driver": item["driver"],
    }
    
def usersEntity(items) -> list:
    return [userEntity(item) for item in items]
    