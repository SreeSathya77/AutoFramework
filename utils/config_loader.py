import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self):
        # Load .env file
        load_dotenv()
        
        # Determine paths
        self.root_dir = Path(__file__).parent.parent
        config_path = self.root_dir / "config" / "config.yaml"
        
        # Load YAML config
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        # Set active environment
        self.env = os.getenv("ENV", "qa").lower()
        
    def get_base_url(self):
        return self.config["environments"][self.env]["base_url"]
    
    def get_credentials(self):
        # Dynamically fetch credentials based on environment prefix (e.g., QA_USERNAME)
        username_key = f"{self.env.upper()}_USERNAME"
        password_key = f"{self.env.upper()}_PASSWORD"
        
        return {
            "username": os.getenv(username_key),
            "password": os.getenv(password_key)
        }
    
    def get_browser_config(self):
        return self.config["default"]

# Instantiate a global config object for easy access
config_loader = ConfigLoader()
