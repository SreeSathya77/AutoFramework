import pytest
from pathlib import Path
import datetime
import base64
import os
from playwright.sync_api import Page, BrowserContext
from pytest_html import extras
from utils.config_loader import config_loader
from utils.logger import Logger
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
    """
    Configures browser launch arguments.
    By default, it runs in Headed mode with slow_mo.
    """
    return {
        "slow_mo": 500,
        "headless": False  # Keep as False for visual review
    }


@pytest.fixture(scope="function")
def login_page(page: Page, run_folder: str):
    return LoginPage(page, report_dir=run_folder)


@pytest.fixture(scope="function")
def workbench_page(page: Page, run_folder: str):
    return WorkbenchPage(page, report_dir=run_folder)


@pytest.fixture(scope="function")
def onboard_customer_page(page: Page, run_folder: str):
    return OnboardCustomerPage(page, report_dir=run_folder)


@pytest.fixture(scope="function")
def logged_in_page(page: Page, login_page: LoginPage, request):
    """
    Performs login and optionally waits for Enter at the end of the test.
    """
    logger.info("Test Session Started.")
    creds = config_loader.get_credentials()
    url = config_loader.get_base_url()
    login_page.navigate_to_login(url)
    login_page.perform_login(creds["username"], creds["password"])

    yield page

    # Use the custom --hold flag from command line
    if request.config.getoption("--hold"):
        print("\n" + "="*80)
        print(">>> HOLD MODE ACTIVE: Test execution finished.")
        print(">>> THE BROWSER IS KEPT OPEN FOR YOUR REVIEW.")
        print(">>> Press ENTER in this console to close the browser...")
        print("="*80 + "\n")
        try:
            input()
        except EOFError:
            pass

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report_extras = getattr(report, "extras", [])

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot = page.screenshot(type="png")
            base64_img = base64.b64encode(screenshot).decode("utf-8")
            report_extras.append(extras.image(base64_img))
            report.extras = report_extras