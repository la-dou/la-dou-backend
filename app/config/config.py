from pydantic import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_USERNAME: str
    MONGO_PASSWORD: str
    MONGO_DB: str
    MONGO_COLLECTION: str
    MONGO_URI: str = ""
    SENDER_EMAIL: str
    SENDGRID_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: dict
    SENDER_EMAIL_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
settings.MONGO_URI = "mongodb+srv://" + settings.MONGO_USERNAME + ":" + settings.MONGO_PASSWORD + \
    "@" + settings.MONGO_URL + '/' + "?retryWrites=true&w=majority"
