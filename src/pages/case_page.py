"""
Case Page Object Model
Handles Case Management navigation and case creation
"""

from playwright.sync_api import Page
from utils.logger import get_logger

logger = get_logger(__name__)


class CasePage:
    def __init__(self, page: Page):
        self.page = page

    # =========================
    # 🔹 NAVIGATION LOCATORS
    # =========================

    @property
    def workbench_icon(self):
        """Workbench (group icon)"""
        return self.page.locator('span.material-symbols-outlined:has-text("group")')

    @property
    def case_management_menu(self):
        """Case Management menu"""
        return self.page.get_by_text("Case Management")

    @property
    def create_case_button(self):
        """Create Case button"""
        return self.page.get_by_text("Create Case")

    # =========================
    # 🔹 FORM LOCATORS (UPDATE IF NEEDED)
    # =========================

    @property
    def case_type_dropdown(self):
        return self.page.locator('select[formcontrolname="caseType"]')

    @property
    def account_dropdown(self):
        return self.page.locator('select[formcontrolname="account"]')

    @property
    def description_input(self):
        return self.page.locator('textarea[formcontrolname="description"]')

    @property
    def priority_dropdown(self):
        return self.page.locator('select[formcontrolname="priority"]')

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Submit")

    @property
    def success_message(self):
        return self.page.locator("text=Case created successfully")

    # =========================
    # 🔹 NAVIGATION METHODS
    # =========================

    def navigate_to_cases(self):
        """Navigate to Case Management via Workbench"""
        logger.info("Navigating to Case Management...")

        # Step 1: Click Workbench
        self.workbench_icon.wait_for(state="visible", timeout=10000)
        self.workbench_icon.click(force=True)

        # Step 2: Wait for menu expand
        self.page.wait_for_timeout(1000)

        # Step 3: Click Case Management
        self.case_management_menu.wait_for(state="visible", timeout=10000)
        self.case_management_menu.click(force=True)

        # Step 4: Wait for page load
        self.page.wait_for_load_state("networkidle")

        logger.info("Navigation to Case Management successful")

    def open_create_case(self):
        """Open Create Case page"""
        logger.info("Opening Create Case screen...")

        self.create_case_button.wait_for(state="visible", timeout=10000)
        self.create_case_button.click(force=True)

        self.page.wait_for_load_state("networkidle")

    # =========================
    # 🔹 FORM ACTIONS
    # =========================

    def fill_case_form(self, case_data: dict):
        """Fill case form"""

        logger.info(f"Filling case form: {case_data}")

        # Case Type
        if case_data.get("type"):
            self.case_type_dropdown.wait_for(state="visible")
            self.case_type_dropdown.select_option(label=case_data["type"])

        # Account
        if case_data.get("account"):
            self.account_dropdown.wait_for(state="visible")
            self.account_dropdown.select_option(label=case_data["account"])

        # Description
        if case_data.get("description"):
            self.description_input.fill(case_data["description"])

        # Priority
        if case_data.get("priority"):
            self.priority_dropdown.select_option(label=case_data["priority"])

    def submit_case(self):
        """Submit case form"""
        logger.info("Submitting case...")

        self.submit_button.wait_for(state="visible")
        self.submit_button.click(force=True)

        self.page.wait_for_load_state("networkidle")

    # =========================
    # 🔹 MAIN FLOW
    # =========================

    def create_case(self, case_data: dict) -> bool:
        """Full flow: Navigate → Create → Submit"""

        try:
            self.navigate_to_cases()
            self.open_create_case()
            self.fill_case_form(case_data)
            self.submit_case()

            # Verify success
            self.page.wait_for_timeout(2000)

            if self.success_message.is_visible():
                logger.info("✅ Case created successfully")
                return True
            else:
                logger.error("❌ Case creation failed (no success message)")
                return False

        except Exception as e:
            logger.error(f"❌ Error in case creation: {str(e)}")
            return False

    # =========================
    # 🔹 HELPER METHODS
    # =========================

    def create_auto_case(self, account_name: str) -> bool:
        """Quick case creation"""

        case_data = {
            "type": "Refund Request",
            "account": account_name,
            "description": "Auto-generated test case",
            "priority": "Medium"
        }

        return self.create_case(case_data)

    def verify_case_exists(self, text: str) -> bool:
        """Verify case exists"""
        try:
            return self.page.locator(f"text={text}").is_visible()
        except:
            return False