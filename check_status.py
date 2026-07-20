import time
from playwright.sync_api import sync_playwright
from utils.config import LOGIN_CREDENTIALS

def dump():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        base_url = "http://operator-qa.qmaastech.com"
        page.goto(f"{base_url}/login")
        
        # Login as Superadmin
        sa_creds = LOGIN_CREDENTIALS["superadmin"]
        page.locator('input[formcontrolname="emailId"]').fill(sa_creds["email"])
        page.locator('input[formcontrolname="password"]').fill(sa_creds["password"])
        page.locator('button.auth-btn').click()
        page.locator(".dash-headding").first.wait_for(state="visible", timeout=20000)
        time.sleep(2)
        
        # Navigate to Search Case
        page.goto(f"{base_url}/operation-workbench/case-management/search-case")
        page.wait_for_timeout(3000)
        
        # Search for case 00815
        page.locator('button.ra-export-btn', has_text="Search Cases").first.click()
        page.locator('input#case[formcontrolname="case"]').fill("00815")
        page.locator('button', has_text="Search").first.click()
        page.wait_for_timeout(2000)
        
        # Print status cell text
        status = page.locator("tr").filter(has_text="00815").first.locator("td").nth(10).inner_text()
        print(f"CASE 00815 STATUS: {status}")
            
        browser.close()

if __name__ == '__main__':
    dump()
