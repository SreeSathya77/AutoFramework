"""
Test Case Dashboard
Tests for case dashboard statistics and functionality
"""

import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.account_page import AccountPage
from src.pages.case_page import CasePage
from src.pages.dashboard_page import DashboardPage
from utils.logger import Logger
logger = Logger.get_logger()


@pytest.fixture
def logged_in_page(page: Page, run_folder):
    """Fixture to provide logged-in page with all page objects"""
    login_page = LoginPage(page, report_dir=run_folder)
    login_page.navigate_to_login()
    login_page.perform_login("superadmin_qm@yopmail.com", "Superadmin@1234")
    login_page.verify_login_success()

    return {
        "page": page,
        "account_page": AccountPage(page, report_dir=run_folder),
        "case_page": CasePage(page, report_dir=run_folder),
        "dashboard_page": DashboardPage(page, report_dir=run_folder)
    }


def test_case_dashboard_stats(logged_in_page):
    """
    Test case dashboard statistics display and accuracy
    """
    page_objects = logged_in_page
    dashboard_page = page_objects["dashboard_page"]

    logger.info("Testing Case Dashboard Statistics")

    # Navigate to case dashboard
    dashboard_page.navigate_to_case_dashboard()

    # Get case statistics
    stats = dashboard_page.get_case_stats()
    assert stats, "Failed to retrieve case statistics"

    # Verify stats are numeric
    for key, value in stats.items():
        try:
            int(value)
            logger.info(f"{key}: {value}")
        except ValueError:
            pytest.fail(f"Non-numeric value for {key}: {value}")

    logger.info("Case dashboard stats test completed successfully")


def test_case_dashboard_filtering(logged_in_page):
    """
    Test case filtering functionality in dashboard
    """
    page_objects = logged_in_page
    dashboard_page = page_objects["dashboard_page"]

    logger.info("Testing Case Dashboard Filtering")

    # Navigate to case dashboard
    dashboard_page.navigate_to_case_dashboard()

    # Test filtering by different statuses
    statuses = ["Open", "Closed", "Pending"]

    for status in statuses:
        logger.info(f"Testing filter for status: {status}")
        count = dashboard_page.get_filtered_case_count(status)
        logger.info(f"Found {count} cases with status: {status}")
        # Note: We don't assert specific counts as they depend on test data

    logger.info("Case dashboard filtering test completed successfully")


def test_case_dashboard_stats_accuracy(logged_in_page):
    """
    Test that dashboard statistics match actual case counts
    """
    page_objects = logged_in_page
    dashboard_page = page_objects["dashboard_page"]

    logger.info("Testing Case Dashboard Stats Accuracy")

    # Navigate to case dashboard
    dashboard_page.navigate_to_case_dashboard()

    # Verify stats accuracy
    stats_accurate = dashboard_page.verify_dashboard_stats_accuracy()
    assert stats_accurate, "Dashboard statistics do not match actual case counts"

    logger.info("Case dashboard stats accuracy test completed successfully")


def test_case_search_in_dashboard(logged_in_page):
    """
    Test case search functionality in dashboard
    """
    page_objects = logged_in_page
    account_page = page_objects["account_page"]
    case_page = page_objects["case_page"]
    dashboard_page = page_objects["dashboard_page"]

    logger.info("Testing Case Search in Dashboard")

    # Create a test case first
    account_data = {
        "name": "Search Test Account",
        "email": "search.test@yopmail.com",
        "phone": "+1555123456",
        "type": "Individual"
    }

    case_data = {
        "type": "refund",
        "account": account_data["name"],
        "description": "Unique Search Test Case Description",
        "priority": "Medium"
    }

    # Create account and case
    account_result = account_page.create_account(account_data)
    assert account_result["success"], f"Account creation failed for search test: {account_result.get('message', 'Unknown error')}"

    # Get generated account name for case creation
    generated_email = account_result.get("email")
    account_name = f"{account_result.get('first_name', 'Search')} {account_result.get('last_name', 'Test')}"

    case_data["account"] = account_name  # Update case data with the generated account name

    case_created = case_page.create_case(case_data)
    assert case_created, "Case creation failed for search test"

    # Navigate to dashboard and search
    dashboard_page.navigate_to_case_dashboard()

    case_found = dashboard_page.verify_case_in_dashboard(case_data["description"])
    assert case_found, f"Case '{case_data['description']}' not found in dashboard search"

    logger.info("Case search in dashboard test completed successfully")
