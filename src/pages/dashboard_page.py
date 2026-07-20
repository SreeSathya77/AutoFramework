"""
Dashboard Page Object Model
Handles dashboard operations including case dashboard stats
"""

from playwright.sync_api import Page, expect
from utils.logger import Logger
logger = Logger.get_logger()


class DashboardPage:
    def __init__(self, page: Page, report_dir=None): # Added report_dir=None
        self.page = page
        self.report_dir = report_dir

        # Dashboard selectors
        self.dashboard_menu = "text=Dashboard"  # Update with actual selector
        self.welcome_header = "h4:has-text('Welcome to QM Toll portal!')"  # From test output

        # Case Dashboard selectors - Update with actual selectors
        self.case_dashboard_tab = "text=Case Dashboard"  # Placeholder
        self.total_cases_stat = ".stat-total-cases"  # Placeholder
        self.open_cases_stat = ".stat-open-cases"  # Placeholder
        self.closed_cases_stat = ".stat-closed-cases"  # Placeholder
        self.pending_cases_stat = ".stat-pending-cases"  # Placeholder

        # Case list/table selectors
        self.cases_table = ".cases-table"  # Placeholder
        self.case_rows = ".case-row"  # Placeholder

        # Filters and search
        self.search_input = "input[placeholder*='Search']"  # Placeholder
        self.filter_status = "select[name='status']"  # Placeholder

    def navigate_to_dashboard(self):
        """Navigate to main dashboard"""
        logger.info("Navigating to Dashboard")
        self.page.click(self.dashboard_menu)
        self.page.wait_for_load_state("networkidle")

    def verify_dashboard_loaded(self) -> bool:
        """
        Verify dashboard is loaded by checking welcome header

        Returns:
            bool: True if dashboard loaded successfully
        """
        logger.info("Verifying dashboard loaded")
        try:
            expect(self.page.locator(self.welcome_header)).to_be_visible()
            logger.info("Dashboard loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Dashboard not loaded: {str(e)}")
            return False

    def navigate_to_case_dashboard(self):
        """Navigate to Case Dashboard tab/section"""
        logger.info("Navigating to Case Dashboard")
        self.page.click(self.case_dashboard_tab)
        self.page.wait_for_load_state("networkidle")

    def get_case_stats(self) -> dict:
        """
        Get case statistics from dashboard

        Returns:
            dict: Case statistics
        """
        logger.info("Getting case statistics")
        try:
            stats = {
                "total_cases": self.page.locator(self.total_cases_stat).text_content().strip(),
                "open_cases": self.page.locator(self.open_cases_stat).text_content().strip(),
                "closed_cases": self.page.locator(self.closed_cases_stat).text_content().strip(),
                "pending_cases": self.page.locator(self.pending_cases_stat).text_content().strip()
            }
            logger.info(f"Case stats retrieved: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting case stats: {str(e)}")
            return {}

    def verify_case_in_dashboard(self, case_description: str) -> bool:
        """
        Verify if a specific case appears in the dashboard

        Args:
            case_description: Case description to search for

        Returns:
            bool: True if case found
        """
        logger.info(f"Verifying case in dashboard: {case_description}")
        try:
            # Search for the case
            self.page.fill(self.search_input, case_description)
            self.page.wait_for_timeout(500)  # Wait for search results

            case_locator = self.page.locator(f"{self.case_rows}:has-text('{case_description}')")
            return case_locator.is_visible()
        except Exception as e:
            logger.error(f"Error verifying case in dashboard: {str(e)}")
            return False

    def get_case_count_from_dashboard(self) -> int:
        """
        Get the total number of cases displayed in dashboard

        Returns:
            int: Number of cases
        """
        logger.info("Getting case count from dashboard")
        try:
            case_rows = self.page.locator(self.case_rows)
            count = case_rows.count()
            logger.info(f"Found {count} cases in dashboard")
            return count
        except Exception as e:
            logger.error(f"Error getting case count: {str(e)}")
            return 0

    def filter_cases_by_status(self, status: str):
        """
        Filter cases by status

        Args:
            status: Status to filter by (Open, Closed, Pending, etc.)
        """
        logger.info(f"Filtering cases by status: {status}")
        self.page.select_option(self.filter_status, status)
        self.page.wait_for_load_state("networkidle")

    def get_filtered_case_count(self, status: str) -> int:
        """
        Get count of cases after filtering by status

        Args:
            status: Status filter applied

        Returns:
            int: Number of filtered cases
        """
        logger.info(f"Getting filtered case count for status: {status}")
        self.filter_cases_by_status(status)
        return self.get_case_count_from_dashboard()

    def verify_dashboard_stats_accuracy(self) -> bool:
        """
        Verify that dashboard stats match the actual case counts

        Returns:
            bool: True if stats are accurate
        """
        logger.info("Verifying dashboard stats accuracy")
        try:
            stats = self.get_case_stats()

            # Get actual counts by filtering
            open_count = self.get_filtered_case_count("Open")
            closed_count = self.get_filtered_case_count("Closed")
            pending_count = self.get_filtered_case_count("Pending")
            total_count = self.get_case_count_from_dashboard()

            # Compare with displayed stats
            stats_match = (
                int(stats.get("total_cases", "0")) == total_count and
                int(stats.get("open_cases", "0")) == open_count and
                int(stats.get("closed_cases", "0")) == closed_count and
                int(stats.get("pending_cases", "0")) == pending_count
            )

            if stats_match:
                logger.info("Dashboard stats are accurate")
                return True
            else:
                logger.error("Dashboard stats do not match actual counts")
                return False

        except Exception as e:
            logger.error(f"Error verifying dashboard stats: {str(e)}")
            return False
