"""
Test Case Management
End-to-end test for account creation and case management flow
"""

import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.account_page import AccountPage
from src.pages.case_page import CasePage
from src.pages.dashboard_page import DashboardPage
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture
def logged_in_page(page: Page, run_folder):
    """Fixture to provide logged-in page with all page objects"""
    login_page = LoginPage(page, report_dir=run_folder)
    login_page.navigate_to_login()
    login_page.perform_login("superadmin_qm@yopmail.com", "Superadmin@1234")
    login_page.verify_login_success()

    # Return page objects for the test
    return {
        "page": page,
        "account_page": AccountPage(page, report_dir=run_folder),
        "case_page": CasePage(page, report_dir=run_folder),
        "dashboard_page": DashboardPage(page, report_dir=run_folder)
    }


def test_end_to_end_case_management(logged_in_page):
    """
    End-to-end test for case management flow:
    1. Create new account
    2. Create case for the account
    3. Verify case details
    4. Check case in dashboard
    """
    page_objects = logged_in_page
    account_page = page_objects["account_page"]
    case_page = page_objects["case_page"]
    dashboard_page = page_objects["dashboard_page"]

    # Test data
    account_data = {
        "name": "Test Account E2E",
        "email": "test.account.e2e@yopmail.com",
        "phone": "+1234567890",
        "type": "PERSONAL"  # Updated to match actual dropdown value
    }

    case_data = {
        "type": "refund",
        "account": account_data["name"],
        "description": "E2E Test Case - Refund Request",
        "priority": "High"
    }

    logger.info("Starting End-to-End Case Management Test")

    # Step 1: Create new account
    logger.info("Step 1: Creating new account")
    account_result = account_page.create_account(account_data)
    assert account_result["success"], f"Account creation failed: {account_result.get('message', 'Unknown error')}"

    # Get the generated email for verification
    generated_email = account_result.get("email")
    assert generated_email, "Generated email not found in account creation result"

    # Verify account exists
    account_exists = account_page.verify_account_exists(generated_email)
    assert account_exists, f"Account {generated_email} not found after creation"

    # Step 2: Create case for the account
    logger.info("Step 2: Creating case for the account")
    case_created = case_page.create_case(case_data)
    assert case_created, "Case creation failed"

    # Verify case exists
    case_exists = case_page.verify_case_exists(case_data["description"])
    assert case_exists, f"Case '{case_data['description']}' not found after creation"

    # Step 3: Verify case details
    logger.info("Step 3: Verifying case details")
    case_details = case_page.get_case_details(case_data["description"])
    assert case_details["description"] == case_data["description"], "Case description mismatch"
    assert case_details["status"] == "Open", "Case status should be Open"

    # Step 4: Check case in dashboard
    logger.info("Step 4: Checking case in dashboard")
    dashboard_page.navigate_to_case_dashboard()

    case_in_dashboard = dashboard_page.verify_case_in_dashboard(case_data["description"])
    assert case_in_dashboard, f"Case '{case_data['description']}' not found in dashboard"

    logger.info("End-to-End Case Management Test completed successfully")


def test_auto_case_creation(logged_in_page):
    """
    Test auto case creation for different case types
    """
    page_objects = logged_in_page
    account_page = page_objects["account_page"]
    case_page = page_objects["case_page"]
    dashboard_page = page_objects["dashboard_page"]

    # Create a test account first
    account_data = {
        "name": "Auto Case Account",
        "email": "auto.case@yopmail.com",
        "phone": "+1987654321",
        "type": "PERSONAL"  # Updated to match actual dropdown value
    }

    account_result = account_page.create_account(account_data)
    assert account_result["success"], f"Account creation failed for auto case test: {account_result.get('message', 'Unknown error')}"

    # Get the generated account name for case creation
    generated_email = account_result.get("email")
    account_name = f"{account_result.get('first_name', 'Test')} {account_result.get('last_name', 'User')}"

    # Test different auto case types
    case_types = ["refund", "vehicle_transfer", "tag_transfer", "toll_adjustment"]

    for case_type in case_types:
        logger.info(f"Testing auto case creation for: {case_type}")

        # Create auto case
        case_created = case_page.create_auto_case(case_type, account_name)
        assert case_created, f"Auto case creation failed for {case_type}"

        # Verify case exists
        expected_description = f"Auto-generated {case_type.replace('_', ' ').title()} case"
        case_exists = case_page.verify_case_exists(expected_description)
        assert case_exists, f"Auto case '{expected_description}' not found"

        # Check in dashboard
        dashboard_page.navigate_to_case_dashboard()
        case_in_dashboard = dashboard_page.verify_case_in_dashboard(expected_description)
        assert case_in_dashboard, f"Auto case '{expected_description}' not in dashboard"

    logger.info("Auto case creation test completed successfully")
