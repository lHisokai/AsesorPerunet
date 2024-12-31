from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from logger import logger
from config import config
from datetime import datetime

data = config["mongo"]

uri = f"mongodb://{data['user']}:{data['password']}@{data['host']}:{data['port']}"

client = MongoClient(uri, server_api=ServerApi("1"))
db = client[data["db"]]
try:
    logger.info("Iniciando conexión a la base de datos")
    client.admin.command("ping")
    logger.info("Conectado a la base de datos")
except Exception as e:
    logger.error(e)


def save_email(chat_id, date, email):
    user_doc = db.users.find_one({"from_id": chat_id})
    user_id = user_doc.get("_id", None) if user_doc else None
    if not user_id:
        return None
    return db.emails.insert_one(
        {
            "email": email,
            "user_id": user_id,
            "date": date,
            "active": True,
        }
    )


def users_exists(user_id):
    doc = db.users.find_one({"from_id": user_id})
    return True if doc else False


def get_email_by_chat_id(chat_id):
    user_doc = db.users.find_one({"chat_id": chat_id})
    user_id = user_doc.get("_id", None) if user_doc else None
    email_doc = db.emails.find_one({"user_id": user_id})
    return email_doc.get("email", None) if email_doc else None


def get_emails_by_user_id(user_id):
    user_doc = db.users.find_one({"from_id": user_id})
    user_id = user_doc.get("_id", None) if user_doc else None
    email_doc = db.emails.find({"user_id": user_id})
    emails = [doc["email"] for doc in email_doc]
    return emails


def delete_email(user_id, email):
    return db.emails.delete_one({"email": email, "user_id": user_id})


def update_action(user_id, action):
    db.user_state.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "action": action,
                "date": datetime.now(),
            }
        },
        upsert=True,
    )


def update_state(user_id, state):
    db.user_state.update_one(
        {"user_id": user_id},
        {"$set": {"state": state, "date": datetime.now()}},
        upsert=True,
    )


def get_user_state(user_id):
    return db.user_state.find_one({"user_id": user_id})


def get_user_id_by_chat_id(chat_id):
    doc_user = db.users.find_one({"chat_id": chat_id}) or {}
    return doc_user.get("_id", None)
