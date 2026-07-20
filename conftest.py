import pytest
from pathlib import Path
import datetime
import base64
import os
from playwright.sync_api import Page, BrowserContext
from pytest_html import extras
from src.utils.config_loader import config_loader
from src.utils.logger import Logger
from src.pages.login_page import LoginPage
from src.pages.workbench_page import WorkbenchPage
from src.pages.onboard_customer_page import OnboardCustomerPage

logger = Logger.get_logger()
VIEWPORT_SIZE = {"width": 1500, "height": 750}


def pytest_addoption(parser):
    """Adds custom command line options to pytest."""
    parser.addoption(
        "--hold", action="store_true", default=False, help="Pause and keep browser open after test finishes"
    )


@pytest.fixture(scope="session")
def run_folder():
    """Creates a unique RUN folder for each session's assets."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_path = Path("reports") / f"RUN_{timestamp}"
    run_path.mkdir(parents=True, exist_ok=True)
    return str(run_path)


@pytest.fixture(scope="session")
def browser_context_args(run_folder: str):
    video_dir = Path(run_folder) / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    return {
        "viewport": VIEWPORT_SIZE,
        "device_scale_factor": 1.0,
        "ignore_https_errors": True,
        "record_video_dir": str(video_dir),
    }


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Forces Headed mode and slow_mo for visual review."""
    return {
        "slow_mo": 500,
        "headless": False
    }


@pytest.fixture(scope="module")
def shared_setup(browser, browser_context_args, run_folder, base_url, request):
    """
    Creates ONE visible browser session for the entire test file.
    Performs login once and shares the page objects.
    """
    logger.info("🚀 Starting Shared Visible Session...")

    # Initialize browser context
    context = browser.new_context(**browser_context_args)

    # 🎯 INSTANT ANCHOR GLOBAL 75% ZOOM INJECTION RULES FOR PRIMARY CONTEXT
    context.add_init_script("""() => {
        const style = document.createElement('style');
        style.innerHTML = 'body { zoom: 75% !important; }';
        document.head.appendChild(style);
    }""")

    page = context.new_page()

    # Perform Login normally under globally enforced 75% layout
    creds = config_loader.get_credentials()
    login_page = LoginPage(page, report_dir=run_folder)
    login_page.navigate_to_login(base_url)
    login_page.perform_login(creds["username"], creds["password"])
    login_page.verify_login_success()

    # Provide shared page and objects
    from src.pages.case_page import CaseManagementPage
    objs = {
        "page": page,
        "browser": browser,
        "onboard": OnboardCustomerPage(page, report_dir=run_folder),
        "case": CaseManagementPage(page, report_dir=run_folder),
        "workbench": WorkbenchPage(page, report_dir=run_folder)
    }

    yield objs
    
    # Close any cached multi-context browsers
    if "contexts" in objs:
        for email, (ctx, ctx_page, _) in objs["contexts"].items():
            try:
                ctx_page.close()
                ctx.close()
                logger.info(f"🧹 Cleaned up cached context for {email}")
            except Exception as e:
                logger.warning(f"Failed to clean up context for {email}: {e}")

    # Use the custom --hold flag at the very end of the module
    if request.config.getoption("--hold"):
        print("\n" + "=" * 80)
        print(">>> HOLD MODE ACTIVE: All tests in this module finished.")
        print(">>> Press ENTER in this console to close the browser...")
        print("=" * 80 + "\n")
        try:
            input()
        except EOFError:
            pass
            
    context.close()

    # Ensure context is closed safely even if tests crashed beforehand
    try:
        if not page.is_closed():
            context.close()
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Captures failure screenshots safely, accounting for shared dictionary
    fixtures and dynamic context switches during multi-user simulation steps.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = None

        # 1. Try to extract direct standalone page fixture
        if "page" in item.funcargs:
            page = item.funcargs["page"]

        # 2. Extract embedded page instance from your shared session dictionary map
        elif "shared_setup" in item.funcargs:
            shared_data = item.funcargs["shared_setup"]
            if isinstance(shared_data, dict) and "page" in shared_data:
                page = shared_data["page"]

        # 3. Double-check viability state & secure screenshot payload stream
        if page:
            try:
                if not page.is_closed():
                    screenshot_bytes = page.screenshot(type="png")

                    # Attach screenshot safely to pytest-html report if plugin is active
                    pytest_html = item.config.pluginmanager.getplugin("html")
                    if pytest_html is not None:
                        extra = getattr(report, "extra", [])
                        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                        html_img = f'<div style="padding:10px;"><img src="data:image/png;base64,{screenshot_base64}" style="width:800px;border:1px solid #ccc;" /></div>'
                        extra.append(extras.html(html_img))
                        report.extra = extra

                    logger.info("📸 Failure visual trace screenshot successfully linked to test report execution maps.")
                else:
                    logger.warning(
                        "⚠️ Skipping screenshot step: Target execution page context instance is already closed.")
            except Exception as e:
                logger.error(f"❌ Failed to extract failure screenshot asset: {str(e)}")