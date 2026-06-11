from playwright.sync_api import Page
from utils.logger import Logger
from utils.config import LOGIN_CREDENTIALS

logger = Logger.get_logger()

class SessionManager:
    @staticmethod
    def ensure_active_session(page: Page, login_page_obj) -> bool:
        """
        Detects if the session has expired and re-logs if necessary.
        """
        page.wait_for_load_state("networkidle")
        if "/login" in page.url or page.locator('input[formcontrolname="emailId"]').is_visible(timeout=2000):
            logger.warning("🔐 Session expiry or logout detected. Re-authenticating...")
            
            creds = LOGIN_CREDENTIALS.get("superadmin", {})
            email = creds.get("email") or creds.get("username")
            password = creds.get("password")
            
            if not email or not password:
                logger.error("❌ Failed to retrieve Superadmin credentials for re-auth.")
                return False

            # Perform manual login sequence since LoginPage.login() is missing
            page.locator('input[formcontrolname="emailId"]').fill(email)
            page.locator('input[formcontrolname="password"]').fill(password)
            
            login_btn = page.locator('button.auth-btn')
            login_btn.wait_for(state="visible")
            login_btn.click()

            page.wait_for_url("**/dashboard", timeout=20000)
            logger.info("✅ Session successfully restored.")
            return True
        else:
            logger.info("🟢 Session is still active.")
        return False

    @staticmethod
    def active_heartbeat(page: Page):
        """
        Sends a non-destructive network request to reset the server's idle timer.
        """
        try:
            # 1. Trigger a network request to a safe endpoint
            page.evaluate("fetch('/api/v1/user/profile').catch(() => {})")
            
            # 2. Perform a safe UI interaction (clicking the body or an empty area)
            page.mouse.click(0, 0)
            
            logger.info("💓 Heartbeat sent (Network + UI) to keep session alive.")
        except Exception:
            pass