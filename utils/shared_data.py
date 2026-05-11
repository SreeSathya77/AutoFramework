# utils/shared_data.py

class SharedData:
    """A central 'mailbox' to store data during a test run."""
    temp_account_id = None
    account_id = None  # This stores the Permanent Account Number