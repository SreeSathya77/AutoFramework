class SharedData:
    """
    A simple singleton-like class to hold data that needs to be shared
    between different test files during a single pytest session.
    """
    def __init__(self):
        self.account_number = None
        self.customer_name = None
        self.email = None
        self.case_id = None
        self.case_type = None
        self.case_subtype = None
        self.reason_code = None
        self.case_priority = None
        self.case_description = None
        self.case_comment = None
        # Add any other data you need to share here
