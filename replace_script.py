import sys

target_file = r"D:\QA_QM_BOS_REG - Copy\src\pages\transfer_tag_case_resolution.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

target_content = '''    # 3. SUPERADMIN SEARCHES, ASSIGNS TO BCM
    logger.info("?? SA on Case Details: Assigning case to BCM...")
    try:
        superadmin_check_case_status(page, base_url, target_case, "Pending Approval", already_on_search_case=False, step_printer=None)
    except Exception as sa_ex:
        logger.warning(f"?? SA refresh prior to BCM assignment failed: {sa_ex}")

    try:
        bcm_email = mgr_creds.get('email', 'boscasemanager2@yopmail.com')
        owner_dropdown = page.locator("select#caseOwner")
        owner_dropdown.wait_for(state="visible", timeout=10000)
        owner_dropdown.scroll_into_view_if_needed()
        current_owner = owner_dropdown.input_value()
        
        if current_owner.strip().lower() != bcm_email.strip().lower():
            logger.info(f"?? Superadmin changing owner from '{current_owner}' to '{bcm_email}'...")
            owner_dropdown.select_option(value=bcm_email)
            page.wait_for_timeout(500)
            
            # Click Save (Triggers the Add Comments modal)
            save_btn = page.locator('button.qm-btn.qm-btn-primary').filter(has_text="Save").first
            base.scroll_focus_click(save_btn)
            
            # Handle the Add Comments modal
            modal_comment = page.locator("div.popup-content textarea, div.modal-content textarea, textarea[placeholder='Comments...']")
            modal_comment.first.wait_for(state="visible", timeout=10000)
            base.scroll_focus_fill(modal_comment.first, "Assigning to BCM for final approval")
            
            submit_btn = page.locator("div.popup-content button, div.modal-content button, button.btn-primary, button.qm-btn").filter(has_text="Submit").first
            base.scroll_focus_click(submit_btn)
            
            # Wait for the modal to completely disappear
            modal_comment.first.wait_for(state="hidden", timeout=15000)
            logger.info("? Superadmin successfully reassigned case to BCM.")
            if step_printer: step_printer(11)
        else:
            logger.info("? Case is already assigned to target BCM.")
            if step_printer: step_printer(11)
            
        page.wait_for_timeout(2000)
        
        # Wait for potential spinners
        try:
            page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=15000)
        except Exception:
            pass
            
        page.wait_for_timeout(2000)
        
        superadmin_check_case_status(page, base_url, target_case, "Transfer Tag Case Assigned to BCM", already_on_search_case=False)
        
    except Exception as ex:
        logger.warning(f"?? SA assign to BCM failed: {ex}")
        return False
        
    # 4. BCM CONTEXT APPROVES ACTIVITY 2
    mgr_cache = shared_setup.setdefault("contexts", {}) if shared_setup else {}
    mgr_email = mgr_creds.get("email")
    if mgr_email in mgr_cache:
        logger.info(f"?? Reusing existing browser context for Manager: {mgr_email}")
        mgr_context, mgr_page, mgr_base = mgr_cache[mgr_email]
        is_mgr_new = False
    else:
        logger.info(f"?? Spawning clean isolated Browser Context for BCM: {mgr_email}")
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
            
            # Handle possible "Session active in another machine" modal that pops up asynchronously after login
            try:
                mgr_page.wait_for_timeout(6000)
                logger.info("?? Checking for active session modal...")
                session_modal = mgr_page.locator(".cdk-overlay-pane, .modal-dialog, .popup-content, .mat-dialog-container, .modal-content, [role='dialog']").filter(has_text=re.compile(r"Session|Machine|Invalidate", re.IGNORECASE)).first
                if session_modal.is_visible(timeout=3000):
                    logger.info(f"?? Detected active session modal! Text: {session_modal.inner_text()}")
                    ok_btn = session_modal.locator("button").filter(has_text=re.compile(r"^(OK|Yes|Continue|Invalidate|Confirm)$", re.IGNORECASE)).first
                    if ok_btn.is_visible():
                        logger.info("?? Clicking confirmation button on modal to clear it...")
                        mgr_base.scroll_focus_click(ok_btn)
                        mgr_page.wait_for_timeout(2000)
            except Exception as e:
                logger.warning(f"?? Modal check exception (safe to ignore): {e}")
        
        # SEARCH CASE
        navigate_to_search_case_via_ui(mgr_page)
        
        search_cases_toggle = mgr_page.locator('button.ra-export-btn', has_text="Search Cases").first
        mgr_base.scroll_focus_click(search_cases_toggle)
        case_number_input = mgr_page.locator('input#case[formcontrolname="case"]').first
        case_number_input.wait_for(state="visible", timeout=5000)
        mgr_base.scroll_focus_fill(case_number_input, str(target_case))
        search_btn = mgr_page.locator('button').filter(has_text="Search").first
        mgr_base.scroll_focus_click(search_btn)
        mgr_page.wait_for_timeout(2000)
        
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
        
        # Try to find "Approve" or "Transfer Tag" buttons inside the grid
        approve_btn_direct = mgr_page.get_by_role("button", name=re.compile(r"^(Approve|Transfer Tag)$", re.IGNORECASE)).first
        
        logger.info("? Waiting for 'Approve' or 'Transfer Tag' button to appear in Activities grid for BCM (up to 30s)...")
        approve_btn_direct.wait_for(state="attached", timeout=30000)
        
        logger.info("?? Found direct 'Approve' or 'Transfer Tag' button on Activities grid for BCM. Clicking it...")
        mgr_base.scroll_focus_click(approve_btn_direct)
        mgr_page.wait_for_timeout(2000)
        
        comment_input = mgr_page.locator('textarea[formcontrolname="comments"]')
        if comment_input.count() > 0 and comment_input.first.is_visible(timeout=2000):
            mgr_base.scroll_focus_fill(comment_input.first, "BCM Approved Transfer Tag")
            update_btn = mgr_page.locator('button').filter(has_text="Update").first
            if update_btn.is_visible():
                mgr_base.scroll_focus_click(update_btn)
                mgr_page.wait_for_timeout(2000)
        else:
            confirm_btn = mgr_page.locator('button').filter(has_text=re.compile(r"^(Yes|OK|Confirm|Approve)$", re.IGNORECASE)).last
            if confirm_btn.is_visible(timeout=3000):
                mgr_base.scroll_focus_click(confirm_btn)
                mgr_page.wait_for_timeout(2000)
        
    except Exception as ex:
        logger.error(f"? BCM Context failed: {ex}")
        return False
    finally:
        if not shared_setup or "contexts" not in shared_setup:
            mgr_page.close()
            mgr_context.close()'''

replacement_content = '''    # 3. SUPERADMIN REASSIGNS BACK TO EXECUTIVE 6 FOR SECOND ACTIVITY
    logger.info("?? SA on Case Details: Reassigning case back to Executive 6 for second activity...")
    try:
        superadmin_check_case_status(page, base_url, target_case, "Pending Second Activity", already_on_search_case=False, step_printer=None)
    except Exception as sa_ex:
        logger.warning(f"?? SA refresh prior to reassignment failed: {sa_ex}")

    try:
        executive_email = exec6_creds.get('email', 'caseexecutive6@yopmail.com')
        owner_dropdown = page.locator("select#caseOwner")
        owner_dropdown.wait_for(state="visible", timeout=10000)
        owner_dropdown.scroll_into_view_if_needed()
        current_owner = owner_dropdown.input_value()
        
        if current_owner.strip().lower() != executive_email.strip().lower():
            logger.info(f"?? Superadmin changing owner from '{current_owner}' back to '{executive_email}'...")
            owner_dropdown.select_option(value=executive_email)
            page.wait_for_timeout(500)
            
            # Click Save (Triggers the Add Comments modal)
            save_btn = page.locator('button.qm-btn.qm-btn-primary').filter(has_text="Save").first
            base.scroll_focus_click(save_btn)
            
            # Handle the Add Comments modal
            modal_comment = page.locator("div.popup-content textarea, div.modal-content textarea, textarea[placeholder='Comments...']")
            modal_comment.first.wait_for(state="visible", timeout=10000)
            base.scroll_focus_fill(modal_comment.first, "Reassigning back to Executive 6 for Transfer Tag activity")
            
            submit_btn = page.locator("div.popup-content button, div.modal-content button, button.btn-primary, button.qm-btn").filter(has_text="Submit").first
            base.scroll_focus_click(submit_btn)
            
            # Wait for the modal to completely disappear
            modal_comment.first.wait_for(state="hidden", timeout=15000)
            logger.info("? Superadmin successfully reassigned case back to Executive 6.")
            if step_printer: step_printer(11)
        else:
            logger.info("? Case is already assigned to target Executive 6.")
            if step_printer: step_printer(11)
            
        page.wait_for_timeout(2000)
        
        # Wait for potential spinners
        try:
            page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=15000)
        except Exception:
            pass
            
        page.wait_for_timeout(2000)
        
        superadmin_check_case_status(page, base_url, target_case, "Ready for Second Activity", already_on_search_case=False)
        
    except Exception as ex:
        logger.warning(f"?? SA reassign to Exec 6 failed: {ex}")
        return False
        
    # 4. EXECUTIVE CONTEXT APPROVES ACTIVITY 2 (TRANSFER TAG)
    try:
        # Re-use the existing Executive 6 context
        if not is_exec_new:
            # We already have the exec_page open from earlier. Let's refresh or re-search the case.
            logger.info("?? Refreshing Case inside Executive 6 context...")
            exec_page.reload()
            exec_page.wait_for_load_state("load")
            exec_page.wait_for_timeout(5000)
        
        # Ensure we are on the activities tab
        activities_tab = exec_page.get_by_role("tab", name="Activities")
        exec_base.scroll_focus_click(activities_tab)
        exec_page.wait_for_timeout(1000)
        
        # Try to find "Transfer Tag" button (which is the second button)
        logger.info("? Waiting for 'Transfer Tag' button to appear in Activities grid for Exec 6...")
        table = exec_page.locator('table.sec-table')
        transfer_btn = table.locator('tr').filter(has_text="Transfer Tag - Transfer Tag").locator('button', has_text="Transfer Tag")
        transfer_btn.first.wait_for(state="attached", timeout=30000)
        
        logger.info("?? Found 'Transfer Tag' button on Activities grid. Clicking it...")
        exec_base.scroll_focus_click(transfer_btn.first)
        exec_page.wait_for_timeout(2000)
        
        comment_input = exec_page.locator('div.popup-content textarea, div.modal-content textarea, textarea[placeholder="Comments..."]')
        if comment_input.count() > 0 and comment_input.first.is_visible(timeout=2000):
            exec_base.scroll_focus_fill(comment_input.first, "Executive Approved Transfer Tag activity")
            update_btn = exec_page.locator('div.popup-content button, div.modal-content button').filter(has_text=re.compile(r"^(Submit|Update)$", re.IGNORECASE)).first
            if update_btn.is_visible():
                exec_base.scroll_focus_click(update_btn)
                exec_page.wait_for_timeout(2000)
        else:
            confirm_btn = exec_page.locator('button').filter(has_text=re.compile(r"^(Yes|OK|Confirm|Approve|Submit)$", re.IGNORECASE)).last
            if confirm_btn.is_visible(timeout=3000):
                exec_base.scroll_focus_click(confirm_btn)
                exec_page.wait_for_timeout(2000)
        
        logger.info("? Executive 6 successfully processed Transfer Tag activity. Case should now be Resolved.")
        
    except Exception as ex:
        logger.error(f"? Exec 6 Context failed on second activity: {ex}")
        return False
    finally:
        # Keep Exec context open if shared_setup is used, exactly as requested by user
        if not shared_setup or "contexts" not in shared_setup:
            exec_page.close()
            exec_context.close()'''

if target_content in content:
    new_content = content.replace(target_content, replacement_content)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("REPLACEMENT SUCCESSFUL")
else:
    print("TARGET CONTENT NOT FOUND")
