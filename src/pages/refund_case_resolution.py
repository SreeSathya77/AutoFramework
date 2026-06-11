# src/pages/refund_case_resolution.py
import time
from playwright.sync_api import Page, Browser
from utils.shared_data import SharedData
from utils.logger import Logger
from utils.config import LOGIN_CREDENTIALS
from utils.session_manager import SessionManager
from src.pages.login_page import LoginPage

logger = Logger.get_logger()


def ensure_superadmin_session(page: Page, base_url: str):
    """
    Helper function to verify if Superadmin is still logged in.
    """
    login_page = LoginPage(page)
    SessionManager.ensure_active_session(page, login_page)
    # Final check to ensure we are back on a safe page
    if "/login" in page.url:
        page.goto(f"{base_url}/operation-workbench/dashboard")


def superadmin_check_case_status(page: Page, base_url: str, target_case: str, stage_description: str):
    """
    Helper to search the case grid and display status using the Superadmin context window.
    """
    logger.info(f"🔄 Superadmin Action: Verifying status update after [{stage_description}]...")
    ensure_superadmin_session(page, base_url)

    logger.info("📍 Routing Superadmin straight to Case Management workbench...")
    page.goto(f"{base_url}/operation-workbench/case-management/search-case")
    page.wait_for_load_state("load")
    page.wait_for_timeout(1000)

    if "/login" in page.url or page.locator('input[formcontrolname="emailId"]').is_visible(timeout=2000):
        logger.warning("⚠️ Security redirect caught post-navigation. Running emergency re-auth triage...")
        ensure_superadmin_session(page, base_url)
        page.goto(f"{base_url}/operation-workbench/case-management/search-case")
        page.wait_for_load_state("load")

    sa_search_toggle = page.locator('button.ra-export-btn', has_text="Search Cases").first
    sa_search_toggle.wait_for(state="visible", timeout=10000)
    sa_search_toggle.focus()
    sa_search_toggle.click()
    page.wait_for_timeout(800)

    sa_case_input = page.locator('input#case[formcontrolname="case"]').first
    sa_case_input.wait_for(state="visible", timeout=5000)
    sa_case_input.focus()
    sa_case_input.fill(str(target_case))
    page.wait_for_timeout(500)

    search_btn = page.locator('button').filter(has_text="Search").first
    search_btn.focus()
    search_btn.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)

    sa_suggestion = page.locator('div.search-suggestions a:has-text("Cases")')
    if sa_suggestion.is_visible(timeout=2000):
        sa_suggestion.focus()
        sa_suggestion.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

    sa_final_row = page.locator("tr").filter(has_text=str(target_case)).first
    sa_final_row.wait_for(state="visible", timeout=5000)
    sa_final_row.scroll_into_view_if_needed()
    page.wait_for_timeout(500)

    try:
        status_cell = sa_final_row.locator("td").nth(10)
        current_status = status_cell.inner_text().strip() if status_cell.is_visible() else "Unknown"
        logger.info(f"📊 Superadmin observed Case Status at stage [{stage_description}]: '{current_status}'")
    except Exception:
        pass

    view_icon = sa_final_row.locator('span:has-text("visibility")').first
    view_icon.focus()
    view_icon.click()
    page.wait_for_url("**/view-case", timeout=15000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)


def execute_refund_case_resolution(page: Page, browser: Browser):
    logger.info("================================================================================")
    logger.info("🚀 Starting Phase 2: Refund Case Multi-Context Resolution Flow...")
    logger.info("================================================================================")

    target_case = SharedData.case_id
    if not target_case:
        logger.error("❌ Shared Data Error: No active case_id found in SharedData cache.")
        return False

    base_url = page.url.split('/operation-workbench')[0]
    exec6_creds = LOGIN_CREDENTIALS.get("caseexecutive6", {})
    mgr2_creds = LOGIN_CREDENTIALS.get("boscasemanager2", {})

    # =====================================================================================
    # TASK 1: REASSIGN CASE TO EXEC6 & SUBMIT COMMENTS (CURRENT SUPERADMIN CONTEXT)
    # =====================================================================================
    try:
        logger.info(f"👤 Inspecting layout assignees for Case ID: #{target_case}...")
        owner_dropdown = page.locator('select#caseOwner')
        owner_dropdown.wait_for(state="visible", timeout=15000)
        owner_dropdown.scroll_into_view_if_needed()
        owner_dropdown.focus()

        current_owner = owner_dropdown.input_value()
        target_executive = exec6_creds.get("email")

        if current_owner.strip().lower() == target_executive.strip().lower():
            logger.info(f"ℹ️ Case is already assigned to {target_executive}. Skipping reassignment save step.")
        else:
            logger.info(f"📝 Reassigning Case Owner from '{current_owner}' to: '{target_executive}'")
            owner_dropdown.select_option(value=target_executive)
            page.wait_for_timeout(800)

            save_btn = page.locator('button.qm-btn.qm-btn-primary:has-text("Save")')
            save_btn.wait_for(state="visible", timeout=5000)
            save_btn.focus()
            save_btn.click()
            logger.info("🔘 Clicked Save assignment changes.")
            page.wait_for_timeout(1000)

            popup_modal = page.locator("div.popup-content")
            if popup_modal.is_visible(timeout=5000):
                logger.info("💬 Comments modal detected. Submitting initialization notes...")
                comment_txt = popup_modal.locator("textarea")
                comment_txt.focus()
                comment_txt.fill("Automation Testing comments.")
                page.wait_for_timeout(500)

                submit_btn = popup_modal.locator('button.qm-btn-primary:has-text("Submit")')
                submit_btn.focus()
                submit_btn.click()
                popup_modal.wait_for(state="hidden", timeout=10000)
                page.wait_for_timeout(800)

        page.wait_for_load_state("networkidle")
        logger.info(f"✅ Case owner successfully verified for {target_executive}.")
    except Exception as e:
        logger.error(f"❌ Failed during Executive 6 reassignment phase: {e}")
        return False

    # =====================================================================================
    # TASK 2: NEW BROWSER CONTEXT FOR EXECUTIVE APPROVAL
    # =====================================================================================
    logger.info(f"🌐 Spawning clean isolated Browser Context for Executive: {exec6_creds.get('email')}")
    exec_context = browser.new_context(viewport={"width": 1600, "height": 850}, ignore_https_errors=True)
    exec_context.add_init_script("() => { document.body.style.zoom = '75%'; }")
    exec_page = exec_context.new_page()

    try:
        logger.info(f"🔑 Logging into operation workbench as: {exec6_creds.get('email')}")
        exec_page.goto(f"{base_url}/login")

        ex_email = exec_page.locator('input[formcontrolname="emailId"]')
        ex_email.focus()
        ex_email.fill(exec6_creds.get("email"))

        ex_pass = exec_page.locator('input[formcontrolname="password"]')
        ex_pass.focus()
        ex_pass.fill(exec6_creds.get("password"))
        page.wait_for_timeout(400)

        exec_page.locator('button.auth-btn').click()
        exec_page.wait_for_url("**/dashboard", timeout=20000)
        page.wait_for_timeout(1000)

        logger.info(f"🔍 Executing Case Lookup query routing for: {target_case}")
        exec_page.goto(f"{base_url}/operation-workbench/case-management/search-case")
        exec_page.wait_for_load_state("networkidle")

        search_cases_toggle = exec_page.locator('button.ra-export-btn', has_text="Search Cases").first
        search_cases_toggle.wait_for(state="visible", timeout=10000)
        search_cases_toggle.focus()
        search_cases_toggle.click()
        page.wait_for_timeout(500)

        case_number_input = exec_page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=5000)
        case_number_input.focus()
        case_number_input.fill(str(target_case))

        exec_page.locator('button').filter(has_text="Search").first.click()
        exec_page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        cases_suggestion = exec_page.locator('div.search-suggestions a:has-text("Cases")')
        if cases_suggestion.is_visible(timeout=3000):
            cases_suggestion.click()

        target_row = exec_page.locator("tr").filter(has_text=str(target_case)).first
        target_row.scroll_into_view_if_needed()

        view_btn = target_row.locator('span:has-text("visibility")').first
        view_btn.focus()
        view_btn.click()
        exec_page.wait_for_url("**/view-case", timeout=15000)
        exec_page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        logger.info("⬇️ Interacting with sequential Activity Table at bottom of layout...")
        activity_table = exec_page.locator('table.sec-table')
        activity_table.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        first_activity_row = activity_table.locator('tbody tr').first
        approve_btn = first_activity_row.locator('button:has-text("Approve")')
        approve_btn.wait_for(state="visible", timeout=10000)
        approve_btn.focus()
        approve_btn.click()

        popup_modal = exec_page.locator("div.popup-content")
        popup_modal.wait_for(state="visible", timeout=10000)
        modal_txt = popup_modal.locator("textarea")
        modal_txt.focus()
        modal_txt.fill("Approved - automation testing")
        page.wait_for_timeout(500)

        popup_modal.locator('button.qm-btn-primary', has_text="Submit").click()
        popup_modal.wait_for(state="hidden", timeout=10000)
        logger.info("✅ First operational case activity approved by Executive 6.")
        page.wait_for_timeout(1500)

    except Exception as e:
        logger.error(f"❌ Workflow sequence broke inside Executive 6 context layer: {e}")
        return False
    finally:
        exec_page.close()
        exec_context.close()

    # =====================================================================================
    # INTERMITTENT CHECK 1: SUPERADMIN VERIFIES STATUS AFTER EXECUTIVE ACTION
    # =====================================================================================
    try:
        superadmin_check_case_status(page, base_url, target_case, "Executive Approved")
    except Exception as sa_ex:
        logger.warning(f"⚠️ Intermittent Run failed to execute: {sa_ex}")

    # =====================================================================================
    # TASK 3: NEW BROWSER CONTEXT FOR MANAGER 2 (POLLING ARCHITECTURE)
    # =====================================================================================
    target_manager = mgr2_creds.get("email")
    logger.info(f"👑 Spawning clean isolated Browser Context for Case Manager: {target_manager}")
    mgr_context = browser.new_context(viewport={"width": 1600, "height": 850}, ignore_https_errors=True)
    mgr_context.add_init_script("() => { document.body.style.zoom = '75%'; }")
    mgr_page = mgr_context.new_page()

    is_verified_successfully = False
    final_status = "unknown"

    try:
        # Send a quick poll check right before we change tabs
        SessionManager.active_heartbeat(page)

        logger.info(f"🔑 Logging into operation workbench as Manager: {target_manager}")
        mgr_page.goto(f"{base_url}/login")

        m_email = mgr_page.locator('input[formcontrolname="emailId"]')
        m_email.focus()
        m_email.fill(mgr2_creds.get("email"))

        m_pass = mgr_page.locator('input[formcontrolname="password"]')
        m_pass.focus()
        m_pass.fill(mgr2_creds.get("password"))
        page.wait_for_timeout(400)

        mgr_page.locator('button.auth-btn').click()
        mgr_page.wait_for_url("**/dashboard", timeout=20000)
        page.wait_for_timeout(1000)

        logger.info(f"🔍 Executing Manager lookup query routing loop for Case ID: {target_case}")
        mgr_page.goto(f"{base_url}/operation-workbench/case-management/search-case")
        mgr_page.wait_for_load_state("networkidle")

        mgr_search_toggle = mgr_page.locator('button.ra-export-btn', has_text="Search Cases").first
        mgr_search_toggle.wait_for(state="visible", timeout=10000)
        mgr_search_toggle.focus()
        mgr_search_toggle.click()
        page.wait_for_timeout(500)

        mgr_case_input = mgr_page.locator('input#case[formcontrolname="case"]').first
        mgr_case_input.wait_for(state="visible", timeout=5000)
        mgr_case_input.focus()
        mgr_case_input.fill(str(target_case))

        mgr_page.locator('button').filter(has_text="Search").first.click()
        mgr_page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # Synchronous pulse keeping the Superadmin window completely locked and fresh
        SessionManager.active_heartbeat(page)

        mgr_suggestion = mgr_page.locator('div.search-suggestions a:has-text("Cases")')
        if mgr_suggestion.is_visible(timeout=3000):
            mgr_suggestion.click()

        mgr_row = mgr_page.locator("tr").filter(has_text=str(target_case)).first
        mgr_row.scroll_into_view_if_needed()

        mgr_view = mgr_row.locator('span:has-text("visibility")').first
        mgr_view.focus()
        mgr_view.click()
        mgr_page.wait_for_url("**/view-case", timeout=15000)
        mgr_page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        owner_dropdown = mgr_page.locator('select#caseOwner')
        owner_dropdown.wait_for(state="visible", timeout=10000)
        owner_dropdown.scroll_into_view_if_needed()
        current_owner = owner_dropdown.input_value()

        if current_owner.strip().lower() != target_manager.strip().lower():
            logger.info(f"📝 Reassigning node responsibility field explicitly to Manager: '{target_manager}'")
            owner_dropdown.focus()
            owner_dropdown.select_option(value=target_manager)
            page.wait_for_timeout(800)

            mgr_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")').click()
            popup_modal = mgr_page.locator("div.popup-content")
            popup_modal.wait_for(state="visible", timeout=10000)

            mgr_txt = popup_modal.locator("textarea")
            mgr_txt.focus()
            mgr_txt.fill("Reassigning case owner ownership to manager context layer.")
            page.wait_for_timeout(500)

            popup_modal.locator('button.qm-btn-primary:has-text("Submit")').focus()
            popup_modal.locator('button.qm-btn-primary:has-text("Submit")').click()
            popup_modal.wait_for(state="hidden", timeout=10000)

            mgr_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)

        logger.info("⬇| Manager re-evaluating activity layout context tree grid maps...")
        approve_btn_mgr = None

        for attempt in range(1, 6):
            logger.info(f"   🔄 DOM Extraction Sync Attempt #{attempt}...")
            SessionManager.active_heartbeat(page)  # Synchronized polling pulse

            fresh_activity_table = mgr_page.locator('table.sec-table')
            fresh_activity_table.scroll_into_view_if_needed()

            named_row = fresh_activity_table.locator('tr').filter(has_text="Refund Approval - Refund Approval").first
            if named_row.is_visible():
                btn = named_row.locator('button:has-text("Approve")')
                if btn.is_visible():
                    approve_btn_mgr = btn
                    logger.info("   🎯 Target matched by string descriptor: 'Refund Approval - Refund Approval'")
                    break

            fallback_row = fresh_activity_table.locator('tbody tr:has(button:has-text("Approve"))').first
            if fallback_row.is_visible():
                btn = fallback_row.locator('button:has-text("Approve")')
                if btn.is_visible():
                    approve_btn_mgr = btn
                    logger.warning("   ⚠️ Falling back to target the first visible active operational row item.")
                    break

            page.wait_for_timeout(1000)

        if not approve_btn_mgr:
            raise RuntimeError(
                "❌ Layout Failure: Activity table did not render any visible action rows inside manager context.")

        approve_btn_mgr.scroll_into_view_if_needed()
        approve_btn_mgr.focus()
        page.wait_for_timeout(500)
        approve_btn_mgr.evaluate("node => node.click()")

        popup_modal = mgr_page.locator("div.popup-content")
        popup_modal.wait_for(state="visible", timeout=10000)

        mgr_final_comment = popup_modal.locator("textarea")
        mgr_final_comment.focus()
        mgr_final_comment.fill("Approved - automation testing")
        page.wait_for_timeout(500)

        popup_modal.locator('button.qm-btn-primary', has_text="Submit").click()
        popup_modal.wait_for(state="hidden", timeout=10000)
        logger.info("✅ 'Refund Approval - Refund Approval' activity processed by Case Manager successfully.")
        page.wait_for_timeout(1500)

        # =====================================================================================
        # INTERLEAVED POLLING DURING STATE SYNCHRONIZATION LOOKUPS
        # =====================================================================================
        logger.info("⏳ Launching streamlined state synchronization verification loops with interleaved polling...")
        expected_terminal_keywords = ["resolved", "closed", "approved", "completed"]

        for check_attempt in range(1, 6):
            try:
                # 🌟 INTERLEAVED POLL STEP: Reset the Superadmin session timer at the start of every loop iteration!
                SessionManager.active_heartbeat(page)

                logger.info(f"   🔎 Searching case grid to verify status update (Attempt #{check_attempt})...")
                mgr_page.goto(f"{base_url}/operation-workbench/case-management/search-case")
                mgr_page.wait_for_load_state("networkidle")

                final_search_toggle = mgr_page.locator('button.ra-export-btn', has_text="Search Cases").first
                if final_search_toggle.is_visible(timeout=3000):
                    final_search_toggle.click()

                final_case_input = mgr_page.locator('input#case[formcontrolname="case"]').first
                final_case_input.wait_for(state="visible", timeout=5000)
                final_case_input.fill(str(target_case))
                mgr_page.locator('button').filter(has_text="Search").first.click()
                mgr_page.wait_for_load_state("networkidle")

                final_suggestion = mgr_page.locator('div.search-suggestions a:has-text("Cases")')
                if final_suggestion.is_visible(timeout=2000):
                    final_suggestion.click()
                    mgr_page.wait_for_load_state("networkidle")

                final_row = mgr_page.locator("tr").filter(has_text=str(target_case)).first
                if final_row.is_visible(timeout=5000):
                    status_cell = final_row.locator("td").nth(10)
                    final_status = status_cell.inner_text().strip() if status_cell.is_visible() else ""

                    if not final_status or final_status.isdigit():
                        all_cells = final_row.locator("td").all_inner_texts()
                        final_status = next(
                            (cell.strip() for cell in all_cells if cell.strip().lower() in expected_terminal_keywords),
                            "Unknown")

                    logger.info(f"   🔹 Scraped Current Status Result: '{final_status}'")

                    if final_status.lower() in expected_terminal_keywords:
                        logger.info("   🎯 Terminal status verified successfully inside Manager session context!")
                        is_verified_successfully = True
                        break

            except Exception as loop_ex:
                logger.warning(f"   ⚠️ Search step warning during poll iteration #{check_attempt}: {loop_ex}")

            page.wait_for_timeout(3000)

    except Exception as e:
        logger.error(f"❌ Workflow sequence broke inside Case Manager context layer: {e}")
        is_verified_successfully = False
    finally:
        mgr_page.close()
        mgr_context.close()

    # =====================================================================================
    # FINAL AT-THE-END CHECK: CLEAN STATE REFRESH FOR SUPERADMIN
    # =====================================================================================
    if is_verified_successfully:
        try:
            logger.info("🔄 Manager finished. Refreshing Superadmin core state to prevent session conflict...")
            page.reload(wait_until="networkidle")
            
            # Use the refined session check
            ensure_superadmin_session(page, base_url)

            # Proceed to the final verification cleanly
            superadmin_check_case_status(page, base_url, target_case, "Manager Resolved (Final Check)")
            logger.info(f"🎉 Success! Milestone Met: Case #{target_case} opened successfully in Superadmin Context!")
        except Exception as sa_refresh_ex:
            logger.warning(f"❌ Final Status Verification Triage Failure: {sa_refresh_ex}")

    logger.info("================================================================================")
    logger.info(f"🏁 FINAL AUTOMATION VERIFICATION REPORT FOR CASE #{target_case}:")
    logger.info(f"   🔹 Terminal Status Read Result: '{final_status}'")
    logger.info("================================================================================")

    return is_verified_successfully