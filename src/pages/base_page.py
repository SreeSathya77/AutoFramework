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

    def get_element(self, selector_or_locator, target_page=None):
        p = target_page or self.page
        return selector_or_locator if isinstance(selector_or_locator, Locator) else p.locator(selector_or_locator)

    def scroll_focus_click(self, selector_or_locator, timeout: int = 15000, target_page: Page = None, highlight_delay: int = 150):
        p = target_page or self.page
        element = self.get_element(selector_or_locator, target_page)
        element.wait_for(state="visible", timeout=timeout)
        element.evaluate("el => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'})")
        p.wait_for_timeout(150)
        
        element.evaluate("""el => {
            el.style.setProperty('border', '3px solid orange', 'important');
            el.style.setProperty('box-shadow', '0 0 10px orange', 'important');
            el.style.setProperty('outline', 'none', 'important');
            el.focus();
        }""")
        p.wait_for_timeout(highlight_delay)

        try:
            element.click(timeout=3000)
        except Exception:
            try:
                element.click(timeout=2000, force=True)
            except Exception:
                element.evaluate("el => el.click()")
        p.wait_for_timeout(20)
        try:
            if element.is_visible(timeout=50):
                element.evaluate("el => { el.style.border = 'none'; el.style.boxShadow = 'none'; el.style.outline = 'none'; }")
        except Exception:
            pass

    def scroll_focus_fill(self, selector_or_locator, text: str, timeout: int = 15000, target_page: Page = None):
        p = target_page or self.page
        element = self.get_element(selector_or_locator, target_page)
        element.wait_for(state="visible", timeout=timeout)
        element.evaluate("el => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'})")
        p.wait_for_timeout(20)

        element.evaluate("""el => {
            el.style.border = '3px solid orange';
            el.style.boxShadow = '0 0 10px orange';
            el.focus();
        }""")
        p.wait_for_timeout(20)
        
        element.fill(text)
        
        p.wait_for_timeout(20)
        try:
            if element.is_visible(timeout=50):
                element.evaluate("el => { el.blur(); el.style.border = 'none'; el.style.boxShadow = 'none'; }")
        except Exception:
            pass

    def scroll_focus_check(self, selector_or_locator, timeout: int = 15000, target_page: Page = None):
        p = target_page or self.page
        element = self.get_element(selector_or_locator, target_page)
        element.wait_for(state="attached", timeout=timeout)
        element.evaluate("el => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'})")
        p.wait_for_timeout(20)

        element.evaluate("""el => {
            el.style.outline = '3px solid orange';
            el.style.boxShadow = '0 0 10px orange';
        }""")
        p.wait_for_timeout(20)
        
        try:
            element.check(timeout=3000, force=True)
        except Exception:
            element.evaluate("el => el.click()")
        
        p.wait_for_timeout(20)
        try:
            if element.is_visible(timeout=50):
                element.evaluate("el => { el.style.outline = 'none'; el.style.boxShadow = 'none'; }")
        except Exception:
            pass

    def scroll_focus_select(self, selector_or_locator, value=None, label=None, index=None, timeout: int = 5000, target_page: Page = None):
        p = target_page or self.page
        element = self.get_element(selector_or_locator, target_page)
        element.wait_for(state="visible", timeout=timeout)
        element.evaluate("el => el.scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'})")
        p.wait_for_timeout(20)

        element.evaluate("""el => {
            el.style.border = '3px solid orange';
            el.style.boxShadow = '0 0 10px orange';
            el.focus();
        }""")
        p.wait_for_timeout(20)
        
        if label is not None:
            element.select_option(label=label)
        elif index is not None:
            element.select_option(index=index)
        else:
            element.select_option(value=value)
            
        try:
            element.dispatch_event("change")
        except Exception:
            pass
            
        p.wait_for_timeout(20)
        try:
            if element.count() > 0:
                element.evaluate("el => { el.blur(); el.style.border = 'none'; el.style.boxShadow = 'none'; }")
        except Exception:
            pass

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