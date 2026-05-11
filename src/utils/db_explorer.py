import sys
import os
import re
from datetime import datetime, timezone
from bson.objectid import ObjectId

# Add the project root to the python path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from utils.mongo_client import get_db, get_case_db # Import both connections

def extract_test_data(log_file_path):
    """
    Parses the test execution log to find the specific data generated during the run.
    Returns a dictionary of values to search for.
    """
    search_values = {
        "ids": set(),
        "strings": set()
    }
    
    if not os.path.exists(log_file_path):
        return search_values

    with open(log_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Extract Account IDs (Temp and Perm)
        account_ids = re.findall(r"AccountID: (\d+)", content)
        search_values["ids"].update(account_ids)
        search_values["strings"].update(account_ids)
        
        # Extract Emails
        emails = re.findall(r"email '([^']+)'", content)
        search_values["strings"].update(emails)
        
        # Extract Plates
        plates = re.findall(r"Plate: ([A-Z0-9]+)", content)
        search_values["strings"].update(plates)
        
        # Extract Case IDs
        case_ids = re.findall(r"CaseID: (\d+)", content)
        search_values["ids"].update(case_ids)
        search_values["strings"].update(case_ids)

    print(f"🔍 Extracted {len(search_values['strings'])} unique data points from log to verify against DB.")
    return search_values

def scan_database(db_client, db_name, cutoff_time, test_data, log_func):
    """
    Helper function to scan a specific database client.
    """
    found_collections = set()
    try:
        collection_names = db_client.list_collection_names()
        log_func(f"📚 Scanning DB '{db_name}': Found {len(collection_names)} collections...")

        timestamp_fields = [
            "createdDate", "createdDateTime", "createdAt", 
            "updatedDate", "updatedDateTime", "updatedAt", 
            "lastModified", "lastModifiedDate", "timestamp", "date",
            "caseCreatedDate", "created_at", "updated_at"
        ]
        
        # Common ID fields to check explicitly
        # Added 'value' to catch the CaseIncrement collection
        id_fields = ["_id", "caseId", "caseNumber", "accountId", "accountNumber", "value"]

        for col_name in collection_names:
            collection = db_client[col_name]
            recent_doc = None
            match_reason = ""
            matched_value = None

            # Strategy 1: Direct ID Match (The most robust check)
            if not recent_doc:
                for search_id in test_data["ids"]:
                    query_conditions = [{field: search_id} for field in id_fields]
                    if str(search_id).isdigit():
                        query_conditions.extend([{field: int(search_id)} for field in id_fields])
                    
                    query = {"$or": query_conditions}
                    try:
                        found_doc = collection.find_one(query)
                        if found_doc:
                            recent_doc = found_doc
                            match_reason = f"Direct Match on ID '{search_id}'"
                            matched_value = search_id
                            break
                    except:
                        pass

            # Strategy 2: Check _id (Creation Time) - Only if _id is ObjectId
            if not recent_doc:
                try:
                    dummy_id = ObjectId.from_datetime(cutoff_time)
                    recent_doc = collection.find_one({"_id": {"$gt": dummy_id}}, sort=[("_id", -1)])
                    if recent_doc:
                        match_reason = "New Document Created (Time)"
                except:
                    pass

            # Strategy 3: Check for explicit timestamp fields (Update Time)
            if not recent_doc:
                try:
                    sample_doc = collection.find_one()
                    if sample_doc:
                        # Check ALL potential timestamp fields
                        fields_in_doc = [f for f in timestamp_fields if f in sample_doc]
                        for field in fields_in_doc:
                            query = {field: {"$gte": cutoff_time}}
                            recent_doc = collection.find_one(query, sort=[(field, -1)])
                            if recent_doc:
                                match_reason = f"Updated (field: {field})"
                                break
                except:
                    pass

            # VERIFICATION: If we found a doc via time, double check it contains our data
            if recent_doc and not matched_value:
                doc_str = str(recent_doc)
                for val in test_data["strings"]:
                    if val in doc_str:
                        matched_value = val
                        break
            
            # REPORTING
            if recent_doc and (matched_value or not test_data["strings"]):
                log_func(f"\n✅ CONFIRMED ACTIVITY in: '{db_name}.{col_name}'")
                log_func(f"   -> Reason: {match_reason}")
                if matched_value:
                    log_func(f"   -> Matched Data: {matched_value}")
                log_func(f"   -> ID: {recent_doc.get('_id')}")
                found_collections.add(f"{db_name}.{col_name}")

    except Exception as e:
        log_func(f"❌ Error scanning DB '{db_name}': {e}")
    
    return found_collections

def find_recent_activity(output_file=None):
    """
    Scans BOTH databases (CSE and Case Management) for activity.
    """
    
    def log(message):
        print(message)
        if output_file:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")

    try:
        with open("test_start_time.txt", "r") as f:
            start_timestamp = float(f.read())
        
        cutoff_time = datetime.fromtimestamp(start_timestamp, tz=timezone.utc)
        log(f"🔍 Scanning DBs for collections modified since: {cutoff_time} (UTC)...")
        
        if output_file:
            run_folder = os.path.dirname(output_file)
            log_path = os.path.join(run_folder, "test_execution.log")
            test_data = extract_test_data(log_path)
        else:
            test_data = {"ids": set(), "strings": set()}

    except Exception as e:
        log(f"❌ Error initializing scan: {e}")
        return

    all_found_collections = set()

    # Scan Main DB
    try:
        cse_db = get_db()
        found_cse = scan_database(cse_db, "cseportal", cutoff_time, test_data, log)
        all_found_collections.update(found_cse)
    except Exception as e:
        log(f"❌ Could not connect to Main DB: {e}")

    # Scan Case DB
    try:
        case_db = get_case_db()
        found_case = scan_database(case_db, "case-management", cutoff_time, test_data, log)
        all_found_collections.update(found_case)
    except Exception as e:
        log(f"❌ Could not connect to Case DB: {e}")

    log(f"\n🎉 Scan Complete. Found {len(all_found_collections)} collections related to this test run.")
    if all_found_collections:
        log("Collections updated:")
        for c in sorted(list(all_found_collections)):
            log(f" - {c}")

if __name__ == "__main__":
    find_recent_activity()