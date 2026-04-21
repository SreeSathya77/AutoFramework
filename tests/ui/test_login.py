import pytest
from utils.logger import Logger

logger = Logger.get_logger()

def test_user_authentication(logged_in_page, login_page):
    """
    Requirement 1: User Authentication (Login/Logout).
    Page: http://operator-qa.qmaastech.com/
    Success Verification: Dashboard URL redirection and Screenshot.
    Pop-up Verification: Capture and validate login success pop-up notification.

    Note: Pop-up validation happens in perform_login() during rapid screenshots
    while the pop-up is still visible (0-100ms window).
    """
    logger.info("Executing test_user_authentication...")

    # The logged_in_page fixture already performed login, captured screenshots,
    # and validated the pop-up during the rapid screenshot window
    logger.info("Pop-up capture and validation completed in login fixture")

    # Verify success using the URL check and Screenshot
    is_success = login_page.verify_login_success()

    assert is_success, "Login authentication failed! Dashboard was not reached."

    logger.info("Test case test_user_authentication completed successfully.")
