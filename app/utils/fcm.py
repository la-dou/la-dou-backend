import firebase_admin
from firebase_admin import credentials, messaging
from ..config.database import db
from ..config.config import settings

firebase_cred = credentials.Certificate(
    settings.GOOGLE_APPLICATION_CREDENTIALS)
firebase_app = firebase_admin.initialize_app(firebase_cred)


def send_notification(title: str, body: str, token: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )
    response = messaging.send(message)
    # print("Successfully sent message:", response)


def send_notification_to_user(title: str, body: str, roll_no: int):
    # fetch user from db
    user = db.find_one({"roll_no": roll_no})
    # send notification to all tokens
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        tokens=user["fcm_device_token"]
    )
    response = messaging.send_multicast(message)
    # print("Successfully sent message:", response)
