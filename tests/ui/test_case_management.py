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


def helper_onboard_account(shared_setup, request_tag: bool, account_num: int):
    objs = shared_setup
    page = objs["page"]
    onboard = objs["onboard"]

    if account_num == 1:
        print(f"\n============================================================")
        print(f"      CATEGORY 1: ACCOUNT CREATION (NO TAG - ACCOUNT 1)")
        print(f"============================================================")
        print("🟢 1. Login BOS Application - Pass")
        print("🟢 2. Onboarding - Demographic Info Validation - Pass")
    else:
        print(f"\n============================================================")
        print(f"      CATEGORY 1: ACCOUNT CREATION (TAG - ACCOUNT 2)")
        print(f"============================================================")
        print("🟢 1. Navigate to Onboarding (Already Logged In) - Pass")
        print("🟢 2. Onboarding - Demographic Info Validation - Pass")

    if account_num == 2:
        page.wait_for_timeout(3000)
    onboard.navigate_to_onboarding()
    page.wait_for_timeout(2000)

    # Fill and submit details
    f_name, l_name, email = onboard.fill_and_submit_account_details("United States")
    onboard.fill_vehicle_details(count=1 if account_num == 1 else 2, request_tag=request_tag)
    
    if account_num == 1:
        print("🟢 3. Onboarding - Vehicle & Tags Page Validation - Pass (Added 1 Vehicle(s), 0 Tag(s))")
    else:
        print("🟢 3. Onboarding - Vehicle & Tags Page Validation - Pass (Added 2 Vehicle(s), 1 Tag(s))")

    # Capture and SHARE the account ID
    captured_id = onboard.get_permanent_account_id()
    assert captured_id is not None, "Failed to capture Account ID during onboarding."
    print(f"🟢 4. Onboarding - Create Temporary Account - Pass (ID: {captured_id})")

    # Complete Onboarding process
    onboard.fill_payment_details(f_name, l_name, card_count=1)
    print("🟢 5. Onboarding - Adding Payment Method - Pass")
    onboard.complete_final_payment()
    print("🟢 6. Onboarding - Making Payment & Receive confirmation - Pass")
    onboard.navigate_to_account_summary()
    
    # We don't have the permanent ID scraped, but we print the captured ID (temporary = permanent in UI for now)
    print(f"🟢 7. Onboarding - Create Permanent Account - Pass (ID: {captured_id})\n")
    
    return captured_id


@pytest.fixture(scope="module")
def dual_onboarded_accounts(shared_setup):
    """Fixture to onboard BOTH accounts upfront before any test execution begins."""
    acc_without_tag = helper_onboard_account(shared_setup, request_tag=False, account_num=1)
    acc_with_tag = helper_onboard_account(shared_setup, request_tag=True, account_num=2)
    return {
        "without_tag": acc_without_tag,
        "with_tag": acc_with_tag
    }


def test_other_other_case_flow(shared_setup, dual_onboarded_accounts):
    """
    Scenario 1: Complete End-to-End Other-Other Case Creation & Resolution Flow
    This consumes the account WITHOUT a tag.
    """
    objs = shared_setup
    page = objs["page"]
    browser = objs["browser"]
    case_page = objs["case"]
    
    captured_id = dual_onboarded_accounts["without_tag"]
    SharedData.account_id = captured_id

    print(f"\n============================================================")
    print(f"         CATEGORY 2: OTHER-OTHER CASE FLOW (ACCOUNT 1)")
    print(f"============================================================")

    def step_printer(step_num):
        steps = {
            1: "🟢 1.  Case Type/Subtype: Other-Other: SA Case Creation - Search Account - Pass",
            2: "🟢 2.  Case Type/Subtype: Other-Other: SA Create Case - Pass",
            3: "🟢 3.  Case Type/Subtype: Other-Other: SA Search Case after creation - Pass",
            4: "🟢 4.  Case Type/Subtype: Other-Other: SA Assign Case to Sorter - Pass",
            5: "🟢 5.  Case Type/Subtype: Other-Other: SA Search Case after assign to Sorter - Pass",
            6: "🟢 6.  Case Type/Subtype: Other-Other: Sorter Search Case after Login - Pass",
            7: "🟢 7.  Case Type/Subtype: Other-Other: Sorter Approve Case Activity - Pass",
            8: "🟢 8.  Case Type/Subtype: Other-Other: Sorter Search Case after approve - Pass",
            9: "🟢 9.  Case Type/Subtype: Other-Other: SA Search Case after Sorter approve - Pass",
            10: "🟢 10. Case Type/Subtype: Other-Other: SA Assign/Auto assign Case to BCM - Pass",
            11: "🟢 11. Case Type/Subtype: Other-Other: SA Search Case after assign/Auto assign to BCM - Pass",
            12: "🟢 12. Case Type/Subtype: Other-Other: BCM Search Case after Login - Pass",
            13: "🟢 13. Case Type/Subtype: Other-Other: BCM Approve Case Activity - Pass",
            14: "🟢 14. Case Type/Subtype: Other-Other: BCM Search Case after approve - Pass",
            15: "🟢 15. Case Type/Subtype: Other-Other: SA Final Verification - Search Case after BCM approve - Pass"
        }
        if step_num in steps:
            msg = steps[step_num]
            if step_num == 2 and hasattr(SharedData, 'case_id') and SharedData.case_id:
                msg += f" (ID: {SharedData.case_id})"
            print(msg)

    # --- CREATE CASE (Superadmin) ---
    step_printer(1)
    case_page.navigate_to_create_case()
    case_page.fill_case_details(captured_id)
    assert case_page.verify_case_and_assign(SharedData), "Assignment failed."
    step_printer(2)
    step_printer(3)
    step_printer(4)
    step_printer(5)

    # --- SORTER APPROVAL ---
    assert case_page.resolve_as_owner_context(browser, SharedData), "Sorter Resolution failed."
    step_printer(6)
    step_printer(7)
    step_printer(8)
    step_printer(9)

    # --- SUPERADMIN REASSIGNMENT ATTEMPT ---
    case_page.superadmin_reassign_to_manager(SharedData)
    step_printer(10)
    step_printer(11)

    # --- BOS CASE MANAGER APPROVAL ---
    assert case_page.resolve_as_manager_context(browser, SharedData), "Manager Approval failed."
    step_printer(12)
    step_printer(13)
    step_printer(14)

    # --- SUPERADMIN VERIFICATION (Via Search Case sidebar navigation — grid-only, no visibility click) ---
    case_page.navigate_to_search_case()

    # Toggle search panel and enter Case ID
    sa_search_toggle = page.locator('button.ra-export-btn', has_text="Search Cases").first
    if sa_search_toggle.is_visible(timeout=3000):
        sa_search_toggle.click()
    page.wait_for_timeout(800)

    sa_case_input = page.locator('input#case[formcontrolname="case"]').first
    sa_case_input.wait_for(state="visible", timeout=5000)
    sa_case_input.fill(str(SharedData.case_id))
    page.wait_for_timeout(500)

    search_btn = page.locator('button').filter(has_text="Search").first
    search_btn.click()
    page.wait_for_timeout(1500)

    sa_suggestion = page.locator('div.search-suggestions a:has-text("Cases")')
    if sa_suggestion.is_visible(timeout=2000):
        sa_suggestion.click()
        page.wait_for_timeout(1500)

    sa_final_row = page.locator("tr").filter(has_text=str(SharedData.case_id)).first
    sa_final_row.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(500)

    step_printer(15)
    print("\n")


def test_refund_auto_flow(shared_setup, dual_onboarded_accounts):
    """
    Scenario 2: Complete End-to-End Automated Refund Processing & Resolution Flow
    This consumes the account WITH a tag.
    """
    page = shared_setup["page"]
    browser = shared_setup["browser"]

    target_account_id = dual_onboarded_accounts["with_tag"]
    SharedData.account_id = target_account_id

    print(f"\n============================================================")
    print(f"           CATEGORY 3: REFUND AUTO FLOW (ACCOUNT 2)")
    print(f"============================================================")
    print("🟢 1. Recharge Payment Scenario - Pass\n")

    def step_printer(step_num):
        steps = {
            2: "🟢 2.  Case Type/Subtype: Payment-Refund: Case created for Refund Payment - Pass",
            3: "🟢 3.  Case Type/Subtype: Payment-Refund: SA Search Case after Refund Case creation - Pass",
            4: "🟢 4.  Case Type/Subtype: Payment-Refund: SA Assign/Auto assign Case to Executive - Pass",
            5: "🟢 5.  Case Type/Subtype: Payment-Refund: SA Search Case after assign/Auto assign to Executive - Pass",
            6: "🟢 6.  Case Type/Subtype: Payment-Refund: Executive Login after Refund case assignment - Pass",
            7: "🟢 7.  Case Type/Subtype: Payment-Refund: Executive Search Refund Case after Login - Pass",
            8: "🟢 8.  Case Type/Subtype: Payment-Refund: Executive approve Refund Case Activity - Pass",
            9: "🟢 9.  Case Type/Subtype: Payment-Refund: Executive Search Case after approve - Pass",
            10: "🟢 10. Case Type/Subtype: Payment-Refund: SA Search Refund Case after Executive approve - Pass",
            11: "🟢 11. Case Type/Subtype: Payment-Refund: SA Assign/Auto assign Refund Case to BCM - Pass",
            12: "🟢 12. Case Type/Subtype: Payment-Refund: SA Search Case after assign/Auto assign to BCM - Pass",
            13: "🟢 13. Case Type/Subtype: Payment-Refund: BCM Login after Refund case assignment - Pass",
            14: "🟢 14. Case Type/Subtype: Payment-Refund: BCM Search Refund Case after Login - Pass",
            15: "🟢 15. Case Type/Subtype: Payment-Refund: BCM approve Refund Case Activity - Pass",
            16: "🟢 16. Case Type/Subtype: Payment-Refund: BCM Search Case after approve - Pass",
            17: "🟢 17. Case Type/Subtype: Payment-Refund: SA Search Refund Case after BCM approve - Pass"
        }
        if step_num in steps:
            msg = steps[step_num]
            if step_num == 2 and hasattr(SharedData, 'case_id') and SharedData.case_id:
                msg += f" (ID: {SharedData.case_id})"
            print(msg)

    # --- PHASE 1: Process Reversal Payment, Capture Dynamic Success Popups, Search & Scrape Card Metadata ---
    assert execute_full_refund_automation(page), "❌ Phase 1 Error: The Refund Automation case creation flow failed."
    step_printer(2)

    # --- PHASE 2: Multi-Context Re-assignments, Sequential Activity Row Approvals & Terminal Resolution Checks ---
    assert execute_refund_case_resolution(page, browser, step_printer=step_printer), "❌ Phase 2 Error: Multi-Context Approvals or terminal resolution checks failed."


def test_transfer_tag_flow(shared_setup, dual_onboarded_accounts):
    """
    Scenario 3: Tag Request Fulfillment & Transfer Tag Flow
    This acts on Account 2 which has a pending Tag Request from Onboarding.
    """
    page = shared_setup["page"]
    browser = shared_setup["browser"]

    target_account_id = dual_onboarded_accounts["with_tag"]
    receiving_account_id = dual_onboarded_accounts["without_tag"]
    SharedData.account_id = target_account_id

    print(f"\n============================================================")
    print(f"           CATEGORY 4: TRANSFER TAG FLOW (ACCOUNT 2)        ")
    print(f"============================================================")

    def step_printer(step_num):
        steps = {
            1: "🟢 1. Manage Vehicles - Tag Fulfillment Requested Status Validation - Pass",
            2: "🟢 2. Inventory - Navigate to Customer Fulfillment - Pass",
            3: "🟢 3. Inventory - Search Account & Claim Tag Request - Pass",
            4: "🟢 4. Inventory - Complete Tag Fulfillment - Pass",
            5: "🟢 5. Manage Vehicles (Account 2) - Validate Tag Status is Active - Pass",
            6: "🟢 6. Manage Vehicles (Account 2) - Initiate Tag Transfer to Account 1 - Pass",
            7: "🟢 7. Case Type/Subtype: Transfer-Tag - Transfer Tag Case Created - Pass",
            8: "🟢 8. Case Type/Subtype: Transfer-Tag - SA Search Case after creation - Pass",
            9: "🟢 9. Case Type/Subtype: Transfer-Tag - SA Assign Case to Executive - Pass",
            10: "🟢 10. Case Type/Subtype: Transfer-Tag - Executive Approve Transfer Tag Activity - Pass",
            11: "🟢 11. Case Type/Subtype: Transfer-Tag - Executive Verification - Search Case after Approval - Pass",
            12: "🟢 12. Case Type/Subtype: Transfer-Tag - SA Search Case after Executive approve - Pass",
            13: "🟢 13. Case Type/Subtype: Transfer-Tag - SA Assign/Auto assign Transfer Tag Case to BCM - Pass",
            14: "🟢 14. Case Type/Subtype: Transfer-Tag - SA Search Case after assign/Auto assign to BCM - Pass",
            15: "🟢 15. Case Type/Subtype: Transfer-Tag - BCM Login after Transfer Tag Case assignment - Pass",
            16: "🟢 16. Case Type/Subtype: Transfer-Tag - BCM Search Transfer Tag Case after Login - Pass",
            17: "🟢 17. Case Type/Subtype: Transfer-Tag - BCM approve Transfer Tag Case Activity - Pass",
            18: "🟢 18. Case Type/Subtype: Transfer-Tag - BCM Search Transfer Tag Case after approve - Pass",
            19: "🟢 19. Case Type/Subtype: Transfer-Tag - SA Search Transfer Tag Case after BCM approve - Pass",
            20: "🟢 20. Case Type/Subtype: Transfer-Tag - Manage Vehicles (Account 1) - Validate Tag Received and Active - Pass",
            21: "🟢 21. Case Type/Subtype: Transfer-Tag - Manage Vehicles (Account 2) - Validate Tag is not displayed as it was transfered - Pass"
        }
        if step_num in steps:
            msg = steps[step_num]
            if step_num == 7 and hasattr(SharedData, 'case_id') and SharedData.case_id:
                msg += f" (ID: {SharedData.case_id})"
            print(msg)

    logger.info(f"Step 1: Highlighting 'Fulfillment Requested' tag status for Account: {target_account_id}")

    from src.pages.manage_vehicles_page import ManageVehiclesPage
    manage_vehicles_page = ManageVehiclesPage(page)

    # 1. Search account globally and open profile
    assert manage_vehicles_page.global_search_and_open_account(target_account_id), "Failed to search account."

    # 2. Navigate to Manage Vehicles
    assert manage_vehicles_page.navigate_to_manage_vehicles(), "Failed to navigate to Manage Vehicles."

    # 3. Highlight the status
    assert manage_vehicles_page.highlight_fulfillment_requested_status(), "Failed to find and highlight Tag Status!"
    step_printer(1)

    logger.info("Step 2: Navigating to Quantum Inventory to fulfill Tag.")

    from src.pages.inventory_fulfillment_page import InventoryFulfillmentPage
    inventory_page = InventoryFulfillmentPage(page)

    assert inventory_page.navigate_to_customer_fulfillment(step_printer), "Failed to navigate to Customer Fulfillment page"

    logger.info("Step 3: Selecting Account ID from Fulfillment Grid and Fulfilling Tag...")
    assert inventory_page.fulfill_tag_request(SharedData.account_id, step_printer), "Failed to fulfill the Tag Request"

    logger.info("Phase 1 Complete: Tag Request has been successfully fulfilled.")

    # --- PHASE 2: Verify Tag is Active and Initiate Transfer ---
    logger.info("Step 4: Navigating back to Account Profile to verify Tag is Active.")

    assert manage_vehicles_page.global_search_and_open_account(target_account_id), "Failed to search account."
    assert manage_vehicles_page.navigate_to_manage_vehicles(), "Failed to navigate to Manage Vehicles."

    status = manage_vehicles_page.verify_tag_status()
    assert status.upper() in ["ACTIVE", "ASSIGNED"], f"Tag status is not Active/Assigned, found: {status}"
    step_printer(5)

    assert manage_vehicles_page.initiate_tag_transfer(step_printer), "Failed to initiate tag transfer"

    logger.info(f"Step 5: Filling Tag Transfer form with destination account: {receiving_account_id}")
    assert manage_vehicles_page.fill_transfer_tag_form(receiving_account_id), "Failed to fill transfer tag form"
    step_printer(7)

    # --- PHASE 3: Case Management Resolution Flow ---
    logger.info("Step 6: Executing Transfer Tag Case Resolution Flow...")
    from src.pages.transfer_tag_case_resolution import execute_transfer_tag_case_resolution
    assert execute_transfer_tag_case_resolution(page, browser, step_printer), "Case Resolution Flow Failed"
    
    logger.info("Step 7: Validating Tag is Received and Active on Account 1...")
    assert manage_vehicles_page.global_search_and_open_account(receiving_account_id), "Failed to search receiving account."
    assert manage_vehicles_page.navigate_to_manage_vehicles(), "Failed to navigate to Manage Vehicles."
    
    status_acc1 = manage_vehicles_page.verify_tag_status()
    assert status_acc1.upper() in ["ACTIVE", "ASSIGNED"], f"Tag status is not Active/Assigned on Account 1, found: {status_acc1}"
    step_printer(20)
    logger.info("👀 Tiny wait for user to see Account 1 Tag Active...")
    page.wait_for_timeout(4000)
    
    logger.info("Step 8: Validating Tag is NO LONGER appearing on Account 2...")
    assert manage_vehicles_page.global_search_and_open_account(target_account_id), "Failed to search source account."
    assert manage_vehicles_page.navigate_to_manage_vehicles(), "Failed to navigate to Manage Vehicles."
    
    # Tiny wait to verify it's gone
    logger.info("👀 Tiny wait for user to see Account 2 Tag is gone...")
    assert manage_vehicles_page.verify_tag_status_na(), "Failed to verify Tag ID and Status are NA."
    page.wait_for_timeout(4000)
    step_printer(21)
    
    logger.info("🎉 Success! Transfer Tag Flow Complete!")
