import os
import sys
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.config import LOGIN_CREDENTIALS

def check_approve_button(email, password, case_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        try:
            print(f"Logging in as {email}...")
            page.goto("http://operator-qa.qmaastech.com/login")
            page.locator('input[formcontrolname="emailId"]').fill(email)
            page.locator('input[formcontrolname="password"]').fill(password)
            page.locator('button.auth-btn').click()
            page.wait_for_url("**/dashboard", timeout=15000)
            
            print(f"Searching for Case {case_id}...")
            page.goto("http://operator-qa.qmaastech.com/operation-workbench/manage-case/search-case")
            page.wait_for_load_state("networkidle")
            page.locator('button.ra-export-btn:has-text("Search Cases")').click()
            page.locator('input[formcontrolname="case"]').fill(case_id)
            page.locator('button.qm-btn.qm-btn-primary:has-text("Search")').click()
            page.wait_for_timeout(2000)
            
            page.locator('span:has-text("visibility")').first.click()
            page.wait_for_url("**/view-case", timeout=15000)
            page.wait_for_timeout(2000)
            
            row = page.locator('table.sec-table tbody tr').filter(has_text="Research Case").first
            btn = row.locator('button:has-text("Approve"), a.ra-link:has-text("Approve")').first
            
            is_enabled = btn.is_enabled()
            print(f"Result for {email}: Approve button enabled? {is_enabled}")
            return is_enabled
        except Exception as e:
            print(f"Error for {email}: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    case_id = "00620"
    
    users_to_test = [
        ("casesorter01@yopmail.com", "Casesorter01@"),
        ("casexecutive8115@yopmail.com", "Casexecutive8115@"),
        ("ashwini@gmail.com", "Test@123"),
        ("boscasemanager2@yopmail.com", "Boscasemanager2@"),
        ("manish@gmail.com", "Test@123")
    ]
    
    for email, pwd in users_to_test:
        check_approve_button(email, pwd, case_id)
