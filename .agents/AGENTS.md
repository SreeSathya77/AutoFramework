# Strict Project Automation Rules for Antigravity

This file defines critical rules that Antigravity must follow at all times in this workspace to ensure test stability and prevent repeating known mistakes.

## Rule 1: No Direct URL Navigation or Reloads
- **NEVER** use `page.goto(url)` to jump directly to specific feature pages (e.g. `**/search-case`, `**/create-case`, etc.).
- **NEVER** use `page.reload()` to refresh the page to "reset state" or try a search query again.
- **RATIONALE**: The development team has not implemented URL synchronization properly across all routes. Hard page reloads or direct URL navigation can break the Angular router state, drop session contexts, or trigger infinite loading spinners.
- **CORRECT ACTION**: Simulate organic user clicks via the left-hand workbench menu sidebar or other UI elements to reset routing or navigate.

## Rule 2: No wait_for_url()
- **NEVER** use `page.wait_for_url(url_pattern)` to assert that a navigation transition completed.
- **RATIONALE**: Because URLs do not reliably update in the browser address bar during front-end transitions in this application, waiting for a URL pattern will result in a hard 30-second timeout failure.
- **CORRECT ACTION**: Use `locator.wait_for(state="visible")` on unique UI elements of the destination page (e.g., waiting for the `Search Cases` toggle button when going to the Search page, or waiting for the case details panel when viewing a case).

## Rule 3: Avoid networkidle
- **NEVER** use `page.wait_for_load_state("networkidle")` in verification loops or page loads.
- **RATIONALE**: Background polling, heartbeats, or web sockets in this Angular application prevent the network from ever going fully idle, leading to 30-second timeouts.
- **CORRECT ACTION**: Use deterministic timeouts (e.g., `page.wait_for_timeout(1500)`) combined with explicit element visibility waits.

## Rule 4: No Unnecessary or Ad-hoc Page Transitions (e.g. Case Dashboard)
- **NEVER** introduce new page transitions or "parking" navigation steps (such as going to the reporting `Case Dashboard`) that are not explicitly defined in the user's test scenario.
- **RATIONALE**: Navigating to unneeded pages can trigger slow widget loading, unexpected layout elements, or timeout errors on pages that are not properly scoped for the current test flow.
- **CORRECT ACTION**: Keep each actor strictly on the page where their last action finished, unless the test scenario explicitly calls for a specific navigation step.

