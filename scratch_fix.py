import sys

with open('src/pages/refund_case_resolution.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
start_marker = "    # TASK 1:"
start_idx = content.find(start_marker)
if start_idx != -1:
    start_idx = content.rfind('\n', 0, start_idx) - 4

end_marker = '        logger.info("⏬️ Interacting with sequential Activity Table at bottom of layout...")'
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find markers")
    sys.exit(1)

new_content = """    # =====================================================================================
    # TASK 1: LOGIN AS EXECUTIVE 6 AND SELF-ASSIGN CASE
    # =====================================================================================
    bp = BasePage(page)
    target_exec = LOGIN_CREDENTIALS.get("caseexecutive6", {}).get("email", "caseexecutive6@yopmail.com")
    
    try:
        # We start by opening the Executive 6 context directly, skipping Superadmin re-assignment
        logger.info(f"🌐 Spawning clean isolated Browser Context for Executive: {target_exec}")
        exec_context = browser.new_context(viewport={"width": 1600, "height": 850}, ignore_https_errors=True)
        exec_context.add_init_script("() => { document.body.style.zoom = '75%'; }")
        exec_page = exec_context.new_page()

        bp_exec = BasePage(exec_page)
        
        logger.info(f"🔑 Logging into operation workbench as: {target_exec}")
        base_url = page.url.split('/operation-workbench')[0]
        exec_page.goto(f"{base_url}/login")

        ex_email = exec_page.locator('input[formcontrolname="emailId"]')
        bp_exec.scroll_focus_fill(ex_email, exec6_creds.get("email"))
        
        ex_pass = exec_page.locator('input[formcontrolname="password"]')
        bp_exec.scroll_focus_fill(ex_pass, exec6_creds.get("password"))
        
        exec_page.wait_for_timeout(400)
        bp_exec.scroll_focus_click(exec_page.locator('button.auth-btn'))
        
        exec_page.wait_for_url("**/dashboard", timeout=20000)
        exec_page.wait_for_load_state("networkidle")

        logger.info(f"🔍 Executing Case Lookup query routing for: {target_case}")
        from src.pages.base_page import BasePage
        # Just use the global navigate_and_search_case
        navigate_and_search_case(exec_page, target_case)
        exec_page.wait_for_load_state("networkidle")

        target_row = exec_page.locator("tbody tr").filter(has_text=str(target_case)).first
        target_row.wait_for(state="visible", timeout=10000)
        target_row.scroll_into_view_if_needed()

        view_btn = target_row.locator('span:has-text("visibility")').first
        bp_exec.scroll_focus_click(view_btn)

        exec_page.wait_for_url("**/view-case", timeout=15000)
        exec_page.wait_for_load_state("networkidle")

        # SELF-ASSIGNMENT LOGIC
        owner_dropdown_exec = exec_page.locator('select#caseOwner')
        owner_dropdown_exec.wait_for(state="visible", timeout=10000)
        owner_dropdown_exec.scroll_into_view_if_needed()
        current_owner_exec = owner_dropdown_exec.input_value()

        if current_owner_exec.strip().lower() != target_exec.strip().lower():
            logger.info(f"📝 Executive 6 self-assigning case: '{target_exec}'")
            bp_exec.scroll_focus_select(owner_dropdown_exec, value=target_exec)
            exec_page.wait_for_timeout(800)

            save_btn_exec = exec_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")').last
            bp_exec.scroll_focus_click(save_btn_exec)

            popup_modal_exec = exec_page.locator("div.popup-content")
            if popup_modal_exec.is_visible(timeout=5000):
                exec_txt = popup_modal_exec.locator("textarea")
                bp_exec.scroll_focus_fill(exec_txt, "Executive claiming case for Research Case activity.")
                exec_page.wait_for_timeout(500)

                bp_exec.scroll_focus_click(popup_modal_exec.locator('button.qm-btn-primary:has-text("Submit")'))
                popup_modal_exec.wait_for(state="hidden", timeout=10000)

            exec_page.wait_for_load_state("networkidle")
            exec_page.wait_for_timeout(1500)
            logger.info("✅ Executive 6 self-assignment completed successfully.")
\n"""

with open('src/pages/refund_case_resolution.py', 'w', encoding='utf-8') as f:
    f.write(content[:start_idx] + new_content + content[end_idx:])
print("Successfully patched file")
