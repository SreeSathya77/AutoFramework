import pytest
from playwright.sync_api import sync_playwright
from src.pages.login_page import LoginPage
from src.pages.onboard_customer_page import OnboardCustomerPage
from src.pages.case_page import CaseManagementPage
from utils.shared_data import SharedData
from utils.logger import Logger
from src.pages.refund_auto_case_creation import execute_full_refund_automation

logger = Logger.get_logger()

@pytest.fixture(scope="module")
def shared_setup(run_folder, base_url, request):
    """
    STRICT VISIBLE SESSION: Maintains one browser for all scenarios in this file.
    The browser only closes after the final scenario is completed.
    """
    if not base_url:
        pytest.fail("base_url is missing from pytest.ini")

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context(viewport={"width": 1500, "height": 800})
    page = context.new_page()

    logger.info("🚀 Launching VISIBLE browser for shared session...")
    login_page = LoginPage(page, report_dir=run_folder)
    login_page.navigate_to_login(base_url)
    login_page.perform_login("superadmin_qm@yopmail.com", "Superadmin@1234")
    login_page.verify_login_success()

    objs = {
        "page": page,
        "onboard": OnboardCustomerPage(page, report_dir=run_folder),
        "case": CaseManagementPage(page, report_dir=run_folder),
    }

    yield objs

    # --- UPDATED TEARDOWN SECTION ---
    if request.config.getoption("--hold"):
        print("\n" + "=" * 60)
        print(">>> SCENARIOS FINISHED.")
        print(">>> Browser held for review. (Application may timeout/logout)")
        print(">>> Press ENTER in this console to terminate.")
        print("=" * 60 + "\n")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

    # Use a try block to ignore errors if the browser already crashed/expired
    try:
        logger.info("Closing browser and stopping playwright...")
        browser.close()
        playwright.stop()
    except Exception as e:
        # This prevents the "Target closed" or "Session expired" errors
        # from appearing in your final console summary.
        pass

def test_onboard_then_create_case(shared_setup):
    """Scenario 1: Detailed Onboarding and Case Creation"""
    objs = shared_setup
    onboard = objs["onboard"]
    case_page = objs["case"]

    logger.info("Step 1: Starting Onboarding...")
    onboard.navigate_to_onboarding()

    # Full data capture logic
    f_name, l_name, email = onboard.fill_and_submit_account_details("United States")
    onboard.fill_vehicle_details(count=1)

    captured_id = onboard.get_permanent_account_id()
    assert captured_id is not None, "Failed to capture Account ID"
    SharedData.account_id = captured_id
    logger.info(f"Account {captured_id} saved to SharedData.")

    onboard.fill_payment_details(f_name, l_name, card_count=1)
    onboard.complete_final_payment()
    onboard.navigate_to_account_summary()

    # Case creation logic
    logger.info(f"Step 2: Creating case for account: {SharedData.account_id}")
    case_page.navigate_to_create_case()
    case_page.fill_case_details(SharedData.account_id)
    case_page.verify_case_and_navigate_to_dashboard(SharedData)

    logger.info("✅ Case Created. Ready for Scenario 2.")

def test_refund_auto_flow(shared_setup):
    """Scenario 2: Refund Flow (Independent but shares browser)"""
    page = shared_setup["page"]
    logger.info("Step 3: Triggering Refund Flow scenario...")
    assert execute_full_refund_automation(page), "The Refund Automation flow failed."
    logger.info("✅ Refund Flow Complete.")
