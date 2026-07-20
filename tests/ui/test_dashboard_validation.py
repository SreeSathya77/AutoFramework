import pytest
from collections import Counter
# 🔄 FIXED IMPORT: Direct referencing to case_page.py
from src.pages.case_page import CaseManagementPage
from src.utils.logger import Logger
from src.utils.db_validator import get_all_cases_from_db
# (Removed explicit import of shared_setup fixture, Pytest automatically injects it)
logger = Logger.get_logger()


def test_case_dashboard_statistics(shared_setup, run_folder):
    """
    Dashboard Validation Suite:
    1. Reuses browser context session and handles 75% page layout zoom.
    2. Collects baseline stats across grid lists vs MongoDB collections.
    3. Triggers auto-scroll to validate bottom card elements.
    """
    logger.info("📊 Starting Case Dashboard statistics validation...")

    # Extract the open browser page session object from your fixture setup dictionary
    objs = shared_setup
    page = objs["page"]

    case_page = CaseManagementPage(page, report_dir=run_folder)
    case_page.navigate_to_case_dashboard()

    # 1. Scrape the detailed data from the "Cases" tab UI
    scraped_cases_data = case_page.get_case_statistics()

    # 2. Get the ground truth from the database
    db_cases = get_all_cases_from_db()

    # --- VALIDATION 1: Compare Scraped UI data against DB data ---
    logger.info("\n" + "*" * 60)
    logger.info("*** VALIDATION 1: Scraped Data (UI) vs. Database (DB) ***")
    logger.info("*" * 60)

    errors = []
    total_scraped_count = sum(len(cases) for cases in scraped_cases_data.values())
    total_db_count = len(db_cases)
    if total_scraped_count == total_db_count:
        logger.info(f"✅ SUCCESS: Total case count matches. UI: {total_scraped_count}, DB: {total_db_count}")
    else:
        error_msg = f"Total case count mismatch. UI: {total_scraped_count}, DB: {total_db_count}"
        logger.error(f"❌ {error_msg}")
        errors.append(error_msg)

    db_status_counts = Counter(case.get("caseStatus") for case in db_cases)

    for status, scraped_cases in scraped_cases_data.items():
        scraped_count = len(scraped_cases)
        db_count = db_status_counts.get(status, 0)
        if scraped_count == db_count:
            logger.info(f"   ✅ {status}: Count matches. UI: {scraped_count}, DB: {db_count}")
        else:
            error_msg = f"{status}: Count mismatch. UI: {scraped_count}, DB: {db_count}"
            logger.error(f"   ❌ {error_msg}")
            errors.append(error_msg)

    # --- VALIDATION 2: Validate UI Summary Widgets vs. Scraped UI Data ---
    logger.info("\n" + "*" * 70)
    logger.info("*** VALIDATION 2: Summary Widgets (UI) vs. Scraped 'Cases' Tab (UI) ***")
    logger.info("*" * 70)

    case_page.navigate_to_cases_summary()

    errors.extend(case_page.validate_summary_statistics(scraped_cases_data))
    errors.extend(case_page.validate_owner_status_grid(scraped_cases_data))
    errors.extend(case_page.validate_owner_priority_grid(scraped_cases_data))
    errors.extend(case_page.validate_case_type_grid(scraped_cases_data))

    logger.info("✅ Case Dashboard statistics validation complete.")

    if errors:
        error_summary = "\n--- BUG SUMMARY ---\n" + "\n".join(f"- {e}" for e in errors)
        pytest.fail(error_summary)
    else:
        logger.info("\n--- All dashboard validations passed successfully! ---")