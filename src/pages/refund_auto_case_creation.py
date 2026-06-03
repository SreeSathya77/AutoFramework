import time
from datetime import datetime
from playwright.sync_api import Page
from utils.shared_data import SharedData
from utils.logger import Logger

logger = Logger.get_logger()


def execute_full_refund_automation(page: Page):
    logger.info("================================================================================")
    logger.info("Starting Refund Automation Flow...")
    logger.info("================================================================================")

    target_account = SharedData.account_id
    if not target_account:
        logger.error("❌ Shared Data Error: No account_id found in SharedData.")
        return False

    # =====================================================================================
    # PHASE 1-3: GLOBAL HEADER SEARCH AND ACCOUNT MANAGEMENT NAVIGATION
    # =====================================================================================
    try:
        logger.info(f"🔍 Initiating Global Search sequence for Account ID: {target_account}...")

        search_bar = page.locator('input.search-input[placeholder="Search here..."]').first
        search_bar.wait_for(state="visible", timeout=15000)
        search_bar.click()

        search_bar.press("Control+A")
        search_bar.press("Backspace")
        search_bar.fill(str(target_account))
        search_bar.press("Enter")
        logger.info(f"⌨️ Account ID '{target_account}' typed and Enter executed.")
        page.wait_for_timeout(2000)

        account_management_tab = page.locator('span:has-text("Account Management")').first
        account_management_tab.wait_for(state="visible", timeout=15000)
        account_management_tab.click()
        logger.info("📁 'Account Management' selection category tab clicked inside global drop-down list.")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        logger.info("📊 Processing results grid matching criteria inside .ra-table...")
        results_table = page.locator('table.ra-table[aria-label="Data table"]').first
        results_table.wait_for(state="visible", timeout=15000)

        target_row = results_table.locator("tbody tr").filter(has_text=str(target_account)).first
        target_row.wait_for(state="visible", timeout=10000)

        eye_icon = target_row.locator('span.material-symbols-outlined:has-text("visibility")').first
        eye_icon.wait_for(state="visible", timeout=10000)

        eye_icon.evaluate("node => node.click()")
        logger.info(f"👁️ Eye symbol (visibility) icon clicked successfully for account: {target_account}.")

        logger.info("⏳ Validating Account Summary dashboard visibility state components...")
        balance_card = page.locator('div.ra-balance-card, div.ra-card').filter(has_text="Balance Information").first
        balance_card.wait_for(state="visible", timeout=20000)

        logger.info("✅ Landed successfully on Account Summary verification dashboard page layout.")
    except Exception as e:
        logger.error(f"❌ Standard UI Search Path failed to execute: {e}")
        return False

    # =====================================================================================
    # PHASE 4: RECHARGE NAVIGATION VIA BALANCE CARD FOOTER BUTTON
    # =====================================================================================
    try:
        logger.info("🕒 Navigating to Recharge screen via Balance Information Card Button...")

        card_recharge_btn = page.locator('.ra-balance-card button, .ra-card button').filter(has_text="Recharge").first
        card_recharge_btn.wait_for(state="visible", timeout=15000)

        card_recharge_btn.evaluate("""node => {
            node.scrollIntoViewIfNeeded();
            node.focus();
            node.style.outline = "4px solid rgba(0, 191, 255, 0.8)";
            node.style.outlineOffset = "2px";
            node.style.transition = "all 0.2s ease";
            node.click();
        }""")

        logger.info("🎯 Focused and clicked direct Recharge button on Balance card successfully.")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        logger.info("✅ Successfully navigated to Recharge screen.")
    except Exception as e:
        logger.error(f"❌ Recharge Navigation Failure: {e}")
        return False

    # =====================================================================================
    # PHASE 5 & 6: INITIAL CARD PAYMENT METHOD SELECTION
    # =====================================================================================
    try:
        logger.info("💳 Initiating Payment Process...")

        card_radio = page.locator('input[type="radio"][name="paymentSelection"]')
        logger.info("⏳ Waiting for saved card option selection entry...")
        card_radio.wait_for(state="visible", timeout=10000)

        logger.info("Selecting the first available saved card container...")
        card_radio.first.click(force=True)

        amount_input = page.locator('input.mp-amount-input')
        logger.info("⏳ Synchronizing actionability state: Waiting for Amount input to enable...")
        page.wait_for_function("el => !el.hasAttribute('disabled')", arg=amount_input.element_handle(), timeout=10000)

        logger.info("Typing processing recharge currency denomination value...")
        amount_input.fill("10.00")
        amount_input.dispatch_event("input")
        amount_input.dispatch_event("change")

        pay_button = page.locator('button.mp-pay-btn')
        logger.info("⏳ Synchronizing actionability state: Waiting for Pay button to enable...")
        page.wait_for_function("el => !el.hasAttribute('disabled')", arg=pay_button.element_handle(), timeout=10000)

        logger.info("🚀 Triggering payment transaction authorization submit action...")
        pay_button.click()
    except Exception as e:
        logger.error(f"❌ Initial Payment Submission Failure: {e}")
        return False

    # =====================================================================================
    # PHASE 6.5: CHECKOUT CONFIRMATION MODAL OVERLAY ("PAY NOW")
    # =====================================================================================
    try:
        logger.info("⏳ Intercepting 'Confirm Payment' checkout modal layout...")
        confirm_modal = page.locator("div.mp-modal").filter(has_text="Confirm Payment").first
        confirm_modal.wait_for(state="visible", timeout=15000)

        pay_now_btn = confirm_modal.locator("button.qm-btn-primary").filter(has_text="Pay Now").first
        pay_now_btn.wait_for(state="visible", timeout=5000)

        logger.info("🎯 Clicking 'Pay Now' button to finalize transaction...")
        pay_now_btn.click()

        confirm_modal.wait_for(state="hidden", timeout=15000)
        logger.info("✅ Confirmation checkout challenge completed.")
    except Exception as e:
        logger.error(f"❌ Confirm Payment Checkout Modal Step Failed: {e}")
        return False

    # =====================================================================================
    # PHASE 6.7: PAYMENT SUCCESS MODAL DISMISSAL & DATA EXTRACTION
    # =====================================================================================
    try:
        logger.info("⏳ Waiting for backend payment gateway authorization and processing success modal...")
        success_modal = page.locator("div.mp-modal--success").filter(
            has_text="Account balance updated successfully.").first
        success_modal.wait_for(state="visible", timeout=20000)

        # 📊 --- METADATA EXTRACTION ENGINE ---
        logger.info("📋 Extracting transaction data tokens from payment receipt summary view...")
        preview_rows = success_modal.locator("div.mp-preview-row")
        row_count = preview_rows.count()

        captured_metadata = {}
        for i in range(row_count):
            row = preview_rows.nth(i)
            label = row.locator("span").text_content().strip().replace(":", "")
            value = row.locator("strong").text_content().strip()
            captured_metadata[label] = value

        logger.info("==========================================================")
        logger.info("💰 SUCCESSFUL RECEIPT METADATA DETAILS RECORDED:")
        for key, val in captured_metadata.items():
            logger.info(f"   🔹 {key} : {val}")
        logger.info("==========================================================")

        if "Account ID" in captured_metadata:
            SharedData.account_id = captured_metadata["Account ID"]
        if "Transaction ID" in captured_metadata:
            SharedData.last_transaction_id = captured_metadata["Transaction ID"]
        if "Status" in captured_metadata:
            SharedData.last_payment_status = captured_metadata["Status"]
        if "Reference #" in captured_metadata:
            SharedData.last_reference_number = captured_metadata["Reference #"]

        close_btn = success_modal.locator("button.qm-btn-secondary").filter(has_text="Close").first
        close_btn.wait_for(state="visible", timeout=5000)

        logger.info("🎯 Clicking 'Close' button to dismiss the payment success modal window...")
        close_btn.click()

        success_modal.wait_for(state="hidden", timeout=15000)
        page.wait_for_load_state("networkidle")
        logger.info("✅ Payment success confirmation notification successfully processed.")
    except Exception as e:
        logger.error(f"❌ Payment Success Modal Resolution & Extraction Step Failed: {e}")
        return False

    # =====================================================================================
    # PHASE 6.9: NAVIGATE TO PAYMENTS > PAYMENT HISTORY
    # =====================================================================================
    try:
        logger.info("🧭 Expanding Payments dropdown navigation header...")
        payments_dropdown = page.locator('a.nav-link.dropdown-toggle', has_text="Payments").first
        payments_dropdown.wait_for(state="visible", timeout=15000)
        payments_dropdown.click()
        logger.info("📁 'Payments' navigation header dropdown toggled open.")

        history_link = page.locator('a.dropdown-item[href*="payment-history"]').first
        history_link.wait_for(state="visible", timeout=10000)
        logger.info("🎯 Clicking 'Payment History' routing option link...")
        history_link.click()

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        logger.info("✅ Arrived successfully inside Payment History ledger views data grid layout.")
    except Exception as e:
        logger.error(f"❌ Navigation to Payment History Link Failed: {e}")
        return False

    # =====================================================================================
    # PHASE 6.95: PAYMENT HISTORY LEDGER MATCHING & REVERSAL TRIGGER
    # =====================================================================================
    try:
        logger.info("📊 Fetching Payment History records table context...")
        history_table = page.locator('table.ra-table[aria-label="Data table"]').first
        history_table.wait_for(state="visible", timeout=15000)

        first_row = history_table.locator("tbody tr").first
        first_row.wait_for(state="visible", timeout=10000)

        logger.info("🔍 Performing integrity verification on the target record columns...")
        row_payment_type = first_row.locator('td').nth(1).text_content().strip()
        logger.info(f"   📋 Row Payment Type Detected: '{row_payment_type}'")

        if "RECHARGE_RECEIPT" not in row_payment_type:
            logger.error("❌ Validation Failed: First row is not a 'RECHARGE_RECEIPT'. Aborting flow.")
            return False

        logger.info("✅ Record entry verified successfully. Isolating Action links...")
        reverse_action_btn = first_row.locator('a.ra-link', has_text="Reverse").first
        reverse_action_btn.wait_for(state="visible", timeout=5000)

        logger.info("🎯 Clicking 'Reverse' option on verified target history record...")
        reverse_action_btn.click()
        page.wait_for_timeout(1000)
    except Exception as e:
        logger.error(f"❌ Verification or Click action within Payment History record table failed: {e}")
        return False

    # =====================================================================================
    # PHASE 7: MODAL REVERSAL FLOW PROCESS
    # =====================================================================================
    try:
        logger.info("🔄 Processing Reversal Context Form details...")

        details_modal = page.locator("div.ra-modal, div.modal-content, div.mp-modal, .modal-dialog").filter(
            has_text="Reversal Details").first

        logger.info("⏳ Waiting for Reversal Details configuration layout frame...")
        details_modal.wait_for(state="visible", timeout=20000)

        reversal_reason_dropdown = details_modal.locator(
            "select#reversalReason, select[formcontrolname*='Reason'], select.form-select").first
        reversal_reason_dropdown.wait_for(state="visible", timeout=5000)
        reversal_reason_dropdown.select_option(label="Refund")
        reversal_reason_dropdown.dispatch_event("change")
        logger.info("Selected Reversal Reason: Refund")

        channel_dropdown = details_modal.locator(
            "select#refundChannel, select[formcontrolname*='Channel'], select.form-select").last
        channel_dropdown.wait_for(state="visible", timeout=5000)
        channel_dropdown.select_option(value="Original Payment Method")
        channel_dropdown.dispatch_event("change")
        logger.info("Selected Refund Channel: Original Payment Method")

        submit_btn = details_modal.locator(
            "button.ra-btn--primary, button:has-text('Submit'), button.btn-primary").filter(
            has_text="Submit").first
        submit_btn.click()

        details_modal.wait_for(state="hidden", timeout=10000)
        logger.info("✅ Reversal Details form processed and sent.")

        # =====================================================================================
        # PHASE 8: FINAL CONFIRMATION OVERLAY
        # =====================================================================================
        logger.info("⚠️ Confirmation Alert wrapper check. Confirming choice...")

        alert_modal = page.locator("div.ra-modal--alert, div.ra-modal, div.modal-content, .swal2-container").filter(
            has_text="Are you sure").first
        alert_modal.wait_for(state="visible", timeout=10000)

        ok_btn = alert_modal.locator(
            "button.ra-btn--primary, button:has-text('OK'), button:has-text('Confirm')").filter(has_text="OK")
        ok_btn.click()

        alert_modal.wait_for(state="hidden", timeout=15000)
        logger.info("✅ Reversal Flow fully completed and confirmed.")
    except Exception as e:
        logger.error(f"❌ Reversal Step Failed: {e}")
        return False

    # =====================================================================================
    # PHASE 9: INTERCEPT 'CASE CREATED' MODAL POP-UP & EXTRACTION
    # =====================================================================================
    try:
        logger.info("⏳ Intercepting 'Case Created' success notification modal layer...")
        case_modal = page.locator("div.ra-modal--alert").filter(has_text="Case Created").first
        case_modal.wait_for(state="visible", timeout=20000)

        case_id_link = case_modal.locator("p.ra-modal__text a.ra-link").first
        case_id_link.wait_for(state="visible", timeout=5000)

        raw_case_text = case_id_link.text_content().strip()
        clean_case_id = raw_case_text.replace("#", "")

        logger.info("==========================================================")
        logger.info(f"🚀 REFUND INITIALIZATION CASE IDENTIFIED: {clean_case_id}")
        logger.info("==========================================================")

        SharedData.case_id = clean_case_id

        logger.info(f"🎯 Clicking Case ID link context (#{clean_case_id}) to drill down to details...")
        case_id_link.click()

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        logger.info("✅ Click processed successfully. Redirected into specialized Case Profile view.")
    except Exception as e:
        logger.error(f"❌ Failed to extract Case ID token or click popup hyperlink reference item: {e}")
        return False

    # =====================================================================================
    # REAL-WORLD REBUILT PHASE 10: CASE NAVIGATION & ROUTED SEARCH (STEPS 1 & 2)
    # =====================================================================================
    try:
        target_case = SharedData.case_id
        if not target_case:
            logger.error("❌ Shared Data Error: No case_id found in SharedData cache storage.")
            return False

        base_url = page.url.split('/operation-workbench')[0]
        logger.info(f"🧭 Directing browser to Search Case routing matrix terminal page...")

        # Explicit navigation match extracted from case_page.py standard context
        page.goto(f"{base_url}/operation-workbench/case-management/search-case")
        page.wait_for_load_state("networkidle")

        # Click the "Search Cases" expansion option container button
        search_cases_toggle = page.locator('button.ra-export-btn', has_text="Search Cases").first
        search_cases_toggle.wait_for(state="visible", timeout=10000)
        search_cases_toggle.click()
        logger.info("🔘 'Search Cases' drawer filter module expanded.")
        page.wait_for_timeout(1000)

        # Locate input context target matching: id="case"
        case_number_input = page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=10000)
        case_number_input.click()
        case_number_input.press("Control+A")
        case_number_input.press("Backspace")

        # Populate input with runtime Case ID digits text trace
        logger.info(f"⌨️ Entering target Case Reference ID: {target_case} inside field...")
        case_number_input.fill(str(target_case))

        # Click search execution action button
        logger.info("🚀 Submitting query parameter index lookup...")
        search_submit_btn = page.locator('button').filter(has_text="Search").first
        search_submit_btn.click()

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # Core Suggestions list drop-down hook sequence from codebase lines
        cases_suggestion = page.locator('div.search-suggestions a:has-text("Cases")')
        if cases_suggestion.is_visible(timeout=3000):
            logger.info("📁 Opening Case suggestion router category reference block link...")
            cases_suggestion.click()
            page.wait_for_timeout(1000)

        # Locate matching records result row within the table body layout elements
        logger.info("📊 Isolating matching row element cell context values...")
        target_row = page.locator("tr").filter(has_text=str(target_case)).first
        target_row.wait_for(state="visible", timeout=10000)

        # Click row viewing eye icon link
        eye_icon = target_row.locator('span:has-text("visibility")').first
        eye_icon.wait_for(state="visible", timeout=10000)
        logger.info("🎯 Clicking eye 'visibility' action button cell context...")
        # ... (This is the end of your Phase 10 script where it clicks the eye icon) ...
        eye_icon.click()

        page.wait_for_url("**/view-case", timeout=15000)
        page.wait_for_load_state("networkidle")
        logger.info(f"✅ Successfully completed search navigation lookup. Opened view for Case: #{target_case}.")

    except Exception as e:
        logger.error(f"❌ Failed to run complete Search Case form query routing loop step: {e}")
        return False

        # =====================================================================================
        # PHASE 11: DATA EXTRACTION ENGINE (LOGS, SHARED_DATA, AND CONSOLE)
        # =====================================================================================
    try:
        logger.info("📊 Initiating Case Profile Data Extraction Engine...")

        extracted_case_data = {}

        # --- 1. EXTRACT "CASE DETAILS" CARD ---
        logger.info("🔍 Scraped Context Group: Case Details...")
        case_details_container = page.locator("div.case-details div.border").first
        case_details_container.wait_for(state="visible", timeout=10000)

        p_elements = case_details_container.locator("p").all()
        for p in p_elements:
            span_count = p.locator("span").count()
            if span_count > 0:
                label = p.locator("span").inner_text().strip()
                full_text = p.inner_text().strip()
                value = full_text.replace(label, "").strip()
                if label:
                    extracted_case_data[label] = value

        # --- 2. EXTRACT DROPDOWN SELECTIONS (STATUS, PRIORITY, OWNER) ---
        logger.info("🔍 Scraped Context Group: Form Formulations/Dropdown values...")
        dropdowns = {
            "Case Status": page.locator("select#caseStatus"),
            "Case Priority": page.locator("select#casePriority"),
            "Case Owner": page.locator("select#caseOwner")
        }
        for field_name, select_locator in dropdowns.items():
            if select_locator.count() > 0:
                dropdown_val = select_locator.input_value()
                extracted_case_data[field_name] = dropdown_val if dropdown_val else "Not Selected"

        # --- 3. EXTRACT "CASE SPECIFIC DETAILS" MATRIX ---
        logger.info("🔍 Scraped Context Group: Case Specific Details...")
        specific_details_divs = page.locator("div.casespecificDetails > div").all()
        for box in specific_details_divs:
            if box.locator("strong").count() > 0:
                label = box.locator("strong").inner_text().strip()
                full_text = box.inner_text().strip()
                value = full_text.replace(label, "").strip()
                if label:
                    extracted_case_data[label] = value

        # --- 4. EXTRACT "CUSTOMER DETAILS" FOOTER CARD ---
        logger.info("🔍 Scraped Context Group: Customer Details...")
        customer_row = page.locator("div.case-details div.row").last
        customer_p_elements = customer_row.locator("p").all()
        for p in customer_p_elements:
            if p.locator("span").count() > 0:
                label = p.locator("span").inner_text().strip().replace(":", "")
                full_text = p.inner_text().strip()
                value = full_text.replace(p.locator("span").inner_text(), "").strip()
                if label:
                    extracted_case_data[label] = value

        # =====================================================================================
        # ROUTING CRADLE: LOGGING AND SAVING MECHANISMS
        # =====================================================================================

        # 1. Output directly to the runtime Console terminal panel via python print
        print("\n🚀 [CONSOLE OUTPUT] --- CAPTURED REFUND CASE DETAIL PROFILE METRICS ---")
        for key, val in extracted_case_data.items():
            print(f"   👉 {key} : {val}")
        print("-----------------------------------------------------------------------\n")

        # 2. Write details down into your infrastructure Logger configuration files
        logger.info("================================================================================")
        logger.info("💾 WRITING EXTRACTION ENGINE BLOCK TO FILE LOGS:")
        for key, val in extracted_case_data.items():
            logger.info(f"   🔹 {key:<35} :: {val}")
        logger.info("================================================================================")

        # 3. Cache inside your global SharedData runtime context memory layer
        SharedData.latest_case_profile_snapshot = extracted_case_data

        SharedData.last_payment_reference_id = extracted_case_data.get("Payment Reference Id", "")
        SharedData.extracted_payment_amount = extracted_case_data.get("Payment Amount", "")
        SharedData.extracted_gateway_transaction_id = extracted_case_data.get("Payment Gate Way Transaction Id", "")
        SharedData.case_current_owner = extracted_case_data.get("Case Owner", "")
        SharedData.case_current_status = extracted_case_data.get("Case Status", "")

        logger.info("✅ Metrics extracted, formatted, logged, and cached into SharedData seamlessly.")
        return True

    except Exception as e:
        logger.error(f"❌ Critical Error running dynamic page metrics capture engine: {e}")
        return False