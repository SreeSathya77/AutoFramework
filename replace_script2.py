import sys

target_file = r"D:\QA_QM_BOS_REG - Copy\src\pages\transfer_tag_case_resolution.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "    # 3. SUPERADMIN SEARCHES, ASSIGNS TO BCM"
end_marker = "    # 5. SUPERADMIN VERIFIES FINAL CASE RESOLUTION"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
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
            exec_context.close()
            
'''
    new_content = content[:start_idx] + replacement_content + content[end_idx:]
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("REPLACEMENT SUCCESSFUL")
else:
    print("MARKERS NOT FOUND")
