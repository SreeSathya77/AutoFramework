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
        
        page.locator('div[role="tab"]', has_text="Activities").click()
        page.wait_for_timeout(2000)
        
        table = page.locator('table.sec-table')
        transfer_btn = table.locator('tr').filter(has_text="Transfer Tag - Transfer Tag").locator('button', has_text="Transfer Tag")
        transfer_btn.click()
        
        popup_modal = page.locator("div.popup-content")
        popup_modal.wait_for(state="visible", timeout=10000)
        
        modal_txt = popup_modal.locator("textarea")
        modal_txt.fill("Transfer Tag approved by Executive 6")
        
        submit_btn = popup_modal.locator('button.qm-btn-primary', has_text="Submit")
        submit_btn.click()
        popup_modal.wait_for(state="hidden", timeout=10000)
        
        print("Transfer Tag button clicked and submitted!")
        page.wait_for_timeout(3000)
        
        browser.close()

if __name__ == '__main__':
    dump()
