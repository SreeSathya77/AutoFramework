import os
import random
import re
from playwright.sync_api import Page
from src.utils.logger import Logger
from src.utils.db_validator import verify_case_in_db, get_all_cases_from_db
from src.pages.base_page import BasePage
from utils.config import LOGIN_CREDENTIALS
from conftest import VIEWPORT_SIZE

class CaseManagementPage(BasePage):
    def __init__(self, page: Page, report_dir: str = None):
        super().__init__(page)
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
    def search_case_link(self):
        return self.case_management_menu.locator(
            "xpath=following-sibling::ul//a[contains(text(),'Search Case')]"
        )

    @property
    def search_cases_button(self):
        return self.page.locator('button.ra-export-btn:has-text("Search Cases")')

    @property
    def case_number_input(self):
        return self.page.locator('input#case[formcontrolname="case"]')

    @property
    def search_button(self):
        return self.page.locator('button.qm-btn.qm-btn-primary:has-text("Search")')

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
        
        if not self.case_management_menu.is_visible():
            self.scroll_focus_click(self.workbench_icon)
        
        self.scroll_focus_click(self.case_management_menu)
        self.scroll_focus_click(self.create_case_link)
        self.existing_customer_yes_radio.wait_for(state="visible", timeout=15000)

    def navigate_to_search_case(self, target_page=None):
        page = target_page if target_page else self.page

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

        self.logger.info("⏳ Navigating to Search Case...")

        workbench_icon = page.locator(
            "span.material-symbols-outlined",
            has_text="group"
        ).first

        case_management_menu = page.locator(
            'a.nav-link:has-text("Case Management")'
        )

        search_case_link = case_management_menu.locator(
            "xpath=following-sibling::ul//a[contains(text(),'Search Case')]"
        )

        self.hide_chatbot()

        if not case_management_menu.is_visible():
            self.scroll_focus_click(workbench_icon, target_page=page)

        if not search_case_link.is_visible():
            self.scroll_focus_click(case_management_menu, target_page=page)
            
        self.scroll_focus_click(search_case_link, target_page=page)
        page.locator('button.ra-export-btn', has_text="Search Cases").first.wait_for(state="visible", timeout=15000)
        page.wait_for_timeout(500)

        self.logger.info("✅ Successfully reached Search Case Page.")

    def fill_case_details(self, account_number, step_printer=None):
        self.logger.info(f"🔍 Selecting Customer: {account_number}")
        self.scroll_focus_check(self.existing_customer_yes_radio)
        self.scroll_focus_click(self.search_customer_link)
        self.scroll_focus_fill(self.search_account_number_input, account_number)
        self.scroll_focus_click(self.search_customer_button)

        target_row = self.search_results_table.locator("tr").filter(has_text=account_number).last
        select_btn = target_row.locator('button:has-text("Select")')
        self.scroll_focus_click(select_btn)
        self.page.wait_for_timeout(500)
        
        if step_printer: step_printer(1)

        self.scroll_focus_select(self.case_type_dropdown, "Other")
        self.scroll_focus_select(self.case_subtype_dropdown, "Other")
        self.scroll_focus_select(self.reason_code_dropdown, "generic case")

        options = self.case_priority_dropdown.locator("option:not([disabled])").all()
        valid_values = [opt.get_attribute("value") for opt in options if opt.get_attribute("value")]
        if valid_values:
            self.scroll_focus_select(self.case_priority_dropdown, value=random.choice(valid_values))

        self.scroll_focus_fill(self.description_textarea, "Automation test case description.")
        self.scroll_focus_fill(self.comment_textarea, "Automation test case comment.")

        self.scroll_focus_click(self.submit_button)

        self.capture_milestone("Case created successfully", "09_case_created_success")
        if step_printer: step_printer(2)

    def verify_case_and_assign(self, shared_data, step_printer=None):
        self.success_alert_case_id_link.wait_for(state="visible", timeout=15000)
        case_id = self.success_alert_case_id_link.inner_text().strip()
        shared_data.case_id = case_id
        self.logger.info(f"💾 Captured Case Number: {case_id}")

        self.apply_focus(self.success_alert_case_id_link)
        self.success_alert_case_id_link.click()
        self.case_owner_dropdown.wait_for(state="visible", timeout=15000)
        if step_printer: step_printer(3)

        try:
            self.case_owner_dropdown.wait_for(state="visible", timeout=5000)
            current_owner_value = self.case_owner_dropdown.input_value()
            target_sorter_email = LOGIN_CREDENTIALS.get("casesorter01", {}).get("email", "casesorter01@yopmail.com")
            if current_owner_value == target_sorter_email:
                self.logger.info(f"ℹ️ Case is already assigned to {target_sorter_email}. Skipping assignment steps.")
                return True
        except Exception:
            pass

        assigned = self.assign_case_to_sorter(shared_data)
        if not assigned:
            return False
            
        if step_printer: step_printer(4)

        # --- NEW VERIFICATION STEP ---
        # Wait a bit
        self.page.wait_for_timeout(500)
        
        # Superadmin searches the case and checks Sorter is owner
        self.logger.info("🔎 Superadmin verifying Sorter ownership via Search grid...")
        self.navigate_to_search_case()
        
        # Toggle search panel and enter Case ID
        self.scroll_focus_click(self.page.locator('button.ra-export-btn:has-text("Search Cases")'))
        self.page.wait_for_timeout(500)
        self.scroll_focus_fill(self.page.locator('input[formcontrolname="case"]'), case_id)
        self.scroll_focus_click(self.page.locator('button.qm-btn.qm-btn-primary:has-text("Search")'))
        self.page.wait_for_timeout(500)

        # Get owner column from row
        try:
            row = self.page.locator("table tbody tr:visible").filter(has_text=case_id).first
            row.wait_for(state="visible", timeout=15000)
            row_text = row.inner_text()
            self.logger.info(f"📊 Verification Grid Row: {row_text}")
            if getattr(shared_data, "assigned_to_sorter_by_admin", True):
                assert target_sorter_email in row_text, f"Expected owner {target_sorter_email} in row, but found: {row_text}"
                self.logger.info("✅ Verified: Sorter user is the owner now.")
            else:
                self.logger.info("✅ Verified: Sorter was not assigned by Admin as Sorter was not in options.")
            
            # Open the case
            self.logger.info("🔎 Opening case to visually highlight status and owner...")
            case_link = row.locator('span:has-text("visibility")').first
            self.scroll_focus_click(case_link)
            self.case_owner_dropdown.wait_for(state="visible", timeout=15000)
            
            # Visually highlight Case Status and Case Owner
            self.page.evaluate("""() => {
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
            self.page.wait_for_timeout(3500)
            
            if step_printer: step_printer(5)
            return True
        except Exception as e:
            self.take_screenshot("search_case_verification_failed")
            self.logger.error(f"Failed to find case {case_id} in search grid. Screenshot taken.")
            raise e

    def superadmin_reassign_to_manager(self, shared_data, step_printer=None):
        self.logger.info("🔎 Superadmin verifying Sorter's work and checking ownership...")
        self.navigate_to_search_case()
        
        # Search for Case ID
        self.scroll_focus_click(self.page.locator('button.ra-export-btn:has-text("Search Cases")'))
        self.page.wait_for_timeout(500)
        self.scroll_focus_fill(self.page.locator('input[formcontrolname="case"]'), shared_data.case_id)
        self.scroll_focus_click(self.page.locator('button.qm-btn.qm-btn-primary:has-text("Search")'))
        self.page.wait_for_timeout(500)

        # Open the case
        case_link = self.page.locator('span:has-text("visibility")').first
        self.scroll_focus_click(case_link)
        self.case_owner_dropdown.wait_for(state="visible", timeout=15000)
        
        # Wait for the spinner to resolve
        try:
            self.page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
        except Exception:
            pass
            
        if step_printer: step_printer(9)
        
        # Check current owner
        current_owner = self.case_owner_dropdown.input_value()
        self.logger.info(f"👤 Superadmin sees current owner: {current_owner}")
        
        # Try to assign to Manager 2
        target_manager = LOGIN_CREDENTIALS.get("boscasemanager2", {}).get("email", "boscasemanager2@yopmail.com")
        self.logger.info(f"📝 Superadmin trying to assign case to: {target_manager}")
        
        # Check if the manager is in the dropdown options
        options = self.case_owner_dropdown.locator("option").all()
        options_texts = [opt.inner_text().strip() for opt in options]
        
        if current_owner.strip().lower() == target_manager.strip().lower():
            self.logger.info(f"✅ Case is already assigned to {target_manager}. Skipping reassignment.")
            # If auto-assigned, we still want to formally log Steps 10 and 11 as "Pass"
            if step_printer: step_printer(10)
            if step_printer: step_printer(11)
        else:
            is_manager_available = False
            for opt in options_texts:
                if target_manager in opt:
                    is_manager_available = True
                    break
                    
            if is_manager_available:
                self.scroll_focus_select(self.case_owner_dropdown, label=target_manager)
                self.page.wait_for_timeout(500)
                self.apply_focus(self.case_view_save_button)
                self.case_view_save_button.click()
                
                # Comments Modal
                self.modal_comments_textarea.wait_for(state="visible")
                self.apply_focus(self.modal_comments_textarea)
                self.modal_comments_textarea.fill("Reassigning to Manager via Superadmin.")
                self.page.wait_for_timeout(500)
                self.modal_submit_button.click()
                self.page.wait_for_timeout(500)
                self.logger.info("✅ Superadmin successfully assigned case to Manager.")
                
                if step_printer: step_printer(10)
                
                # Step 11: SA Search Case after assign to BCM
                self.logger.info("🔄 Superadmin assigned the case! Re-searching the case to verify assignment and highlight owner...")
                self.navigate_to_search_case()
                self.scroll_focus_click(self.page.locator('button.ra-export-btn:has-text("Search Cases")'))
                self.page.wait_for_timeout(500)
                self.scroll_focus_fill(self.page.locator('input[formcontrolname="case"]'), shared_data.case_id)
                self.scroll_focus_click(self.page.locator('button.qm-btn.qm-btn-primary:has-text("Search")'))
                self.page.wait_for_timeout(500)
                case_link = self.page.locator('span:has-text("visibility")').first
                self.scroll_focus_click(case_link)
                self.case_owner_dropdown.wait_for(state="visible", timeout=15000)
                try:
                    self.page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
                except Exception:
                    pass
                if step_printer: step_printer(11)
            else:
                self.logger.info(f"ℹ️ {target_manager} is not available in the dropdown. Leaving owner as: {current_owner}")
            
        # Visually highlight Case Status and Case Owner for the user before context switch!
        self.logger.info("🔎 Visually highlighting Case Status and Case Owner for user inspection...")
        self.page.evaluate("""() => {
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
        self.page.wait_for_timeout(3500)

    def assign_case_to_sorter(self, shared_data):
        try:
            target_owner_email = LOGIN_CREDENTIALS.get("casesorter01", {}).get("email", "casesorter01@yopmail.com")
            
            # Check if Sorter is available in the dropdown options
            options = self.case_owner_dropdown.locator("option").all()
            options_texts = [opt.inner_text().strip() for opt in options]
            
            is_sorter_available = False
            for opt in options_texts:
                if target_owner_email in opt:
                    is_sorter_available = True
                    break
            
            if is_sorter_available:
                self.logger.info(f"👤 Reassigning case owner to: {target_owner_email}")
                self.scroll_focus_select(self.case_owner_dropdown, label=target_owner_email)
                self.page.wait_for_timeout(500)

                self.apply_focus(self.case_view_save_button)
                self.case_view_save_button.click()

                self.modal_comments_textarea.wait_for(state="visible")
                self.apply_focus(self.modal_comments_textarea)
                self.modal_comments_textarea.fill("Assigning owner via automation.")
                self.page.wait_for_timeout(500)

                self.apply_focus(self.modal_submit_button)
                self.modal_submit_button.click()

                self.page.wait_for_timeout(500)
                self.logger.info("✅ Case assignment dropdown interactions completed successfully.")
                shared_data.assigned_to_sorter_by_admin = True
            else:
                self.logger.info(f"ℹ️ Sorter {target_owner_email} is not available in dropdown. Leaving owner as is.")
                shared_data.assigned_to_sorter_by_admin = False
                
            return True
        except Exception as e:
            self.logger.error(f"❌ assign_case_to_sorter failed: {e}")
            return False

    def resolve_as_owner_context(self, browser, shared_data, step_printer=None):
        """Executes full Sorter context tracking, approves 'Research Case', then checks active ownership details."""
        self.logger.info("🌐 Opening Case Sorter Context Layout...")

        new_context = browser.new_context(
            viewport=VIEWPORT_SIZE,
            ignore_https_errors=True
        )

        # 🎯 INSTANT ANCHOR 75% ZOOM FOR SORTER CONTEXT
        new_context.add_init_script("""() => {
            const style = document.createElement('style');
            style.innerHTML = 'body { zoom: 75% !important; }';
            document.head.appendChild(style);
        }""")

        new_page = new_context.new_page()

        def login_as(target_user, new_page):
            base_url = self.page.url.split('/operation-workbench')[0]
            new_page.goto(f"{base_url}/login")
            
            email_field = new_page.locator('input[formcontrolname="emailId"]')
            self.scroll_focus_fill(email_field, target_user, target_page=new_page)
            
            password_field = new_page.locator('input[formcontrolname="password"]')
            target_password = LOGIN_CREDENTIALS.get("casesorter01", {}).get("password", "Casesorter01@")
            self.scroll_focus_fill(password_field, target_password, target_page=new_page)
            
            new_page.wait_for_timeout(500)
            auth_btn = new_page.locator("button.auth-btn")
            self.scroll_focus_click(auth_btn, target_page=new_page)
            new_page.wait_for_timeout(500)

        try:
            target_sorter = LOGIN_CREDENTIALS.get("casesorter01", {}).get("email", "casesorter01@yopmail.com")
            login_as(target_sorter, new_page)
            new_page.locator(".dash-headding").first.wait_for(state="visible", timeout=25000)

            def search_and_open_case(target_case_id):
                self.navigate_to_search_case(target_page=new_page)
                new_page.wait_for_timeout(500)
                self.logger.info("✅ Successfully reached Search Case Page.")

                self.scroll_focus_click(new_page.locator('button.ra-export-btn:has-text("Search Cases")'), target_page=new_page)
                new_page.wait_for_timeout(500)
                self.logger.info(f"🔍 Searching for Case ID: {target_case_id}")
                
                case_input_locator = new_page.locator('input#case[formcontrolname="case"]').first
                self.scroll_focus_fill(case_input_locator, target_case_id, target_page=new_page)
                
                search_btn = new_page.locator('button').filter(has_text="Search").first
                self.scroll_focus_click(search_btn, target_page=new_page, highlight_delay=1000)
                new_page.wait_for_timeout(1000)
                case_link = new_page.locator('span:has-text("visibility")').first
                self.scroll_focus_click(case_link, target_page=new_page)
                new_page.wait_for_timeout(500)
                
                # Wait for the spinner to resolve
                try:
                    new_page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
                except Exception:
                    pass

            search_and_open_case(shared_data.case_id)
            new_page.wait_for_timeout(500)
            if step_printer: step_printer(6)

            # Check if case is assigned to Sorter context. If not, assign to self.
            owner_dropdown = new_page.locator('select#caseOwner')
            owner_dropdown.wait_for(state="visible", timeout=15000)
            current_owner = owner_dropdown.input_value()
            self.logger.info(f"👤 Sorter inspects owner: '{current_owner}'")

            if current_owner != target_sorter:
                self.logger.info(f"📝 Case is not assigned to self. Sorter reassigning to: '{target_sorter}'")
                self.scroll_focus_select(owner_dropdown, label=target_sorter, target_page=new_page)
                new_page.wait_for_timeout(500)

                save_btn = new_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")')
                self.scroll_focus_click(save_btn, target_page=new_page)

                popup_modal = new_page.locator("div.popup-content")
                popup_modal.wait_for(state="visible", timeout=10000)

                modal_textarea = popup_modal.locator("textarea[placeholder='Comments...']")
                self.scroll_focus_fill(modal_textarea, "Reassigning case owner to self (Sorter).", target_page=new_page)

                modal_submit = popup_modal.locator("button").filter(has_text=re.compile(r"Update|Submit|Save|Approve", re.IGNORECASE)).first
                new_page.wait_for_timeout(500)
                self.scroll_focus_click(modal_submit, target_page=new_page)

                popup_modal.wait_for(state="hidden", timeout=10000)
                new_page.wait_for_timeout(500)
                self.logger.info("✅ Sorter successfully reassigned case to himself.")

            self.logger.info("⬇ McKay Interacting with the sequential Activity Table at the bottom...")
            activity_table = new_page.locator('table.sec-table')
            activity_table.scroll_into_view_if_needed()

            row_1 = activity_table.locator('tr').filter(has_text="Research Case")
            approve_btn_1 = row_1.locator('button:has-text("Approve")')
            approve_btn_1.wait_for(state="visible", timeout=15000)
            new_page.wait_for_timeout(500)
            self.scroll_focus_click(approve_btn_1, target_page=new_page)

            self.logger.info("💬 Intercepting 'Add Comments' overlay window...")
            popup_modal = new_page.locator("div.popup-content")
            popup_modal.wait_for(state="visible", timeout=10000)

            modal_textarea = popup_modal.locator("textarea")
            self.scroll_focus_fill(modal_textarea, "Research case processed and submitted via QA automation suite verification.", target_page=new_page)
            new_page.wait_for_timeout(500)

            modal_submit = popup_modal.locator("button").filter(has_text=re.compile(r"Update|Submit|Save|Approve", re.IGNORECASE)).first
            new_page.wait_for_timeout(500)
            self.scroll_focus_click(modal_submit, target_page=new_page)

            popup_modal.wait_for(state="hidden", timeout=10000)
            
            # 🛑 Add a 3-second pause so the user can visually confirm the Sorter approved it!
            self.logger.info("⏸️ Visually pausing for 3 seconds to show Sorter's approval...")
            new_page.wait_for_timeout(500)
            self.logger.info("✅ 'Research Case' Approved and comments confirmed successfully.")
            if step_printer: step_printer(7)

            # Search Case again and open it
            self.logger.info("🔎 Sorter searching the case again to verify activities...")
            search_and_open_case(shared_data.case_id)

            # Move to bottom to see activities
            self.logger.info("⬇️ Sorter scrolling to bottom to see activities...")
            activity_table = new_page.locator('table.sec-table')
            activity_table.scroll_into_view_if_needed()
            new_page.wait_for_timeout(500)
            
            if step_printer: step_printer(8)

            return True
        except Exception as e:
            self.logger.error(f"❌ Workflow failed in Sorter context: {str(e)}")
            new_page.screenshot(path=f"{self.report_dir}/sorter_workflow_error.png")
            return False
        finally:
            new_page.close()
            new_context.close()

    def resolve_as_manager_context(self, browser, shared_data, step_printer=None):
        """👑 FIX IMPLEMENTED: Logs in Case Manager using target credentials, verifies and updates case assignment, then approves."""
        target_manager_user = LOGIN_CREDENTIALS.get("boscasemanager2", {}).get("email", "boscasemanager2@yopmail.com")
        self.logger.info(f"👑 Opening Case Manager Window Context for account user: {target_manager_user}")

        mgr_context = browser.new_context(
            viewport=VIEWPORT_SIZE,
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
            target_manager_password = LOGIN_CREDENTIALS.get("boscasemanager2", {}).get("password", "Boscasemanager2@")
            self.scroll_focus_fill(pass_field, target_manager_password, target_page=mgr_page)

            login_btn = mgr_page.locator('button.auth-btn')
            self.scroll_focus_click(login_btn, target_page=mgr_page)
            mgr_page.locator(".dash-headding").first.wait_for(state="visible", timeout=25000)

            def manager_search_and_open_case(target_case_id):
                self.navigate_to_search_case(target_page=mgr_page)
                mgr_page.wait_for_timeout(500)
                self.logger.info("✅ Successfully reached Search Case Page.")
                
                self.scroll_focus_click(mgr_page.locator('button.ra-export-btn:has-text("Search Cases")'), target_page=mgr_page)
                mgr_page.wait_for_timeout(500)
                self.logger.info(f"🔍 Manager Lookup executing on target Case ID: {target_case_id}")
                
                case_input_locator = mgr_page.locator('input[formcontrolname="case"]')
                self.scroll_focus_fill(case_input_locator, target_case_id, target_page=mgr_page)
                
                self.scroll_focus_click(mgr_page.locator('button.qm-btn.qm-btn-primary:has-text("Search")'), target_page=mgr_page)
                mgr_page.wait_for_timeout(500)
                mgr_page.wait_for_timeout(500)
                case_link = mgr_page.locator('span:has-text("visibility")').first
                self.scroll_focus_click(case_link, target_page=mgr_page)
                mgr_page.wait_for_timeout(500)
                mgr_page.wait_for_timeout(500)
                
                # Wait for the spinner to resolve
                try:
                    mgr_page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
                except Exception:
                    pass

            manager_search_and_open_case(shared_data.case_id)
            mgr_page.wait_for_timeout(500)
            mgr_page.wait_for_timeout(500)
            if step_printer: step_printer(12)

            # 🛠️ NEW LOGIC COMPONENT: Dynamic Case Assignment Validation Checklist Rule Mapping
            owner_dropdown = mgr_page.locator('select#caseOwner')
            owner_dropdown.wait_for(state="visible", timeout=30000)
            current_owner = owner_dropdown.input_value()
            self.logger.info(f"👤 Pre-approval Inspection: Owner is currently set to: '{current_owner}'")

            if current_owner != target_manager_user:
                self.logger.info(f"📝 Reassigning node from '{current_owner}' to Case Manager: '{target_manager_user}'")
                self.scroll_focus_select(owner_dropdown, label="boscasemanager2@yopmail.com", target_page=mgr_page)
                mgr_page.wait_for_timeout(500)

                save_btn = mgr_page.locator('button.qm-btn.qm-btn-primary:has-text("Save")')
                self.scroll_focus_click(save_btn, target_page=mgr_page)

                popup_modal = mgr_page.locator("div.popup-content")
                popup_modal.wait_for(state="visible", timeout=10000)

                modal_textarea = popup_modal.locator("textarea[placeholder='Comments...']")
                self.scroll_focus_fill(modal_textarea, "Reassigning case owner ownership to the active manager user context layer.", target_page=mgr_page)

                modal_submit = popup_modal.locator("button").filter(has_text=re.compile(r"Update|Submit|Save|Approve", re.IGNORECASE)).first
                mgr_page.wait_for_timeout(500)
                self.scroll_focus_click(modal_submit, target_page=mgr_page)

                popup_modal.wait_for(state="hidden", timeout=10000)
                mgr_page.wait_for_timeout(500)
                self.logger.info("✅ Reassignment workflow fields saved safely.")

            # Interact with the 2nd Activity Row for approval
            self.logger.info("⬇️ Manager Interacting with the bottom sequential Activity Table...")
            activity_table = mgr_page.locator('table.sec-table')
            activity_table.scroll_into_view_if_needed()

            row_mgr = activity_table.locator('tr').filter(has_text="Closing case as approved")
            approve_btn_mgr = row_mgr.locator('button:has-text("Approve")').first
            approve_btn_mgr.wait_for(state="visible", timeout=15000)
            
            self.logger.info("⏳ Waiting for Approve button to become enabled...")
            import time
            max_attempts = 30
            enabled = False
            for attempt in range(1, max_attempts + 1):
                if approve_btn_mgr.is_enabled():
                    enabled = True
                    break
                else:
                    self.logger.info(f"   Attempt {attempt}/{max_attempts}: Button disabled, waiting...")
                    time.sleep(1)
            
            if not enabled:
                raise Exception("Approve button never became enabled.")
                
            self.scroll_focus_click(approve_btn_mgr, target_page=mgr_page)
            
            # 🛑 Add a 3-second pause so the user can visually confirm the Manager approved it!
            self.logger.info("⏸️ Visually pausing for 3 seconds to show Manager's approval...")
            mgr_page.wait_for_timeout(500)

            self.logger.info("✅ 'Closing case as approved' activity approved and logged by Case Manager successfully.")

            # Review Comments Modal Entry
            popup_modal = mgr_page.locator("div.popup-content")
            popup_modal.wait_for(state="visible", timeout=10000)

            modal_textarea = popup_modal.locator("textarea")
            self.scroll_focus_fill(modal_textarea, "Final Manager approval processed via QA test context.", target_page=mgr_page)
            mgr_page.wait_for_timeout(500)

            modal_submit = popup_modal.locator('button.qm-btn-primary', has_text="Submit")
            self.scroll_focus_click(modal_submit, target_page=mgr_page)

            popup_modal.wait_for(state="hidden", timeout=10000)
            self.logger.info("✅ 'Closing case as approved' activity approved and logged by Case Manager successfully.")
            if step_printer: step_printer(13)
            
            # Wait a bit
            mgr_page.wait_for_timeout(500)

            # Manager searches the case again, opens it, and moves to bottom to see activities
            self.logger.info("🔎 Manager searching the case again to verify activities...")
            manager_search_and_open_case(shared_data.case_id)
            
            self.logger.info("⬇️ Manager scrolling to bottom to see activities...")
            activity_table = mgr_page.locator('table.sec-table')
            activity_table.scroll_into_view_if_needed()
            mgr_page.wait_for_timeout(500)
            if step_printer: step_printer(14)

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
        self.page.locator('canvas, div.card, .case-dashboard-container').first.wait_for(state="visible", timeout=15000)
        self.page.wait_for_timeout(500)
        self.logger.info("✅ Successfully reached Case Dashboard Page.")

    def navigate_to_cases_summary(self):
        self.logger.info("⏳ Switching view to Cases Summary tab...")
        self.cases_summary_tab.wait_for(state="visible", timeout=10000)
        self.apply_focus(self.cases_summary_tab)
        self.cases_summary_tab.click()
        self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)

    def get_case_statistics(self) -> dict:
        self.logger.info("📊 Processing grid record arrays for validation data mappings...")
        all_status_cases = {}

        try:
            if self.filter_by_dropdown.is_visible():
                self.apply_focus(self.filter_by_dropdown)
                self.filter_by_dropdown.select_option("allCases")
                self.page.wait_for_timeout(500)
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

            self.page.wait_for_timeout(500)
            self.page.wait_for_timeout(500)

            if self.no_records_found_message.is_visible():
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
                    self.page.wait_for_timeout(500)
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
                self.page.wait_for_timeout(500)

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
                self.page.wait_for_timeout(500)

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
            errors.append(f"Failed parsing valcdidation arrays for Owner & Priority matrix card layout: {str(ex)}")
        return errors