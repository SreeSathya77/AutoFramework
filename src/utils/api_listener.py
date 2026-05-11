import os
import json
from datetime import datetime
from playwright.sync_api import Page, Response
from src.utils.logger import Logger

def start_api_logging(page: Page, log_path: str):
    """
    Attaches a listener to the page to log detailed API request/response cycles.
    
    Args:
        page (Page): The Playwright page object to listen to.
        log_path (str): The full path to the log file where API calls will be written.
    """
    logger = Logger.get_logger()
    
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    logger.info(f"📡 Detailed API request logging enabled. Output file: {log_path}")

    def log_api_response(response: Response):
        """
        This function is called for every network response.
        It filters for API calls and logs the full request/response cycle.
        """
        # Filter for API calls
        if "/api/" in response.url:
            try:
                # --- 1. Gather all data ---
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                request = response.request
                method = request.method
                url = response.url
                status = response.status
                
                # Determine result
                result = "✅ SUCCESS" if 200 <= status < 300 else f"❌ FAILURE ({status})"

                # Get request body
                request_body = request.post_data
                if request_body:
                    try:
                        # Try to format it as pretty JSON
                        request_body = json.dumps(json.loads(request_body), indent=2)
                    except:
                        # If not JSON, just use the raw text
                        pass
                else:
                    request_body = "N/A (GET request or no body)"

                # Get response body
                try:
                    response_body = response.json()
                    response_body = json.dumps(response_body, indent=2)
                except:
                    # If not JSON, get as raw text
                    response_body = response.text()
                    if not response_body:
                        response_body = "N/A (No response body)"

                # --- 2. Format the log entry ---
                log_entry = (
                    f"-------------------- API Call at {timestamp} --------------------\n"
                    f"➡️  REQUEST\n"
                    f"   Method: {method}\n"
                    f"   URL: {url}\n"
                    f"   Body:\n{request_body}\n\n"
                    f"⬅️  RESPONSE\n"
                    f"   Status: {status} ({result})\n"
                    f"   Body:\n{response_body}\n"
                    f"----------------------------------------------------------------------\n\n"
                )

                # --- 3. Write to file ---
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(log_entry)

            except Exception as e:
                logger.error(f"Could not write to API log file: {e}")

    # Attach the listener to the 'response' event
    page.on("response", log_api_response)