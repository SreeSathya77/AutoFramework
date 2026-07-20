import os
import re
import csv
import random
import string
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from faker import Faker
from .base_page import BasePage
from utils.logger import Logger

logger = Logger.get_logger()


class OnboardCustomerPage(BasePage):
    def __init__(self, page: Page, report_dir: str = None):
        super().__init__(page, report_dir)
        self.fake = Faker('en_IN')
        self.focus_style = "outline: 4px solid rgba(0, 191, 255, 0.6); outline-offset: 2px; transition: all 0.3s ease;"

        self.country_map = {
            "United States": {"value": "US", "code": "+1"},
            "Mexico": {"value": "MX", "code": "+52"},
            "Canada": {"value": "CA", "code": "+1"}
        }

    # --- Navigation Locators ---
    @property
    def workbench_icon(self):
        return self.page.locator('span[apphosttooltip="Workbench"]')

    @property
    def manage_accounts_toggle(self):
        return self.page.locator('a.nav-link').filter(has_text="Manage Accounts")

    @property
    def onboard_customer_link(self):
        return self.page.locator('a[href*="onboard-a-customer"]')

    # --- Step 1 Locators ---
    @property
    def account_type_dropdown(self):
        return self.page.locator('select[formcontrolname="accountType"]')

    @property
    def revenue_category_radio(self):
        return self.page.locator('input[formcontrolname="revenueCategory"]').first

    @property
    def payment_model_prepaid_radio(self):
        return self.page.locator('input[formcontrolname="paymentModel"][value="PREPAID"]')

    @property
    def first_name_input(self):
        return self.page.locator('input[formcontrolname="firstName"]')

    @property
    def middle_name_input(self):
        return self.page.locator('input[formcontrolname="middleName"]')

    @property
    def last_name_input(self):
        return self.page.locator('input[formcontrolname="lastName"]')

    @property
    def same_billing_checkbox(self):
        return self.page.locator('input[formcontrolname="useSameForBilling"]')

    @property
    def same_shipping_checkbox(self):
        return self.page.locator('input[formcontrolname="useSameForShipping"]')

    @property
    def primary_address_checkbox(self):
        return self.page.locator('#primaryMailing')

    @property
    def email_address_input(self):
        return self.page.locator('input[formcontrolname="emailAddress"]')

    @property
    def confirm_email_address_input(self):
        return self.page.locator('input[formcontrolname="confirmEmailAddress"]')

    @property
    def save_next_button(self):
        return self.page.get_by_role("button", name="Save & Next")

    # --- Step 2 Locators ---
    @property
    def permanent_account_id_span(self):
        """The Permanent Account ID displayed on the Payment Info page."""
        return self.page.locator('div.acount-details li:has-text("Account Id:") span')

    @property
    def plate_number_input(self):
        return self.page.locator('input[formcontrolname="plateNumber"]')

    @property
    def plate_country_dropdown(self):
        return self.page.locator('select[formcontrolname="plateCountry"]')

    @property
    def plate_state_dropdown(self):
        return self.page.locator('select[formcontrolname="plateState"]')

    @property
    def vehicle_class_dropdown(self):
        return self.page.locator('select[formcontrolname="vehicleClass"]')

    @property
    def vehicle_make_dropdown(self):
        return self.page.locator('select[formcontrolname="vehicleMake"]')

    @property
    def vehicle_model_dropdown(self):
        return self.page.locator('select[formcontrolname="vehicleModel"]')

    @property
    def vehicle_color_dropdown(self):
        return self.page.locator('select[formcontrolname="vehicleColor"]')

    @property
    def plate_start_date_input(self):
        return self.page.locator('input[formcontrolname="plateRegistrationStartDate"]')

    @property
    def request_tag_radio(self):
        # Targets the radio button input specifically associated with the 'Request Tag' label
        return self.page.locator('div.form-check:has-text("Request Tag") input[type="radio"]')

    @property
    def tag_mode_dropdown(self):
        return self.page.locator('select[formcontrolname="mode"]')

    @property
    def tag_item_type_dropdown(self):
        return self.page.locator('select[formcontrolname="itemType"]')

    @property
    def tag_type_dropdown(self):
        return self.page.locator('select[formcontrolname="tagType"]')

    @property
    def tag_mounting_dropdown(self):
        return self.page.locator('select[formcontrolname="mounting"]')

    @property
    def tag_delivery_method_dropdown(self):
        return self.page.locator('select[formcontrolname="tagDeliveryMethod"]')

    @property
    def tag_retailer_location_dropdown(self):
        return self.page.locator('select[formcontrolname="retailerLocation"]')

    @property
    def add_vehicle_button(self):
        # Targets the button by class and partial text to handle dynamic label changes
        return self.page.locator('button.qm-btn-primary-bordered').filter(has_text="Add")

    # --- Step 3 Locators (Payment Info) ---
    @property
    def payment_method_dropdown(self):
        """Locator for the Payment Method dropdown within the active tab."""
        return self.page.locator('select[name="paymentMethod"]')

    @property
    def add_payment_method_button(self):
        """The button to open the card details modal."""
        return self.page.get_by_role("button", name="Add Payment Method")

    @property
    def save_and_pay_tab(self):
        """The 'Save and Pay' tab label."""
        return self.page.locator('span.mdc-tab__text-label', has_text="Save and Pay")

    @property
    def submit_payment_button(self):
        return self.page.locator('button.qm-btn-primary.p-3.mt-3')

    @property
    def card_name_input(self):
        return self.page.locator('#fullName')

    @property
    def card_number_input(self):
        return self.page.locator('#cardNumber')

    @property
    def expiry_date_input(self):
        return self.page.locator('#expirationDate')

    @property
    def cvv_input(self):
        return self.page.locator('#cvvNumber')

    @property
    def add_card_submit_button(self):
        return self.page.locator('button[type="submit"].qm-btn-primary:has-text("Add Card")')

    @property
    def credit_card_radio_button(self):
        # Targets the radio button in the row containing 'Credit Card'
        return self.page.locator('tr').filter(has_text="Credit Card").locator('input[type="radio"]')

    @property
    def preview_and_pay_button(self):
        """1. The blue button on the initial Payment Info tab."""
        return self.page.get_by_role("button", name="Preview and Pay")

    @property
    def summary_page_pay_button(self):
        """2. The 'PAY' button in the Summary Card (Preview Page) before the modal."""
        summary_card = self.page.locator("div.payment-summary-card")
        return summary_card.locator("button.confirm-btn").filter(has_text=re.compile(r"PAY", re.IGNORECASE))

    @property
    def confirmation_modal_pay_button(self):
        """3. The final 'Pay' button inside the Confirmation Modal pop-up."""
        modal = self.page.locator('div.modal-content').filter(has_text="Payment Confirmation")
        return modal.locator('button.qm-btn-primary').filter(has_text=re.compile(r"^\s*Pay\s*$", re.IGNORECASE))

    @property
    def account_summary_button(self):
        """The 'Account Summary' button on the Payment Successful window."""
        return self.page.locator('div.modal-content1 button').filter(has_text="Account Summary")

    # --- HELPER METHODS ---

    def _highlight_and_fill(self, locator, value, name):
        try:
            locator.scroll_into_view_if_needed()
            locator.evaluate(f"el => el.style.cssText += '{self.focus_style}'")
            locator.fill(value)
            logger.info(f"Filled {name}: {value}")
        except Exception as e:
            logger.warning(f"Highlight/Fill failed for {name}: {str(e)}")
            locator.fill(value)

    def _safe_check(self, locator, name):
        try:
            locator.scroll_into_view_if_needed()
            if not locator.is_checked():
                locator.check(force=True)
                logger.info(f"Checked: {name}")
        except Exception as e:
            logger.warning(f"Could not check {name}: {str(e)}")

    def hide_chatbot(self):
        """Injects a CSS rule to permanently hide chatbot and intercepting widgets."""
        try:
            self.page.add_style_tag(content="""
                .chatbot-icon, #chat-widget-container, .drift-frame-controller, 
                #freshworks-frame, .intercom-launcher, .chatbot-selector,
                iframe[title="Chat window"] { 
                    display: none !important; 
                    visibility: hidden !important;
                    pointer-events: none !important;
                }
            """)
            logger.info("Chatbot elements hidden via CSS injection.")
        except Exception:
            pass

    # --- MAIN ACTIONS ---

    def navigate_to_onboarding(self):
        logger.info("Executing Sidebar Navigation Sequence...")
        try:
            self.workbench_icon.wait_for(state="visible", timeout=10000)
            self.workbench_icon.click()
            self.page.wait_for_timeout(500)
            self.manage_accounts_toggle.wait_for(state="visible", timeout=5000)
            self.manage_accounts_toggle.click()
            self.onboard_customer_link.wait_for(state="visible", timeout=5000)
            self.onboard_customer_link.click()
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"Navigation Failure: {str(e)}")
            raise

    def get_unique_identity(self):
        f_name, l_name = self.fake.first_name(), self.fake.last_name()
        email = f"{f_name.lower()}.{l_name.lower()}{random.randint(10, 99)}@testmail.com"
        return f_name, l_name, email

    def fill_and_submit_account_details(self, country_name="United States"):
        logger.info("Filling Step 1: Account Details...")
        f_name, l_name, email = self.get_unique_identity()

        self.account_type_dropdown.wait_for(state="visible", timeout=15000)
        self.account_type_dropdown.select_option("PERSONAL")
        self.revenue_category_radio.click(force=True)
        self.payment_model_prepaid_radio.click(force=True)

        self._highlight_and_fill(self.first_name_input, f_name, "First Name")
        # Restored: Filling Middle Name with hardcoded value
        self._highlight_and_fill(self.middle_name_input, "QA Team", "Middle Name")
        self._highlight_and_fill(self.last_name_input, l_name, "Last Name")

        self._safe_check(self.same_billing_checkbox, "Use Same for Billing")
        self._safe_check(self.same_shipping_checkbox, "Use Same for Shipping")
        self._safe_check(self.primary_address_checkbox, "Primary Address")

        country_data = self.country_map.get(country_name)
        self.page.locator('select[formcontrolname="country"]').select_option(country_data["value"])
        self.page.wait_for_timeout(500)
        self.page.locator('select[formcontrolname="state"]').select_option(index=1)
        self.page.locator('select[formcontrolname="city"]').select_option(index=1)

        self._highlight_and_fill(self.page.locator('input[formcontrolname="address"]'), "123 Automation Blvd", "Address")
        self._highlight_and_fill(self.page.locator('input[formcontrolname="zipCode"]'), "12345", "Zip Code")

        self.page.locator('select[formcontrolname="countryCode"]').select_option(country_data["code"])
        self._highlight_and_fill(self.page.locator('input[formcontrolname="phoneNumber"]'),
                                 str(random.randint(7000000000, 9999999999)), "Phone")
        self._highlight_and_fill(self.email_address_input, email, "Email")
        self._highlight_and_fill(self.confirm_email_address_input, email, "Confirm Email")

        logger.info("Clicking Save & Next...")
        # --- ENHANCED FINALIZATION ---
        logger.info("Finalizing Step 1: Disabling chatbot interference...")

        # 1. First, hide and physically remove the chatbot from the DOM
        # This prevents it from receiving any 'click' events entirely
        self.hide_chatbot()
        self.page.evaluate("""() => {
                    const chatbot = document.querySelector('app-chatbot, #chat-widget-container, .chatbot-selector');
                    if (chatbot) { chatbot.remove(); }

                    // Also remove the Angular backdrop which often intercepts clicks
                    document.querySelectorAll('.cdk-overlay-backdrop').forEach(el => el.remove());
                }""")

        # 2. Scroll the button into view but away from the bottom corner
        # (Where chatbots usually live)
        self.save_next_button.evaluate("el => el.scrollIntoView({block: 'center'})")
        self.page.wait_for_timeout(500)

        # 3. Perform an Atomic JS Click
        # This triggers the button handler without a physical mouse coordinate click
        logger.info("Triggering Atomic Click on Save & Next...")
        self.save_next_button.evaluate("el => el.click()")

        logger.info("Step 1 Submitted - Navigation to Vehicles should be clean.")
        return True

    def fill_vehicle_details(self, count=1):
        logger.info(f"Adding {count} Vehicle(s)...")
        try:
            self.plate_number_input.wait_for(state="visible", timeout=15000)
            logger.info("Step 2 loaded successfully.")
        except Exception:
            raise

        for i in range(count):
            # Ensuring any widgets are gone before each interaction
            self.hide_chatbot()

            plate_num = f"QA{random.randint(1000, 9999)}GP"
            self._highlight_and_fill(self.plate_number_input, plate_num, f"Plate {i + 1}")
            self.page.locator('select[formcontrolname="plateCountry"]').select_option("US")
            self.page.locator('select[formcontrolname="plateState"]').select_option(index=1)
            self.page.locator('select[formcontrolname="vehicleClass"]').select_option("2")
            self.page.locator('select[formcontrolname="vehicleMake"]').select_option(label="AUDI")
            self.page.locator('select[formcontrolname="vehicleModel"]').select_option(index=1)
            self.page.locator('select[formcontrolname="vehicleColor"]').select_option(label="White")

            today_date = datetime.now().strftime("%Y-%m-%d")
            self._highlight_and_fill(self.plate_start_date_input, today_date, "Plate Start Date")
            self.plate_start_date_input.dispatch_event("blur")

            self.request_tag_radio.click(force=True)
            self.page.wait_for_timeout(500)
            self.tag_mode_dropdown.select_option("BUY")
            self.tag_mode_dropdown.dispatch_event("change")
            self.page.wait_for_timeout(500)

            tag_selections = {
                'itemType': "QBOS_Class_Three",
                'tagType': "Regular",
                'mounting': "Windshield",
                'tagDeliveryMethod': "Mail To Customer",
                'retailerLocation': "NewYork"
            }
            for control, value in tag_selections.items():
                loc = self.page.locator(f'select[formcontrolname="{control}"]')
                loc.select_option(value=value) if control == 'itemType' else loc.select_option(label=value)
                loc.dispatch_event("change")
                self.page.wait_for_timeout(300)

            # Robust Click on Add Button using direct JS handler
            logger.info(f"Clicking 'Add' button for Vehicle {i+1}...")
            self.hide_chatbot()
            self.add_vehicle_button.scroll_into_view_if_needed()
            self.add_vehicle_button.evaluate("el => el.style.cssText += 'outline: 4px solid red;'")
            
            # Using evaluate click to ensure the handler triggers even if obscured
            self.add_vehicle_button.evaluate("el => el.click()")
            
            # GAP FOR VISUAL FEEDBACK: Wait for vehicle list to update
            self.page.wait_for_timeout(500)
            logger.info(f"Vehicle {i + 1} added successfully.")

        # GAP FOR VISUAL FEEDBACK: Before moving to Next page
        self.page.wait_for_timeout(500)
        next_btn = self.page.get_by_role("button", name="Next")
        
        # HIGHLIGHT AND CLICK NEXT
        logger.info("Highlighting and clicking 'Next' button...")
        self.hide_chatbot()
        
        # ADDED: Explicit scroll to ensure visibility
        next_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)

        next_btn.evaluate("el => el.style.cssText += 'outline: 4px solid red;'")
        next_btn.evaluate("el => el.click()")
        
        self.permanent_account_id_span.wait_for(state="attached", timeout=15000)
        return True

    def get_permanent_account_id(self):
        try:
            self.permanent_account_id_span.wait_for(state="visible", timeout=15000)
            account_id = self.permanent_account_id_span.inner_text().strip()
            logger.info(f"Captured Permanent Account Number: {account_id}")
            return account_id
        except Exception as e:
            logger.error(f"Failed to capture Permanent Account Number: {str(e)}")
            return None

    def generate_random_payment_data(self):
        name_length = random.randint(5, 45)
        full_name = "".join(random.choices(string.ascii_letters, k=name_length))
        card_number = "".join(random.choices(string.digits, k=16))
        future_date = datetime.now() + timedelta(days=730)
        expiry_date = future_date.strftime("%m/%y")
        cvv = "".join(random.choices(string.digits, k=3))
        return full_name, card_number, expiry_date, cvv

    def fill_payment_details(self, card_count=1):
        logger.info("Starting Step 3: Payment Information...")
        try:
            # Ensuring any widgets are gone before interaction
            self.hide_chatbot()

            self.save_and_pay_tab.click(force=True)
            self.page.wait_for_timeout(500)
            self.payment_method_dropdown.select_option(label="Credit Card")
            self.payment_method_dropdown.dispatch_event("change")

            for i in range(card_count):
                self.add_payment_method_button.evaluate("el => el.click()")
                self.page.wait_for_selector('.modal-content', state="visible", timeout=10000)
                name, number, expiry, cvv = self.generate_random_payment_data()
                self._highlight_and_fill(self.card_name_input, name, "Cardholder Name")
                self._highlight_and_fill(self.card_number_input, number, "Card Number")
                self._highlight_and_fill(self.expiry_date_input, expiry, "Expiry Date")
                self._highlight_and_fill(self.cvv_input, cvv, "CVV")
                self.add_card_submit_button.click(force=True)
                self.page.wait_for_selector('.modal-content', state="hidden", timeout=15000)

            self.credit_card_radio_button.first.check(force=True)
            self.page.wait_for_timeout(500) # Small delay for selection to settle

            # ROBUST PREVIEW & PAY CLICK
            logger.info("Clicking 'Preview and Pay'...")
            self.hide_chatbot()
            self.preview_and_pay_button.scroll_into_view_if_needed()
            self.preview_and_pay_button.evaluate("el => el.style.cssText += 'outline: 4px solid red;'")
            
            # Using evaluate click to ensure the handler triggers
            self.preview_and_pay_button.evaluate("el => el.click()")

            logger.info("Waiting for Payment Summary card...")
            self.page.wait_for_selector("div.payment-summary-card", state="visible", timeout=15000)
            
            # ROBUST SUMMARY PAY CLICK
            self.summary_page_pay_button.wait_for(state="visible", timeout=10000)
            self.summary_page_pay_button.evaluate("el => el.click()")

            return True
        except Exception as e:
            logger.error(f"Payment Step Error: {str(e)}")
            return False

    def complete_final_payment(self):
        logger.info("Starting Final Confirmation Modal...")
        try:
            self.confirmation_modal_pay_button.wait_for(state="visible", timeout=15000)
            self.confirmation_modal_pay_button.evaluate("el => el.click()")
            self.page.wait_for_selector('div.modal-content', state="hidden", timeout=15000)
            logger.info("✅ Account onboarding completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Final Confirmation Modal Failed: {str(e)}")
            return False

    def navigate_to_account_summary(self):
        logger.info("Finalizing process: Clicking 'Account Summary' button...")
        try:
            self.account_summary_button.wait_for(state="visible", timeout=15000)
            self.account_summary_button.evaluate("el => el.click()")
            return True
        except Exception as e:
            logger.error(f"Failed to click Account Summary: {str(e)}")
            return False
