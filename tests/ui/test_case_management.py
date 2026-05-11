import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.onboard_customer_page import OnboardCustomerPage
from src.pages.case_page import CaseManagementPage # Updated to use the correct class name
from src.pages.dashboard_page import DashboardPage
from utils.shared_data import SharedData
from utils.logger import Logger

logger = Logger.get_logger()

@pytest.fixture
def test_setup(page: Page, run_folder, base_url):
    if not base_url:
        pytest.fail("base_url is missing from pytest.ini")

    login_page = LoginPage(page, report_dir=run_folder)
    login_page.navigate_to_login(base_url)
    login_page.perform_login("superadmin_qm@yopmail.com", "Superadmin@1234")
    login_page.verify_login_success()

    return {
        "page": page,
        "onboard": OnboardCustomerPage(page, report_dir=run_folder),
        "case": CaseManagementPage(page, report_dir=run_folder), # Updated class name
        "dashboard": DashboardPage(page)
    }


def test_onboard_then_create_case(test_setup):
    objs = test_setup
    page = objs["page"]
    onboard = objs["onboard"]
    case_page = objs["case"]

    # --- STEP 1: ACCOUNT CREATION ---
    logger.info("Step 1: Navigating and Starting Onboarding...")

    onboard.navigate_to_onboarding()
    page.wait_for_load_state("networkidle")

    # FIX 1: Capture the returned names and email
    f_name, l_name, email = onboard.fill_and_submit_account_details("United States")

    onboard.fill_vehicle_details(count=1)

    # Capture and SHARE the account ID
    captured_id = onboard.get_permanent_account_id()
    assert captured_id is not None
    SharedData.account_id = captured_id
    logger.info(f"Account {captured_id} saved to SharedData.")

    # FIX 2: Pass the f_name and l_name into the payment details[cite: 4, 5]
    onboard.fill_payment_details(f_name, l_name, card_count=1)

    onboard.complete_final_payment()
    onboard.navigate_to_account_summary()

    # --- STEP 2: CREATE CASE ---
    logger.info(f"Step 2: Creating case for account: {SharedData.account_id}")

    case_page.navigate_to_create_case()
    case_page.fill_case_details(SharedData.account_id)

    case_page.verify_case_and_navigate_to_dashboard(SharedData)

    logger.info("✅ Full Flow Success!")