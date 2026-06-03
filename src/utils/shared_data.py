# utils/shared_data.py

class SharedData:
    """
    A class-level data store to hold details shared between 
    different test files during a single pytest session execution.
    """
    # Global Identifiers
    account_id = None
    account_number = None
    customer_name = None
    email = None

    # Case Management details
    case_id = None
    case_type = None
    case_subtype = None
    reason_code = None
    case_priority = None
    case_description = None
    case_comment = None

    # Extracted Payment Gateways Tokens (Captured from Phase 6.7 Modal)
    last_transaction_id = None
    last_payment_status = None
    last_reference_number = None