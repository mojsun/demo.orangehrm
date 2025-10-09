from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class OrangeLoginPage:
    URL_PATH = "/web/index.php/auth/login"
    DASHBOARD_URL_FRAGMENT = "/dashboard"

    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    DASHBOARD_HEADING = (By.XPATH, "//h6[normalize-space()='Dashboard']")
    ERROR_TOAST = (By.CSS_SELECTOR, "div.oxd-alert-content-text")
    ERROR_ALERT = (By.CSS_SELECTOR, "div.oxd-alert.oxd-alert--error")
    FIELD_ERROR = (By.CSS_SELECTOR, "span.oxd-input-field-error-message")
    NAV_SIDEPANEL = (By.CSS_SELECTOR, "aside.oxd-sidepanel")

    def __init__(self, driver: WebDriver, wait: WebDriverWait, base_url: str):
        self.driver = driver
        self.wait = wait
        self.base_url = base_url

    def open(self):
        if self.base_url.endswith(self.URL_PATH):
            url = self.base_url
        else:
            # If someone provides BASE_URL as domain root, append path
            url = self.base_url.rstrip("/") + self.URL_PATH
        self.driver.get(url)
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        return self

    def login(self, username: str, password: str):
        self.driver.find_element(*self.USERNAME).clear()
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).clear()
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
        return self

    def assert_logged_in(self):
        # Wait for either success (dashboard) or error toast, then assert success
        try:
            self.wait.until(EC.any_of(
                EC.presence_of_element_located(self.DASHBOARD_HEADING),
                EC.visibility_of_element_located(self.NAV_SIDEPANEL),
                EC.visibility_of_element_located(self.ERROR_TOAST),
            ))
        except Exception:
            # Fall back to checking heading only to surface timeout if both missing
            self.wait.until(EC.presence_of_element_located(self.DASHBOARD_HEADING))

        # If error toast is visible, fail with message
        error_elems = self.driver.find_elements(*self.ERROR_TOAST)
        if error_elems and error_elems[0].is_displayed():
            error_text = error_elems[0].text.strip()
            assert False, f"Login failed: {error_text or 'Unknown error'}"

        # Optionally ensure URL contains dashboard
        try:
            self.wait.until(EC.url_contains(self.DASHBOARD_URL_FRAGMENT))
        except Exception:
            pass
        # Confirm a stable dashboard indicator is present
        assert self.driver.find_elements(*self.NAV_SIDEPANEL) or self.driver.find_elements(*self.DASHBOARD_HEADING), (
            "Expected to be on dashboard after login"
        )

    def assert_login_error(self):
        # Accept either error alert, toast text, or in-field 'Required' validation
        try:
            self.wait.until(EC.any_of(
                EC.visibility_of_element_located(self.ERROR_ALERT),
                EC.visibility_of_element_located(self.ERROR_TOAST),
                EC.visibility_of_element_located(self.FIELD_ERROR),
            ))
        except Exception:
            # Fall back to checking each individually
            try:
                self.wait.until(EC.visibility_of_element_located(self.ERROR_ALERT))
            except Exception:
                try:
                    self.wait.until(EC.visibility_of_element_located(self.ERROR_TOAST))
                except Exception:
                    self.wait.until(EC.visibility_of_element_located(self.FIELD_ERROR))

        # Prefer explicit error text from alert/toast
        alert = self.driver.find_elements(*self.ERROR_ALERT)
        if alert and alert[0].is_displayed():
            # Try to find inner content text, else use container text
            try:
                txt = self.driver.find_element(*self.ERROR_TOAST).text.strip()
            except Exception:
                txt = alert[0].text.strip()
            assert txt != "", "Expected an error message for invalid credentials"
            return

        toast = self.driver.find_elements(*self.ERROR_TOAST)
        if toast and toast[0].is_displayed():
            assert toast[0].text.strip() != "", "Expected an error message for invalid credentials"
            return

        # Otherwise in-field validation messages
        field_errs = self.driver.find_elements(*self.FIELD_ERROR)
        assert field_errs and any(e.text.strip() for e in field_errs), "Expected validation error messages"

    def assert_login_page_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        return self

    def logout_via_url(self):
        # Compute root from base_url; supports both full login URL and domain root
        if self.base_url.endswith(self.URL_PATH):
            root_base = self.base_url[: -len(self.URL_PATH)]
        else:
            root_base = self.base_url.rstrip("/")
        logout_url = root_base + "/web/index.php/auth/logout"
        self.driver.get(logout_url)
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        return self


