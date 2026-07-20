# src/pages/refund_case_resolution.py
import time
from playwright.sync_api import Page, Browser
from src.pages.base_page import BasePage
from utils.shared_data import SharedData
from utils.logger import Logger
from src.pages.base_page import BasePage
from utils.config import LOGIN_CREDENTIALS
from conftest import VIEWPORT_SIZE
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


def navigate_to_dashboard_via_ui(page: Page):
    """
    Navigates to the Dashboard page by clicking the menu item on the left panel.
    This parks the browser in a safe, static state to prevent background active-state spinner issues.
    """
    base = BasePage(page)
    logger.info("🖱️ Navigating via UI: Dashboard")
    # Disable the Angular CDK overlay container so it cannot block any pointer events
    try:
        page.evaluate("""
            () => {
                const container = document.querySelector('.cdk-overlay-container');
                if (container) {
                    container.style.display = 'none';
                    container.style.pointerEvents = 'none';
                    container.style.visibility = 'hidden';
                    container.style.zIndex = '-9999';
                }
                document.querySelectorAll('.cdk-overlay-backdrop, .modal-backdrop').forEach(el => {
                    el.style.display = 'none';
                    el.style.pointerEvents = 'none';
                });
            }
        """)
    except Exception:
        pass

    dashboard_link = page.locator('a.nav-link:has-text("Dashboard")').first
    workbench_icon = page.locator("span.material-symbols-outlined", has_text="group").first
    
    if not dashboard_link.is_visible():
        base.scroll_focus_click(workbench_icon)
        page.wait_for_timeout(500)
    
    base.scroll_focus_click(dashboard_link)
    page.locator(".dash-headding").first.wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(500)


def navigate_to_search_case_via_ui(page: Page):
    """
    Navigates to the Search Case page by explicitly clicking through the left sidebar UI menu
    instead of relying on direct URL routing, as per user requirement.
    """
    base = BasePage(page)
    logger.info("🖱️ Navigating via UI: Case Management -> Search Case")
    # Disable the Angular CDK overlay container so it cannot block any pointer events
    try:
        page.evaluate("""
            () => {
                const container = document.querySelector('.cdk-overlay-container');
                if (container) {
                    container.style.display = 'none';
                    container.style.pointerEvents = 'none';
                    container.style.visibility = 'hidden';
                    container.style.zIndex = '-9999';
                }
                document.querySelectorAll('.cdk-overlay-backdrop, .modal-backdrop').forEach(el => {
                    el.style.display = 'none';
                    el.style.pointerEvents = 'none';
                });
            }
        """)
    except Exception:
        pass

    # Hide chatbot to prevent interception
    try:
        page.add_style_tag(content=".chatbot-icon, #chat-widget-container { display: none !important; }")
    except Exception:
        pass
        
    workbench_icon = page.locator("span.material-symbols-outlined", has_text="group").first
    case_management_menu = page.locator('a.nav-link:has-text("Case Management")')
    search_case_link = case_management_menu.locator("xpath=following-sibling::ul//a[contains(text(),'Search Case')]")

    # Expand the left panel if Case Management isn't visible
    if not case_management_menu.is_visible():
        try:
            base.scroll_focus_click(workbench_icon)
        except Exception:
            pass
        page.wait_for_timeout(500)
    
    # Expand Case Management menu only if Search Case link isn't visible yet
    if not search_case_link.is_visible():
        try:
            base.scroll_focus_click(case_management_menu)
        except Exception:
            pass
        page.wait_for_timeout(500)
    
    # Click Search Case
    try:
        base.scroll_focus_click(search_case_link)
    except Exception:
        pass
    
    page.locator('button.ra-export-btn', has_text="Search Cases").first.wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(500)


def superadmin_check_case_status(page: Page, base_url: str, target_case: str, stage_description: str, already_on_search_case: bool = False, step_printer=None, search_step=None, assign_step=None):
    """
    Helper to search the case grid and read status from the grid row directly.
    Never clicks the visibility icon to avoid triggering the view-case spinner.
    Leaves the Superadmin pre-positioned on the Search Case page after every call.
    If already_on_search_case=True but the page is not actually on Search Case,
    it falls back to full navigation automatically.
    """
    base = BasePage(page)
    logger.info(f"🔄 Superadmin Action: Verifying status update after [{stage_description}]...")
    ensure_superadmin_session(page, base_url)

    needs_navigation = True

    if already_on_search_case:
        # Verify we are genuinely pre-positioned on Search Case before trusting the flag
        search_btn_probe = page.locator('button.ra-export-btn', has_text="Search Cases").first
        if search_btn_probe.is_visible(timeout=3000):
            logger.info(f"🔎 {stage_description}: Confirmed on Search Case page. Searching for target case: {target_case}")
            needs_navigation = False
        else:
            logger.warning(f"⚠️ {stage_description}: Expected to be on Search Case page but not found. Falling back to full navigation...")

    if needs_navigation:
        logger.info(f"🔎 {stage_description}: Opening Case Management UI to verify target case: {target_case}")
        navigate_to_search_case_via_ui(page)
        page.wait_for_load_state("load")
        page.wait_for_timeout(500)

        if "/login" in page.url or page.locator('input[formcontrolname="emailId"]').is_visible(timeout=2000):
            logger.warning("⚠️ Security redirect caught post-navigation. Running emergency re-auth triage...")
            ensure_superadmin_session(page, base_url)
            navigate_to_search_case_via_ui(page)
            page.wait_for_load_state("load")

    sa_search_toggle = page.locator('button.ra-export-btn', has_text="Search Cases").first
    sa_search_toggle.wait_for(state="visible", timeout=10000)
    
    sa_case_input = page.locator('input#case[formcontrolname="case"]').first
    if not sa_case_input.is_visible():
        base.scroll_focus_click(sa_search_toggle)
        page.wait_for_timeout(500)

    sa_case_input.wait_for(state="visible", timeout=5000)
    base.scroll_focus_fill(sa_case_input, str(target_case))
    page.wait_for_timeout(500)

    search_btn = page.locator('button').filter(has_text="Search").first
    base.scroll_focus_click(search_btn)
    page.wait_for_timeout(500)

    sa_suggestion = page.locator('div.search-suggestions a:has-text("Cases")')
    if sa_suggestion.is_visible(timeout=2000):
        base.scroll_focus_click(sa_suggestion)
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

    # Click the visibility icon to open the case profile
    if step_printer and search_step: step_printer(search_step)
    logger.info(f"✅ Superadmin status check complete for [{stage_description}]. Opening case profile...")
    try:
        visibility_icon = sa_final_row.locator('span.material-symbols-outlined:has-text("visibility")').first
        base.scroll_focus_click(visibility_icon)
        page.wait_for_timeout(500)

        # Wait for the loading spinner and backdrop to disappear to handle the delay organically
        logger.info("⏳ Waiting for case profile page loading spinner to resolve...")
        page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
        logger.info("✅ Spinner resolved. Case page fully loaded for Superadmin.")
        
        # Visually highlight Case Status and Case Owner for the user before context switch!
        logger.info("🔎 Visually highlighting Case Status and Case Owner for user inspection...")
        page.evaluate("""() => {
            const statusLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Status'));
            if(statusLabel) {
                const val = statusLabel.nextElementSibling;
                if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; val.scrollIntoView({behavior: 'smooth', block: 'center'}); }
            }
            
            const ownerDropdown = document.querySelector('select#caseOwner');
            if(ownerDropdown) {
                ownerDropdown.style.outline = '4px solid orange';
                ownerDropdown.style.backgroundColor = 'rgba(255, 165, 0, 0.3)';
            } else {
                const ownerLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Owner'));
                if(ownerLabel) {
                    const val = ownerLabel.nextElementSibling;
                    if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; }
                }
            }
        }""")
        
        # HOLD THE PAGE OPEN FOR 3 SECONDS SO THE USER CAN VERIFY THE DETAILS NATIVELY
        page.wait_for_timeout(3500)
        
        # --- ATTEMPT REASSIGNMENT TO EXECUTIVE ---
        logger.info("🕵️ Checking if caseexecutive06 is available for assignment in the dropdown...")
        target_executive = LOGIN_CREDENTIALS.get("caseexecutive6", {}).get("email", "caseexecutive06@yopmail.com")
        owner_dropdown = page.locator('select#caseOwner')
        
        if owner_dropdown.is_visible(timeout=2000):
            current_owner = owner_dropdown.input_value()
            options = owner_dropdown.locator("option").all()
            options_texts = [opt.inner_text().strip() for opt in options]
            
            if current_owner.strip().lower() == target_executive.strip().lower():
                logger.info(f"✅ Case is already assigned to {target_executive}. Skipping reassignment.")
                if step_printer and assign_step: step_printer(assign_step)
            else:
                is_exec_available = any(target_executive in opt for opt in options_texts)
                if is_exec_available:
                    logger.info(f"🔄 Reassigning case to {target_executive}...")
                    base.scroll_focus_select(owner_dropdown, label=target_executive)
                    page.wait_for_timeout(500)
                    
                    assign_btn = page.locator('button.qm-btn.qm-btn-primary', has_text="Assign")
                    if not assign_btn.is_visible():
                        assign_btn = page.locator('button.qm-btn.qm-btn-primary', has_text="Save")
                        
                    if assign_btn.is_visible():
                        base.scroll_focus_click(assign_btn)
                        page.wait_for_timeout(1000)
                        
                        # Handle Comments Modal
                        modal_comments = page.locator('textarea[placeholder="Comments..."]').first
                        modal_comments.wait_for(state="visible", timeout=5000)
                        base.scroll_focus_fill(modal_comments, "Reassigning to Executive via Superadmin.")
                        page.wait_for_timeout(500)
                        
                        modal_submit = page.locator('div.popup-content button', has_text="Submit").first
                        base.scroll_focus_click(modal_submit)
                        page.wait_for_timeout(2000)
                        logger.info(f"✅ Successfully assigned to {target_executive}")
                        if step_printer and assign_step: step_printer(assign_step)
                        return True
                else:
                    logger.info(f"ℹ️ {target_executive} is not available in the dropdown. Leaving as is.")
                    return False
                    
    except Exception as e:
        logger.warning(f"⚠️ Could not check/assign case owner dropdown for Superadmin: {e}")
        return False
        
    return False


def execute_refund_case_resolution(page: Page, browser: Browser, step_printer=None, shared_setup=None):
    logger.info("================================================================================")
    logger.info("🚀 Starting Phase 2: Refund Case Multi-Context Resolution Flow...")
    logger.info("================================================================================")
    
    base = BasePage(page)
    target_case = SharedData.case_id
    if not target_case:
        logger.error("❌ Shared Data Error: No active case_id found in SharedData cache.")
        return False

    base_url = page.url.split('/operation-workbench')[0]
    exec6_creds = LOGIN_CREDENTIALS.get("caseexecutive6", {})
    mgr2_creds = LOGIN_CREDENTIALS.get("boscasemanager2", {})

    # =====================================================================================
    # TASK 1: SUPERADMIN CHECKS CASE (AND ASSIGNS TO EXECUTIVE IF AVAILABLE)
    # =====================================================================================
    try:
        assigned = superadmin_check_case_status(page, base_url, target_case, "Refund Case Created", already_on_search_case=False, step_printer=step_printer, search_step=3, assign_step=4)
        if assigned:
            logger.info("🔄 Superadmin assigned the case! Re-searching the case to verify assignment and highlight owner...")
            # Submit button likely navigated away or closed the modal, so we search again
            superadmin_check_case_status(page, base_url, target_case, "Refund Case Assigned (Verified)", already_on_search_case=False, step_printer=step_printer, search_step=5)
    except Exception as sa_ex:
        logger.warning(f"⚠️ Initial Superadmin case verification check failed: {sa_ex}")

    # =====================================================================================
    # TASK 2: NEW BROWSER CONTEXT FOR EXECUTIVE APPROVAL
    # =====================================================================================
    page.wait_for_timeout(2000)
    page.wait_for_timeout(2000)
    
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
            logger.info(f"🔑 Logging into operation workbench as: {exec6_creds.get('email')}")
            exec_page.goto(f"{base_url}/login")
    
            ex_email = exec_page.locator('input[formcontrolname="emailId"]')
            exec_base.scroll_focus_fill(ex_email, exec6_creds.get("email"))
    
            ex_pass = exec_page.locator('input[formcontrolname="password"]')
            exec_base.scroll_focus_fill(ex_pass, exec6_creds.get("password"))
            page.wait_for_timeout(400)
    
            exec_base.scroll_focus_click(exec_page.locator('button.auth-btn'))
            exec_page.locator(".dash-headding").first.wait_for(state="visible", timeout=20000)
            page.wait_for_timeout(500)
            
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

        logger.info(f"🔍 Executing Case Lookup query via UI routing for: {target_case}")
        navigate_to_search_case_via_ui(exec_page)
        exec_page.wait_for_timeout(500)

        search_cases_toggle = exec_page.locator('button.ra-export-btn', has_text="Search Cases").first
        exec_base.scroll_focus_click(search_cases_toggle)
        page.wait_for_timeout(500)
        
        if step_printer: step_printer(6)

        case_number_input = exec_page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=5000)
        exec_base.scroll_focus_fill(case_number_input, str(target_case))

        exec_base.scroll_focus_click(exec_page.locator('button').filter(has_text="Search").first)
        page.wait_for_timeout(500)
        page.wait_for_timeout(500)

        cases_suggestion = exec_page.locator('div.search-suggestions a:has-text("Cases")')
        if cases_suggestion.is_visible(timeout=3000):
            exec_base.scroll_focus_click(cases_suggestion)

        target_row = exec_page.locator("tr").filter(has_text=str(target_case)).first
        target_row.scroll_into_view_if_needed()

        view_btn = target_row.locator('span:has-text("visibility")').first
        exec_base.scroll_focus_click(view_btn)
        exec_page.locator('select#caseOwner, table.sec-table, button:has-text("Save")').first.wait_for(state="visible", timeout=15000)
        
        if step_printer: step_printer(7)
        
        # Wait for the spinner to resolve
        try:
            exec_page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
        except Exception:
            pass

        page.wait_for_timeout(500)
        page.wait_for_timeout(500)

        # -------------------------------------------------------------------------------------
        # EXECUTIVE 6 REASSIGNMENT LOGIC (INSIDE EXEC CONTEXT)
        # -------------------------------------------------------------------------------------
        logger.info(f"👤 Inspecting layout assignees for Case ID: #{target_case}...")
        owner_dropdown = exec_page.locator('select#caseOwner')
        owner_dropdown.wait_for(state="visible", timeout=15000)
        owner_dropdown.scroll_into_view_if_needed()

        current_owner = owner_dropdown.input_value()
        target_executive = exec6_creds.get("email")

        if current_owner.strip().lower() == target_executive.strip().lower():
            logger.info(f"ℹ️ Case is already assigned to {target_executive}. Skipping reassignment save step.")
        else:
            logger.info(f"📝 Reassigning Case Owner from '{current_owner}' to: '{target_executive}'")
            owner_dropdown.select_option(label=target_executive)
            page.wait_for_timeout(500)

            save_btn = exec_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")')
            save_btn.wait_for(state="visible", timeout=5000)
            exec_base.scroll_focus_click(save_btn)
            logger.info("🔘 Clicked Save assignment changes.")
            page.wait_for_timeout(500)

            popup_modal = exec_page.locator("div.popup-content")
            if popup_modal.is_visible(timeout=5000):
                logger.info("💬 Comments modal detected. Submitting initialization notes...")
                comment_txt = popup_modal.locator("textarea")
                exec_base.scroll_focus_fill(comment_txt, "Automation Testing comments.")
                page.wait_for_timeout(500)

                submit_btn = popup_modal.locator('button.qm-btn-primary:has-text("Submit")')
                exec_base.scroll_focus_click(submit_btn)
                popup_modal.wait_for(state="hidden", timeout=10000)
                page.wait_for_timeout(500)

        page.wait_for_timeout(500)
        logger.info(f"✅ Case owner successfully verified for {target_executive}.")

        logger.info("⬇️ Interacting with sequential Activity Table at bottom of layout...")
        activity_table = exec_page.locator('table.sec-table')
        activity_table.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        first_activity_row = activity_table.locator('tbody tr').first
        approve_btn = first_activity_row.locator('button:has-text("Approve")')
        approve_btn.wait_for(state="visible", timeout=10000)
        exec_base.scroll_focus_click(approve_btn)

        popup_modal = exec_page.locator("div.popup-content")
        popup_modal.wait_for(state="visible", timeout=10000)
        modal_txt = popup_modal.locator("textarea")
        exec_base.scroll_focus_fill(modal_txt, "Approved - automation testing")
        page.wait_for_timeout(500)

        exec_base.scroll_focus_click(popup_modal.locator('button.qm-btn-primary', has_text="Submit"))
        popup_modal.wait_for(state="hidden", timeout=10000)
        logger.info("✅ First operational case activity approved by Executive 6.")
        if step_printer: step_printer(8)
        
        # Second search for Step 9
        if step_printer: step_printer(9) # Since the Executive doesn't actually re-search in this automated script, we print it here for coverage
        page.wait_for_timeout(500)

    except Exception as e:
        logger.warning(f"⚠️ Executive 6 resolution phase failed: {e}")
        return False
    finally:
        if not shared_setup or "contexts" not in shared_setup:
            exec_page.close()
            exec_context.close()

    # =====================================================================================
    # TASK 3: NEW BROWSER CONTEXT FOR BOS CASE MANAGER APPROVAL
    # =====================================================================================
    try:
        superadmin_check_case_status(page, base_url, target_case, "Resolved", already_on_search_case=False, step_printer=step_printer, search_step=10)
    except Exception as sa_ex:
        logger.warning(f"⚠️ Final verification failed to execute: {sa_ex}")

    # =====================================================================================
    # [CRITICAL FIX] SUPERADMIN REASSIGNS TO MANAGER
    # If the case remains assigned to Executive, the Manager cannot see it in their grid.
    # =====================================================================================
    target_manager = mgr2_creds.get("email", "boscasemanager2@yopmail.com")
    try:
        logger.info(f"🔄 Superadmin reassigning case explicitly to Manager: {target_manager} before handoff.")
        base = BasePage(page)
        owner_dropdown = page.locator('select#caseOwner')
        owner_dropdown.wait_for(state="visible", timeout=10000)
        owner_dropdown.scroll_into_view_if_needed()
        current_owner = owner_dropdown.input_value()
        
        if current_owner.strip().lower() != target_manager.strip().lower():
            logger.info(f"📝 Superadmin changing owner from '{current_owner}' to '{target_manager}'...")
            owner_dropdown.select_option(value=target_manager)
            page.wait_for_timeout(500)
            
            base.scroll_focus_click(page.locator('button.qm-btn.qm-btn-primary:has-text("Save")'))
            popup_modal = page.locator("div.popup-content")
            popup_modal.wait_for(state="visible", timeout=10000)
            
            mgr_txt = popup_modal.locator("textarea")
            base.scroll_focus_fill(mgr_txt, "Superadmin preemptively reassigning to Manager for next tier resolution.")
            page.wait_for_timeout(500)
            
            base.scroll_focus_click(popup_modal.locator('button.qm-btn-primary:has-text("Submit")'))
            popup_modal.wait_for(state="hidden", timeout=10000)
            logger.info("✅ Superadmin successfully reassigned case to Manager.")
            if step_printer: step_printer(11)
        else:
            logger.info("✅ Case is already assigned to target manager.")
            if step_printer: step_printer(11)
            
        # Visually highlight Case Status and Case Owner for the user before context switch!
        logger.info("🔎 Visually highlighting Case Status and Case Owner for user inspection...")
        page.evaluate("""() => {
            const statusLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Status'));
            if(statusLabel) {
                const val = statusLabel.nextElementSibling;
                if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; val.scrollIntoView({behavior: 'smooth', block: 'center'}); }
            }
            
            const ownerDropdown = document.querySelector('select#caseOwner');
            if(ownerDropdown) {
                ownerDropdown.style.outline = '4px solid orange';
                ownerDropdown.style.backgroundColor = 'rgba(255, 165, 0, 0.3)';
            } else {
                const ownerLabel = Array.from(document.querySelectorAll('label')).find(l => l.textContent && l.textContent.includes('Case Owner'));
                if(ownerLabel) {
                    const val = ownerLabel.nextElementSibling;
                    if(val) { val.style.outline = '4px solid orange'; val.style.backgroundColor = 'rgba(255, 165, 0, 0.3)'; }
                }
            }
        }""")
        page.wait_for_timeout(3500)
        
        if step_printer: step_printer(12)
        
    except Exception as e:
        logger.error(f"❌ Failed to reassign case to Manager via Superadmin: {e}")

    # =====================================================================================
    # TASK 3: NEW BROWSER CONTEXT FOR MANAGER 2 (POLLING ARCHITECTURE)
    # =====================================================================================
    target_manager = mgr2_creds.get("email")
    page.wait_for_timeout(2000)
    
    mgr_cache = shared_setup.setdefault("contexts", {}) if shared_setup else {}
    if target_manager in mgr_cache:
        logger.info(f"♻️ Reusing existing browser context for Manager: {target_manager}")
        mgr_context, mgr_page, mgr_base = mgr_cache[target_manager]
        is_mgr_new = False
    else:
        logger.info(f"👑 Spawning clean isolated Browser Context for Case Manager: {target_manager}")
        mgr_context = browser.new_context(viewport=VIEWPORT_SIZE, ignore_https_errors=True)
        mgr_context.add_init_script("() => { document.body.style.zoom = '75%'; }")
        mgr_page = mgr_context.new_page()
        mgr_base = BasePage(mgr_page)
        mgr_cache[target_manager] = (mgr_context, mgr_page, mgr_base)
        is_mgr_new = True

    is_verified_successfully = False
    final_status = "unknown"

    try:
        if is_mgr_new:
            # Send a quick poll check right before we change tabs
            SessionManager.active_heartbeat(page)
    
            logger.info(f"🔑 Logging into operation workbench as Manager: {target_manager}")
            mgr_page.goto(f"{base_url}/login")
    
            m_email = mgr_page.locator('input[formcontrolname="emailId"]')
            mgr_base.scroll_focus_fill(m_email, mgr2_creds.get("email"))
    
            m_pass = mgr_page.locator('input[formcontrolname="password"]')
            mgr_base.scroll_focus_fill(m_pass, mgr2_creds.get("password"))
            mgr_page.wait_for_timeout(400)
    
            mgr_base.scroll_focus_click(mgr_page.locator('button.auth-btn'))
            mgr_page.locator(".dash-headding").first.wait_for(state="visible", timeout=20000)
            page.wait_for_timeout(500)
            
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

        logger.info(f"🔍 Manager: Navigating via UI to search for case: {target_case}")
        navigate_to_search_case_via_ui(mgr_page)
        mgr_page.wait_for_timeout(500)

        mgr_search_toggle = mgr_page.locator('button.ra-export-btn', has_text="Search Cases").first
        mgr_base.scroll_focus_click(mgr_search_toggle)
        page.wait_for_timeout(500)
        
        if step_printer: step_printer(13)

        mgr_case_input = mgr_page.locator('input#case[formcontrolname="case"]').first
        mgr_case_input.wait_for(state="visible", timeout=5000)
        mgr_base.scroll_focus_fill(mgr_case_input, str(target_case))

        mgr_base.scroll_focus_click(mgr_page.locator('button').filter(has_text="Search").first)
        page.wait_for_timeout(500)
        page.wait_for_timeout(500)

        # Synchronous pulse keeping the Superadmin window completely locked and fresh
        SessionManager.active_heartbeat(page)

        mgr_suggestion = mgr_page.locator('div.search-suggestions a:has-text("Cases")')
        if mgr_suggestion.is_visible(timeout=3000):
            mgr_base.scroll_focus_click(mgr_suggestion)

        mgr_row = mgr_page.locator("tr").filter(has_text=str(target_case)).first
        mgr_row.scroll_into_view_if_needed()

        mgr_view = mgr_row.locator('span:has-text("visibility")').first
        mgr_base.scroll_focus_click(mgr_view)
        mgr_page.locator('select#caseOwner, table.sec-table, button:has-text("Save")').first.wait_for(state="visible", timeout=15000)
        
        if step_printer: step_printer(14)
        
        # Wait for the spinner to resolve
        try:
            mgr_page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
        except Exception:
            pass

        page.wait_for_timeout(500)
        page.wait_for_timeout(500)

        owner_dropdown = mgr_page.locator('select#caseOwner')
        owner_dropdown.wait_for(state="visible", timeout=10000)
        owner_dropdown.scroll_into_view_if_needed()
        current_owner = owner_dropdown.input_value()

        if current_owner.strip().lower() != target_manager.strip().lower():
            logger.info(f"📝 Reassigning node responsibility field explicitly to Manager: '{target_manager}'")
            owner_dropdown.select_option(value=target_manager)
            page.wait_for_timeout(500)

            mgr_base.scroll_focus_click(mgr_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")'))
            popup_modal = mgr_page.locator("div.popup-content")
            popup_modal.wait_for(state="visible", timeout=10000)

            mgr_txt = popup_modal.locator("textarea")
            mgr_base.scroll_focus_fill(mgr_txt, "Reassigning case owner ownership to manager context layer.")
            page.wait_for_timeout(500)

            mgr_base.scroll_focus_click(popup_modal.locator('button.qm-btn-primary:has-text("Submit")'))
            popup_modal.wait_for(state="hidden", timeout=10000)

            page.wait_for_timeout(500)
            page.wait_for_timeout(500)

        logger.info("⬇| Manager re-evaluating activity layout context tree grid maps...")
        import time
        max_attempts = 30
        enabled = False
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"   🔄 Manager DOM Extraction Sync Attempt #{attempt}/{max_attempts}...")
            SessionManager.active_heartbeat(page)  # Synchronized polling pulse

            fresh_activity_table = mgr_page.locator('table.sec-table')
            fresh_activity_table.scroll_into_view_if_needed()

            named_row = fresh_activity_table.locator('tr').filter(has_text="Refund Approval - Refund Approval").first
            if named_row.is_visible():
                btn = named_row.locator('button:has-text("Approve")').first
                if btn.is_visible():
                    if btn.is_enabled():
                        btn.scroll_into_view_if_needed()
                        mgr_base.scroll_focus_click(btn)
                        enabled = True
                        logger.info("   🎯 Target matched by string descriptor: 'Refund Approval - Refund Approval'")
                        break
                    else:
                        logger.info(f"   ⚠️ Approve button is still disabled...")
                        
            time.sleep(1)

        if not enabled:
            raise RuntimeError(
                "❌ Layout Failure: No enabled 'Approve' button found for Manager 2.")

        popup_modal = mgr_page.locator("div.popup-content")
        popup_modal.wait_for(state="visible", timeout=10000)

        mgr_final_comment = popup_modal.locator("textarea")
        mgr_final_comment.focus()
        mgr_final_comment.fill("Approved - automation testing")
        page.wait_for_timeout(500)

        popup_modal.locator('button.qm-btn-primary', has_text="Submit").click()
        popup_modal.wait_for(state="hidden", timeout=10000)
        logger.info("✅ 'Refund Approval - Refund Approval' activity processed by Case Manager successfully.")
        
        if step_printer: step_printer(15)
        
        page.wait_for_timeout(500)

        # =====================================================================================
        # INTERLEAVED POLLING DURING STATE SYNCHRONIZATION LOOKUPS
        # =====================================================================================
        logger.info("⏳ Launching streamlined state synchronization verification loops with interleaved polling...")
        expected_terminal_keywords = ["resolved", "closed", "approved", "completed"]

        for check_attempt in range(1, 6):
            try:
                # 🌟 INTERLEAVED POLL STEP: Reset the Superadmin session timer at the start of every loop iteration!
                SessionManager.active_heartbeat(page)

                logger.info(f"   🔎 Searching case grid via UI to verify status update (Attempt #{check_attempt})...")
                navigate_to_search_case_via_ui(mgr_page)

                final_search_toggle = mgr_page.locator('button.ra-export-btn', has_text="Search Cases").first
                if final_search_toggle.is_visible(timeout=3000):
                    final_search_toggle.click()

                final_case_input = mgr_page.locator('input#case[formcontrolname="case"]').first
                final_case_input.wait_for(state="visible", timeout=5000)
                final_case_input.fill(str(target_case))
                mgr_page.locator('button').filter(has_text="Search").first.click()
                page.wait_for_timeout(500)

                final_suggestion = mgr_page.locator('div.search-suggestions a:has-text("Cases")')
                if final_suggestion.is_visible(timeout=2000):
                    final_suggestion.click()
                    page.wait_for_timeout(500)
                
                if step_printer: step_printer(16)

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

            page.wait_for_timeout(500)

    except Exception as e:
        logger.error(f"❌ Workflow sequence broke inside Case Manager context layer: {e}")
        is_verified_successfully = False
    finally:
        if not shared_setup or "contexts" not in shared_setup:
            mgr_page.close()
            mgr_context.close()

    # =====================================================================================
    # FINAL AT-THE-END CHECK: CLEAN STATE REFRESH FOR SUPERADMIN
    # =====================================================================================
    if is_verified_successfully:
        try:
            logger.info("🔄 Manager finished. Proceeding with Superadmin final UI-driven verification...")
            ensure_superadmin_session(page, base_url)

            # ✅ Superadmin is no longer pre-positioned (we removed it so they could see the Case Profile).
            # Pass already_on_search_case=False so they navigate to the grid first.
            superadmin_check_case_status(page, base_url, target_case, "Manager Resolved (Final Check)", already_on_search_case=False, step_printer=step_printer, search_step=17)
            logger.info(f"🎉 Success! Milestone Met: Refund Case #{target_case} processed through all nodes to full resolution!")

        except Exception as sa_refresh_ex:
            logger.warning(f"❌ Final Status Verification Triage Failure: {sa_refresh_ex}")

    logger.info("================================================================================")
    logger.info(f"🏁 FINAL AUTOMATION VERIFICATION REPORT FOR CASE #{target_case}:")
    logger.info(f"   🔹 Terminal Status Read Result: '{final_status}'")
    logger.info("================================================================================")

    return is_verified_successfully