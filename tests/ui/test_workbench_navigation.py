import pytest
from utils.logger import Logger
from src.pages.workbench_page import WorkbenchPage

logger = Logger.get_logger()

def test_navigate_to_onboard_customer(authenticated_page, session_run_folder):
    """
    Tests navigation to the 'Onboard a Customer' page.
    Uses 'authenticated_page' to ensure login is handled first.
    """
    logger.info("Executing navigation test...")
    
    # Initialize WorkbenchPage
    workbench = WorkbenchPage(authenticated_page, report_dir=session_run_folder)
    
    # Perform navigation
    workbench.navigate_to_onboard_customer()
    
    # Final URL Assertion
    assert "onboard-a-customer" in authenticated_page.url, \
        f"Unexpected URL: {authenticated_page.url}"
    
    logger.info("Navigation test passed successfully.")
