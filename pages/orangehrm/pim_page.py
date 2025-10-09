from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class OrangePIMPage:
    MENU_PIM = (By.XPATH, "//span[normalize-space()='PIM']")
    ADD_BUTTON = (By.XPATH, "//button[normalize-space()='Add']")
    FIRST_NAME = (By.NAME, "firstName")
    MIDDLE_NAME = (By.NAME, "middleName")
    LAST_NAME = (By.NAME, "lastName")
    PERSONAL_LAST_NAME_INPUT = (By.XPATH, "//label[normalize-space()='Last Name']/../following-sibling::div//input")
    PERSONAL_EMP_ID_INPUT = (By.XPATH, "//label[normalize-space()='Employee Id']/../following-sibling::div//input")
    EDIT_BUTTON = (By.XPATH, "//button[normalize-space()='Edit']")
    SAVE_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SAVE_TEXT_BUTTON = (By.XPATH, "//button[normalize-space()='Save']")
    PERSONAL_DETAILS_HEADER = (By.XPATH, "//h6[normalize-space()='Personal Details']")
    ADD_EMPLOYEE_HEADER = (By.XPATH, "//h6[normalize-space()='Add Employee']")
    EMPLOYEE_NAME_INPUT = (By.XPATH, "//label[normalize-space()='Employee Name']/../following-sibling::div//input")
    EMPLOYEE_ID_INPUT = (By.XPATH, "//label[normalize-space()='Employee Id']/../following-sibling::div//input")
    SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search']")
    RESULT_ROWS = (By.CSS_SELECTOR, "div.oxd-table-body div.oxd-table-card")
    ROW_CHECKBOX_WRAPPERS = (By.CSS_SELECTOR, "div.oxd-table-body div.oxd-table-card div.oxd-checkbox-wrapper")
    TOP_DELETE_BUTTON = (By.XPATH, "//button[.//i[contains(@class,'bi-trash')]]")
    CONFIRM_DELETE_BUTTON = (By.XPATH, "//div[@role='document']//button[normalize-space()='Yes, Delete']")
    NO_ROWS_PLACEHOLDER = (By.XPATH, "//span[normalize-space()='No Records Found']")
    FIELD_ERROR = (By.CSS_SELECTOR, "span.oxd-input-field-error-message")
    AUTOCOMPLETE_OPTIONS = (By.CSS_SELECTOR, "div.oxd-autocomplete-option")
    TOAST_SUCCESS = (By.CSS_SELECTOR, "div.oxd-toast.oxd-toast--success")

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def go_to_pim(self):
        self.wait.until(EC.element_to_be_clickable(self.MENU_PIM)).click()
        self.wait.until(EC.visibility_of_element_located(self.ADD_BUTTON))
        return self

    def click_add_employee(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_BUTTON)).click()
        # Wait for Add Employee page/form
        try:
            self.wait.until(EC.visibility_of_element_located(self.ADD_EMPLOYEE_HEADER))
        except Exception:
            pass
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
        return self

    def fill_employee_name(self, first: str, middle: str, last: str):
        self.driver.find_element(*self.FIRST_NAME).clear()
        self.driver.find_element(*self.FIRST_NAME).send_keys(first)
        if middle:
            self.driver.find_element(*self.MIDDLE_NAME).clear()
            self.driver.find_element(*self.MIDDLE_NAME).send_keys(middle)
        self.driver.find_element(*self.LAST_NAME).clear()
        self.driver.find_element(*self.LAST_NAME).send_keys(last)
        return self

    def save(self):
        self.driver.find_element(*self.SAVE_BUTTON).click()
        return self

    def assert_personal_details_loaded(self):
        # Wait for either the page header or a known input on Personal Details
        try:
            self.wait.until(EC.any_of(
                EC.visibility_of_element_located(self.PERSONAL_DETAILS_HEADER),
                EC.visibility_of_element_located(self.LAST_NAME),
            ))
        except Exception:
            # Fallback to header to raise a clear timeout if both missing
            self.wait.until(EC.visibility_of_element_located(self.PERSONAL_DETAILS_HEADER))

    def search_employee_by_name(self, full_name: str):
        # Ensure we are on the PIM page
        self.wait.until(EC.visibility_of_element_located(self.ADD_BUTTON))
        self.wait.until(EC.visibility_of_element_located(self.EMPLOYEE_NAME_INPUT))
        def do_search():
            name_input = self.driver.find_element(*self.EMPLOYEE_NAME_INPUT)
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", name_input)
            except Exception:
                pass
            name_input.clear()
            name_input.send_keys(full_name)
            # If autocomplete appears, select first option; otherwise press Enter
            try:
                self.wait.until(EC.visibility_of_any_elements_located(self.AUTOCOMPLETE_OPTIONS))
                self.driver.find_elements(*self.AUTOCOMPLETE_OPTIONS)[0].click()
            except Exception:
                name_input.send_keys(Keys.ENTER)
            self.wait.until(EC.element_to_be_clickable(self.SEARCH_BUTTON)).click()

        # Try search up to 2 times in case indexing is delayed
        attempts = 0
        while attempts < 2:
            do_search()
            try:
                self.wait.until(EC.any_of(
                    EC.presence_of_all_elements_located(self.RESULT_ROWS),
                    EC.visibility_of_element_located(self.NO_ROWS_PLACEHOLDER),
                ))
                break
            except Exception:
                attempts += 1
                time.sleep(1)
        return self

    def assert_search_results_contains(self, expected_name: str):
        # Wait for either rows or placeholder
        try:
            self.wait.until(EC.any_of(
                EC.presence_of_all_elements_located(self.RESULT_ROWS),
                EC.visibility_of_element_located(self.NO_ROWS_PLACEHOLDER),
            ))
        except Exception:
            self.wait.until(EC.presence_of_all_elements_located(self.RESULT_ROWS))
        # If "No Records Found" is visible, fail explicitly
        no_rows = self.driver.find_elements(*self.NO_ROWS_PLACEHOLDER)
        if no_rows:
            assert False, f"No results after search for: {expected_name}"
        rows = self.driver.find_elements(*self.RESULT_ROWS)
        combined_text = "\n".join(row.text for row in rows)
        tokens = [expected_name, expected_name.split(" ")[0]]
        assert any(token and token in combined_text for token in tokens), "Expected employee to appear in search results"

    def edit_last_name_on_personal_details(self, new_last: str):
        # Assumes we are on personal details page after creation or navigation
        # Some pages require clicking Edit before fields become enabled
        try:
            self.wait.until(EC.element_to_be_clickable(self.EDIT_BUTTON)).click()
        except Exception:
            pass
        self.wait.until(EC.visibility_of_element_located(self.LAST_NAME))
        last_input = self.driver.find_element(*self.LAST_NAME)
        # Ensure the field is enabled; if not, click Edit again and wait
        if not last_input.is_enabled():
            try:
                self.driver.find_element(*self.EDIT_BUTTON).click()
            except Exception:
                pass
            self.wait.until(lambda d: d.find_element(*self.LAST_NAME).is_enabled())
            last_input = self.driver.find_element(*self.LAST_NAME)
        # Ensure in view, then robustly set value
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_input)
        except Exception:
            pass
        try:
            last_input.clear()
        except Exception:
            # Fallback to select-all + delete
            last_input.send_keys(Keys.CONTROL, "a")
            last_input.send_keys(Keys.DELETE)
        last_input.send_keys(new_last)
        # If value didn't change, force-set via JS and dispatch input event
        try:
            self.wait.until(lambda d: d.find_element(*self.LAST_NAME).get_attribute("value") == new_last)
        except Exception:
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                last_input,
                new_last,
            )
        # Click the visible Save button (some pages have multiple submit buttons)
        try:
            self.wait.until(EC.element_to_be_clickable(self.SAVE_TEXT_BUTTON)).click()
        except Exception:
            self.driver.find_element(*self.SAVE_BUTTON).click()
        # Wait until the value reflects the change
        try:
            self.wait.until(EC.visibility_of_element_located(self.TOAST_SUCCESS))
        except Exception:
            pass
        # Re-find input after save and verify
        self.wait.until(lambda d: d.find_element(*self.LAST_NAME).get_attribute("value") == new_last)
        return self

    def select_first_search_result(self):
        self.wait.until(EC.presence_of_all_elements_located(self.RESULT_ROWS))
        wrappers = self.driver.find_elements(*self.ROW_CHECKBOX_WRAPPERS)
        if not wrappers:
            raise AssertionError("No search results to select")
        wrappers[0].click()
        return self

    def delete_selected_and_confirm(self):
        # Click toolbar delete, confirm dialog
        self.wait.until(EC.element_to_be_clickable(self.TOP_DELETE_BUTTON)).click()
        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_DELETE_BUTTON)).click()
        # After deletion, either 'No Records Found' appears or rows reduce
        return self

    def assert_no_search_results(self):
        # Either placeholder shows or no cards exist
        try:
            self.wait.until(EC.visibility_of_element_located(self.NO_ROWS_PLACEHOLDER))
            return self
        except Exception:
            rows = self.driver.find_elements(*self.RESULT_ROWS)
            assert len(rows) == 0, "Expected no search results after deletion"
            return self

    def attempt_save_with_empty_required_fields(self):
        # On Add Employee form: clear names and try save, expect validation errors
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
        self.driver.find_element(*self.FIRST_NAME).clear()
        try:
            self.driver.find_element(*self.MIDDLE_NAME).clear()
        except Exception:
            pass
        self.driver.find_element(*self.LAST_NAME).clear()
        self.driver.find_element(*self.SAVE_BUTTON).click()
        self.wait.until(EC.visibility_of_any_elements_located(self.FIELD_ERROR))
        return self

    def assert_required_field_errors_present(self):
        errors = self.driver.find_elements(*self.FIELD_ERROR)
        assert errors, "Expected required field validation errors to be shown"
        return self

    def get_current_employee_id(self) -> str:
        # On Personal Details: read the Employee Id value
        self.wait.until(EC.visibility_of_element_located(self.PERSONAL_EMP_ID_INPUT))
        return self.driver.find_element(*self.PERSONAL_EMP_ID_INPUT).get_attribute("value").strip()

    def search_employee_by_id(self, emp_id: str):
        self.wait.until(EC.visibility_of_element_located(self.ADD_BUTTON))
        self.wait.until(EC.visibility_of_element_located(self.EMPLOYEE_ID_INPUT))
        emp_input = self.driver.find_element(*self.EMPLOYEE_ID_INPUT)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", emp_input)
        except Exception:
            pass
        emp_input.clear()
        emp_input.send_keys(emp_id)
        self.wait.until(EC.element_to_be_clickable(self.SEARCH_BUTTON)).click()
        self.wait.until(EC.any_of(
            EC.presence_of_all_elements_located(self.RESULT_ROWS),
            EC.visibility_of_element_located(self.NO_ROWS_PLACEHOLDER),
        ))
        return self

    def assert_results_count_at_least(self, minimum: int = 1):
        rows = self.driver.find_elements(*self.RESULT_ROWS)
        assert len(rows) >= minimum, f"Expected at least {minimum} search result(s)"
        return self


