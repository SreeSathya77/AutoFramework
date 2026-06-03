from playwright.sync_api import sync_playwright


def test_login_scaled_page():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            viewport={
                "width": 1920,
                "height": 1080
            }
        )

        page = context.new_page()

        page.goto(
            "https://www.saucedemo.com/"
        )

        # ==================================================
        # APPLY STABLE PAGE SCALE
        # ==================================================

        page.evaluate("""
            document.body.style.transform = 'scale(0.8)';
            document.body.style.transformOrigin = 'top left';
            document.body.style.width = '125%';
        """)

        page.wait_for_timeout(3000)

        # ==================================================
        # LOGIN
        # ==================================================

        page.locator("#user-name").fill(
            "standard_user"
        )

        page.locator("#password").fill(
            "secret_sauce"
        )

        page.locator("#login-button").click()

        page.wait_for_timeout(5000)

        # ==================================================
        # VALIDATION
        # ==================================================

        assert "inventory.html" in page.url

        # ==================================================
        # APPLY AGAIN AFTER LOGIN
        # some apps rerender DOM after navigation
        # ==================================================

        page.evaluate("""
            document.body.style.transform = 'scale(0.8)';
            document.body.style.transformOrigin = 'top left';
            document.body.style.width = '125%';
        """)

        page.wait_for_timeout(5000)

        input("Press ENTER to close browser...")

        context.close()

        browser.close()