import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.onboard_customer_page import OnboardCustomerPage
from src.pages.case_page import CaseManagementPage
from utils.shared_data import SharedData
from utils.logger import Logger

# Import both specialized phase engines for the Refund automation flow
from src.pages.refund_auto_case_creation import execute_full_refund_automation
from src.pages.refund_case_resolution import execute_refund_case_resolution

from utils.config import LOGIN_CREDENTIALS

logger = Logger.get_logger()


@pytest.fixture(scope="module")
def onboarded_account_id(shared_setup):
    """
    Fixture to perform account onboarding and yield the captured account ID.
    This ensures the refund flow has a valid account to work with.
    """
    objs = shared_setup
    page = objs["page"]
    browser = objs["browser"]
    onboard = objs["onboard"]
    case_page = objs["case"]

    logger.info("Step 1: Starting Onboarding...")
    onboard.navigate_to_onboarding()
    page.wait_for_load_state("networkidle")

    # Fill and submit details
    f_name, l_name, email = onboard.fill_and_submit_account_details("United States")
    onboard.fill_vehicle_details(count=1)

    # Capture and SHARE the account ID
    captured_id = onboard.get_permanent_account_id()
    assert captured_id is not None, "Failed to capture Account ID during onboarding."

    SharedData.account_id = captured_id
    logger.info(f"Account {captured_id} saved to SharedData.")

    # Complete Onboarding process
    onboard.fill_payment_details(f_name, l_name, card_count=1)
    onboard.complete_final_payment()
    onboard.navigate_to_account_summary()

    # --- STEP 2: CREATE CASE (Superadmin) ---
    logger.info(f"Step 2: Creating case for account: {captured_id}")
    case_page.navigate_to_create_case()
    case_page.fill_case_details(captured_id)
    assert case_page.verify_case_and_assign(SharedData), "Assignment failed."

    # --- STEP 3 & 4: SORTER APPROVAL ---
    logger.info("🔓 Step 4: Executing Sorter resolution context window validation...")
    assert case_page.resolve_as_owner_context(browser, SharedData), "Sorter Resolution failed."

    # --- STEP 5: BOS CASE MANAGER APPROVAL ---
    logger.info("👑 Step 5: Executing BOS Case Manager approval context window validation...")
    assert case_page.resolve_as_manager_context(browser, SharedData), "Manager Approval failed."

    # --- STEP 6: SUPERADMIN VERIFICATION (Direct Link Dropdown Value Verification) ---
    logger.info("🔄 Step 6: Verifying final case resolution state as Superadmin...")
    base_url = page.url.split('/operation-workbench')[0]
    direct_case_url = f"{base_url}/operation-workbench/case-management/view-case?caseId={SharedData.case_id}"

    # Refresh/navigate the main Superadmin page directly to the case view
    page.goto(direct_case_url)
    page.wait_for_load_state("networkidle")

    # Target the select dropdown wrapper explicitly
    case_status_dropdown = page.locator("select#caseStatus")
    case_status_dropdown.wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(2000)

    # Robustly target the active checked option inner text value
    selected_option = case_status_dropdown.locator("option:checked, option[selected]")
    selected_status = selected_option.inner_text().strip() if selected_option.count() > 0 else ""
    logger.info(f"Dropdown Extraction Value Snapshot: '{selected_status}'")

    # If the value hasn't updated yet or read empty due to lag, reload once
    if "Resolved" not in selected_status:
        logger.warning("⚠️ Dropdown value is stale. Triggering full page reload to sync database state...")
        page.reload()
        page.wait_for_load_state("networkidle")
        case_status_dropdown.wait_for(state="visible", timeout=10000)
        page.wait_for_timeout(2000)

        selected_option = case_status_dropdown.locator("option:checked, option[selected]")
        selected_status = selected_option.inner_text().strip() if selected_option.count() > 0 else ""
        logger.info(f"Post-Reload Dropdown Extraction Value Snapshot: '{selected_status}'")

    # Assertion checks if 'Resolved' text pattern exists anywhere inside the active option text string
    assert "Resolved" in selected_status, f"❌ Validation Fail: Expected status to contain 'Resolved', but found '{selected_status}'"
    logger.info(f"✅ Step 6 Success: Case {SharedData.case_id} verified as fully 'Resolved' inside drop-down context.")

    yield captured_id


def test_onboard_then_create_case_flow(onboarded_account_id):
    """
    This test function simply consumes the 'onboarded_account_id' fixture.
    This test will pass if the fixture setup passes.
    """
    logger.info(f"✅ Full Onboarding and Case Creation Flow Passed for account: {onboarded_account_id}")


def test_refund_auto_flow(shared_setup, onboarded_account_id):
    """
    Scenario 2: Complete End-to-End Automated Refund Processing & Resolution Flow
    """
    page = shared_setup["page"]
    browser = shared_setup["browser"]  # Safely extracting the active browser engine context to handle multiple sessions

    target_account_id = onboarded_account_id
    SharedData.account_id = target_account_id

    # --- PHASE 1: Process Reversal Payment, Capture Dynamic Success Popups, Search & Scrape Card Metadata ---
    logger.info(f"Step 7: Triggering full automated refund case creation for account: {target_account_id}...")
    assert execute_full_refund_automation(page), "❌ Phase 1 Error: The Refund Automation case creation flow failed."
    logger.info("✅ Phase 1 Complete: Case generated, logged, and targets cached successfully into SharedData memory.")

    # --- PHASE 2: Multi-Context Re-assignments, Sequential Activity Row Approvals & Terminal Resolution Checks ---
    logger.info(
        f"Step 8: Spawning multi-context tracks to drive Case ID #{SharedData.case_id} to complete verification...")
    assert execute_refund_case_resolution(page,
                                          browser), "❌ Phase 2 Error: Multi-Context Approvals or terminal resolution checks failed."

    logger.info(
        f"🎉 Success! Milestone Met: Refund Case #{SharedData.case_id} processed through all nodes to full resolution!")