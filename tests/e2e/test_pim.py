import pytest
from faker import Faker

from pages.orangehrm.login_page import OrangeLoginPage
from pages.orangehrm.pim_page import OrangePIMPage


fake = Faker()


@pytest.mark.pim
def test_add_employee_minimal(browser, wait, base_url):
    # Login first
    OrangeLoginPage(browser, wait, base_url).open().login("Admin", "admin123").assert_logged_in()

    pim = OrangePIMPage(browser, wait)
    first, last = fake.first_name(), fake.last_name()
    pim.go_to_pim().click_add_employee().fill_employee_name(first, "", last).save().assert_personal_details_loaded()


@pytest.mark.smoke
@pytest.mark.pim
def test_search_employee_by_name(browser, wait, base_url):
    # Login and ensure at least one employee exists (create then search)
    OrangeLoginPage(browser, wait, base_url).open().login("Admin", "admin123").assert_logged_in()

    pim = OrangePIMPage(browser, wait)
    first, last = fake.first_name(), fake.last_name()
    full_name = f"{first} {last}"
    pim.go_to_pim().click_add_employee().fill_employee_name(first, "", last).save().assert_personal_details_loaded()

    pim.go_to_pim().search_employee_by_name(full_name).assert_search_results_contains(full_name)


@pytest.mark.regression
@pytest.mark.pim
def test_edit_employee_last_name(browser, wait, base_url):
    OrangeLoginPage(browser, wait, base_url).open().login("Admin", "admin123").assert_logged_in()
    pim = OrangePIMPage(browser, wait)
    first, last = fake.first_name(), fake.last_name()
    pim.go_to_pim().click_add_employee().fill_employee_name(first, "", last).save().assert_personal_details_loaded()
    new_last = fake.last_name()
    pim.edit_last_name_on_personal_details(new_last)


@pytest.mark.regression
@pytest.mark.pim
def test_delete_employee(browser, wait, base_url):
    OrangeLoginPage(browser, wait, base_url).open().login("Admin", "admin123").assert_logged_in()
    pim = OrangePIMPage(browser, wait)
    first, last = fake.first_name(), fake.last_name()
    full_name = f"{first} {last}"
    pim.go_to_pim().click_add_employee().fill_employee_name(first, "", last).save().assert_personal_details_loaded()
    pim.go_to_pim().search_employee_by_name(full_name).select_first_search_result().delete_selected_and_confirm().assert_no_search_results()


@pytest.mark.negative
@pytest.mark.pim
def test_add_employee_required_field_validation(browser, wait, base_url):
    OrangeLoginPage(browser, wait, base_url).open().login("Admin", "admin123").assert_logged_in()
    pim = OrangePIMPage(browser, wait)
    pim.go_to_pim().click_add_employee().attempt_save_with_empty_required_fields().assert_required_field_errors_present()

