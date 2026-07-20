import time
from playwright.sync_api import sync_playwright
from utils.config import LOGIN_CREDENTIALS

def dump():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        base_url = "http://operator-qa.qmaastech.com"
        # Log in as superadmin
        page.goto(f"{base_url}/login")
        creds = LOGIN_CREDENTIALS["superadmin"]
        page.locator('input[formcontrolname="emailId"]').fill(creds["email"])
        page.locator('input[formcontrolname="password"]').fill(creds["password"])
        page.locator('button.auth-btn').click()
        page.locator(".dash-headding").first.wait_for(state="visible", timeout=20000)
        time.sleep(2)
        
        page.goto(f"{base_url}/operation-workbench/case-management/search-case")
        page.wait_for_timeout(3000)
        
        page.locator('button.ra-export-btn', has_text="Search Cases").first.click()
        page.locator('input#case[formcontrolname="case"]').fill("00815")
        page.locator('button', has_text="Search").first.click()
        page.wait_for_timeout(2000)
        
        page.locator("tr").filter(has_text="00815").first.locator('span:has-text("visibility")').first.click()
        page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
        page.wait_for_timeout(3000)
        
        owner_dropdown = page.locator('select#caseOwner')
        print(f"Current owner selected: {owner_dropdown.input_value()}")
        
        executive_email = LOGIN_CREDENTIALS["caseexecutive6"]["email"]
        owner_dropdown.select_option(value=executive_email)
        page.wait_for_timeout(1000)
        
        save_btn = page.locator('button.qm-btn.qm-btn-primary').filter(has_text="Save").first
        save_btn.click()
        
        modal_comment = page.locator("div.popup-content textarea, div.modal-content textarea, textarea[placeholder='Comments...']")
        modal_comment.first.wait_for(state="visible", timeout=10000)
        modal_comment.first.fill("Assigning to Case executive for the second time")
        
        submit_btn = page.locator("div.popup-content button", has_text="Submit").first
        submit_btn.click()
        page.wait_for_timeout(4000)
        print("Reassigned to caseexecutive6")
        
        browser.close()

if __name__ == '__main__':
    dump()
