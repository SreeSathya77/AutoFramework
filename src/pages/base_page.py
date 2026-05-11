import os
from datetime import datetime
from playwright.sync_api import Page
from src.utils.logger import Logger

logger = Logger.get_logger()

class BasePage:
    def __init__(self, page: Page, report_dir: str = None):
        self.page = page
        self.report_dir = report_dir

    def navigate(self, url: str):
        """Navigates to the specified URL."""
        logger.info(f"Navigating to: {url}")
        self.page.goto(url)

    def wait_for_element(self, selector: str, timeout: int = 30000):
        """Waits for an element to be visible on the page."""
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    def click_element(self, selector: str):
        """Clicks on an element."""
        self.page.click(selector)

    def fill_field(self, selector: str, text: str):
        """Fills a text field with the given text."""
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """Gets the text content of an element."""
        return self.page.text_content(selector)

    def take_screenshot(self, name: str, report_dir: str = None):
        """Takes a screenshot and saves it to the RUN specific folder."""
        timestamp = datetime.now().strftime("%H%M%S")
        
        # Determine the directory to save screenshots
        # Use provided report_dir parameter, fallback to instance report_dir, then default to global screenshots folder
        target_dir = report_dir or self.report_dir
        if target_dir:
            screenshot_dir = os.path.join(target_dir, "screenshots")
        else:
            screenshot_dir = os.path.join(os.getcwd(), "screenshots")
            
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        path = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
        self.page.screenshot(path=path)
        logger.info(f"Screenshot captured: {path}")
        return path

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Checks if an element is visible within the given timeout."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except:
            return False
