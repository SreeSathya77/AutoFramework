from .base_page import BasePage
from utils.logger import Logger
logger = Logger.get_logger()

class WorkbenchPage(BasePage):
    def __init__(self, page, report_dir=None):
        super().__init__(page, report_dir)
        
    @property
    def workbench_li(self):
        """The parent container for the Workbench menu."""
        return self.page.locator('li.nav-item.has-submenu').filter(has=self.page.locator('span:has-text("group")'))

    @property
    def workbench_icon(self):
        """The main icon/link to expand Workbench."""
        return self.workbench_li.locator('a.nav-link').first

    @property
    def manage_accounts_menu(self):
        """The 'Manage Accounts' toggle within the Workbench submenu."""
        return self.workbench_li.locator('a.nav-link:has-text("Manage Accounts")')

    @property
    def onboard_customer_link(self):
        """The final 'Onboard a Customer' link."""
        return self.page.locator('a.nav-link[href="/operation-workbench/manage-customer-account/onboard-a-customer"]')

    def navigate_to_onboard_customer(self):
        """
        Navigates through the sidebar menu: 
        Workbench -> Manage Accounts -> Onboard a Customer
        """
        logger.info("Starting navigation to Onboard Customer page...")
        
        # 1. Expand Workbench
        logger.info("Clicking Workbench icon...")
        self.workbench_icon.click()
        
        # Wait for 'Manage Accounts' to be visible within the expanded menu
        self.manage_accounts_menu.wait_for(state="visible", timeout=5000)
        logger.info("Workbench menu expanded.")

        # 2. Expand Manage Accounts
        logger.info("Clicking 'Manage Accounts' sub-menu...")
        # We use force=True in case the span inside the link is overlaying the hit area
        self.manage_accounts_menu.click(force=True)
        
        # Wait for 'Onboard a Customer' to be visible
        self.onboard_customer_link.wait_for(state="visible", timeout=5000)
        logger.info("'Manage Accounts' submenu expanded.")

        # 3. Click Onboard a Customer
        logger.info("Clicking 'Onboard a Customer' link...")
        self.onboard_customer_link.click()
        
        # 4. Confirm navigation
        self.page.wait_for_url("**/onboard-a-customer", timeout=15000)
        logger.info("Successfully navigated to Onboard Customer page.")
        
        # Take a screenshot of the landing page
        self.take_screenshot("02_Onboard_Customer_Landing")
