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
        
        creds = LOGIN_CREDENTIALS["caseexecutive6"]
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
        
        print("Clicking Activities Tab...")
        page.locator('div[role="tab"]', has_text="Activities").click()
        page.wait_for_timeout(2000)
        
        activity_table = page.locator('table.sec-table')
        activity_table.scroll_into_view_if_needed()
        row = activity_table.locator('tr').filter(has_text="Research Case - Research Case")
        btn = row.locator('button:has-text("Approve")')
        if btn.is_visible():
            print("Clicking Approve for Research Case...")
            btn.click()
            page.wait_for_timeout(2000)
            
            modal = page.locator("div.popup-content")
            if modal.is_visible():
                print("Modal is visible! Filling textarea...")
                modal.locator("textarea").fill("Done Research Case")
                modal.locator('button', has_text="Submit").click()
                page.wait_for_timeout(3000)
                print("Submitted!")
            else:
                print("Modal NOT visible!")
        else:
            print("Approve button not visible!")
            
        # Check current owner options again (as executive, to see if they changed, though SA would see them)
        print("DROPDOWN OPTIONS FOR EXEC:")
        opts = page.locator('select#caseOwner option').all()
        for opt in opts:
            print(f"Option Value: {opt.get_attribute('value')}, Text: {opt.inner_text().strip()}")

        browser.close()

if __name__ == '__main__':
    dump()
