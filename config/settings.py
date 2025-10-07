import os

BASE_URL = os.getenv("BASE_URL", "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
DEFAULT_BROWSER = os.getenv("BROWSER", "chrome")  # chrome|firefox
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
IMPLICIT_WAIT_SECONDS = int(os.getenv("IMPLICIT_WAIT_SECONDS", "0"))
EXPLICIT_WAIT_SECONDS = int(os.getenv("EXPLICIT_WAIT_SECONDS", "15"))
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "artifacts")

