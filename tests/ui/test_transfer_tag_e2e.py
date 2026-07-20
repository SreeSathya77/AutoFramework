import pytest
from playwright.sync_api import sync_playwright
import os
import sys
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.pages.transfer_tag_case_resolution import execute_transfer_tag_case_resolution
from utils.config import LOGIN_CREDENTIALS, BASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_transfer_tag_e2e")

def test_transfer_tag_e2e():
    target_case = "00815" # Assuming this is our test case
    logger.info(f"Starting E2E test for case {target_case}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        
        shared_setup = {
            "browser": browser,
            "contexts": {}
        }
        
        try:
            result = execute_transfer_tag_case_resolution(
                browser=browser,
                base_url=BASE_URL,
                target_case=target_case,
                sa_creds=LOGIN_CREDENTIALS["superadmin"],
                exec_creds=LOGIN_CREDENTIALS["caseexecutive6"],
                mgr_creds=LOGIN_CREDENTIALS["boscasemanager2"],
                shared_setup=shared_setup
            )
            logger.info(f"Execution Result: {result}")
        finally:
            browser.close()

if __name__ == '__main__':
    test_transfer_tag_e2e()
