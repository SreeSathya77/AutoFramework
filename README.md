# QA QM BOS Regression Framework

## Project Overview
The goal of this project is to build a robust, scalable, and maintainable automated regression testing framework for the QM BOS Web Application. This framework uses **Python**, **Pytest**, and **Playwright** to ensure high-quality software delivery through end-to-end (E2E) UI and API testing.

## Setup Instructions
### Prerequisites
*   Python 3.10+
*   Node.js (for Playwright, if not already handled by pip)

### Installation
1.  Clone the repository (if applicable).
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Install Playwright browsers:
    ```bash
    playwright install
    ```

### Folder Structure
*   `tests/`: Test scripts divided into `ui/` and `api/`.
*   `src/pages/`: Page Object Model (POM) classes.
*   `utils/`: Utility functions (config loader, logger, helpers).
*   `data/`: Test data files (Excel, JSON).
*   `reports/`: Test execution reports.
*   `screenshots/`: Captured screenshots during test failure or specific validations.
*   `config/`: Environment-specific configuration files.

## Build Progress
### Current Status
*   **Week 1:** 
    *   Defined Product Requirements Document (PRD).
    *   Initial Project Structure created.
    *   `requirements.txt` and Environment Configuration (`.env`, `config.yaml`) set up.
    *   Implemented `ConfigLoader` utility.
    *   Created `BasePage` parent class for Page Object Model.

## Framework Architecture
This framework follows the **Page Object Model (POM)** design pattern to separate test logic from page-specific interactions.
*   **Configuration:** Managed via `.yaml` and `.env` files for environment switching.
*   **Fixtures:** Pytest fixtures in `conftest.py` handle browser and context initialization.
*   **Validation:** Dual-layer verification (UI + API) as defined in the PRD.

## Running Tests
To run all tests:
```bash
pytest -v
```
To run tests in headed mode (visible browser):
```bash
pytest --headed
```
To run a specific test file:
```bash
pytest tests/ui/test_login.py
```

## Next Steps
*   Implement `LoginPage` object with specific selectors.
*   Develop `conftest.py` for browser and API context fixtures.
*   Write the first UI test for Requirement 1 (Login/Logout).
*   Add API interception logic to capture network traffic.

