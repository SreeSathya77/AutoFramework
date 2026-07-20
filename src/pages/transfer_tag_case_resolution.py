# src/pages/transfer_tag_case_resolution.py
import time
import re
from playwright.sync_api import Page, Browser
from src.pages.base_page import BasePage
from utils.shared_data import SharedData
from utils.logger import Logger
from utils.config import LOGIN_CREDENTIALS
from conftest import VIEWPORT_SIZE
from src.pages.refund_case_resolution import (
    superadmin_check_case_status, 
    ensure_superadmin_session, 
    navigate_to_dashboard_via_ui,
    navigate_to_search_case_via_ui
)

logger = Logger.get_logger()

def execute_transfer_tag_case_resolution(page: Page, browser: Browser, step_printer=None, shared_setup=None):
    logger.info("================================================================================")
    logger.info("🚀 Starting Phase 2: Transfer Tag Case Multi-Context Resolution Flow...")
    logger.info("================================================================================")
    
    base = BasePage(page)
    target_case = SharedData.case_id
    if not target_case:
        logger.error("❌ Shared Data Error: No active case_id found in SharedData cache.")
        return False

    base_url = page.url.split('/operation-workbench')[0]
    exec6_creds = LOGIN_CREDENTIALS.get("caseexecutive6", {"email": "caseexecutive6@yopmail.com", "password": "Caseexecutive6@"})
    mgr_creds = LOGIN_CREDENTIALS.get("boscasemanager2", {"email": "boscasemanager2@yopmail.com", "password": "Boscasemanager2@"})
    
    # 1. SUPERADMIN (ALREADY ON CASE PROFILE PAGE) ASSIGNS TO EXECUTIVE 6
    logger.info("👑 SA on Case Details: Assigning case to Executive 6...")
    try:
        executive_email = exec6_creds.get('email', 'caseexecutive6@yopmail.com')
        owner_dropdown = page.locator("select#caseOwner")
        owner_dropdown.wait_for(state="visible", timeout=10000)
        owner_dropdown.scroll_into_view_if_needed()
        current_owner = owner_dropdown.input_value()
        
        if current_owner.strip().lower() != executive_email.strip().lower():
            logger.info(f"📝 Superadmin changing owner from '{current_owner}' to '{executive_email}'...")
            
            options = owner_dropdown.locator("option").all()
            available = False
            for opt in options:
                val = opt.get_attribute("value")
                if executive_email.lower() in opt.inner_text().lower() or (val and executive_email.lower() == val.lower()):
                    available = True
                    break
            
            if available:
                owner_dropdown.select_option(value=executive_email)
                page.wait_for_timeout(500)
                
                # Click Save or Assign
                assign_btn = page.locator('button.qm-btn.qm-btn-primary', has_text="Assign")
                if not assign_btn.is_visible():
                    assign_btn = page.locator('button.qm-btn.qm-btn-primary', has_text="Save")
                
                if assign_btn.is_visible():
                    base.scroll_focus_click(assign_btn)
                    
                    # Handle the Add Comments modal
                    modal_comment = page.locator("div.popup-content textarea, div.modal-content textarea, textarea[placeholder='Comments...']")
                    modal_comment.first.wait_for(state="visible", timeout=10000)
                    base.scroll_focus_fill(modal_comment.first, "Assigning this Case to Case executive to check tag transfer")
                    
                    submit_btn = page.locator("div.popup-content button, div.modal-content button, button.btn-primary, button.qm-btn").filter(has_text="Submit").first
                    base.scroll_focus_click(submit_btn)
                    
                    # Wait for the modal to completely disappear
                    modal_comment.first.wait_for(state="hidden", timeout=15000)
                    logger.info("✅ Superadmin successfully reassigned case to Executive 6.")
                else:
                    logger.warning("⚠️ Could not find 'Assign' or 'Save' button. Assuming auto-saved.")
            else:
                logger.info(f"ℹ️ '{executive_email}' not in dropdown. Leaving owner as '{current_owner}'.")

            logger.info('👀 Tiny wait for user to see the SA Assignment to Exec')
            page.wait_for_timeout(3000)
        else:
            logger.info("✅ Case is already assigned to target Executive 6.")
        
        # Wait for potential spinners
        try:
            page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=15000)
        except Exception:
            pass
            
        page.wait_for_timeout(2000)
        
        # SA searches case and sees owner again (Step 8 logic but for assignment)
        superadmin_check_case_status(page, base_url, target_case, "Transfer Tag Case Assigned to Exec", already_on_search_case=False, step_printer=step_printer, search_step=8, assign_step=9)
        
    except Exception as ex:
        logger.warning(f"⚠️ SA assign to Exec 6 failed: {ex}")
        return False

    # 2. EXECUTIVE CONTEXT APPROVES ACTIVITY 1
    exec_cache = shared_setup.setdefault("contexts", {}) if shared_setup else {}
    exec_email = exec6_creds.get("email")
    if exec_email in exec_cache:
        logger.info(f"♻️ Reusing existing browser context for Executive: {exec_email}")
        exec_context, exec_page, exec_base = exec_cache[exec_email]
        is_exec_new = False
    else:
        logger.info(f"🌐 Spawning clean isolated Browser Context for Executive: {exec_email}")
        exec_context = browser.new_context(viewport=VIEWPORT_SIZE, ignore_https_errors=True)
        exec_context.add_init_script("() => { document.body.style.zoom = '75%'; }")
        exec_page = exec_context.new_page()
        exec_base = BasePage(exec_page)
        exec_cache[exec_email] = (exec_context, exec_page, exec_base)
        is_exec_new = True
    
    try:
        if is_exec_new:
            # LOG IN
            exec_page.goto(f"{base_url}/login")
            ex_email = exec_page.locator('input[formcontrolname="emailId"]')
            exec_base.scroll_focus_fill(ex_email, exec6_creds.get("email"))
            ex_pass = exec_page.locator('input[formcontrolname="password"]')
            exec_base.scroll_focus_fill(ex_pass, exec6_creds.get("password"))
            exec_base.scroll_focus_click(exec_page.locator('button.auth-btn'))
            
            exec_page.locator(".dash-headding").first.wait_for(state="visible", timeout=20000)
            
            # Handle possible "Session active in another machine" modal that pops up asynchronously after login
            try:
                exec_page.wait_for_timeout(6000)
                logger.info("👀 Checking for active session modal...")
                session_modal = exec_page.locator(".cdk-overlay-pane, .modal-dialog, .popup-content, .mat-dialog-container, .modal-content, [role='dialog']").filter(has_text=re.compile(r"Session|Machine|Invalidate", re.IGNORECASE)).first
                if session_modal.is_visible(timeout=3000):
                    logger.info(f"⚠️ Detected active session modal! Text: {session_modal.inner_text()}")
                    ok_btn = session_modal.locator("button").filter(has_text=re.compile(r"^(OK|Yes|Continue|Invalidate|Confirm)$", re.IGNORECASE)).first
                    if ok_btn.is_visible():
                        logger.info("🔘 Clicking confirmation button on modal to clear it...")
                        exec_base.scroll_focus_click(ok_btn)
                        exec_page.wait_for_timeout(2000)
            except Exception as e:
                logger.warning(f"⚠️ Modal check exception (safe to ignore): {e}")
        
        # SEARCH CASE
        navigate_to_search_case_via_ui(exec_page)
        
        search_cases_toggle = exec_page.locator('button.ra-export-btn', has_text="Search Cases").first
        exec_base.scroll_focus_click(search_cases_toggle)
        case_number_input = exec_page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=5000)
        exec_base.scroll_focus_fill(case_number_input, str(target_case))
        search_btn = exec_page.locator('button.qm-btn-primary').filter(has_text="Search").first
        exec_base.scroll_focus_click(search_btn)
        exec_page.wait_for_timeout(2000)
        
        # PRE-APPROVAL CHECK ON GRID
        case_row = exec_page.locator("tr").filter(has_text=str(target_case)).first
        case_row.wait_for(state="visible", timeout=25000)
        logger.info("👀 Executive checking case on grid before approval...")
        exec_page.evaluate("""() => {
            const rows = document.querySelectorAll('tr');
            for(let r of rows) {
                if(r.innerText.includes('""" + str(target_case) + """')) {
                    r.style.outline = '4px solid orange';
                    r.style.backgroundColor = 'rgba(255, 165, 0, 0.3)';
                    r.scrollIntoView({behavior: 'smooth', block: 'center'});
                }
            }
        }""")
        exec_page.wait_for_timeout(3000)
        
        # OPEN CASE
        case_row = exec_page.locator("tr").filter(has_text=str(target_case)).first
        case_row.wait_for(state="visible", timeout=10000)
        visibility_icon = case_row.locator('span.material-symbols-outlined:has-text("visibility")').first
        exec_base.scroll_focus_click(visibility_icon)
        
        # Wait for profile load
        exec_page.wait_for_timeout(3000)
        
        # ACTIVITY 1 APPROVAL
        activities_tab = exec_page.get_by_role("tab", name="Activities")
        exec_base.scroll_focus_click(activities_tab)
        exec_page.wait_for_timeout(1000)
        
        # Try to find an enabled "Approve" or "Transfer Tag" button inside the grid
        approve_btn_direct = exec_page.locator("button:not([disabled])").filter(has_text=re.compile(r"Approve|Transfer Tag", re.IGNORECASE)).first
        
        logger.info("⏳ Waiting for 'Approve' or 'Transfer Tag' button to appear in Activities grid (up to 30s)...")
        approve_btn_direct.wait_for(state="attached", timeout=30000)
        
        logger.info("🎯 Found direct 'Approve' or 'Transfer Tag' button on Activities grid. Clicking it...")
        exec_base.scroll_focus_click(approve_btn_direct)
        exec_page.wait_for_timeout(2000)
        
        # Wait for the Comments modal and submit
        popup_modal = exec_page.locator("div.popup-content, mat-dialog-container, div.modal-content").first
        popup_modal.wait_for(state="visible", timeout=10000)
        
        modal_txt = popup_modal.locator("textarea").first
        exec_base.scroll_focus_fill(modal_txt, "Executive Approved Transfer Tag")
        exec_page.wait_for_timeout(500)
        
        submit_btn = popup_modal.locator("button").filter(has_text=re.compile(r"Update|Submit|Save|Approve", re.IGNORECASE)).first
        exec_base.scroll_focus_click(submit_btn)
        popup_modal.wait_for(state="hidden", timeout=10000)
        logger.info("✅ Executive submitted approval modal.")
        exec_page.wait_for_timeout(2000)
        
        if step_printer: step_printer(10)
        
        # POST-APPROVAL CHECK ON GRID
        logger.info("👀 Executive verifying status after approval...")
        navigate_to_search_case_via_ui(exec_page)
        search_cases_toggle = exec_page.locator('button.ra-export-btn', has_text="Search Cases").first
        exec_base.scroll_focus_click(search_cases_toggle)
        case_number_input = exec_page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=5000)
        exec_base.scroll_focus_fill(case_number_input, str(target_case))
        search_btn = exec_page.locator('button.qm-btn-primary').filter(has_text="Search").first
        exec_base.scroll_focus_click(search_btn)
        exec_page.wait_for_timeout(2000)
        
        case_row = exec_page.locator("tr").filter(has_text=str(target_case)).first
        case_row.wait_for(state="visible", timeout=25000)
        
        # OPEN CASE
        visibility_icon = case_row.locator('span.material-symbols-outlined:has-text("visibility")').first
        exec_base.scroll_focus_click(visibility_icon)
        exec_page.wait_for_timeout(3000)
        
        logger.info("👀 Executive verifying status in case profile after approval...")
        exec_page.evaluate("""() => {
            const statusLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Status'));
            if(statusLabel) {
                const val = statusLabel.nextElementSibling;
                if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; val.scrollIntoView({behavior: 'smooth', block: 'center'}); }
            }
            const ownerLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Owner'));
            if(ownerLabel) {
                const val = ownerLabel.nextElementSibling;
                if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; }
            }
        }""")
        exec_page.wait_for_timeout(3500)
        if step_printer: step_printer(11)
        
    except Exception as ex:
        logger.error(f"❌ Exec 6 Context failed: {ex}")
        try:
            with open("debug_exec6_timeout.html", "w", encoding="utf-8") as f:
                f.write(exec_page.content())
            logger.info("Saved page HTML to debug_exec6_timeout.html")
        except Exception:
            pass
        return False
    finally:
        if not shared_setup or "contexts" not in shared_setup:
            exec_page.close()
            exec_context.close()
            
    # 3. SUPERADMIN SEARCHES, ASSIGNS TO BCM
    logger.info("👑 SA on Case Details: Assigning case to BCM...")
    try:
        superadmin_check_case_status(page, base_url, target_case, "Pending Approval", already_on_search_case=False, step_printer=step_printer, search_step=12)
    except Exception as sa_ex:
        logger.warning(f"⚠️ SA refresh prior to BCM assignment failed: {sa_ex}")

    try:
        bcm_email = mgr_creds.get('email', 'boscasemanager2@yopmail.com')
        owner_dropdown = page.locator("select#caseOwner")
        owner_dropdown.wait_for(state="visible", timeout=10000)
        owner_dropdown.scroll_into_view_if_needed()
        current_owner = owner_dropdown.input_value()
        
        if current_owner.strip().lower() != bcm_email.strip().lower():
            logger.info(f"📝 Superadmin changing owner from '{current_owner}' to '{bcm_email}'...")
            
            options = owner_dropdown.locator("option").all()
            available = False
            for opt in options:
                val = opt.get_attribute("value")
                if bcm_email.lower() in opt.inner_text().lower() or (val and bcm_email.lower() == val.lower()):
                    available = True
                    break
            
            if available:
                owner_dropdown.select_option(value=bcm_email)
                page.wait_for_timeout(500)
                
                # Click Save or Assign
                assign_btn = page.locator('button.qm-btn.qm-btn-primary').filter(has_text=re.compile(r"Assign|Save", re.IGNORECASE))
                if not assign_btn.is_visible():
                    assign_btn = page.locator('button.qm-btn.qm-btn-primary').filter(has_text="Save")
                
                if assign_btn.is_visible():
                    base.scroll_focus_click(assign_btn.first)
                    
                    # Handle the Add Comments modal
                    modal_comment = page.locator("div.popup-content textarea, div.modal-content textarea, textarea[placeholder='Comments...']")
                    modal_comment.first.wait_for(state="visible", timeout=10000)
                    base.scroll_focus_fill(modal_comment.first, "Assigning to BCM for final approval")
                    
                    submit_btn = page.locator("div.popup-content button, div.modal-content button, button.btn-primary, button.qm-btn").filter(has_text="Submit").first
                    base.scroll_focus_click(submit_btn)
                    
                    # Wait for the modal to completely disappear
                    modal_comment.first.wait_for(state="hidden", timeout=15000)
                    logger.info("✅ Superadmin successfully reassigned case to BCM.")
                else:
                    logger.warning("⚠️ Could not find 'Assign' or 'Save' button. Assuming auto-saved.")
            else:
                logger.info(f"ℹ️ '{bcm_email}' not in dropdown. Leaving owner as '{current_owner}'.")

            if step_printer: step_printer(13)
            logger.info('👀 Tiny wait for user to see the SA Assignment to BCM')
            page.wait_for_timeout(3000)
        else:
            logger.info("✅ Case is already assigned to target BCM.")
            if step_printer: step_printer(13)
            
        page.wait_for_timeout(2000)
        
        # Wait for potential spinners
        try:
            page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=15000)
        except Exception:
            pass
            
        page.wait_for_timeout(2000)
        
        superadmin_check_case_status(page, base_url, target_case, "Transfer Tag Case Assigned to BCM", already_on_search_case=False, step_printer=step_printer, search_step=14)
        
    except Exception as ex:
        logger.warning(f"⚠️ SA assign to BCM failed: {ex}")
        return False
        
    # 4. BCM CONTEXT APPROVES ACTIVITY 2
    mgr_cache = shared_setup.setdefault("contexts", {}) if shared_setup else {}
    mgr_email = mgr_creds.get("email")
    if mgr_email in mgr_cache:
        logger.info(f"♻️ Reusing existing browser context for Manager: {mgr_email}")
        mgr_context, mgr_page, mgr_base = mgr_cache[mgr_email]
        is_mgr_new = False
    else:
        logger.info(f"🌐 Spawning clean isolated Browser Context for BCM: {mgr_email}")
        mgr_context = browser.new_context(viewport=VIEWPORT_SIZE, ignore_https_errors=True)
        mgr_context.add_init_script("() => { document.body.style.zoom = '75%'; }")
        mgr_page = mgr_context.new_page()
        mgr_base = BasePage(mgr_page)
        mgr_cache[mgr_email] = (mgr_context, mgr_page, mgr_base)
        is_mgr_new = True
    
    try:
        if is_mgr_new:
            # LOG IN
            mgr_page.goto(f"{base_url}/login")
            mg_email = mgr_page.locator('input[formcontrolname="emailId"]')
            mgr_base.scroll_focus_fill(mg_email, mgr_creds.get("email"))
            mg_pass = mgr_page.locator('input[formcontrolname="password"]')
            mgr_base.scroll_focus_fill(mg_pass, mgr_creds.get("password"))
            mgr_base.scroll_focus_click(mgr_page.locator('button.auth-btn'))
            
            mgr_page.locator(".dash-headding").first.wait_for(state="visible", timeout=20000)
            if step_printer: step_printer(15)
            
            # Handle possible "Session active in another machine" modal that pops up asynchronously after login
            try:
                mgr_page.wait_for_timeout(6000)
                logger.info("👀 Checking for active session modal...")
                session_modal = mgr_page.locator(".cdk-overlay-pane, .modal-dialog, .popup-content, .mat-dialog-container, .modal-content, [role='dialog']").filter(has_text=re.compile(r"Session|Machine|Invalidate", re.IGNORECASE)).first
                if session_modal.is_visible(timeout=3000):
                    logger.info(f"⚠️ Detected active session modal! Text: {session_modal.inner_text()}")
                    ok_btn = session_modal.locator("button").filter(has_text=re.compile(r"^(OK|Yes|Continue|Invalidate|Confirm)$", re.IGNORECASE)).first
                    if ok_btn.is_visible():
                        logger.info("🔘 Clicking confirmation button on modal to clear it...")
                        mgr_base.scroll_focus_click(ok_btn)
                        mgr_page.wait_for_timeout(2000)
            except Exception as e:
                logger.warning(f"⚠️ Modal check exception (safe to ignore): {e}")
        
        # SEARCH CASE
        navigate_to_search_case_via_ui(mgr_page)
        
        search_cases_toggle = mgr_page.locator('button.ra-export-btn', has_text="Search Cases").first
        mgr_base.scroll_focus_click(search_cases_toggle)
        case_number_input = mgr_page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=5000)
        mgr_base.scroll_focus_fill(case_number_input, str(target_case))
        search_btn = mgr_page.locator('button.qm-btn-primary').filter(has_text="Search").first
        mgr_base.scroll_focus_click(search_btn)
        mgr_page.wait_for_timeout(2000)
        
        if step_printer: step_printer(16)
        
        # PRE-APPROVAL CHECK ON GRID
        case_row = mgr_page.locator("tr").filter(has_text=str(target_case)).first
        case_row.wait_for(state="visible", timeout=25000)
        logger.info("👀 BCM checking case on grid before approval...")
        mgr_page.evaluate("""() => {
            const rows = document.querySelectorAll('tr');
            for(let r of rows) {
                if(r.innerText.includes('""" + str(target_case) + """')) {
                    r.style.outline = '4px solid orange';
                    r.style.backgroundColor = 'rgba(255, 165, 0, 0.3)';
                    r.scrollIntoView({behavior: 'smooth', block: 'center'});
                }
            }
        }""")
        mgr_page.wait_for_timeout(3000)
        
        # OPEN CASE
        case_row = mgr_page.locator("tr").filter(has_text=str(target_case)).first
        case_row.wait_for(state="visible", timeout=10000)
        visibility_icon = case_row.locator('span.material-symbols-outlined:has-text("visibility")').first
        mgr_base.scroll_focus_click(visibility_icon)
        
        mgr_page.wait_for_timeout(3000)
        
        # ACTIVITY 2 APPROVAL
        activities_tab = mgr_page.get_by_role("tab", name="Activities")
        mgr_base.scroll_focus_click(activities_tab)
        mgr_page.wait_for_timeout(1000)
        
        # Try to find an enabled "Approve" or "Transfer Tag" button inside the grid
        approve_btn_direct = mgr_page.locator("button:not([disabled])").filter(has_text=re.compile(r"Approve|Transfer Tag", re.IGNORECASE)).first
        
        logger.info("⏳ Waiting for 'Approve' or 'Transfer Tag' button to appear in Activities grid for BCM (up to 30s)...")
        approve_btn_direct.wait_for(state="attached", timeout=30000)
        
        # Check if it's disabled (safety check, though CSS :not([disabled]) should prevent it)
        is_disabled = approve_btn_direct.evaluate("el => el.disabled || el.classList.contains('disabled')")
        
        if is_disabled:
            logger.info("🎯 Found 'Transfer Tag' button, but it is disabled. This implies the case is already fully approved. BCM does not need to approve again.")
            if step_printer: step_printer(17)
            mgr_page.wait_for_timeout(2000)
        else:
            logger.info("🎯 Found direct 'Approve' or 'Transfer Tag' button on Activities grid for BCM. Clicking it...")
            mgr_base.scroll_focus_click(approve_btn_direct)
            
            # Wait for the Comments modal and submit
            popup_modal = mgr_page.locator("div.popup-content, mat-dialog-container, div.modal-content").first
            popup_modal.wait_for(state="visible", timeout=10000)
            
            modal_txt = popup_modal.locator("textarea").first
            mgr_base.scroll_focus_fill(modal_txt, "Approving Transfer Tag case as bos case manager")
            mgr_page.wait_for_timeout(500)
            
            submit_btn = popup_modal.locator("button").filter(has_text=re.compile(r"Update|Submit|Save|Approve", re.IGNORECASE)).first
            mgr_base.scroll_focus_click(submit_btn)
            popup_modal.wait_for(state="hidden", timeout=10000)
            logger.info("✅ BCM submitted approval modal.")
            if step_printer: step_printer(17)
            mgr_page.wait_for_timeout(2000)
        
        # POST-APPROVAL CHECK ON GRID
        logger.info("👀 BCM verifying status after approval...")
        navigate_to_search_case_via_ui(mgr_page)
        search_cases_toggle = mgr_page.locator('button.ra-export-btn', has_text="Search Cases").first
        mgr_base.scroll_focus_click(search_cases_toggle)
        case_number_input = mgr_page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=5000)
        mgr_base.scroll_focus_fill(case_number_input, str(target_case))
        search_btn = mgr_page.locator('button.qm-btn-primary').filter(has_text="Search").first
        mgr_base.scroll_focus_click(search_btn)
        mgr_page.wait_for_timeout(2000)
        
        if step_printer: step_printer(18)
        
        case_row = mgr_page.locator("tr").filter(has_text=str(target_case)).first
        case_row.wait_for(state="visible", timeout=25000)
        
        # OPEN CASE
        visibility_icon = case_row.locator('span.material-symbols-outlined:has-text("visibility")').first
        mgr_base.scroll_focus_click(visibility_icon)
        mgr_page.wait_for_timeout(3000)
        
        logger.info("👀 BCM verifying status in case profile after approval...")
        mgr_page.evaluate("""() => {
            const statusLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Status'));
            if(statusLabel) {
                const val = statusLabel.nextElementSibling;
                if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; val.scrollIntoView({behavior: 'smooth', block: 'center'}); }
            }
            const ownerLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Owner'));
            if(ownerLabel) {
                const val = ownerLabel.nextElementSibling;
                if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; }
            }
        }""")
        mgr_page.wait_for_timeout(3500)
        
    except Exception as ex:
        logger.error(f"❌ BCM Context failed: {ex}")
        return False
    finally:
        if not shared_setup or "contexts" not in shared_setup:
            mgr_page.close()
            mgr_context.close()
            
    # 5. SUPERADMIN VERIFIES FINAL CASE RESOLUTION
    try:
        superadmin_check_case_status(page, base_url, target_case, "Final SA Verification", already_on_search_case=False, step_printer=step_printer, search_step=19)
        page.wait_for_timeout(3000)
    except Exception as ex:
        logger.warning(f"⚠️ SA final check failed: {ex}")
        return False
        
    return True
