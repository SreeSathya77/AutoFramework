from .base_page import BasePage
from utils.logger import Logger
import re

logger = Logger.get_logger()

class ManageVehiclesPage(BasePage):
    def __init__(self, page, report_dir=None):
        super().__init__(page, report_dir)

    def global_search_and_open_account(self, account_id: str) -> bool:
        """
        Uses the top global search bar to find an account and opens its profile.
        """
        logger.info(f"🔍 Global searching for Account ID: {account_id}")
        
        # 1. Fill the search box using sequential typing so Angular detects it
        search_input = self.page.locator('input.search-input').first
        search_input.click()
        search_input.fill("") # clear it
        search_input.press_sequentially(account_id, delay=100)
        self.page.wait_for_timeout(2000) # Give API time to fetch results
        
        # 2. Click on 'Account Management' from the dropdown results
        account_mgmt_option = self.page.locator('span').filter(has_text="Account Management").first
        account_mgmt_option.wait_for(state="visible", timeout=15000)
        self.scroll_focus_click(account_mgmt_option)
        self.page.wait_for_timeout(1000)
        
        # 3. Click 'visibility' icon to open the account profile
        visibility_icon = self.page.locator('span.material-symbols-outlined:has-text("visibility")').first
        self.scroll_focus_click(visibility_icon)
        self.page.wait_for_timeout(1500)
        
        logger.info(f"✅ Successfully opened Account Profile for {account_id}.")
        return True

    def navigate_to_manage_vehicles(self) -> bool:
        """
        Navigates to the Manage Vehicles screen from within a Customer Profile.
        """
        logger.info("🚗 Navigating to Vehicles -> Manage Vehicles...")
        
        # Click the Vehicles dropdown
        vehicles_menu = self.page.locator('a.nav-link.dropdown-toggle').filter(has_text="Vehicles").first
        self.scroll_focus_click(vehicles_menu)
        self.page.wait_for_timeout(500)
        
        # Click Manage Vehicles
        manage_vehicles_option = self.page.locator('a.dropdown-item[href*="/manage-vehicles"]').filter(has_text="Manage Vehicles").first
        self.scroll_focus_click(manage_vehicles_option)
        self.page.wait_for_timeout(1000)
        
        logger.info("✅ Successfully reached Manage Vehicles page.")
        return True

    def highlight_fulfillment_requested_status(self) -> bool:
        """
        Finds the Tag Status cell for the vehicle, scrolls it into view, and highlights it.
        """
        logger.info("✨ Searching for 'Fulfillment Requested' tag status to highlight...")
        
        try:
            self.page.evaluate("window.scrollBy(0, 500)")
            self.page.wait_for_timeout(1000)
            
            # Wait for grid to load by waiting for 'TAG STATUS' header
            self.page.locator('th').filter(has_text=re.compile(r"TAG STATUS", re.IGNORECASE)).first.wait_for(state="visible", timeout=15000)
            
            from utils.shared_data import SharedData
            target_plate = SharedData.tagged_plate_number
            
            cell_handle = self.page.evaluate_handle("""(targetPlate) => {
                const ths = Array.from(document.querySelectorAll('th'));
                const tagStatusIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'TAG STATUS');
                const plateIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'PLATE NUMBER');
                if (tagStatusIdx === -1) return null;
                
                const rows = Array.from(document.querySelectorAll('tbody tr'));
                
                // 1. If we have a target plate, find its exact row
                if (targetPlate && plateIdx !== -1) {
                    for (const row of rows) {
                        const tds = Array.from(row.querySelectorAll('td'));
                        if (tds.length > Math.max(tagStatusIdx, plateIdx)) {
                            const plateText = tds[plateIdx].innerText.trim();
                            if (plateText === targetPlate) {
                                return tds[tagStatusIdx];
                            }
                        }
                    }
                }
                
                // 2. Fallback: We want the row where the tag status contains 'PENDING' or 'FULFILLMENT'
                for (const row of rows) {
                    const tds = Array.from(row.querySelectorAll('td'));
                    if (tds.length > tagStatusIdx) {
                        const statusText = tds[tagStatusIdx].innerText.trim().toUpperCase();
                        if (statusText.includes('PENDING') || statusText.includes('FULFILLMENT')) {
                            return tds[tagStatusIdx];
                        }
                    }
                }
                // No fallback! If we don't find it, we return null so the test fails.
                return null;
            }""", target_plate)
            
            if not cell_handle:
                raise Exception("Could not locate TAG STATUS cell.")
                
            cell_handle.evaluate("(el) => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'auto'})")
            self.page.wait_for_timeout(1000)
            
            status_text = cell_handle.evaluate("(el) => el.innerText.trim()")
            cell_handle.evaluate("(el) => { el.style.backgroundColor = 'orange'; el.style.color = 'white'; el.style.fontWeight = 'bold'; }")
            logger.info(f"🟠 Highlighted Tag Status: {status_text}")
            
            self.take_screenshot("Tag_Status_Fulfillment_Requested")
            self.page.wait_for_timeout(3000)
            
            if "PENDING" not in status_text.upper() and "FULFILLMENT" not in status_text.upper():
                logger.warning(f"⚠️ Found Tag Status for Plate {target_plate}, but status was: '{status_text}'")
                return False
                
            return True
        except Exception as e:
            logger.warning(f"⚠️ Could not find 'Fulfillment Requested' status to highlight: {str(e)}")
            return False

    def verify_tag_status(self) -> str:
        """
        Category 4 Phase 1: Verifies the Tag Status in the Manage Vehicles grid.
        Returns the status string found (e.g., 'ACTIVE', 'ASSIGNED').
        """
        logger.info("🔍 Verifying Tag Status in the Manage Vehicles grid...")
        try:
            self.page.evaluate("window.scrollBy(0, 500)")
            self.page.wait_for_timeout(1000)
            
            # Wait for grid to load by waiting for 'TAG STATUS' header
            self.page.locator('th').filter(has_text=re.compile(r"TAG STATUS", re.IGNORECASE)).first.wait_for(state="visible", timeout=15000)
            
            from utils.shared_data import SharedData
            target_plate = SharedData.tagged_plate_number
            
            cell_handle = self.page.evaluate_handle("""(targetPlate) => {
                const ths = Array.from(document.querySelectorAll('th'));
                const tagStatusIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'TAG STATUS');
                const tagIdIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'TAG ID');
                const plateIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'PLATE NUMBER');
                
                if (tagStatusIdx === -1) return null;
                
                const rows = Array.from(document.querySelectorAll('tbody tr'));
                
                // 1. If we have a target plate, find its exact row
                if (targetPlate && plateIdx !== -1) {
                    for (const row of rows) {
                        const tds = Array.from(row.querySelectorAll('td'));
                        if (tds.length > Math.max(tagStatusIdx, plateIdx)) {
                            const plateText = tds[plateIdx].innerText.trim();
                            if (plateText === targetPlate) {
                                return tds[tagStatusIdx];
                            }
                        }
                    }
                }
                
                // 2. Fallback: Return the Tag Status for the first row that actually has a Tag ID (i.e. not 'NA')
                for (const row of rows) {
                    const tds = Array.from(row.querySelectorAll('td'));
                    if (tagIdIdx !== -1 && tds.length > tagIdIdx) {
                        const tagId = tds[tagIdIdx].innerText.trim();
                        if (tagId !== 'NA' && tagId !== '') {
                            return tds[tagStatusIdx];
                        }
                    }
                }
                // No fallback! If we don't find it, we return null so the test fails.
                return null;
            }""", target_plate)
            
            if not cell_handle:
                raise Exception("Could not locate TAG STATUS cell.")
                
            cell_handle.evaluate("(el) => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'auto'})")
            self.page.wait_for_timeout(1000)
            
            status_text = cell_handle.evaluate("(el) => el.innerText.trim()")
            cell_handle.evaluate("(el) => { el.style.backgroundColor = 'orange'; el.style.color = 'white'; el.style.fontWeight = 'bold'; }")
            logger.info(f"🟠 Highlighted Tag Status: {status_text}")
            
            self.take_screenshot(f"Tag_Status_{status_text}")
            self.page.wait_for_timeout(2000)
            
            return status_text
        except Exception as e:
            logger.warning(f"⚠️ Could not verify Tag Status: {str(e)}")
            return ""

    def verify_tag_status_na(self) -> bool:
        """
        Category 4 Phase 3: Verifies that Tag ID and Tag Status are 'NA' for the source plate after transfer.
        """
        logger.info("🔍 Verifying Tag ID and Status are NA after transfer...")
        try:
            self.page.evaluate("window.scrollBy(0, 500)")
            self.page.wait_for_timeout(1000)
            
            self.page.locator('th').filter(has_text=re.compile(r"TAG STATUS", re.IGNORECASE)).first.wait_for(state="visible", timeout=15000)
            
            from utils.shared_data import SharedData
            target_plate = SharedData.tagged_plate_number
            
            result = self.page.evaluate("""(targetPlate) => {
                const ths = Array.from(document.querySelectorAll('th'));
                const tagStatusIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'TAG STATUS');
                const tagIdIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'TAG ID');
                const plateIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'PLATE NUMBER');
                
                if (tagStatusIdx === -1 || tagIdIdx === -1 || plateIdx === -1) return null;
                
                const rows = Array.from(document.querySelectorAll('tbody tr'));
                
                if (targetPlate) {
                    for (const row of rows) {
                        const tds = Array.from(row.querySelectorAll('td'));
                        if (tds.length > Math.max(tagStatusIdx, tagIdIdx, plateIdx)) {
                            const plateText = tds[plateIdx].innerText.trim();
                            if (plateText === targetPlate) {
                                // Highlight them orange
                                tds[tagIdIdx].style.backgroundColor = 'orange';
                                tds[tagIdIdx].style.color = 'white';
                                tds[tagIdIdx].style.fontWeight = 'bold';
                                
                                tds[tagStatusIdx].style.backgroundColor = 'orange';
                                tds[tagStatusIdx].style.color = 'white';
                                tds[tagStatusIdx].style.fontWeight = 'bold';
                                
                                tds[tagIdIdx].scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'});
                                
                                return {
                                    tagId: tds[tagIdIdx].innerText.trim(),
                                    tagStatus: tds[tagStatusIdx].innerText.trim()
                                };
                            }
                        }
                    }
                }
                return null;
            }""", target_plate)
            
            if result and result.get("tagId") == "NA" and result.get("tagStatus") == "NA":
                logger.info("🟠 Highlighted Tag ID and Tag Status as NA")
                self.take_screenshot("Tag_Status_NA_Verified")
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Could not verify Tag Status NA: {str(e)}")
            return False
            
    def initiate_tag_transfer(self, step_printer=None) -> bool:
        """
        Initiates a tag transfer by selecting the checkbox for the target plate and clicking 'Transfer Tag'.
        """
        logger.info("🚗 Initiating Tag Transfer...")
        try:
            from utils.shared_data import SharedData
            target_plate = SharedData.tagged_plate_number
            
            # Find the checkbox for the specific row
            checkbox_handle = self.page.evaluate_handle("""(targetPlate) => {
                const ths = Array.from(document.querySelectorAll('th'));
                const plateIdx = ths.findIndex(th => th.innerText.trim().toUpperCase() === 'PLATE NUMBER');
                
                if (plateIdx === -1) return null;
                
                const rows = Array.from(document.querySelectorAll('tbody tr'));
                
                if (targetPlate) {
                    for (const row of rows) {
                        const tds = Array.from(row.querySelectorAll('td'));
                        if (tds.length > plateIdx) {
                            const plateText = tds[plateIdx].innerText.trim();
                            if (plateText === targetPlate) {
                                // Find checkbox in this row
                                return row.querySelector('input[type="checkbox"]');
                            }
                        }
                    }
                }
                return null;
            }""", target_plate)
            
            if not checkbox_handle:
                logger.error(f"❌ Could not find checkbox for plate: {target_plate}")
                return False
                
            # Scroll and click checkbox
            checkbox_handle.evaluate("(el) => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'auto'})")
            self.page.wait_for_timeout(500)
            # Use javascript click because the checkbox might be obscured or purely a CSS custom checkbox
            checkbox_handle.evaluate("(el) => el.click()")
            logger.info(f"✅ Selected checkbox for vehicle with plate: {target_plate}")
            self.page.wait_for_timeout(1000)
            
            # Find and click Transfer Tag button
            transfer_btn = self.page.locator('button').filter(has_text="Transfer Tag").first
            self.scroll_focus_click(transfer_btn)
            self.page.wait_for_timeout(2000)
            
            if step_printer:
                step_printer(6)
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initiate Tag Transfer: {str(e)}")
            return False

    def fill_transfer_tag_form(self, target_account_id: str) -> bool:
        """
        Fills out the first part of the Tag Transfer form by entering the destination account
        and clicking 'Search customer for transfer'.
        """
        logger.info(f"🔄 Entering Destination Account ID: {target_account_id} into Transfer Form...")
        try:
            # Wait for the transfer form to appear
            account_input = self.page.locator('input[formcontrolname="transferToAccount"]')
            account_input.wait_for(state="visible", timeout=15000)
            
            # Use scroll_focus_fill to enter the account number
            self.scroll_focus_fill(account_input, target_account_id)
            self.page.wait_for_timeout(500)
            
            # Click the Search button
            search_btn = self.page.locator('button').filter(has_text="Search customer for transfer").first
            self.scroll_focus_click(search_btn)
            
            # Wait a moment for the search to trigger any API calls
            self.page.wait_for_timeout(2000)
            
            # Now the "Search Customer" modal appears
            logger.info("🔍 Interacting with 'Search Customer' modal...")
            modal = self.page.locator('div.modal-content').filter(has_text="Search Customer")
            modal.wait_for(state="visible", timeout=10000)
            
            # Fill account number in modal
            modal_account_input = modal.locator('input#accountNumber[formcontrolname="accountNumber"]')
            self.scroll_focus_fill(modal_account_input, target_account_id)
            self.page.wait_for_timeout(500)
            
            # Click Search button in modal
            modal_search_btn = modal.locator('button.btn-primary').filter(has_text="Search")
            self.scroll_focus_click(modal_search_btn)
            self.page.wait_for_timeout(1500)
            
            # Click the Select text in the table
            select_btn = modal.locator('table.table-striped tbody tr p').filter(has_text="Select").first
            select_btn.wait_for(state="visible", timeout=10000)
            self.scroll_focus_click(select_btn)
            
            # Wait for modal to close
            modal.wait_for(state="hidden", timeout=10000)
            self.page.wait_for_timeout(1000)
            
            logger.info("✅ Customer Selected from Search Modal successfully.")
            
            # Back on Tag Transfer page, select the first available destination plate
            logger.info("🚗 Selecting Destination Plate Number from dropdown...")
            plate_dropdown = self.page.locator('select[formcontrolname="transferToPlate"]')
            plate_dropdown.wait_for(state="visible", timeout=10000)
            
            # Index 1 because Index 0 is the disabled 'Select Plate #' option
            plate_dropdown.select_option(index=1)
            self.page.wait_for_timeout(500)
            logger.info("✅ Destination Plate Number selected.")
            
            # Click the final Request Transfer Tag button
            logger.info("🚗 Clicking 'Request Transfer Tag' button...")
            submit_btn = self.page.locator('button.qm-btn.qm-btn-primary').filter(has_text="Request Transfer Tag").first
            self.scroll_focus_click(submit_btn)
            
            # Wait for confirmation modal
            logger.info("🔍 Interacting with Confirmation Modal...")
            confirm_modal = self.page.locator('div.modal-content1').filter(has_text="Do you wish to continue to do Tag Transfer")
            confirm_modal.wait_for(state="visible", timeout=15000)
            
            # Read and log confirmation message
            message_text = confirm_modal.locator('p').inner_text()
            logger.info(f"Confirmation Message: {message_text}")
            
            from utils.shared_data import SharedData
            if SharedData.account_id not in message_text or target_account_id not in message_text:
                logger.warning("⚠️ From/To Account IDs not found in confirmation message. Proceeding anyway.")
                
            # Click OK button
            ok_btn = confirm_modal.locator('button.qm-btn.qm-btn-primary').filter(has_text="OK")
            self.scroll_focus_click(ok_btn)
            
            # Wait for modal to disappear
            confirm_modal.wait_for(state="hidden", timeout=10000)
            self.page.wait_for_timeout(2000)
            
            # Wait for the success case modal
            logger.info("🔍 Waiting for Success Case Modal...")
            success_modal = self.page.locator('div.modal-content').filter(has_text="is created for tag transfer successfully")
            success_modal.wait_for(state="visible", timeout=15000)
            
            # Extract Case ID from the span inside the p tag
            case_id_span = success_modal.locator('p span').first
            case_id = case_id_span.inner_text().strip()
            
            logger.info(f"🎉 Captured Transfer Tag Case ID: {case_id}")
            SharedData.case_id = case_id
            
            # Click the Case ID link instead of Cancel
            logger.info("🖱️ Clicking the Case ID link to navigate to Case Details...")
            self.scroll_focus_click(case_id_span)
            
            # The app likely navigates to the case details view here
            self.page.wait_for_timeout(3000)
            
            logger.info("🎉 Tag Transfer Request successfully submitted and Case ID navigated!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to fill transfer tag form: {str(e)}")
            return False
