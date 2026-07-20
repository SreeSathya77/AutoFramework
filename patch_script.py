import sys

with open('src/pages/refund_case_resolution.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD SELF ASSIGNMENT TO EXECUTIVE 6 BEFORE LINE 206
insert_idx = content.find('logger.info("⬇️ Interacting with sequential Activity Table at bottom of layout...")')
if insert_idx == -1:
    print("Could not find insert_idx")
    sys.exit(1)

self_assign = """
        # SELF-ASSIGNMENT LOGIC FOR EXECUTIVE 6
        owner_dropdown_exec = exec_page.locator('select#caseOwner')
        owner_dropdown_exec.wait_for(state="visible", timeout=10000)
        owner_dropdown_exec.scroll_into_view_if_needed()
        current_owner_exec = owner_dropdown_exec.input_value()

        if current_owner_exec.strip().lower() != exec6_creds.get('email').strip().lower():
            logger.info(f"📝 Executive 6 self-assigning case: '{exec6_creds.get('email')}'")
            owner_dropdown_exec.select_option(value=exec6_creds.get('email'))
            exec_page.wait_for_timeout(800)

            save_btn_exec = exec_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")').last
            save_btn_exec.scroll_into_view_if_needed()
            save_btn_exec.click()
            exec_page.wait_for_timeout(2000)

            popup_modal_exec = exec_page.locator("div.popup-content")
            if popup_modal_exec.is_visible(timeout=5000):
                exec_txt = popup_modal_exec.locator("textarea")
                exec_txt.scroll_into_view_if_needed()
                exec_txt.fill("Executive claiming case for Research Case activity.")
                exec_page.wait_for_timeout(500)
                popup_modal_exec.locator('button.qm-btn-primary:has-text("Submit")').click()
                popup_modal_exec.wait_for(state="hidden", timeout=10000)

            exec_page.wait_for_load_state("networkidle")
            exec_page.wait_for_timeout(1500)
            logger.info("✅ Executive 6 self-assignment completed successfully.")
        
        """

content = content[:insert_idx] + self_assign + content[insert_idx:]

# 2. ADD POLLING FOR APPROVE BUTTON IN EXEC 6 (replaces lines 212-215 of original)
exec_approve_start = content.find("approve_btn = first_activity_row.locator('button:has-text(\"Approve\")')")
exec_approve_end = content.find("popup_modal = exec_page.locator(\"div.popup-content\")", exec_approve_start)

polling_exec = """
        logger.info("⏳ Waiting for Approve button to become enabled for Executive 6 (max 30s)...")
        import time
        max_attempts = 30
        enabled = False
        for attempt in range(1, max_attempts + 1):
            btn = first_activity_row.locator('button:has-text("Approve")').first
            if btn.is_visible():
                if btn.is_enabled():
                    btn.scroll_into_view_if_needed()
                    btn.focus()
                    btn.click()
                    enabled = True
                    break
                else:
                    logger.info(f"  Attempt {attempt}/{max_attempts}: Approve button still disabled, waiting...")
            time.sleep(1)
        
        if not enabled:
            # HTML Dump
            html_dump = activity_table.evaluate("el => el.outerHTML")
            with open("row_dump.html", "w", encoding="utf-8") as dump:
                dump.write(html_dump)
            raise Exception("Layout Failure: No enabled 'Approve' button found for Executive 6.")
        
        """
content = content[:exec_approve_start] + polling_exec + content[exec_approve_end:]


# 3. ADD POLLING FOR APPROVE BUTTON IN MANAGER 2
mgr_approve_start = content.find("approve_btn_mgr = row_2.locator('button:has-text(\"Approve\")')")
mgr_approve_end = content.find("popup_modal_mgr = mgr_page.locator(\"div.popup-content\")", mgr_approve_start)

polling_mgr = """
        logger.info("⏳ Waiting for Approve button to become enabled for Manager 2 (max 30s)...")
        max_attempts = 30
        enabled = False
        for attempt in range(1, max_attempts + 1):
            btn_mgr = row_2.locator('button:has-text("Approve")').first
            if btn_mgr.is_visible():
                if btn_mgr.is_enabled():
                    btn_mgr.scroll_into_view_if_needed()
                    btn_mgr.focus()
                    btn_mgr.click()
                    enabled = True
                    break
                else:
                    logger.info(f"  Attempt {attempt}/{max_attempts}: Approve button still disabled, waiting...")
            time.sleep(1)
            
        if not enabled:
            raise Exception("Layout Failure: No enabled 'Approve' button found for Manager 2.")
            
        """
content = content[:mgr_approve_start] + polling_mgr + content[mgr_approve_end:]


with open('src/pages/refund_case_resolution.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied")
