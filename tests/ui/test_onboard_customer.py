import pytest
from utils.logger import Logger
from utils.shared_data import SharedData  # Import the central mailbox

logger = Logger.get_logger()

def test_onboard_new_customer_full_flow(logged_in_page, workbench_page, onboard_customer_page):
    logger.info("Starting Onboarding Flow Test")

    # 1. Navigation
    workbench_page.navigate_to_onboard_customer()

    # 2. Step 1: Demographic Info
    f_name, l_name, email = onboard_customer_page.fill_and_submit_account_details()

    # Simple check to ensure we got data back
    assert f_name and l_name, "Step 1: Failed to generate customer names!"

    # 3. Step 2: Vehicles & Tags
    onboard_customer_page.fill_vehicle_details(count=2)

    # Capture Permanent Account ID
    permanent_id = onboard_customer_page.get_permanent_account_id()
    assert permanent_id is not None, "Permanent Account ID was not displayed!"

    # --- UPDATED: Store the ID in shared_data.py ---
    SharedData.account_id = permanent_id
    logger.info(f"📌 Permanent Account ID {permanent_id} stored in SharedData.")
    # ----------------------------------------------

    # 4. Step 3: Payment Info
    step3_success = onboard_customer_page.fill_payment_details(f_name, l_name)
    assert step3_success, "Step 3: Payment details or Summary Card 'PAY' failed!"

    # 5. Step 4: Final Confirmation Modal
    final_success = onboard_customer_page.complete_final_payment()
    assert final_success, "Step 4: Final Modal Confirmation failed!"

    # 6. Step 5: Post-Payment Navigation
    summary_nav_success = onboard_customer_page.navigate_to_account_summary()
    assert summary_nav_success, "Step 5: Navigation to Account Summary failed!"

    logger.info("Test completed successfully.")