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
        
        # Login as Executive 6
        creds = LOGIN_CREDENTIALS["caseexecutive6"]
        page.locator('input[formcontrolname="emailId"]').fill(creds["email"])
        page.locator('input[formcontrolname="password"]').fill(creds["password"])
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
        
        page.locator("tr").filter(has_text="00815").first.locator('span:has-text("visibility")').first.click()
        page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
        page.wait_for_timeout(3000)
        
        print("Clicking Transfer Tag button...")
        page.locator('div[role="tab"]', has_text="Activities").click()
        page.wait_for_timeout(2000)
        
        activity_table = page.locator('table.sec-table')
        activity_table.scroll_into_view_if_needed()
        row = activity_table.locator('tr').filter(has_text="Transfer Tag - Transfer Tag")
        btn = row.locator('button:has-text("Transfer Tag")')
        if btn.is_visible():
            btn.click()
            page.wait_for_timeout(2000)
            print("Modal visible:", page.locator("div.popup-content").is_visible())
            page.locator("div.popup-content textarea").fill("Done")
            page.locator('div.popup-content button:has-text("Submit")').click()
            page.wait_for_timeout(3000)
            print("Clicked submit on modal!")
        else:
            print("Transfer Tag button not visible!")

        browser.close()

if __name__ == '__main__':
    dump()
