from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# --- Connection Details ---

# Main Application DB (cseportal)
MONGO_URI_CSE = (
    "mongodb://quantumqa:quantumqa@"
    "mongors0-3:9042,"
    "mongors0-4:9142,"
    "mongors0-5:9242/"
    "cseportal?replicaSet=rs0&authSource=admin"
)

# Case Management DB
# Updated authSource to match the target database
MONGO_URI_CASE = (
    "mongodb://quantumdev:quantumdev@"
    "mongo-case-management-qa-rs0-0:9001,"
    "mongo-case-management-qa-rs0-1:9002,"
    "mongo-case-management-qa-rs0-2:9003/"
    "case-management?replicaSet=rs0&authSource=case-management"
)
# Note: Assumed DB name is 'case-management-qa'. This might need to be changed.

# --- Connection Functions ---

def get_db():
    """Returns the main 'cseportal' database client."""
    try:
        client = MongoClient(MONGO_URI_CSE, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client["cseportal"]
    except ServerSelectionTimeoutError as e:
        raise RuntimeError(f"MongoDB (CSE) connection failed: {e}") from e

def get_case_db():
    """Returns the 'case-management' database client."""
    try:
        # We might need to adjust the URI if the replica set name or db name is different
        client = MongoClient(MONGO_URI_CASE, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client["case-management"]
    except ServerSelectionTimeoutError as e:
        raise RuntimeError(f"MongoDB (Case Management) connection failed: {e}") from e
