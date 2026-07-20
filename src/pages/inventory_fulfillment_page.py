from playwright.sync_api import Page
from src.utils.logger import Logger
from src.pages.base_page import BasePage

class InventoryFulfillmentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = Logger.get_logger()

    def navigate_to_customer_fulfillment(self, step_printer=None):
        """
        Navigates to the Quantum Inventory -> Customer Fulfillment screen via the left sidebar.
        """
        self.logger.info("🖱️ Navigating via UI: Quantum Inventory -> Customer Fulfillment")
        
        # Disable the Angular CDK overlay container so it cannot block any pointer events
        try:
            self.page.evaluate("""
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
            self.page.add_style_tag(content=".chatbot-icon, #chat-widget-container { display: none !important; }")
        except Exception:
            pass

        # Quantum Inventory Main Menu
        quantum_inventory_menu = self.page.locator('a.nav-link:has-text("Quantum Inventory")').first
        
        # Submenu: Customer Fulfillment
        customer_fulfillment_submenu = self.page.locator('a.nav-link:has-text("Customer Fulfillment")').first
        
        # Inner Menu: Customer Fulfillment (the actual link)
        customer_fulfillment_link = self.page.locator('a.nav-link[href="/operation-workbench/quantum-inventory/customer-fulfillment"]').first

        # Ensure the main sidebar is expanded (click Dashboard icon or Workbench icon if needed)
        workbench_icon = self.page.locator("span.material-symbols-outlined", has_text="group").first
        dashboard_link = self.page.locator('a.nav-link:has-text("Dashboard")').first
        
        if not dashboard_link.is_visible():
            self.logger.info("   👉 Expanding main sidebar...")
            try:
                self.scroll_focus_click(workbench_icon)
                self.page.wait_for_timeout(500)
            except Exception:
                pass

        # 1. Click Quantum Inventory if not already expanded
        if not customer_fulfillment_submenu.is_visible():
            self.logger.info("   👉 Expanding 'Quantum Inventory' menu...")
            try:
                self.scroll_focus_click(quantum_inventory_menu)
            except Exception:
                # Fallback if first click fails or element is intercepted
                quantum_inventory_menu.click(force=True)
            self.page.wait_for_timeout(500)

        # 2. Click Customer Fulfillment submenu if link not visible
        if not customer_fulfillment_link.is_visible():
            self.logger.info("   👉 Expanding 'Customer Fulfillment' submenu...")
            try:
                self.scroll_focus_click(customer_fulfillment_submenu)
            except Exception:
                customer_fulfillment_submenu.click(force=True)
            self.page.wait_for_timeout(500)

        # 3. Click the actual Customer Fulfillment link
        self.logger.info("   👉 Clicking 'Customer Fulfillment' link...")
        try:
            self.scroll_focus_click(customer_fulfillment_link)
        except Exception:
            customer_fulfillment_link.click(force=True)
        
        # Wait for the page to load natively via spinner
        self.logger.info("⏳ Waiting for Customer Fulfillment page loading spinner to resolve...")
        try:
            self.page.locator("mat-spinner, mat-progress-spinner, .spinner, .loader, .loading, .cdk-overlay-backdrop").first.wait_for(state="hidden", timeout=25000)
        except Exception:
            pass
            
        self.page.wait_for_timeout(1500)
        
        # Visually highlight for user to confirm navigation
        self.page.evaluate("""() => {
            const header = document.querySelector('.dash-headding');
            if(header) {
                header.style.outline = '4px solid orange';
                header.style.backgroundColor = 'rgba(255, 165, 0, 0.3)';
            }
        }""")
        self.page.wait_for_timeout(3500)
        
        self.logger.info("✅ Successfully reached Customer Fulfillment Page.")
        if step_printer: step_printer(2)
        return True

    def fulfill_tag_request(self, account_id: str, step_printer=None):
        """
        Locates the specific Account ID in the fulfillment grid and clicks the Select button.
        """
        self.logger.info(f"🔍 Searching for Tag Request for Account: {account_id} in the Fulfillment Grid...")
        
        # Wait for the grid to render
        self.page.locator('table.ra-table').first.wait_for(state="visible", timeout=15000)
        
        # Handle pagination to find the row
        found = False
        target_row = None
        for _ in range(10):  # Try up to 10 pages
            target_row = self.page.locator(f'table.ra-table tbody tr:visible:has(td:has-text("{account_id}"))').first
            if target_row.is_visible():
                found = True
                break
            
            # Try clicking "Next" button if it exists
            next_btn = self.page.locator('button.page-link:has(span:has-text("keyboard_double_arrow_right"))').first
            if next_btn.is_visible() and not next_btn.get_attribute("disabled") and not next_btn.evaluate("el => el.disabled"):
                self.logger.info("👉 Row not found on current page. Clicking 'Next' page...")
                self.scroll_focus_click(next_btn)
                self.page.wait_for_timeout(2000)  # Wait for grid to render
            else:
                break
                
        if found:
            self.logger.info(f"✅ Found row for Account: {account_id}")
            if step_printer: step_printer(3)
        else:
            self.logger.warning(f"⚠️ Account ID {account_id} not found in the grid. Clicking 'Claim Request'...")
            claim_btn = self.page.locator('button.ra-export-btn--primary', has_text="Claim Request")
            self.scroll_focus_click(claim_btn)
            
            # Wait for the popup
            self.logger.info("⏳ Waiting for Claim Request popup to load...")
            popup_drawer = self.page.locator('div.drawer-content form:visible')
            popup_drawer.wait_for(state="visible", timeout=15000)
            
            # Fill account id and count
            self.logger.info(f"✍️ Entering Account ID: {account_id}")
            self.scroll_focus_fill(popup_drawer.locator('input#accountId'), account_id)
            self.scroll_focus_fill(popup_drawer.locator('input#count'), "1")
            
            # Select Item Type, Tag Type, and Location
            self.logger.info("📦 Selecting Item Type: 'QBOS_Class_Three'")
            self.scroll_focus_select(popup_drawer.locator('select#itemType'), value="QBOS_Class_Three")
            self.page.wait_for_timeout(500)
            
            self.logger.info("🏷️ Selecting Tag Type: 'Regular'")
            # "Regular" might not be the exact value attribute, so we use label
            self.scroll_focus_select(popup_drawer.locator('select#tagType'), label="Regular")
            self.page.wait_for_timeout(500)
            
            self.logger.info("📍 Selecting Location: 'NewYork'")
            self.scroll_focus_select(popup_drawer.locator('select#location'), value="NewYork")
            self.page.wait_for_timeout(500)
            
            # Submit Claim Request
            self.logger.info("🖱️ Clicking 'Submit' to claim request...")
            submit_btn = popup_drawer.locator('button.qm-btn-primary', has_text="Submit")
            self.scroll_focus_click(submit_btn)
            
            # Wait for grid to update
            self.logger.info("⏳ Waiting for grid to update after claiming request...")
            self.page.wait_for_timeout(3000)
            
            # Handle pagination to find the row
            found = False
            target_row = None
            for _ in range(10):  # Try up to 10 pages
                target_row = self.page.locator(f'table.ra-table tbody tr:visible:has(td:has-text("{account_id}"))').first
                if target_row.is_visible():
                    found = True
                    break
                
                # Try clicking "Next" button if it exists
                next_btn = self.page.locator('button.page-link:has(span:has-text("keyboard_double_arrow_right"))').first
                if next_btn.is_visible() and not next_btn.get_attribute("disabled") and not next_btn.evaluate("el => el.disabled"):
                    self.logger.info("👉 Row not found on current page. Clicking 'Next' page...")
                    self.scroll_focus_click(next_btn)
                    self.page.wait_for_timeout(2000)  # Wait for grid to render
                else:
                    break
                    
            if not found:
                raise Exception(f"Account ID {account_id} not found in fulfillment grid even after searching through pages.")
            
            self.logger.info(f"✅ Found row for Account: {account_id} after claiming.")
            if step_printer: step_printer(3)
        # Locate the Select button inside that row
        select_btn = target_row.locator('button:has-text("Select")')
        
        self.logger.info("🖱️ Clicking 'Select' button...")
        self.scroll_focus_click(select_btn)
        
        # Wait for the "Fulfill Request" section to appear
        self.logger.info("⏳ Waiting for 'Fulfill Request' section to load...")
        tag_agency_dropdown = self.page.locator('select#tagAgency[formcontrolname="tagAgencyInitial"]')
        tag_agency_dropdown.wait_for(state="visible", timeout=15000)
        
        self.logger.info("🏢 Selecting Tag Agency: 'HCTR'")
        self.scroll_focus_select(tag_agency_dropdown, value="HCTR")
        self.page.wait_for_timeout(500)
        
        self.logger.info("🏷️ Selecting the first available Tag ID...")
        tag_id_dropdown = self.page.locator('select#tagId[formcontrolname="tagId"]')
        # Wait for options to populate
        tag_id_dropdown.wait_for(state="visible", timeout=10000)
        self.page.wait_for_timeout(1500) # Give API time to populate
        
        # Get the second option (index 1) since index 0 is "Select Tag ID"
        first_tag_id_option = tag_id_dropdown.locator('option').nth(1)
        first_tag_id_option.wait_for(state="attached", timeout=20000)
        tag_id_value = first_tag_id_option.get_attribute("value") or first_tag_id_option.inner_text().strip()
        
        self.logger.info(f"👉 Chose Tag ID: {tag_id_value}")
        self.scroll_focus_select(tag_id_dropdown, label=tag_id_value)
        self.page.wait_for_timeout(500)
        
        self.logger.info("🖱️ Clicking 'Fulfill Request' button to submit...")
        fulfill_btn = self.page.locator('button.qm-btn-primary', has_text="Fulfill Request")
        self.scroll_focus_click(fulfill_btn)
        
        # Handle the confirmation modal: "Are You Sure You want to Assign Tag Request?"
        self.logger.info("🛑 Waiting for confirmation modal...")
        confirm_ok_btn = self.page.locator('div.ra-modal__actions button.ra-btn--primary', has_text="OK").first
        confirm_ok_btn.wait_for(state="visible", timeout=10000)
        self.logger.info("🖱️ Clicking 'OK' on confirmation modal...")
        self.scroll_focus_click(confirm_ok_btn)
        
        # Pause for user to verify success toast
        self.logger.info("✅ Fulfill Tag Request complete. Waiting for success toast...")
        self.page.wait_for_timeout(3000)
        if step_printer: step_printer(4)
        return True
