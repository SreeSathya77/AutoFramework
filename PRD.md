# Product Requirements Document (PRD): QA QM BOS Regression Framework

## 1. Overview
The goal of this project is to rebuild the automated regression testing framework for the QM BOS Web Application, focusing on comprehensive end-to-end testing including login authentication and case management workflows.

## 2. Objectives
*   Restore the testing capabilities for the core login authentication flow.
*   Implement comprehensive case management testing including account creation, case creation, and dashboard verification.
*   Focus on end-to-end flow for login authentication with pop-up validation.
*   Test auto case creation for various case types (refund, vehicle transfer, tag transfer, toll adjustment).
*   Provide clear reporting and logging for test executions.

## 3. Tech Stack (Proposed)
*   **Language:** Python 3.x
*   **Testing Framework:** Pytest
*   **Web Automation:** Playwright (Python)
*   **Reporting:** HTML Reports / Allure
*   **Design Pattern:** Page Object Model (POM)

## 4. Framework Requirements
*   **Configuration Management:** Support for multiple environments (Dev, QA, Prod) via `.env` or `config.yaml`.
*   **Logging:** Detailed logs for debugging failures.
*   **Parallel Execution:** Support for running tests in parallel to save time.
*   **CI/CD Integration:** Ready for Jenkins/GitHub Actions.
*   **UI Validation Strategy:** Comprehensive UI element validation with screenshot capture and element verification for login and case management flows.

## 5. Scope of UI Testing
### UI Test Scenarios:

**Requirement 1: User Authentication (Login)**
*   **Page:** http://operator-qa.qmaastech.com/
*   **UI Validations:**
    1.  Verify successful navigation to the Login page (Page Title/URL).
    2.  Verify successful Login with valid credentials.
    3.  **Screenshot Capture:** Capture the "Login successful" pop-up notification.
    4.  Verify redirect to the Dashboard/Home page.
    5.  Verify presence of user-specific elements (e.g., Logout button, Profile name).

**Requirement 2: Case Management End-to-End Flow**
*   **Page:** Dashboard and Case Management sections
*   **UI Validations:**
    1.  Create a new account with valid details.
    2.  Verify account creation success and account details.
    3.  Create a new case for the created account.
    4.  Verify case creation success and case details.
    5.  Navigate to Case Dashboard and verify the newly created case appears.
    6.  Verify Case Dashboard statistics and metrics.
    7.  Test auto case creation for refund cases.
    8.  Test auto case creation for vehicle transfer cases.
    9.  Test auto case creation for tag transfer cases.
    10. Test auto case creation for toll adjustment cases.
    11. Verify all auto-created cases appear in Case Dashboard.
    12. Validate case status transitions and updates.

### UI Validation Strategy:
1.  **Element Verification:** 
      Validate presence, visibility, and content of critical UI elements.
2.  **Screenshot Capture:** 
      Automated screenshots for visual verification of UI states.
3.  **Text Validation:** 
      Verify displayed text content matches expected values.
4.  **Navigation Verification:** 
      Confirm URL redirects and page transitions work correctly.
5.  **Data Validation:**
      Verify created accounts and cases have correct data persistence.
6.  **Dashboard Validation:**
      Verify dashboard statistics and case listings are accurate.

## 6. Out of Scope
*   API Testing and Verification
*   Additional UI Test Cases (data-driven testing with Excel/CSV)
*   Performance Testing
*   Security Testing
*   Mobile Responsiveness Testing
*   Cross-browser compatibility beyond Chromium
