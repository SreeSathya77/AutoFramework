"""
Account Page Object Model
Handles account creation and management operations
"""

import os
from datetime import datetime
from playwright.sync_api import Page, expect
from faker import Faker
from utils.logger import get_logger

logger = get_logger(__name__)


class AccountPage:
    def __init__(self, page: Page, report_dir: str = None):
        self.page = page
        self.fake = Faker('en_IN')
        self.logger = logger
        self.focus_style = "outline: 4px solid rgba(0, 191, 255, 0.6); outline-offset: 2px; transition: all 0.3s ease;"
        self.report_dir = report_dir if report_dir else "reports/screenshots"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir, exist_ok=True)

    # Updated selectors based on actual application formcontrolname attributes
    @property
    def account_type_dropdown(self):
        return self.page.locator('select[formcontrolname="accountType"]')

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

    # Success/Error messages - Update based on actual application
    @property
    def success_message(self):
        return self.page.locator("text=Temporary Account successfully created")

    @property
    def error_message(self):
        return self.page.locator(".error-message")  # Placeholder

    def _apply_focus(self, locator):
        """Apply visual focus highlighting to a field"""
        try:
            locator.scroll_into_view_if_needed()
            locator.evaluate(f"el => el.style.cssText += '{self.focus_style}'")
        except Exception as e:
            logger.warning(f"Could not apply focus to element: {str(e)}")

    def _clear_focus(self, locator):
        """Clear visual focus highlighting from a field"""
        try:
            locator.evaluate("el => el.style.outline = ''", timeout=200)
        except Exception as e:
            logger.warning(f"Could not clear focus from element: {str(e)}")

    def capture_success(self, text, filename_prefix):
        """Capture screenshot when success message appears"""
        logger.info(f"⏳ Verifying alert: '{text}'...")
        try:
            alert = self.page.locator(f"text={text}").last
            alert.wait_for(state="visible", timeout=10000)
            self.page.screenshot(path=f"{self.report_dir}/{filename_prefix}.png")
            logger.info(f"✅ Success screenshot captured: {filename_prefix}.png")
        except Exception as e:
            logger.warning(f"Success message not found, capturing debug screenshot")
            self.page.screenshot(path=f"{self.report_dir}/DEBUG_{filename_prefix}.png")

    def navigate_to_accounts(self):
        """Navigate to Accounts section"""
        logger.info("Navigating to Accounts section")
        # Update selector based on actual navigation
        accounts_menu = self.page.locator("text=Accounts")  # Placeholder
        accounts_menu.click()
        self.page.wait_for_load_state("networkidle")

    def click_create_account(self):
        """Click Create Account button"""
        logger.info("Clicking Create Account button")
        # Update selector based on actual button
        create_button = self.page.locator("text=Create Account")  # Placeholder
        create_button.click()
        self.page.wait_for_load_state("networkidle")

    def fill_account_form(self, account_data: dict):
        """
        Fill account creation form with proper highlighting and waits

        Args:
            account_data: Dictionary containing account information
                - name: Account name (optional, will use generated if not provided)
                - email: Account email (optional, will use generated if not provided)
                - phone: Phone number (optional)
                - type: Account type (default: PERSONAL)
        """
        logger.info("📝 Filling account details with highlighting...")

        # Account Type
        account_type = account_data.get('type', 'PERSONAL')
        self.account_type_dropdown.select_option(account_type)

        # Generate names if not provided
        first_name = account_data.get('first_name', self.fake.first_name())
        last_name = account_data.get('last_name', self.fake.last_name())

        # First Name
        self._apply_focus(self.first_name_input)
        self.first_name_input.fill(first_name)

        # Last Name
        self._apply_focus(self.last_name_input)
        self.last_name_input.fill(last_name)

        # Country (default to United States)
        self._apply_focus(self.country_dropdown)
        self.country_dropdown.select_option("United States")
        self.page.wait_for_timeout(1000)  # Wait for state dropdown to populate

        # State (select first available option)
        self._apply_focus(self.state_dropdown)
        self.state_dropdown.select_option(index=1)

        # City (select first available option)
        self._apply_focus(self.city_dropdown)
        self.city_dropdown.select_option(index=1)

        # Address
        address = account_data.get('address', "123 Test St")
        self._apply_focus(self.address_line1_input)
        self.address_line1_input.fill(address)

        # Zip Code
        zip_code = account_data.get('zip_code', "12345")
        self._apply_focus(self.zip_code_input)
        self.zip_code_input.fill(zip_code)

        # Email (generate if not provided)
        email = account_data.get('email', f"{first_name.lower()}@qmbos.test")
        self._apply_focus(self.email_address_input)
        self.email_address_input.fill(email)

        # Confirm Email
        self._apply_focus(self.confirm_email_address_input)
        self.confirm_email_address_input.fill(email)

        # Store generated email for return
        account_data['generated_email'] = email
        account_data['generated_first_name'] = first_name
        account_data['generated_last_name'] = last_name

    def submit_account_form(self):
        """Submit the account creation form"""
        logger.info("Submitting account creation form")
        self.save_next_button.click()
        self.page.wait_for_load_state("networkidle")

    def create_account(self, account_data: dict) -> dict:
        """
        Complete account creation process

        Args:
            account_data: Account information dictionary

        Returns:
            dict: Result with success status and account details
        """
        try:
            logger.info("Starting account creation process")
            self.navigate_to_accounts()
            self.click_create_account()
            self.fill_account_form(account_data)
            self.submit_account_form()

            # Check for success message
            try:
                self.success_message.wait_for(state="visible", timeout=10000)
                self.capture_success("Temporary Account successfully created", "02_account_creation_success")
                logger.info("✅ Account created successfully")

                return {
                    "success": True,
                    "email": account_data.get('generated_email'),
                    "first_name": account_data.get('generated_first_name'),
                    "last_name": account_data.get('generated_last_name'),
                    "message": "Account created successfully"
                }
            except Exception as e:
                logger.error(f"Account creation failed - success message not found: {str(e)}")
                return {
                    "success": False,
                    "message": "Account creation failed - success message not found"
                }

        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating account: {str(e)}"
            }

    def verify_account_exists(self, account_email: str) -> bool:
        """
        Verify if account exists by searching for email

        Args:
            account_email: Email address of the account to verify

        Returns:
            bool: True if account exists
        """
        logger.info(f"Verifying account exists: {account_email}")
        try:
            # Navigate to accounts list if not already there
            self.navigate_to_accounts()

            # Search functionality - update selector based on actual search field
            search_field = self.page.locator("input[placeholder*='Search']")  # Placeholder
            search_field.fill(account_email)
            self.page.wait_for_timeout(1000)  # Wait for search results

            # Check if account appears in results
            account_locator = self.page.locator(f"text={account_email}")
            return account_locator.is_visible()
        except Exception as e:
            logger.error(f"Error verifying account: {str(e)}")
            return False

    def get_account_details(self, account_email: str) -> dict:
        """
        Get account details from the list

        Args:
            account_email: Email address of the account

        Returns:
            dict: Account details
        """
        logger.info(f"Getting details for account: {account_email}")
        try:
            if self.verify_account_exists(account_email):
                # Placeholder - implement based on actual UI structure
                return {
                    "email": account_email,
                    "status": "Active",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "type": "PERSONAL"
                }
            else:
                return {"error": "Account not found"}
        except Exception as e:
            logger.error(f"Error getting account details: {str(e)}")
            return {"error": str(e)}
