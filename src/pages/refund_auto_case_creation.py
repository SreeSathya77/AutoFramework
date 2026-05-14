import time
from datetime import datetime
from playwright.sync_api import Page
from utils.shared_data import SharedData
from utils.logger import Logger

logger = Logger.get_logger()


def execute_full_refund_automation(page: Page):
    target_account = SharedData.account_id
    if not target_account:
        logger.error("❌ Shared Data Error: No account_id found in SharedData.")
        return False

    # --- PHASES 1-3: SEARCH & VIEW (Existing Logic) ---
    time.sleep(5)
    search_input = page.locator("input.search-input[placeholder='Search here...']")
    try:
        search_input.wait_for(state="visible", timeout=15000)
        search_input.fill(target_account)
        page.keyboard.press("Enter")

        suggestions = page.locator("div.search-suggestions")
        suggestions.wait_for(state="visible", timeout=15000)
        page.locator("a").filter(has_text="Account Management").click()
        page.wait_for_load_state("networkidle")

        result_row = page.locator("table.ra-table tbody tr").filter(has_text=target_account).last
        result_row.wait_for(state="visible", timeout=15000)
        view_button = result_row.locator("a.qm-btn-icon").filter(has_text="visibility")
        view_button.scroll_into_view_if_needed()
        view_button.evaluate("el => { el.focus(); el.style.outline = '3px solid #ffc107'; }")
        view_button.click()
    except Exception as e:
        logger.error(f"❌ Initial Setup Failure: {e}")
        return False

    # --- PHASE 4: NAVIGATE TO RECHARGE (With Micro-Wait) ---
    try:
        page.wait_for_url("**/account-summary", timeout=15000)

        # Click Payments Menu
        payments_nav = page.locator("div.top-sub-nav a.nav-link").filter(has_text="Payments")
        payments_nav.evaluate("el => el.style.backgroundColor = '#e8f0fe'")  # Light blue highlight
        payments_nav.click()

        # Micro-wait to see the dropdown open
        time.sleep(0.8)

        recharge_item = page.locator("ul.dropdown-menu a.dropdown-item").filter(has_text="Recharge")
        recharge_item.evaluate("el => el.style.borderLeft = '4px solid #007bff'")  # Highlight selection
        logger.info("🖱️ Selecting 'Recharge' from menu.")
        recharge_item.click()
        page.wait_for_load_state("networkidle")
    except Exception as e:
        logger.error(f"❌ Recharge Navigation Failure: {e}")
        return False

    # --- PHASE 5-7: PAYMENT & SUCCESS (Existing Logic) ---
    try:
        # (Select Card and Pay logic remains same)
        first_card = page.locator("div.mp-card-item").first
        first_card.locator("input[type='radio']").click(force=True)
        page.wait_for_selector(".mp-card-item--selected", timeout=5000)

        amount_input = page.locator(".mp-card-item--selected input.mp-amount-input")
        amount_input.type("5000", delay=100)
        amount_input.dispatch_event("blur")
        time.sleep(1)
        page.locator(".mp-card-item--selected button.mp-pay-btn").click(force=True)

        # Modal Confirm
        page.locator("div.mp-modal button").filter(has_text="Pay Now").click()

        # Scrape Success Data
        success_modal = page.locator("div.mp-modal--success")
        success_modal.wait_for(state="visible", timeout=15000)

        # (Data scraping logic remains same as per previous verified version)
        rows = success_modal.locator(".mp-preview-row")
        txn_data = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "account_id": target_account}
        for i in range(rows.count()):
            label = rows.nth(i).locator("span").inner_text().strip()
            value = rows.nth(i).locator("strong").inner_text().strip()
            key = label.lower().replace(" ", "_").replace("#", "no")
            txn_data[key] = value
        SharedData.last_transaction_details = txn_data

        success_modal.locator("button").filter(has_text="Close").click()
    except Exception as e:
        logger.error(f"❌ Payment/Success Logic Failure: {e}")
        return False

    # --- PHASE 8: NAVIGATE TO PAYMENT HISTORY (With Polished Micro-Wait) ---
    try:
        logger.info("🕒 Navigating to Payment History...")

        # 1. Highlight and Click Payments Menu
        payments_menu = page.locator("div.top-sub-nav a.nav-link").filter(has_text="Payments")
        payments_menu.evaluate("el => el.style.backgroundColor = '#e8f0fe'")
        payments_menu.click()

        # 2. Micro-wait so the user sees the dropdown
        time.sleep(1)

        # 3. Locate, Highlight, and Click Payment History
        history_item = page.locator("ul.dropdown-menu a.dropdown-item").filter(has_text="Payment History")
        history_item.wait_for(state="visible")

        # Programmatic focus and left-border highlight
        history_item.evaluate(
            "el => { el.focus(); el.style.borderLeft = '4px solid #007bff'; el.style.backgroundColor = '#f8f9fa'; }")

        logger.info("🖱️ Clicking 'Payment History' option.")
        time.sleep(0.5)  # Final pause before the click
        history_item.click()

        page.wait_for_load_state("networkidle")
        logger.info("✅ Phase 5 Complete: Payment History screen is open.")

        return True

    except Exception as e:
        logger.error(f"❌ Navigation to Payment History failed: {e}")
        return False