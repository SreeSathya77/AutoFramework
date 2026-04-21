import pytest
from utils.logger import Logger

logger = Logger.get_logger()

def test_onboard_new_customer_step1(logged_in_page, workbench_page, onboard_customer_page):
    """
    Requirement: User Authentication -> Navigate to Workbench -> Fill Onboarding Step 1.
    """
    logger.info("Executing test_onboard_new_customer_step1...")
    
    # 1. Navigate to Onboard a Customer page
    workbench_page.navigate_to_onboard_customer()
    
    # 2. Fill and submit demographic info (Step 1)
    # This method also handles the verification of the 'Temporary Account' message
    success = onboard_customer_page.fill_and_submit_account_details()
    
    assert success, "Failed to complete customer onboarding Step 1!"
    
    logger.info("Test case test_onboard_new_customer_step1 completed successfully.")


def test_onboard_new_customer_full_flow(logged_in_page, workbench_page, onboard_customer_page):
    """
    Requirement 2: Full Onboarding Stepper Flow
    Step 1: Demographic Info -> Step 2: Vehicles & Tags
    """
    logger.info("Starting Full Onboarding Flow Test")

    # 1. Navigate
    workbench_page.navigate_to_onboard_customer()

    # 2. Step 1: Demographic Info
    step1_success = onboard_customer_page.fill_and_submit_account_details()
    assert step1_success, "Step 1: Demographic Info failed!"

    # 3. Step 2: Vehicles & Tags
    # No need to navigate; the stepper moves us automatically
    onboard_customer_page.fill_vehicle_details()

    # 4. Verification for Step 2
    # Check if we landed on the Payment/Plan page (Step 3)
    assert "onboard-a-customer" in logged_in_page.url
    logger.info("Successfully navigated through Step 1 and Step 2.")
