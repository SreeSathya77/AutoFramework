import time
from utils.mongo_client import get_db, get_case_db # Import both
from src.utils.logger import Logger

log = Logger.get_logger()

def get_account_id_from_temp_account(email, retries=5, delay=1):
    """
    Finds the most recent temporary account with a given email and returns its accountId.
    Retries several times to handle DB write delays.
    """
    try:
        log.info(f"🔍 [DB_VALIDATION] Searching 'temporary_account' for email '{email}'...")
        db = get_db()
        collection = db["temporary_account"]
        
        for attempt in range(retries):
            # Find the most recent document for that email
            temp_doc = collection.find_one({"emailAddress": email}, sort=[("_id", -1)])
            
            if temp_doc and "accountId" in temp_doc:
                account_id = temp_doc["accountId"]
                log.info(f"✅ [DB_VALIDATION] SUCCESS: Found temporary account with AccountID '{account_id}' on attempt {attempt + 1}.")
                return account_id
            
            log.warning(f"   -> Attempt {attempt + 1}/{retries}: Account not found yet. Retrying in {delay}s...")
            time.sleep(delay)

        log.error(f"❌ [DB_VALIDATION] FAILURE: Could not find 'accountId' in temporary_account for email '{email}' after {retries} attempts.")
        return None
            
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while fetching from temporary_account: {e}")
        return None

def verify_account_in_db(account_id):
    """
    Connects to the DB and verifies that an account exists in the 
    'registered_account' collection.
    """
    try:
        log.info(f"🔍 [DB_VALIDATION] Verifying AccountID '{account_id}' in 'registered_account' collection...")
        db = get_db()
        collection = db["registered_account"]
        
        # The _id field in this collection is the accountId string itself
        account_doc = collection.find_one({"_id": account_id})
        
        if account_doc:
            log.info(f"✅ [DB_VALIDATION] SUCCESS: Found account document for ID '{account_id}'.")
            return True
        else:
            log.error(f"❌ [DB_VALIDATION] FAILURE: Account document for ID '{account_id}' not found.")
            return False
            
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while verifying account: {e}")
        return False

def verify_vehicle_in_db(account_ref_id, plate_number):
    """
    Verifies that a vehicle exists for a given Temporary Account ID (accountRefId) in the 'vehicle_info' collection.
    """
    try:
        log.info(f"🔍 [DB_VALIDATION] Verifying Plate '{plate_number}' for Temp AccountID '{account_ref_id}' in 'vehicle_info'...")
        db = get_db()
        collection = db["vehicle_info"]
        
        # FIX: Search by accountRefId instead of accountId
        vehicle_doc = collection.find_one({"accountRefId": account_ref_id, "plateNumber": plate_number})
        
        if vehicle_doc:
            log.info(f"✅ [DB_VALIDATION] SUCCESS: Found vehicle document for plate '{plate_number}'.")
            return True
        else:
            log.error(f"❌ [DB_VALIDATION] FAILURE: Vehicle document for plate '{plate_number}' not found.")
            return False
            
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while verifying vehicle: {e}")
        return False

def verify_tag_in_db(account_ref_id, tag_alias):
    """
    Verifies that a tag exists for a given Temporary Account ID (accountRefId) in the 'tag_info' collection.
    """
    try:
        log.info(f"🔍 [DB_VALIDATION] Verifying Tag Alias '{tag_alias}' for Temp AccountID '{account_ref_id}' in 'tag_info'...")
        db = get_db()
        collection = db["tag_info"]
        
        # FIX: Search by accountRefId instead of accountId
        tag_doc = collection.find_one({"accountRefId": account_ref_id})
        
        if tag_doc:
            log.info(f"✅ [DB_VALIDATION] SUCCESS: Found tag document for Temp AccountID '{account_ref_id}'.")
            return True
        else:
            log.error(f"❌ [DB_VALIDATION] FAILURE: Tag document for Temp AccountID '{account_ref_id}' not found.")
            return False
            
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while verifying tag: {e}")
        return False

def verify_case_in_db(case_id):
    """
    Connects to the CASE MANAGEMENT DB and verifies that a case exists.
    """
    try:
        log.info(f"🔍 [DB_VALIDATION] Verifying CaseID '{case_id}' in Case Management DB...")
        db = get_case_db() # Use the new connection
        collection = db["cases"] 
        
        case_doc = collection.find_one({"_id": case_id})
        
        if case_doc:
            log.info(f"✅ [DB_VALIDATION] SUCCESS: Found case document for ID '{case_id}'.")
            return True
        else:
            log.error(f"❌ [DB_VALIDATION] FAILURE: Case document for ID '{case_id}' not found in 'cases' collection.")
            return False
            
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while verifying case: {e}")
        return False

def get_current_case_sequence():
    """
    Connects to the Case DB and gets the current value from the CaseIncrement collection.
    """
    try:
        log.info("🔍 [DB_VALIDATION] Getting current case sequence from 'CaseIncrement'...")
        db = get_case_db()
        collection = db["CaseIncrement"]
        
        # Find the specific document where _id is "caseIncrementSeq"
        seq_doc = collection.find_one({"_id": "caseIncrementSeq"})
        
        if seq_doc and "value" in seq_doc:
            # The value is stored as a string, e.g., "01075". Convert to int.
            sequence_value_str = seq_doc["value"]
            sequence_value_int = int(sequence_value_str)
            log.info(f"✅ [DB_VALIDATION] Current case sequence is: {sequence_value_int}")
            return sequence_value_int
        else:
            log.error("❌ [DB_VALIDATION] Could not find document with _id 'caseIncrementSeq' or it is missing the 'value' field.")
            return None
            
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while getting case sequence: {e}")
        return None

def verify_case_sequence_incremented(previous_sequence, new_case_id):
    """
    Verifies that the case sequence has incremented by 1 and matches the new case ID.
    """
    if previous_sequence is None:
        log.error("❌ [DB_VALIDATION] Cannot verify sequence increment because the previous sequence was not retrieved.")
        return

    log.info(f"🔍 [DB_VALIDATION] Verifying case sequence increment. Previous value: {previous_sequence}, New Case ID: {new_case_id}")
    
    # Get the new sequence value from the DB
    new_sequence = get_current_case_sequence()
    
    if new_sequence is None:
        log.error("❌ [DB_VALIDATION] Cannot verify sequence increment because the new sequence could not be retrieved.")
        return

    # Verification 1: Check if it incremented by 1
    expected_sequence = previous_sequence + 1
    if new_sequence == expected_sequence:
        log.info(f"✅ [DB_VALIDATION] SUCCESS: Sequence incremented correctly to {new_sequence}.")
    else:
        log.error(f"❌ [DB_VALIDATION] FAILURE: Sequence did not increment correctly. Expected: {expected_sequence}, but got: {new_sequence}.")

    # Verification 2: Check if it matches the new Case ID
    try:
        new_case_id_int = int(new_case_id)
        if new_sequence == new_case_id_int:
            log.info(f"✅ [DB_VALIDATION] SUCCESS: New sequence '{new_sequence}' matches the created Case ID '{new_case_id}'.")
        else:
            log.error(f"❌ [DB_VALIDATION] FAILURE: New sequence '{new_sequence}' does not match the created Case ID '{new_case_id}'.")
    except ValueError:
        log.error(f"❌ [DB_VALIDATION] Could not compare sequence to Case ID '{new_case_id}' because it is not a valid integer.")

def get_all_cases_from_db():
    """
    Fetches all documents from the 'cases' collection in the case-management DB.
    """
    log.info("🔍 [DB_VALIDATION] Fetching all cases from the 'cases' collection...")
    try:
        db = get_case_db()
        collection = db["cases"]
        cases = list(collection.find({}))
        log.info(f"✅ [DB_VALIDATION] Found {len(cases)} total cases in the database.")
        return cases
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while fetching all cases: {e}")
        return []

def get_case_type_configurations():
    """
    Fetches and formats all CaseType-SubType combinations from the caseTypeConfiguration collection.
    """
    log.info("🔍 [DB_VALIDATION] Fetching all case type configurations...")
    try:
        db = get_case_db()
        collection = db["caseTypeConfiguration"]
        configs = list(collection.find({}))
        
        type_subtype_list = []
        for config in configs:
            case_type = config.get("caseType")
            sub_types = config.get("subTypes", [])
            if case_type and sub_types:
                for sub_type in sub_types:
                    sub_type_name = sub_type.get("name")
                    if sub_type_name:
                        # Replicate the UI's "Type-SubType" format
                        type_subtype_list.append(f"{case_type}-{sub_type_name}")
        
        log.info(f"✅ [DB_VALIDATION] Found {len(type_subtype_list)} CaseType-SubType configurations.")
        return type_subtype_list
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while fetching case type configurations: {e}")
        return []

def get_case_by_id(case_id):
    """
    Fetches a single case document from the database by its ID.
    """
    log.info(f"🔍 [DB_VALIDATION] Fetching case document for ID '{case_id}'...")
    try:
        db = get_case_db()
        collection = db["cases"]
        case = collection.find_one({"_id": case_id})
        
        if case:
            log.info(f"✅ [DB_VALIDATION] SUCCESS: Retrieved document for Case ID '{case_id}'.")
            return case
        else:
            log.error(f"❌ [DB_VALIDATION] FAILURE: No document found for Case ID '{case_id}'.")
            return None
    except Exception as e:
        log.exception(f"❌ [DB_VALIDATION] An error occurred while fetching case by ID: {e}")
        return None