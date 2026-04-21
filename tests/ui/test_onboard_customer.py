import pytest
from utils.logger import Logger

logger = Logger.get_logger()


def test_onboard_new_customer_full_flow(logged_in_page, workbench_page, onboard_customer_page):
    logger.info("Starting Onboarding Flow Test")

    # 1. Navigation
    workbench_page.navigate_to_onboard_customer()

    # 2. Step 1: Demographic Info
    step1_success = onboard_customer_page.fill_and_submit_account_details()
    assert step1_success, "Step 1: Demographic Info failed!"

    account_id = onboard_customer_page.get_temp_account_id()
    logger.info(f"Step 1 Success. ID: {account_id}")

    # 3. Step 2: Vehicles & Tags
    # Note: Ensure count matches your test data requirements
    onboard_customer_page.fill_vehicle_details(count=2)

    # NEW: Capture Permanent Account ID at the start of the Payment Info Page
    permanent_id = onboard_customer_page.get_permanent_account_id()
    assert permanent_id is not None, "Permanent Account ID was not displayed!"

    # Store in a shared dictionary or list if needed for later verification
    # e.g., shared_data['permanent_id'] = permanent_id

    # 4. Step 3: Payment Info (Card Selection & Summary Page 'PAY')
    step3_success = onboard_customer_page.fill_payment_details()
    assert step3_success, "Step 3: Payment details or Summary Card 'PAY' failed!"

    # 5. Step 4: Final Confirmation Modal
    # This clicks 'Pay' inside the modal pop-up
    final_success = onboard_customer_page.complete_final_payment()
    assert final_success, "Step 4: Final Modal Confirmation failed!"

    # 6. Step 5: Post-Payment Navigation
    # This clicks 'Account Summary' on the success screen source you provided
    summary_nav_success = onboard_customer_page.navigate_to_account_summary()
    assert summary_nav_success, "Step 5: Navigation to Account Summary failed!"

    logger.info("Test completed successfully.")