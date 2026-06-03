import os
import random
import re
from playwright.sync_api import Page
from src.utils.logger import Logger
from src.utils.db_validator import verify_case_in_db, get_all_cases_from_db


class CaseManagementPage:
    def __init__(self, page: Page, report_dir: str = None):
        self.page = page
        self.logger = Logger.get_logger()
        self.focus_style = "outline: 4px solid rgba(0, 191, 255, 0.6); outline-offset: 2px; transition: all 0.3s ease;"

        self.report_dir = report_dir if report_dir else "reports/screenshots"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir, exist_ok=True)

    # --- Locators ---
    @property
    def workbench_icon(self):
        return self.page.locator("span.material-symbols-outlined", has_text="group").first

    @property
    def case_management_menu(self):
        return self.page.locator('a.nav-link:has-text("Case Management")')

    @property
    def create_case_link(self):
        return self.page.locator('a.nav-link[href="/operation-workbench/case-management/create-case"]')

    @property
    def existing_customer_yes_radio(self):
        return self.page.locator('input[formcontrolname="existingCustomer"][value="yes"]')

    @property
    def search_customer_link(self):
        return self.page.locator('a.text-primary:has-text("Search Customer")')

    @property
    def search_account_number_input(self):
        return self.page.locator('input#account[formcontrolname="account"]')

    @property
    def search_customer_button(self):
        return self.page.locator('button.ra-btn.ra-btn--primary:has-text("Search")')

    @property
    def search_results_table(self):
        return self.page.locator('div.search-container table.ra-table')

    @property
    def case_type_dropdown(self):
        return self.page.locator('select[formcontrolname="caseType"]')

    @property
    def case_subtype_dropdown(self):
        return self.page.locator('select[formcontrolname="caseSubType"]')

    @property
    def reason_code_dropdown(self):
        return self.page.locator('select[formcontrolname="reasonCode"]')

    @property
    def case_priority_dropdown(self):
        return self.page.locator('select[formcontrolname="casePriority"]')

    @property
    def description_textarea(self):
        return self.page.locator('textarea[formcontrolname="description"]')

    @property
    def comment_textarea(self):
        return self.page.locator('textarea[formcontrolname="comment"]')

    @property
    def submit_button(self):
        return self.page.locator('button[type="submit"].ra-btn--primary')

    @property
    def success_alert_case_id_link(self):
        return self.page.locator('p:has-text("Case created successfully") span.text-primary')

    @property
    def case_owner_dropdown(self):
        return self.page.locator('select#caseOwner')

    @property
    def case_view_save_button(self):
        return self.page.locator('button.qm-btn.qm-btn-primary:has-text("Save")')

    @property
    def modal_comments_textarea(self):
        return self.page.locator('div.popup-content textarea[placeholder="Comments..."]')

    @property
    def modal_submit_button(self):
        return self.page.locator('div.popup-content button.qm-btn-primary:has-text("Submit")')

    @property
    def case_management_submenu(self):
        return self.page.locator('a.nav-link:has-text("Case Management") + ul.submenu')

    @property
    def case_dashboard_link(self):
        return self.page.locator('a.nav-link[href="/operation-workbench/case-management/case-dashboard"]')

    @property
    def cases_tab(self):
        return self.page.locator('div.mat-mdc-tab', has_text="Cases").first

    @property
    def cases_summary_tab(self):
        return self.page.locator('div.mat-mdc-tab', has_text="Cases Summary")

    @property
    def filter_by_dropdown(self):
        return self.page.locator('select.cd-select').first

    @property
    def case_status_dropdown(self):
        return self.page.locator('select:has(option[value="Open"])')

    @property
    def dashboard_results_table(self):
        return self.page.locator('table.table').first

    @property
    def items_per_page_dropdown(self):
        return self.page.locator('label:has-text("Items per page:") + select')

    @property
    def pagination_container(self):
        return self.page.locator('ul.pagination')

    @property
    def table_body_rows(self):
        return self.dashboard_results_table.locator('tbody tr')

    @property
    def table_headers(self):
        return self.dashboard_results_table.locator('thead th')

    @property
    def no_records_found_message(self):
        return self.page.locator('text="No records found"')

    def apply_focus(self, locator, target_page=None):
        try:
            active_page = target_page if target_page else self.page
            if locator.count() > 0:
                locator.first.scroll_into_view_if_needed()
                locator.first.evaluate(f"node => node.style.cssText += '{self.focus_style}'")
                active_page.wait_for_timeout(150)
        except Exception:
            pass

    def hide_chatbot(self):
        try:
            self.page.add_style_tag(content="""
                .chatbot-icon, #chat-widget-container, app-chatbot, .quick-link-btn { 
                    display: none !important; visibility: hidden !important; 
                }
            """)
        except Exception:
            pass

    def capture_milestone(self, keyword, filename):
        try:
            self.page.locator(f"text={keyword}").last.wait_for(state="visible", timeout=15000)
            self.page.screenshot(path=f"{self.report_dir}/{filename}.png")
        except Exception:
            pass

    def navigate_to_create_case(self):
        self.logger.info("⏳ Navigating to Create Case...")
        self.hide_chatbot()
        self.apply_focus(self.workbench_icon)
        self.workbench_icon.click()
        self.apply_focus(self.case_management_menu)
        self.case_management_menu.click()
        self.apply_focus(self.create_case_link)
        self.create_case_link.click()
        self.page.wait_for_url("**/create-case", timeout=15000)

    def fill_case_details(self, account_number):
        self.logger.info(f"🔍 Selecting Customer: {account_number}")
        self.apply_focus(self.existing_customer_yes_radio)
        self.existing_customer_yes_radio.check()
        self.apply_focus(self.search_customer_link)
        self.search_customer_link.click()
        self.apply_focus(self.search_account_number_input)
        self.search_account_number_input.fill(account_number)
        self.apply_focus(self.search_customer_button)
        self.search_customer_button.click()

        target_row = self.search_results_table.locator("tr").filter(has_text=account_number).last
        select_btn = target_row.locator('button:has-text("Select")')
        self.apply_focus(select_btn)
        select_btn.click()
        self.page.wait_for_timeout(2000)

        self.apply_focus(self.case_type_dropdown)
        self.case_type_dropdown.select_option("Other")
        self.apply_focus(self.case_subtype_dropdown)
        self.case_subtype_dropdown.select_option("Other")
        self.apply_focus(self.reason_code_dropdown)
        self.reason_code_dropdown.select_option("generic case")

        options = self.case_priority_dropdown.locator("option:not([disabled])").all()
        valid_values = [opt.get_attribute("value") for opt in options if opt.get_attribute("value")]
        if valid_values:
            self.apply_focus(self.case_priority_dropdown)
            self.case_priority_dropdown.select_option(random.choice(valid_values))

        self.apply_focus(self.description_textarea)
        self.description_textarea.fill("Automation test case description.")
        self.apply_focus(self.comment_textarea)
        self.comment_textarea.fill("Automation test case comment.")

        self.apply_focus(self.submit_button)
        try:
            self.submit_button.click(timeout=5000)
        except Exception:
            self.page.evaluate("document.querySelector('button[type=\"submit\"]').click()")

        self.capture_milestone("Case created successfully", "09_case_created_success")

    def verify_case_and_assign(self, shared_data):
        self.success_alert_case_id_link.wait_for(state="visible", timeout=15000)
        case_id = self.success_alert_case_id_link.inner_text().strip()
        shared_data.case_id = case_id
        self.logger.info(f"💾 Captured Case Number: {case_id}")

        self.apply_focus(self.success_alert_case_id_link)
        self.success_alert_case_id_link.click()
        self.page.wait_for_url("**/view-case", timeout=15000)

        try:
            self.case_owner_dropdown.wait_for(state="visible", timeout=5000)
            current_owner_value = self.case_owner_dropdown.input_value()
            if current_owner_value == "casesorter01@yopmail.com":
                self.logger.info("ℹ️ Case is already assigned to casesorter01@yopmail.com. Skipping assignment steps.")
                return True
        except Exception:
            pass

        return self.assign_case_to_sorter()

    def assign_case_to_sorter(self):
        try:
            self.logger.info("👤 Reassigning case owner to: casesorter01@yopmail.com")
            self.case_owner_dropdown.wait_for(state="visible")
            self.apply_focus(self.case_owner_dropdown)
            self.case_owner_dropdown.select_option(value="casesorter01@yopmail.com")
            self.page.wait_for_timeout(500)

            self.apply_focus(self.case_view_save_button)
            self.case_view_save_button.click()

            self.modal_comments_textarea.wait_for(state="visible")
            self.apply_focus(self.modal_comments_textarea)
            self.modal_comments_textarea.fill("Assigning owner via automation.")
            self.page.wait_for_timeout(500)

            self.apply_focus(self.modal_submit_button)
            self.modal_submit_button.click()

            self.page.wait_for_load_state("networkidle")
            return True
        except Exception:
            return False

    def resolve_as_owner_context(self, browser, shared_data):
        """Executes full Sorter context tracking, approves 'Research Case', then checks active ownership details."""
        self.logger.info("🌐 Opening Case Sorter Context Layout...")

        new_context = browser.new_context(
            viewport={"width": 1600, "height": 850},
            ignore_https_errors=True
        )

        # 🎯 INSTANT ANCHOR 75% ZOOM FOR SORTER CONTEXT
        new_context.add_init_script("""() => {
            const style = document.createElement('style');
            style.innerHTML = 'body { zoom: 75% !important; }';
            document.head.appendChild(style);
        }""")

        new_page = new_context.new_page()

        try:
            base_url = self.page.url.split('/operation-workbench')[0]
            new_page.goto(f"{base_url}/login")

            email_field = new_page.locator('input[formcontrolname="emailId"]')
            self.apply_focus(email_field, new_page)
            email_field.fill("casesorter01@yopmail.com")

            pass_field = new_page.locator('input[formcontrolname="password"]')
            self.apply_focus(pass_field, new_page)
            pass_field.fill("Casesorter01@")

            login_btn = new_page.locator('button.auth-btn')
            self.apply_focus(login_btn, new_page)
            login_btn.click()

            new_page.wait_for_url("**/dashboard", timeout=25000)

            def search_and_open_case():
                new_page.goto(f"{base_url}/operation-workbench/case-management/search-case")
                search_bar = new_page.locator('input.search-input')
                search_bar.wait_for(state="visible", timeout=15000)

                self.logger.info(f"🔍 Searching for Case ID: {shared_data.case_id}")
                self.apply_focus(search_bar, new_page)
                search_bar.fill(shared_data.case_id)
                search_bar.press("Enter")
                new_page.wait_for_timeout(1500)

                search_bar.click()
                new_page.keyboard.press("Control+A")
                new_page.keyboard.press("Backspace")
                search_bar.fill(shared_data.case_id)
                search_bar.press("Enter")

                cases_suggestion = new_page.locator('div.search-suggestions a:has-text("Cases")')
                cases_suggestion.wait_for(state="visible", timeout=10000)
                self.apply_focus(cases_suggestion, new_page)
                cases_suggestion.click()

                target_row = new_page.locator("tr").filter(has_text=shared_data.case_id)
                eye_icon = target_row.locator('span:has-text("visibility")')
                eye_icon.wait_for(state="visible", timeout=10000)
                self.apply_focus(eye_icon, new_page)
                eye_icon.click()

                new_page.wait_for_load_state("networkidle")
                new_page.wait_for_timeout(2000)

            search_and_open_case()

            self.logger.info("⬇ McKay Interacting with the sequential Activity Table at the bottom...")
            activity_table = new_page.locator('table.sec-table')
            activity_table.scroll_into_view_if_needed()

            row_1 = activity_table.locator('tr').filter(has_text="Research Case")
            approve_btn_1 = row_1.locator('button:has-text("Approve")')
            approve_btn_1.wait_for(state="visible", timeout=15000)
            self.apply_focus(approve_btn_1, new_page)
            approve_btn_1.evaluate("node => node.click()")

            self.logger.info("💬 Intercepting 'Add Comments' overlay window...")
            popup_modal = new_page.locator("div.popup-content")
            popup_modal.wait_for(state="visible", timeout=10000)

            modal_textarea = popup_modal.locator("textarea")
            self.apply_focus(modal_textarea, new_page)
            modal_textarea.fill("Research case processed and submitted via QA automation suite verification.")
            new_page.wait_for_timeout(500)

            modal_submit = popup_modal.locator('button.qm-btn-primary', has_text="Submit")
            self.apply_focus(modal_submit, new_page)
            modal_submit.click()

            popup_modal.wait_for(state="hidden", timeout=10000)
            self.logger.info("✅ 'Research Case' Approved and comments confirmed successfully.")

            self.logger.info("🔄 Initiating secondary lookup loop to refresh case and check active ownership details...")
            search_and_open_case()

            try:
                owner_dropdown = new_page.locator('select#caseOwner')
                owner_dropdown.wait_for(state="visible", timeout=5000)
                current_owner = owner_dropdown.input_value()
                self.logger.info(f"👤 Verification Snapshot: Current Owner on Screen is: '{current_owner}'")
            except Exception:
                self.logger.warning("⚠️ Dynamic owner value snapshot could not be parsed.")

            return True
        except Exception as e:
            self.logger.error(f"❌ Workflow failed in Sorter context: {str(e)}")
            new_page.screenshot(path=f"{self.report_dir}/sorter_workflow_error.png")
            return False
        finally:
            new_page.close()
            new_context.close()

    def resolve_as_manager_context(self, browser, shared_data):
        """👑 FIX IMPLEMENTED: Logs in Case Manager using target credentials, verifies and updates case assignment, then approves."""
        target_manager_user = "boscasemanager2@yopmail.com"
        self.logger.info(f"👑 Opening Case Manager Window Context for account user: {target_manager_user}")

        mgr_context = browser.new_context(
            viewport={"width": 1600, "height": 850},
            ignore_https_errors=True
        )

        # 🎯 INSTANT ANCHOR 75% ZOOM FOR MANAGER CONTEXT
        mgr_context.add_init_script("""() => {
            const style = document.createElement('style');
            style.innerHTML = 'body { zoom: 75% !important; }';
            document.head.appendChild(style);
        }""")

        mgr_page = mgr_context.new_page()

        try:
            base_url = self.page.url.split('/operation-workbench')[0]
            mgr_page.goto(f"{base_url}/login")

            email_field = mgr_page.locator('input[formcontrolname="emailId"]')
            self.apply_focus(email_field, mgr_page)
            email_field.fill(target_manager_user)

            pass_field = mgr_page.locator('input[formcontrolname="password"]')
            self.apply_focus(pass_field, mgr_page)
            pass_field.fill("Boscasemanager2@")

            login_btn = mgr_page.locator('button.auth-btn')
            self.apply_focus(login_btn, mgr_page)
            login_btn.click()

            mgr_page.wait_for_url("**/dashboard", timeout=25000)

            # Search Case Subroutine
            mgr_page.goto(f"{base_url}/operation-workbench/case-management/search-case")
            search_bar = mgr_page.locator('input.search-input')
            search_bar.wait_for(state="visible", timeout=15000)

            self.logger.info(f"🔍 Manager Lookup executing on target Case ID: {shared_data.case_id}")
            self.apply_focus(search_bar, mgr_page)
            search_bar.fill(shared_data.case_id)
            search_bar.press("Enter")
            mgr_page.wait_for_timeout(1500)

            cases_suggestion = mgr_page.locator('div.search-suggestions a:has-text("Cases")')
            cases_suggestion.wait_for(state="visible", timeout=10000)
            cases_suggestion.click()

            target_row = mgr_page.locator("tr").filter(has_text=shared_data.case_id)
            eye_icon = target_row.locator('span:has-text("visibility")')
            eye_icon.wait_for(state="visible", timeout=10000)
            eye_icon.click()

            mgr_page.wait_for_load_state("networkidle")
            mgr_page.wait_for_timeout(2000)

            # 🛠️ NEW LOGIC COMPONENT: Dynamic Case Assignment Validation Checklist Rule Mapping
            owner_dropdown = mgr_page.locator('select#caseOwner')
            owner_dropdown.wait_for(state="visible", timeout=10000)
            current_owner = owner_dropdown.input_value()
            self.logger.info(f"👤 Pre-approval Inspection: Owner is currently set to: '{current_owner}'")

            if current_owner != target_manager_user:
                self.logger.info(f"📝 Reassigning node from '{current_owner}' to Case Manager: '{target_manager_user}'")
                self.apply_focus(owner_dropdown, mgr_page)
                owner_dropdown.select_option(value=target_manager_user)
                mgr_page.wait_for_timeout(500)

                save_btn = mgr_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")')
                self.apply_focus(save_btn, mgr_page)
                save_btn.click()

                popup_modal = mgr_page.locator("div.popup-content")
                popup_modal.wait_for(state="visible", timeout=10000)

                modal_textarea = popup_modal.locator("textarea[placeholder='Comments...']")
                self.apply_focus(modal_textarea, mgr_page)
                modal_textarea.fill("Reassigning case owner ownership to the active manager user context layer.")

                modal_submit = popup_modal.locator('button.qm-btn-primary:has-text("Submit")')
                self.apply_focus(modal_submit, mgr_page)
                modal_submit.click()

                popup_modal.wait_for(state="hidden", timeout=10000)
                mgr_page.wait_for_load_state("networkidle")
                self.logger.info("✅ Reassignment workflow fields saved safely.")

            # Interact with the 2nd Activity Row for approval
            self.logger.info("⬇️ Manager Interacting with the bottom sequential Activity Table...")
            activity_table = mgr_page.locator('table.sec-table')
            activity_table.scroll_into_view_if_needed()

            row_mgr = activity_table.locator('tr').filter(has_text="Closing case as approved")
            approve_btn_mgr = row_mgr.locator('button:has-text("Approve")')
            approve_btn_mgr.wait_for(state="visible", timeout=15000)
            self.apply_focus(approve_btn_mgr, mgr_page)
            approve_btn_mgr.evaluate("node => node.click()")

            # Review Comments Modal Entry
            popup_modal = mgr_page.locator("div.popup-content")
            popup_modal.wait_for(state="visible", timeout=10000)

            modal_textarea = popup_modal.locator("textarea")
            modal_textarea.fill(
                "Final operational resolution activity finalized by Case Manager automated suite script execution.")

            modal_submit = popup_modal.locator('button.qm-btn-primary', has_text="Submit")
            modal_submit.click()

            popup_modal.wait_for(state="hidden", timeout=10000)
            self.logger.info("✅ 'Closing case as approved' activity approved and logged by Case Manager successfully.")
            return True

        except Exception as e:
            self.logger.error(f"❌ Workflow failed in Case Manager context: {str(e)}")
            mgr_page.screenshot(path=f"{self.report_dir}/manager_workflow_error.png")
            return False
        finally:
            mgr_page.close()
            mgr_context.close()

    def navigate_to_case_dashboard(self):
        self.logger.info("⏳ Navigating to Case Dashboard...")
        if not self.case_management_menu.is_visible():
            self.apply_focus(self.workbench_icon)
            self.workbench_icon.click()
            self.page.wait_for_timeout(500)

        is_submenu_open = "show" in (self.case_management_submenu.get_attribute("class") or "")
        if not is_submenu_open:
            self.apply_focus(self.case_management_menu)
            self.case_management_menu.click()

        self.apply_focus(self.case_dashboard_link)
        self.case_dashboard_link.click()
        self.page.wait_for_url("**/case-dashboard", timeout=15000)
        self.page.wait_for_load_state("networkidle")
        self.logger.info("✅ Successfully reached Case Dashboard Page.")

    def navigate_to_cases_summary(self):
        self.logger.info("⏳ Switching view to Cases Summary tab...")
        self.cases_summary_tab.wait_for(state="visible", timeout=10000)
        self.apply_focus(self.cases_summary_tab)
        self.cases_summary_tab.click()
        self.page.wait_for_load_state("networkidle", timeout=10000)
        self.page.wait_for_timeout(1000)

    def get_case_statistics(self) -> dict:
        self.logger.info("📊 Processing grid record arrays for validation data mappings...")
        all_status_cases = {}

        try:
            if self.filter_by_dropdown.is_visible(timeout=2000):
                self.apply_focus(self.filter_by_dropdown)
                self.filter_by_dropdown.select_option("allCases")
                self.page.wait_for_timeout(1000)
        except Exception:
            pass

        status_options = self.case_status_dropdown.locator("option").all()
        valid_statuses = [opt.get_attribute("value") for opt in status_options if opt.get_attribute("value")]
        if not valid_statuses:
            valid_statuses = ["Open", "On Hold", "Escalated", "Pending Customer Feedback"]

        headers = [th.inner_text().strip() for th in self.table_headers.all()]
        headers = [re.sub(r'\s[▲▼]\s*$', '', h).strip() for h in headers]

        for status in valid_statuses:
            self.apply_focus(self.case_status_dropdown)
            try:
                self.case_status_dropdown.select_option(status)
            except Exception:
                self.case_status_dropdown.select_option(label=status)

            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(1000)

            if self.no_records_found_message.is_visible(timeout=1500):
                all_status_cases[status] = []
                self.logger.info(f"   ℹ️ Category [{status}]: 0 records found in UI.")
                continue

            cases_for_status = []
            while True:
                rows = self.table_body_rows.all()
                for row_el in rows:
                    cols = [td.inner_text().strip() for td in row_el.locator('td').all()]
                    if not cols or len(cols) < 2:
                        continue

                    case_number_button = row_el.locator('td:first-child button')
                    if case_number_button.count() > 0:
                        cols[0] = case_number_button.inner_text().strip()

                    case_detail = {headers[i]: cols[i] for i in range(len(cols)) if i < len(headers)}
                    cases_for_status.append(case_detail)

                next_btn = self.page.locator(
                    'button.pagination-next, ul.pagination li.next button, button:has(span:has-text("chevron_right"))').first

                if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                    self.apply_focus(next_btn)
                    next_btn.click()
                    self.page.wait_for_load_state("networkidle")
                    self.page.wait_for_timeout(500)
                else:
                    break

            all_status_cases[status] = cases_for_status
            self.logger.info(f"   ✅ Extracted {len(cases_for_status)} cases for status state: '{status}'")

        return all_status_cases

    def validate_summary_statistics(self, scraped_data: dict) -> list:
        self.logger.info("📊 Checking card widgets counts...")
        errors = []
        status_map = {
            "Open": "Open Cases",
            "On Hold": "On Hold Cases",
            "Escalated": "Escalated Cases",
            "Pending Customer Feedback": "Pending Customer Feedback Cases"
        }
        for status_key, widget_title in status_map.items():
            expected = len(scraped_data.get(status_key, []))
            try:
                card_locator = self.page.locator("div.cd-stat-card").filter(
                    has=self.page.locator(f"span.cd-stat-card__label:has-text('{widget_title}')"))
                actual = int(card_locator.locator("span.cd-stat-card__value").inner_text().strip())

                if actual == expected:
                    self.logger.info(f"   ✅ Card verified '{widget_title}': Metric [{actual}] matches perfectly.")
                else:
                    errors.append(
                        f"Card summary widget error '{widget_title}': UI stated {actual}, calculated expected data count {expected}")
            except Exception as ex:
                errors.append(
                    f"Failed to isolate text value node target for summary card widget '{widget_title}': {str(ex)}")
        return errors

    def _extract_grid_data(self, grid_header_text: str) -> list:
        grid_card = self.page.locator("div.cd-table-card").filter(
            has=self.page.locator(f"div.cd-table-card__header:has-text('{grid_header_text}')")
        ).first
        grid_card.scroll_into_view_if_needed(timeout=5000)
        headers = [th.inner_text().strip() for th in grid_card.locator("thead th").all()]
        rows_data = []
        rows = grid_card.locator("tbody tr").all()
        for row in rows:
            cells = [td.inner_text().strip() for td in row.locator("td").all()]
            if cells:
                rows_data.append({headers[i]: cells[i] for i in range(len(cells))})
        return rows_data

    def validate_owner_status_grid(self, scraped_data: dict) -> list:
        self.logger.info("📊 Validating 'Cases by Owner & Status' matrix distributions...")
        errors = []
        try:
            ui_grid = self._extract_grid_data("Cases by Owner & Status")
            expected_matrix = {}
            for status, cases in scraped_data.items():
                for c in cases:
                    owner = c.get("Case Owner", "Unassigned") or "Unassigned"
                    if owner not in expected_matrix:
                        expected_matrix[owner] = {"Escalated": 0, "On Hold": 0, "Open": 0,
                                                  "Pending Customer Feedback": 0}
                    if status in expected_matrix[owner]:
                        expected_matrix[owner][status] += 1

            for row in ui_grid:
                owner = row.get("Case Owner")
                if owner in expected_matrix:
                    for status_col in ["Escalated", "On Hold", "Open", "Pending Customer Feedback"]:
                        ui_val = int(row.get(status_col, 0))
                        exp_val = expected_matrix[owner].get(status_col, 0)
                        if ui_val != exp_val:
                            errors.append(
                                f"Grid item discrepancy for Owner [{owner}] Status [{status_col}]: UI holds {ui_val}, expected {exp_val}")
            if not errors:
                self.logger.info("   ✅ Matrix alignments check passed for 'Cases by Owner & Status' layout grid.")
        except Exception as ex:
            errors.append(f"Failed parsing validation arrays for Owner & Status matrix card layout: {str(ex)}")
        return errors

    def validate_case_type_grid(self, scraped_data: dict) -> list:
        self.logger.info("📊 Validating 'Count by Case Type' classifications...")
        errors = []
        try:
            card_container = self.page.locator("div.cd-table-card").filter(
                has=self.page.locator("div.cd-table-card__header:has-text('Count by Case Type')")
            ).first
            if card_container.count() > 0:
                card_container.scroll_into_view_if_needed(timeout=5000)
                self.page.wait_for_timeout(750)

            ui_grid = self._extract_grid_data("Count by Case Type")
            expected_counts = {}
            for status, cases in scraped_data.items():
                for c in cases:
                    c_type = c.get("Case Type", "").strip()
                    c_sub = c.get("Case Sub Type", "").strip()
                    combined_key = f"{c_type}-{c_sub}"
                    expected_counts[combined_key] = expected_counts.get(combined_key, 0) + 1

            for row in ui_grid:
                type_key = row.get("CaseType-SubType")
                ui_count = int(row.get("Count", 0))
                exp_count = expected_counts.get(type_key, 0)
                if ui_count != exp_count:
                    errors.append(
                        f"Grid item discrepancy for Type [{type_key}]: UI holds {ui_count}, expected {exp_count}")
            if not errors:
                self.logger.info("   ✅ Matrix alignments check passed for 'Count by Case Type' grid layout.")
        except Exception as ex:
            errors.append(f"Failed parsing validation arrays for Count by Case Type card layout: {str(ex)}")
        return errors

    def validate_owner_priority_grid(self, scraped_data: dict) -> list:
        self.logger.info("📊 Validating 'Cases by Owner & Priority' distributions...")
        errors = []
        try:
            card_container = self.page.locator("div.cd-table-card").filter(
                has=self.page.locator("div.cd-table-card__header:has-text('Cases by Owner & Priority')")
            ).first
            if card_container.count() > 0:
                card_container.scroll_into_view_if_needed(timeout=5000)
                self.page.wait_for_timeout(750)

            ui_grid = self._extract_grid_data("Cases by Owner & Priority")
            expected_matrix = {}
            for status, cases in scraped_data.items():
                for c in cases:
                    owner = c.get("Case Owner", "Unassigned") or "Unassigned"
                    priority = c.get("Priority", "Medium")
                    if owner not in expected_matrix:
                        expected_matrix[owner] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
                    if priority in expected_matrix[owner]:
                        expected_matrix[owner][priority] += 1

            for row in ui_grid:
                owner = row.get("Owner")
                if owner in expected_matrix:
                    for priority_col in ["Critical", "High", "Medium", "Low"]:
                        ui_val = int(row.get(priority_col, 0))
                        exp_val = expected_matrix[owner].get(priority_col, 0)
                        if ui_val != exp_val:
                            errors.append(
                                f"Grid item discrepancy for Owner [{owner}] Priority [{priority_col}]: UI holds {ui_val}, expected {exp_val}")
            if not errors:
                self.logger.info("   ✅ Matrix alignments check passed for 'Cases by Owner & Priority' layout grid.")
        except Exception as ex:
            errors.append(f"Failed parsing validation arrays for Owner & Priority matrix card layout: {str(ex)}")
        return errors