from playwright.sync_api import sync_playwright
import pyautogui
import time


def test_login_with_real_keyboard_zoom():

    with sync_playwright() as p:

        # ==========================================================
        # Launch Browser
        # ==========================================================

        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,
            args=["--start-maximized"]
        )

        context = browser.new_context(
            no_viewport=True
        )

        page = context.new_page()

        # ==========================================================
        # Open Website
        # ==========================================================

        page.goto(
            "https://www.saucedemo.com/"
        )

        # ==========================================================
        # Wait For Browser To Fully Appear
        # ==========================================================

        page.wait_for_timeout(5000)

        # ==========================================================
        # CLICK CENTER OF PAGE
        # makes browser active/focused
        # ==========================================================

        page.mouse.click(800, 400)

        page.wait_for_timeout(2000)

        # ==========================================================
        # REAL USER-LIKE CTRL + -
        # ==========================================================

        pyautogui.hotkey("ctrl", "-")

        print("Applied CTRL + - once")

        time.sleep(3)

        pyautogui.hotkey("ctrl", "-")

        print("Applied CTRL + - twice")

        time.sleep(3)

        # ==========================================================
        # Login
        # ==========================================================

        page.locator("#user-name").fill(
            "standard_user"
        )

        page.locator("#password").fill(
            "secret_sauce"
        )

        page.locator("#login-button").click()

        # ==========================================================
        # Wait After Login
        # ==========================================================

        page.wait_for_timeout(5000)

        # ==========================================================
        # Apply Zoom Again After Login
        # ==========================================================

        pyautogui.hotkey("ctrl", "-")

        print("Applied CTRL + - after login")

        time.sleep(3)

        pyautogui.hotkey("ctrl", "-")

        print("Applied CTRL + - second time after login")

        time.sleep(5)

        # ==========================================================
        # Validation
        # ==========================================================

        assert "inventory.html" in page.url

        print("\nLogin successful.")
        print("Browser will remain open.")
        print("Press ENTER in terminal to close browser...\n")

        input()

        # ==========================================================
        # Cleanup
        # ==========================================================

        context.close()

        browser.close()