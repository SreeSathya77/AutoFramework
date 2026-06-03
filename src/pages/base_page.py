import os
from datetime import datetime
from playwright.sync_api import Page, Locator
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

    def scroll_focus_click(self, selector_or_locator, timeout: int = 5000, target_page: Page = None):
        """
        A robust interaction method that ensures an element is scrolled into view, 
        visually highlighted, focused, and clicked.
        """
        # Determine the target page context
        p = target_page or self.page

        # Determine if we are dealing with a selector string or an existing Locator bound to a page
        element = selector_or_locator if isinstance(selector_or_locator, Locator) else p.locator(selector_or_locator)
        
        # 1. Wait for visibility
        element.wait_for(state="visible", timeout=timeout)
        
        # 2. Force scroll to document bottom to ensure layout is triggered
        p.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        p.wait_for_timeout(300)
        
        # 3. Smoothly center the element in the viewport
        element.evaluate("el => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'})")
        p.wait_for_timeout(800)
        
        # 4. Visual Highlight and Focus
        # We use orange to make it very obvious during the test run
        element.evaluate("""el => {
            el.style.border = '3px solid orange';
            el.style.boxShadow = '0 0 10px orange';
            el.focus();
        }""")
        element.hover()
        p.wait_for_timeout(400)
        
        # 5. Interaction with fallback
        try:
            logger.info(f"Performing focused click on element...")
            element.click(timeout=3000, force=True)
        except Exception as e:
            logger.warning(f"Standard click failed, attempting JS click. Error: {str(e)}")
            element.evaluate("el => el.click()")

    def scroll_to_bottom(self):
        """Utility to force scroll to the bottom of the page."""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Checks if an element is visible within the given timeout."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except:
            return False
