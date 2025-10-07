import pytest

from pages.orangehrm.login_page import OrangeLoginPage


@pytest.mark.smoke
def test_login_success(browser, wait, base_url):
    page = OrangeLoginPage(browser, wait, base_url)
    page.open().login("Admin", "admin123").assert_logged_in()


@pytest.mark.negative
@pytest.mark.parametrize("username,password", [
    ("Admin", "wrongpass"),
    ("WrongUser", "admin123"),
    ("", ""),
])
def test_login_negative(browser, wait, base_url, username, password):
    page = OrangeLoginPage(browser, wait, base_url)
    page.open().login(username, password).assert_login_error()


@pytest.mark.smoke
def test_logout_returns_to_login(browser, wait, base_url):
    page = OrangeLoginPage(browser, wait, base_url)
    page.open().login("Admin", "admin123").assert_logged_in()
    page.logout_via_url().assert_login_page_loaded()

