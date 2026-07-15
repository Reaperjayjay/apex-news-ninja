import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load the existing .env file
load_dotenv()

# Retrieve the hidden credentials
uri = os.getenv("MONGODB_URI")
ca_path = os.getenv("CA_FILE_PATH")

if not uri or not ca_path:
    raise ValueError("Database credentials or CA file path missing from .env file.")

# Establish the secure connection
client = MongoClient(
    uri,
    tls=True,
    tlsCAFile=ca_path,
    tlsAllowInvalidCertificates=False
)

try:
    client.admin.command("ping")
    print("Connected Successfully with Python 3.12!")
except Exception as e:
    print("Connection failed:", e)
