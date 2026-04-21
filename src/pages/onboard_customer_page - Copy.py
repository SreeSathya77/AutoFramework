import os
import re
import random
from datetime import datetime
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

    # Locators
    @property
    def account_type_dropdown(self): return self.page.locator('select[formcontrolname="accountType"]')
    @property
    def first_name_input(self): return self.page.locator('input[formcontrolname="firstName"]')
    @property
    def last_name_input(self): return self.page.locator('input[formcontrolname="lastName"]')
    
    # Address Section Locators
    @property
    def country_dropdown(self): return self.page.locator('select[formcontrolname="country"]')
    @property
    def state_dropdown(self): return self.page.locator('select[formcontrolname="state"]')
    @property
    def city_dropdown(self): return self.page.locator('select[formcontrolname="city"]')
    @property
    def address_line1_input(self): return self.page.locator('input[formcontrolname="address"]')
    @property
    def address_line2_input(self): return self.page.locator('input[formcontrolname="address1"]')
    @property
    def zip_code_input(self): return self.page.locator('input[formcontrolname="zipCode"]')
    
    # Checkboxes
    @property
    def same_billing_checkbox(self): return self.page.locator('input[formcontrolname="useSameForBilling"]')
    @property
    def same_shipping_checkbox(self): return self.page.locator('input[formcontrolname="useSameForShipping"]')
    @property
    def primary_address_checkbox(self): return self.page.locator('#primaryMailing')
    
    # Contact Section Locators
    @property
    def country_code_dropdown(self): return self.page.locator('select[formcontrolname="countryCode"]')
    @property
    def phone_number_input(self): return self.page.locator('input[formcontrolname="phoneNumber"]')
    @property
    def email_address_input(self): return self.page.locator('input[formcontrolname="emailAddress"]')
    @property
    def confirm_email_address_input(self): return self.page.locator('input[formcontrolname="confirmEmailAddress"]')
    
    @property
    def save_next_button(self): return self.page.get_by_role("button", name="Save & Next")

    # --- New Locators for Step 2: Vehicles & Tags ---
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
        return self.page.locator('div.form-check').filter(has_text="Request Tag").locator('input[type="radio"]')

    @property
    def tag_alias_name_input(self):
        return self.page.locator('input[formcontrolname="tagAliasName"]')

    @property
    def add_vehicle_button(self):
        return self.page.locator('button:has-text("Add Vehicle")')

    @property
    def next_step_button(self):
        return self.page.locator('button:has-text("Next")')

    def fill_vehicle_details(self):
        """Refactored logic for Requirement 2: Step 2 (Vehicles & Tags)"""
        logger.info("Filling Vehicle and Tag details...")

        # 1. Vehicle Information
        plate = f"QA{random.randint(100, 999)}TB"
        self._highlight_and_fill(self.plate_number_input, plate, "Plate Number")

        self.plate_country_dropdown.select_option("US")
        self.plate_state_dropdown.select_option("AZ")
        self.vehicle_class_dropdown.select_option("2")

        # Select first available for Make/Model/Color
        for dropdown in [self.vehicle_make_dropdown, self.vehicle_model_dropdown, self.vehicle_color_dropdown]:
            dropdown.select_option(index=1)

        self._highlight_and_fill(self.plate_start_date_input, datetime.now().strftime("%Y-%m-%d"), "Start Date")

        # 2. Tag Request
        logger.info("Selecting 'Request Tag'...")
        self.request_tag_radio.check()

        # Tag detail dropdowns
        self.page.locator('select[formcontrolname="mode"]').select_option("BUY")
        self.page.locator('select[formcontrolname="itemType"]').select_option("STICKER_TAG")
        self.page.locator('select[formcontrolname="tagType"]').select_option("Regular")
        self.page.locator('select[formcontrolname="mounting"]').select_option("WINDSHIELD")
        self.page.locator('select[formcontrolname="tagDeliveryMethod"]').select_option("Mail To Customer")

        # Random Retailer
        retailer_loc = self.page.locator('select[formcontrolname="retailerLocation"]')
        retailer_loc.select_option(index=1)

        self._highlight_and_fill(self.tag_alias_name_input, f"TAG-{plate}", "Tag Alias")

        # 3. Add and Proceed
        self.take_screenshot("05_Step2_Filled_Data")
        self.add_vehicle_button.click()

        # Verify Vehicle added to the grid
        try:
            success_msg = self.page.locator("text=Vehicle added successfully").last
            success_msg.wait_for(state="visible", timeout=8000)
            logger.info("✅ Vehicle added to the grid successfully.")
            self.take_screenshot("06_Step2_Vehicle_Added")
        except:
            logger.warning("Could not confirm 'Vehicle added' message, proceeding anyway.")

        logger.info("Clicking 'Next' to move to Step 3...")
        self.next_step_button.click()

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
                locator.check()
                logger.info(f"Checked: {name}")
        except Exception as e:
            logger.warning(f"Could not check {name}: {str(e)}")

    def fill_and_submit_account_details(self, country_name=None):
        """
        Step 1: Demographic Info (Personal & Account)
        If country_name is None, it randomly selects a country from the map.
        """
        # RANDOM SELECTION LOGIC
        if country_name is None:
            country_name = random.choice(list(self.country_map.keys()))
            logger.info(f"🎲 Randomly selected Country: {country_name}")
        else:
            logger.info(f"Using provided Country: {country_name}")

        country_data = self.country_map.get(country_name)

        # 1. Select Account Type
        self.account_type_dropdown.select_option("PERSONAL")

        # 2. Fill Names
        f_name = self.fake.first_name()
        self._highlight_and_fill(self.first_name_input, f_name, "First Name")
        self._highlight_and_fill(self.last_name_input, self.fake.last_name(), "Last Name")

        # 3. Handle Checkboxes
        self._safe_check(self.same_billing_checkbox, "Use Same for Billing")
        self._safe_check(self.same_shipping_checkbox, "Use Same for Shipping")
        self._safe_check(self.primary_address_checkbox, "Primary Address")

        # 4. Select Location (Linked to Country)
        self.country_dropdown.select_option(country_data["value"])
        logger.info(f"Selected Country: {country_name} ({country_data['value']})")
        
        self.page.wait_for_timeout(1000)
        self.state_dropdown.select_option(index=1)
        self.page.wait_for_timeout(500)
        self.city_dropdown.select_option(index=1)

        # 5. Fill Address
        self._highlight_and_fill(self.address_line1_input, "123 Automation Lane", "Address Line 1")
        self._highlight_and_fill(self.zip_code_input, "12345", "Zip Code")

        # 6. Fill Contact Info (Dynamically linked to Country)
        logger.info(f"Selecting Country Code: {country_data['code']} based on {country_name}")
        self.country_code_dropdown.select_option(country_data["code"])
        self._highlight_and_fill(self.phone_number_input, str(random.randint(7000000000, 9999999999)), "Random Phone Number")
        
        email = f"auto_{f_name.lower()}_{datetime.now().strftime('%H%M%S')}@test.com"
        self._highlight_and_fill(self.email_address_input, email, "Email")
        self._highlight_and_fill(self.confirm_email_address_input, email, "Confirm Email")

        # 7. Submit
        logger.info("Clicking 'Save & Next'...")
        self.save_next_button.scroll_into_view_if_needed()
        self.take_screenshot("03_Step1_Filled_Data")
        self.save_next_button.click()

        # 8. Verify Success
        try:
            success_msg = self.page.locator("text=Temporary Account successfully created").last
            success_msg.wait_for(state="visible", timeout=15000)
            logger.info("Successfully created temporary account.")
            self.take_screenshot("04_Step1_Submission_Success")
            return True
        except:
            logger.error("Failed to verify Step 1 success message.")
            self.take_screenshot("04_Step1_Submission_Error")
            return False
