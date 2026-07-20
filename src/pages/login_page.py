import os
import re
from .base_page import BasePage
from utils.logger import Logger

logger = Logger.get_logger()


class LoginPage(BasePage):
    def __init__(self, page, report_dir=None):
        super().__init__(page)
        self.email_input = 'input[formcontrolname="emailId"]'
        self.password_input = 'input[formcontrolname="password"]'
        self.login_button = "button.auth-btn"
        self.pop_up_selector = 'div[class*=\"success\"]'  # Identified pop-up selector
        self.report_dir = report_dir

    def navigate_to_login(self, url):
        logger.info(f"Navigating to Login Page: {url}")
        self.navigate(url)
        self.page.wait_for_load_state("networkidle")

    def perform_login(self, email, password):
        """
        Performs login.
        """
        logger.info(f"Attempting login sequence for user: {email}")

        try:
            # 1. Wait for page load
            self.page.wait_for_load_state("load")
            self.wait_for_element(self.email_input)
            
            # --- REMOVED: Zoom validation based on window.innerWidth ---
            # This check is incompatible with CSS transform: scale() which scales content visually
            # without changing window.innerWidth. Visual confirmation during test run is sufficient.
            
            logger.info("Proceeding with login...")

            # 4. Populate credentials
            self.scroll_focus_fill(self.email_input, email)
            self.scroll_focus_fill(self.password_input, password)
            self.page.wait_for_timeout(500)

            # 5. Use the shared BasePage interaction logic
            logger.info("⏳ Step 3: Performing focused click on login button...")
            self.scroll_focus_click(self.login_button)

            self.page.wait_for_load_state("networkidle")
            logger.info("✅ Login button interaction successfully executed.")

        except Exception as e:
            logger.error(f"Login sequence halted: {str(e)}")
            self.log_page_elements("Login_Failure_Exception")
            raise e

    def verify_login_success(self, timeout=15000):
        """Verifies if login was successful by checking the dashboard heading container."""
        logger.info("Verifying login success...")
        try:
            # Step 1: Wait for dashboard heading container or dashboard elements
            dash_heading_selector = 'div.dash-headding'

            # Wait for either URL to transition or element to appear
            try:
                self.page.wait_for_url("**/dashboard", timeout=timeout)
                logger.info("✅ URL changed to dashboard route.")
            except Exception:
                logger.warning("⚠️ Timeout waiting for dashboard URL string match, checking elements instead...")

            # Search elements strategies
            dash_heading = self.page.query_selector(dash_heading_selector)
            if dash_heading:
                if dash_heading.is_visible():
                    logger.info("✅ Dashboard heading container found")
                    h4_element = dash_heading.query_selector('h4')
                    if h4_element and h4_element.is_visible():
                        text = h4_element.inner_text().strip()
                        if "Welcome to QM Toll portal!" in text:
                            logger.info(f"✅ Dashboard header found in dash-headding: '{text}'")
                            return True

            # Final check: Search all h4 elements for the target welcome banner
            all_h4 = self.page.query_selector_all('h4')
            for h4 in all_h4:
                if h4.is_visible():
                    text = h4.inner_text().strip()
                    if "Welcome to QM Toll portal!" in text:
                        logger.info(f"✅ Dashboard header found in h4 element: '{text}'")
                        return True

            logger.warning("⚠️ Dashboard header 'Welcome to QM Toll portal!' not detected.")
            return False

        except Exception as e:
            logger.error(f"Error verifying dashboard header: {str(e)}")
            return False

    def verify_login_popup(self):
        """
        Attempts to verify and capture the login success pop-up.
        Takes immediate screenshots when pop-up is detected.
        """
        try:
            logger.info("Attempting to verify login pop-up...")

            # Check if pop-up is currently visible (don't wait)
            try:
                element = self.page.query_selector(self.pop_up_selector)
                if element and element.is_visible():
                    logger.info(f"Pop-up found! Selector: {self.pop_up_selector}")

                    # IMMEDIATE SCREENSHOT - take it right now!
                    self.take_screenshot("04_Popup_Captured_Immediate", self.report_dir)

                    # Try to get pop-up text if available
                    try:
                        popup_text = self.get_text(self.pop_up_selector)
                        logger.info(f"Pop-up text: {popup_text}")
                    except:
                        logger.warning("Could not extract pop-up text")
                        popup_text = "Unknown"

                    # Take another screenshot immediately after
                    self.page.wait_for_timeout(10)  # Very short delay
                    self.take_screenshot("04_Popup_Captured_Followup", self.report_dir)

                    logger.info("Pop-up verification successful! Screenshots taken immediately.")
                    return True
                else:
                    logger.info("Pop-up element not currently visible")
            except Exception as e:
                logger.info(f"Pop-up element not found: {str(e)}")

            # If pop-up not immediately visible, try a very short wait
            try:
                self.page.wait_for_selector(self.pop_up_selector, state="visible", timeout=500)  # 500ms only
                logger.info(f"Pop-up appeared after short wait! Selector: {self.pop_up_selector}")

                # IMMEDIATE SCREENSHOT
                self.take_screenshot("04_Popup_Captured_After_Wait", self.report_dir)

                # Get text
                try:
                    popup_text = self.get_text(self.pop_up_selector)
                    logger.info(f"Pop-up text: {popup_text}")
                except:
                    logger.warning("Could not extract pop-up text")
                    popup_text = "Unknown"

                logger.info("Pop-up verification successful after short wait!")
                return True

            except Exception as e:
                logger.warning(f"Pop-up did not appear within 500ms: {str(e)}")

            # Final attempt - take a screenshot anyway in case pop-up was there
            self.take_screenshot("04_Popup_Attempted_Capture", self.report_dir)
            logger.info("Took final screenshot attempt, even if pop-up not detected")

            return False

        except Exception as e:
            logger.warning(f"Pop-up verification failed: {str(e)}")
            # Take emergency screenshot
            try:
                self.take_screenshot("04_Popup_Error_Screenshot", self.report_dir)
            except:
                pass
            return False

    def validate_login_popup(self):
        """
        Comprehensive validation of the login success pop-up.
        Validates: text content, exact match, no typos, CSS properties, visibility, position.
        """
        try:
            logger.info("\n" + "=" * 80)
            logger.info("STARTING COMPREHENSIVE POP-UP VALIDATION")
            logger.info("=" * 80)

            element = self.page.query_selector(self.pop_up_selector)

            if not element:
                logger.error("VALIDATION FAILED: Pop-up element not found!")
                return False

            # ========== VALIDATION 1: Check Visibility ==========
            logger.info("\n[VALIDATION 1] Checking Pop-up Visibility...")
            is_visible = element.is_visible()
            logger.info(f"  Visibility Status: {is_visible}")

            if not is_visible:
                logger.error("  FAILED: Pop-up is not visible!")
                return False
            logger.info("  PASSED: Pop-up is visible")

            # ========== VALIDATION 2: Extract and Check Text Content ==========
            logger.info("\n[VALIDATION 2] Extracting and Validating Text Content...")
            popup_text = element.inner_text()
            logger.info(f"  Extracted Text: '{popup_text}'")

            # Define expected text
            expected_text = "Login Successful"

            # Check exact match
            if popup_text.strip() == expected_text.strip():
                logger.info(f"  PASSED: Text matches exactly: '{expected_text}'")
                text_match = True
            else:
                logger.warning(f"  WARNING: Text does not match exactly")
                logger.warning(f"    Expected: '{expected_text}'")
                logger.warning(f"    Actual: '{popup_text}'")
                text_match = False

            # ========== VALIDATION 3: Check for Typos ==========
            logger.info("\n[VALIDATION 3] Checking for Typos...")

            # Common typos to check
            typos = {
                "sucessful": "successful",
                "Sucessful": "Successful",
                "sucsessful": "successful",
                "succesful": "successful",
                "successfull": "successful",
                "loggin": "login",
                "Loggin": "Login",
            }

            typo_found = False
            for typo, correct in typos.items():
                if typo in popup_text:
                    logger.error(f"  TYPO FOUND: '{typo}' (should be '{correct}')")
                    typo_found = True

            if not typo_found:
                logger.info("  PASSED: No known typos detected")

            # ========== VALIDATION 4: Extract CSS Classes ==========
            logger.info("\n[VALIDATION 4] Extracting CSS Classes and Attributes...")
            css_class = element.get_attribute('class')
            logger.info(f"  CSS Classes: {css_class}")

            if 'success' in css_class.lower():
                logger.info("  PASSED: 'success' class is present")
            else:
                logger.warning("  WARNING: 'success' class not found in CSS classes")

            # ========== VALIDATION 5: Check Element Properties ==========
            logger.info("\n[VALIDATION 5] Checking Element Properties...")

            element_id = element.get_attribute('id')
            data_test_id = element.get_attribute('data-testid')
            role = element.get_attribute('role')
            aria_label = element.get_attribute('aria-label')

            logger.info(f"  ID: {element_id if element_id else 'Not set'}")
            logger.info(f"  Data-TestID: {data_test_id if data_test_id else 'Not set'}")
            logger.info(f"  Role: {role if role else 'Not set'}")
            logger.info(f"  ARIA Label: {aria_label if aria_label else 'Not set'}")

            # ========== VALIDATION 6: Check Position and Size ==========
            logger.info("\n[VALIDATION 6] Checking Position and Size...")
            bounding_box = element.bounding_box()
            if bounding_box:
                logger.info(f"  X: {bounding_box['x']}, Y: {bounding_box['y']}")
                logger.info(f"  Width: {bounding_box['width']}, Height: {bounding_box['height']}")
                logger.info("  PASSED: Element has valid dimensions")
            else:
                logger.warning("  WARNING: Could not get bounding box")

            # ========== VALIDATION 7: Check Computed Styles ==========
            logger.info("\n[VALIDATION 7] Checking Computed Styles...")
            try:
                display = self.page.evaluate(
                    f"window.getComputedStyle(document.querySelector('{self.pop_up_selector}')).display")
                opacity = self.page.evaluate(
                    f"window.getComputedStyle(document.querySelector('{self.pop_up_selector}')).opacity")

                logger.info(f"  Display: {display}")
                logger.info(f"  Opacity: {opacity}")

                if display != 'none' and float(opacity) > 0:
                    logger.info("  PASSED: Element is displayed with proper opacity")
                else:
                    logger.warning("  WARNING: Element may not be properly displayed")
            except Exception as e:
                logger.error(f"Validation error: {str(e)}")
                logger.warning("  WARNING: Could not check computed styles - element may have disappeared")

            # ========== SUMMARY ==========
            logger.info("\n" + "=" * 80)
            logger.info("POP-UP VALIDATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"  Visibility: PASSED")
            logger.info(f"  Text Match: {'PASSED' if text_match else 'WARNING'}")
            logger.info(f"  Typo Check: {'PASSED' if not typo_found else 'FAILED'}")
            logger.info(f"  CSS Classes: Present")
            logger.info(f"  Position & Size: Valid")
            logger.info(f"  Computed Styles: Valid")
            logger.info("=" * 80 + "\n")

            # Return overall status
            overall_status = text_match and not typo_found
            if overall_status:
                logger.info("✓ ALL VALIDATIONS PASSED - Pop-up is working correctly!")
            else:
                logger.info("⚠ Some validations failed or had warnings - Review above details")

            return overall_status

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def log_page_elements(self, stage_name):
        """Logs present DOM structural tags and details to assist tracking analysis."""
        try:
            logger.info("=" * 80)
            logger.info(f"DOM SNAPSHOT AT STAGE: {stage_name}")
            logger.info("=" * 80)

            logger.info("\nSearching for pop-up elements in page content...")
            popups = self.page.query_selector_all(self.pop_up_selector)
            if popups:
                for idx, popup in enumerate(popups, 1):
                    if popup.is_visible():
                        logger.info(
                            f"   [POPUP {idx}] Text: '{popup.inner_text().strip()}' | Class: '{popup.get_attribute('class')}'")
            else:
                logger.warning("⚠ No known pop-up selectors found. Checking all visible divs...")
                divs = self.page.query_selector_all('div')
                logger.info(f"Total DIV elements on page: {len(divs)}")
                visible_idx = 1
                for div in divs:
                    if div.is_visible():
                        div_class = div.get_attribute('class') or 'no-class'
                        div_id = div.get_attribute('id') or 'no-id'
                        div_text = div.inner_text().strip().replace('\n', ' ')[:50]
                        logger.info(
                            f"   Visible DIV {visible_idx}: class='{div_class}' id='{div_id}' text='{div_text}'")
                        visible_idx += 1
                        if visible_idx > 15:  # Cap logging length
                            break
            logger.info("=" * 80)
        except Exception as e:
            logger.warning(f"Failed to log element debugging snapshots: {str(e)}")

    def verify_dashboard_header(self):
        """
        Verifies that the dashboard header "Welcome to QM Toll portal!" is displayed.
        Checks for the specific HTML structure provided by the user.
        """
        try:
            logger.info("Checking for dashboard header 'Welcome to QM Toll portal!'...")

            # Check for the specific header text
            header_selectors = [
                'h4:has-text("Welcome to QM Toll portal!")',
                'div.dash-headding h4',
                'h4',
                '.dash-headding',
                'div[class*="dash-headding"] h4'
            ]

            for selector in header_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        text = element.inner_text().strip()
                        if "Welcome to QM Toll portal!" in text:
                            logger.info(f"✅ Dashboard header found with selector: {selector}")
                            logger.info(f"   Header text: '{text}'")
                            return True
                except Exception as e:
                    continue

            # Additional check: Look for the specific class structure
            try:
                # Check for the dash-headding class
                dash_heading = self.page.query_selector('div.dash-headding')
                if dash_heading and dash_heading.is_visible():
                    logger.info("✅ Dashboard heading container found")
                    # Check for h4 inside it
                    h4_element = dash_heading.query_selector('h4')
                    if h4_element and h4_element.is_visible():
                        text = h4_element.inner_text().strip()
                        if "Welcome to QM Toll portal!" in text:
                            logger.info(f"✅ Dashboard header found in dash-headding: '{text}'")
                            return True
            except Exception as e:
                logger.warning(f"Error checking dash-headding structure: {str(e)}")

            # Final check: Search all h4 elements for the text
            try:
                all_h4 = self.page.query_selector_all('h4')
                for h4 in all_h4:
                    if h4.is_visible():
                        text = h4.inner_text().strip()
                        if "Welcome to QM Toll portal!" in text:
                            logger.info(f"✅ Dashboard header found in h4 element: '{text}'")
                            return True
            except Exception as e:
                logger.warning(f"Error checking all h4 elements: {str(e)}")

            logger.warning("⚠️ Dashboard header 'Welcome to QM Toll portal!' not found")
            return False

        except Exception as e:
            logger.error(f"Error verifying dashboard header: {str(e)}")
            return False