import dotenv
import os

dotenv.load_dotenv()
production = os.getenv("PYTHON_ENV", "DEV").lower() == "prod"

config = {
    "host": {
        "ip": os.getenv("GOOGLE_OAUTH_HOST", "localhost"),
        "port": os.getenv("GOOGLE_OAUTH_PORT", 8080),
    },
    "mongo": {
        "host": os.getenv("MONGO_DB_HOST", "localhost"),
        "port": os.getenv("MONGO_DB_PORT", 27017),
        "user": os.getenv("MONGO_DB_USER"),
        "password": os.getenv("MONGO_DB_PASS"),
        "db": os.getenv("MONGO_DB_NAME", "netflix"),
    },
}
