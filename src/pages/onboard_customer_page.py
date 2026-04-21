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

        # Mapping Country to its Value and Phone Code
        self.country_map = {
            "United States": {"value": "US", "code": "+1"},
            "Mexico": {"value": "MX", "code": "+52"},
            "Canada": {"value": "CA", "code": "+1"}
        }

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
    def country_dropdown(self):
        return self.page.locator('select[formcontrolname="country"]')

    @property
    def state_dropdown(self):
        return self.page.locator('select[formcontrolname="state"]')

    @property
    def city_dropdown(self):
        return self.page.locator('select[formcontrolname="city"]')

    @property
    def address_line1_input(self):
        return self.page.locator('input[formcontrolname="address"]')

    @property
    def address_line2_input(self):
        return self.page.locator('input[formcontrolname="address1"]')

    @property
    def zip_code_input(self):
        return self.page.locator('input[formcontrolname="zipCode"]')

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
    def country_code_dropdown(self):
        return self.page.locator('select[formcontrolname="countryCode"]')

    @property
    def phone_number_input(self):
        return self.page.locator('input[formcontrolname="phoneNumber"]')

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

    def get_unique_identity(self):
        """Generates realistic names and ensures they haven't been used in previous runs."""
        file_path = "used_identities.csv"

        # Create CSV with headers if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["first_name", "last_name", "email"])

        # Load used names into a set for fast lookup
        used_names = set()  # ✅ ALWAYS define first

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)

            # Validate headers
            if not reader.fieldnames or 'first_name' not in reader.fieldnames:
                logger.warning("⚠️ CSV headers invalid. Recreating file...")

                with open(file_path, 'w', newline='') as fw:
                    writer = csv.writer(fw)
                    writer.writerow(["first_name", "last_name", "email"])

            else:
                for row in reader:
                    fname = row.get('first_name', '').strip()
                    lname = row.get('last_name', '').strip()

                    if fname and lname:
                        used_names.add(f"{fname}_{lname}".lower())

        while True:
            # Generate realistic names
            f_name = self.fake.first_name()
            l_name = self.fake.last_name()

            # Check length constraints (3-50 characters)
            if 3 <= len(f_name) <= 50 and 3 <= len(l_name) <= 50:
                identity_key = f"{f_name}_{l_name}".lower()

                if identity_key not in used_names:
                    email_val = f"{f_name.lower()}.{l_name.lower()}@testmail.com"

                    # Record the new unique identity
                    with open(file_path, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([f_name, l_name, email_val])

                    return f_name, l_name, email_val

    def _highlight_and_fill(self, locator, value, name):
        """Helper to scroll, highlight and fill."""
        try:
            locator.scroll_into_view_if_needed()
            self.page.wait_for_timeout(200)
            locator.evaluate(f"el => el.style.cssText += '{self.focus_style}'")
            locator.fill(value)
            logger.info(f"Filled {name}: {value}")
        except Exception as e:
            logger.warning(f"Could not highlight/fill {name}: {str(e)}")
            locator.fill(value)

    def _safe_check(self, locator, name):
        """Helper to scroll and check a checkbox."""
        try:
            locator.scroll_into_view_if_needed()
            if not locator.is_checked():
                locator.check(force=True)
                logger.info(f"Checked: {name}")
        except Exception as e:
            logger.warning(f"Could not check {name}: {str(e)}")

    def fill_and_submit_account_details(self, country_name="United States"):
        """Step 1: Demographic Info using Unique Registry and Realistic Names."""
        logger.info(f"Filling Onboarding details for {country_name}...")

        # --- Get unique names from the CSV registry ---
        f_name, l_name, email = self.get_unique_identity()
        middle_name = "QATeam"

        # Robust Account Type selection
        # Wait for stable DOM (VERY IMPORTANT)
        self.page.wait_for_load_state("networkidle")

        # Re-locate element fresh (avoid stale reference)
        dropdown = self.page.locator('select[formcontrolname="accountType"]').last

        # Wait until it is attached & stable
        dropdown.wait_for(state="attached", timeout=10000)
        dropdown.wait_for(state="visible", timeout=10000)

        # Retry logic (Angular-safe)
        for i in range(3):
            try:
                dropdown.select_option(value="PERSONAL")
                dropdown.dispatch_event("change")

                # Validate selection
                if dropdown.input_value() == "PERSONAL":
                    print("✅ Account Type selected successfully")
                    break
            except:
                self.page.wait_for_timeout(500)
        else:
            raise Exception("❌ Failed to select Account Type after retries")


        # 2. Select Category and Payment Model (New fields from your source)
        # Choosing 'Revenue' and 'Pre-paid' to satisfy mandatory fields
        # 2. Select Revenue Category
        self.revenue_category_radio.wait_for(state="visible", timeout=10000)
        self.revenue_category_radio.scroll_into_view_if_needed()
        self.revenue_category_radio.click(force=True)
        logger.info("Selected Revenue Category")

        # 3. Select Payment Model (Prepaid)
        self.payment_model_prepaid_radio.wait_for(state="visible", timeout=10000)
        self.payment_model_prepaid_radio.scroll_into_view_if_needed()
        self.payment_model_prepaid_radio.click(force=True)
        logger.info("Selected Payment Model: PREPAID")

        # 3. Fill Customer Details
        self._highlight_and_fill(self.first_name_input, f_name, "First Name")
        # RESTORED: Filling Middle Name with hardcoded value
        self._highlight_and_fill(self.middle_name_input, "QATeam", "Middle Name")
        self._highlight_and_fill(self.last_name_input, l_name, "Last Name")
        
        self._safe_check(self.same_billing_checkbox, "Use Same for Billing")
        self._safe_check(self.same_shipping_checkbox, "Use Same for Shipping")
        # Ensure 'Primary Address' is checked (id="primaryMailing" in your source)
        self.page.locator("#primaryMailing").check()

        country_data = self.country_map.get(country_name)
        self.country_dropdown.select_option(country_data["value"])
        self.page.wait_for_timeout(1000)

        # Select first available State/City (Angular dynamic dropdowns)
        self.state_dropdown.select_option(index=1)
        self.page.wait_for_timeout(500)
        self.city_dropdown.select_option(index=1)

        self._highlight_and_fill(self.address_line1_input, "123 Automation Way", "Address")
        self._highlight_and_fill(self.zip_code_input, "12345", "Zip Code")

        # 5. Contact Details
        self.country_code_dropdown.select_option(country_data["code"])
        random_phone = str(random.randint(7000000000, 9999999999))
        self._highlight_and_fill(self.phone_number_input, random_phone, "Unique Phone Number")

        self._highlight_and_fill(self.email_address_input, email, "Email")
        self._highlight_and_fill(self.confirm_email_address_input, email, "Confirm Email")

        # 6. Submit
        logger.info("Clicking 'Save & Next'...")
        self.confirm_email_address_input.dispatch_event("blur")
        self.page.wait_for_timeout(500)
        self.save_next_button.click(force=True)

        try:
            success_msg = self.page.locator('div.snackbar.success-snackbar').get_by_text(
                "Temporary Account successfully created")
            success_msg.first.wait_for(state="attached", timeout=15000)
            logger.info(f"Successfully verified Step 1 for: {f_name} {l_name}")
            return True
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False

    def get_temp_account_id(self):
        """Retrieves the Temporary Account ID."""
        try:
            account_span = self.page.locator('ul > li:has-text("Account Ref ID :") > span')
            account_span.wait_for(state="visible", timeout=15000)
            account_id = account_span.inner_text().strip()
            logger.info(f"Retrieved Temporary Account ID: {account_id}")
            return account_id
        except Exception as e:
            logger.error(f"Failed to retrieve Account ID: {str(e)}")
            return "ID_NOT_FOUND"

    def hide_chatbot(self):
        """Hides the chatbot icon via CSS to prevent overlap issues."""
        try:
            # Note: Ensure '.chatbot-selector' matches the actual class of the icon
            self.page.add_style_tag(content=".chatbot-selector { display: none !important; }")
            logger.info("Chatbot icon hidden via CSS injection.")
        except Exception as e:
            logger.warning(f"Could not hide chatbot: {str(e)}")

    def fill_vehicle_details(self, count=2):
        """Step 2: Vehicles & Tags with Blur event to clear focus highlights."""
        logger.info(f"Starting Step 2: Adding {count} Vehicle(s)...")
        for i in range(count):
            plate_num = f"QA{random.randint(1000, 9999)}GP"

            # 1. Fill and then Blur Plate Number to remove highlight
            self._highlight_and_fill(self.plate_number_input, plate_num, f"Plate Number {i + 1}")
            self.plate_number_input.dispatch_event("blur")

            self.plate_country_dropdown.select_option("US")
            self.page.wait_for_timeout(500)
            self.plate_state_dropdown.select_option(index=1)

            self.vehicle_class_dropdown.select_option("2")
            self.vehicle_class_dropdown.dispatch_event("change")

            self.page.locator('select[formcontrolname="vehicleMake"]').select_option(label="AUDI")
            self.page.wait_for_timeout(500)
            self.page.locator('select[formcontrolname="vehicleModel"]').select_option(index=1)
            self.page.locator('select[formcontrolname="vehicleColor"]').select_option(label="White")

            today_date = datetime.now().strftime("%Y-%m-%d")

            # 2. Fill and then Blur Plate Start Date to remove highlight
            self._highlight_and_fill(self.plate_start_date_input, today_date, "Plate Start Date")
            self.plate_start_date_input.dispatch_event("blur")

            self.request_tag_radio.click(force=True)
            self.page.wait_for_timeout(1000)

            self.tag_mode_dropdown.select_option("BUY")
            self.tag_mode_dropdown.dispatch_event("change")
            self.page.wait_for_timeout(1000)

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

            self.add_vehicle_button.click(force=True)
            self.page.wait_for_timeout(2000)
            logger.info(f"Vehicle {i + 1} added.")

        # Final navigation remains the same...
        self.page.wait_for_timeout(1000)
        next_btn = self.page.get_by_role("button", name="Next")
        self.hide_chatbot()
        next_btn.evaluate("node => node.click()")
        self.permanent_account_id_span.wait_for(state="attached", timeout=15000)
        return True

    def get_permanent_account_id(self):
        """Captures and returns the Permanent Account ID from the Payment Info page."""
        try:
            # 1. Ensure the element is visible after navigation
            self.permanent_account_id_span.wait_for(state="visible", timeout=15000)

            # 2. Extract and clean the ID text
            account_id = self.permanent_account_id_span.inner_text().strip()

            # 3. Log to console and logger
            print(f"\n[CONFIRMED] Permanent Account Number: {account_id}")
            logger.info(f"Captured Permanent Account Number: {account_id}")

            return account_id
        except Exception as e:
            logger.error(f"Failed to capture Permanent Account Number: {str(e)}")
            return None

    def generate_random_payment_data(self):
        """Generates random data meeting specific field requirements."""
        name_length = random.randint(5, 45)
        full_name = "".join(random.choices(string.ascii_letters, k=name_length))
        card_number = "".join(random.choices(string.digits, k=16))
        future_date = datetime.now() + timedelta(days=730)
        expiry_date = future_date.strftime("%m/%y")
        cvv = "".join(random.choices(string.digits, k=3))
        return full_name, card_number, expiry_date, cvv

    def fill_payment_details(self, card_count=1):
        """Step 3: Payment Information with sequential Card names (CardOne to CardFive)."""
        logger.info("Starting Step 3: Payment Information...")
        try:
            # 1. Ensure the "Save and Pay" tab is selected and active
            logger.info("Activating 'Save and Pay' tab...")
            self.save_and_pay_tab.click(force=True)
            self.page.wait_for_timeout(1000)

            # 2. Select "Credit Card" from the dropdown
            logger.info("Selecting 'Credit Card'...")
            self.payment_method_dropdown.scroll_into_view_if_needed()
            self.payment_method_dropdown.wait_for(state="visible", timeout=10000)
            self.payment_method_dropdown.select_option(label="Credit Card")
            self.payment_method_dropdown.dispatch_event("change")

            # Mapping for sequential card names
            card_name_map = {1: "CardOne", 2: "CardTwo", 3: "CardThree", 4: "CardFour", 5: "CardFive"}

            for i in range(1, card_count + 1):
                # 3. Click 'Add Payment Method'
                logger.info(f"Opening 'Add Payment Method' modal for Card {i}...")
                self.add_payment_method_button.wait_for(state="visible", timeout=10000)
                self.add_payment_method_button.evaluate("node => node.click()")

                # 4. Fill 'Add Card' Modal
                self.page.wait_for_selector('.modal-content', state="visible", timeout=10000)

                # Get the sequential name (e.g., CardOne)
                card_name = card_name_map.get(i, f"Card{i}")
                _, number, expiry, cvv = self.generate_random_payment_data()

                # Use the sequential name instead of random characters
                self._highlight_and_fill(self.card_name_input, card_name, "Cardholder Name")
                self._highlight_and_fill(self.card_number_input, number, "Card Number")
                self._highlight_and_fill(self.expiry_date_input, expiry, "Expiry Date")
                self._highlight_and_fill(self.cvv_input, cvv, "CVV")

                logger.info(f"Clicking 'Add Card' submit for {card_name}...")
                self.add_card_submit_button.click(force=True)
                self.page.wait_for_selector('.modal-content', state="hidden", timeout=15000)
                self.page.wait_for_timeout(1000)

            # 5. Select the added card in the table
            logger.info("Selecting the first Credit Card from the list...")
            self.credit_card_radio_button.first.scroll_into_view_if_needed()
            self.credit_card_radio_button.first.check(force=True)

            # 6. Click 'Preview and Pay'
            logger.info("Clicking 'Preview and Pay'...")
            self.preview_and_pay_button.scroll_into_view_if_needed()
            expect(self.preview_and_pay_button).to_be_enabled(timeout=10000)
            self.preview_and_pay_button.click(force=True)

            # 7. Click 'PAY' on the Summary Page
            logger.info("Waiting for Payment Summary card...")
            self.page.wait_for_selector("div.payment-summary-card", state="visible", timeout=15000)
            self.summary_page_pay_button.wait_for(state="visible", timeout=10000)
            self.summary_page_pay_button.click(force=True)

            logger.info("✅ Step 3 (Payment & Summary) complete.")
            return True
        except Exception as e:
            logger.error(f"Payment Step Error: {str(e)}")
            return False

    def complete_final_payment(self):
        """Step 5: Final Confirmation Modal Submission"""
        logger.info("Starting Final Confirmation Modal...")
        try:
            # 1. Wait for the 'Payment Confirmation' pop-up modal to appear
            logger.info("Waiting for Payment Confirmation modal...")
            self.confirmation_modal_pay_button.wait_for(state="visible", timeout=15000)

            # 2. Highlight and click the very last 'Pay' button
            self.confirmation_modal_pay_button.evaluate(f"el => el.style.cssText += '{self.focus_style}'")
            logger.info("Clicking the final 'Pay' button inside the Confirmation Modal...")
            self.confirmation_modal_pay_button.click(force=True)

            # 3. Wait for modal to disappear and verify completion
            self.page.wait_for_selector('div.modal-content', state="hidden", timeout=15000)
            self.page.wait_for_timeout(2000)
            logger.info("✅ Account onboarding completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Final Confirmation Modal Failed: {str(e)}")
            return False

    def navigate_to_account_summary(self):
        """Step 6: Click 'Account Summary' after successful payment."""
        logger.info("Finalizing process: Clicking 'Account Summary' button...")
        try:
            # 1. Wait for the success window to be visible
            self.account_summary_button.wait_for(state="visible", timeout=15000)

            # 2. Highlight and click
            self.account_summary_button.evaluate(f"el => el.style.cssText += '{self.focus_style}'")
            self.account_summary_button.click(force=True)

            logger.info("✅ Navigating to Account Summary page.")
            return True
        except Exception as e:
            logger.error(f"Failed to click Account Summary: {str(e)}")
            return False