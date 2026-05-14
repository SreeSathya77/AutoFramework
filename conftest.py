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
        "viewport": {"width": 1500, "height": 725},
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


# --- MODULE SCOPED FIXTURE: This is the fix for session persistence ---

@pytest.fixture(scope="module")
def shared_setup(browser, browser_context_args, run_folder, base_url, request):
    """
    Creates ONE visible browser session for the entire test file.
    Performs login once and shares the page objects.
    """
    logger.info("🚀 Starting Shared Visible Session...")

    # Initialize browser context and page
    context = browser.new_context(**browser_context_args)
    page = context.new_page()

    # Perform Login
    creds = config_loader.get_credentials()
    login_page = LoginPage(page, report_dir=run_folder)
    login_page.navigate_to_login(base_url)
    login_page.perform_login(creds["username"], creds["password"])
    login_page.verify_login_success()

    # Provide shared page and objects
    from src.pages.case_page import CaseManagementPage
    objs = {
        "page": page,
        "onboard": OnboardCustomerPage(page, report_dir=run_folder),
        "case": CaseManagementPage(page, report_dir=run_folder),
        "workbench": WorkbenchPage(page, report_dir=run_folder)
    }

    yield objs

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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Ensures screenshots are captured even in shared sessions."""
    outcome = yield
    report = outcome.get_result()
    report_extras = getattr(report, "extras", [])

    if report.when == "call" and report.failed:
        # Try to retrieve page from shared_setup
        setup = item.funcargs.get("shared_setup")
        page = setup["page"] if setup else item.funcargs.get("page")

        if page:
            screenshot = page.screenshot(type="png")
            base64_img = base64.b64encode(screenshot).decode("utf-8")
            report_extras.append(extras.image(base64_img))
            report.extras = report_extras