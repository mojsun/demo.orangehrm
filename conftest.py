import os
import pathlib
import time
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config.settings import BASE_URL, DEFAULT_BROWSER, HEADLESS, EXPLICIT_WAIT_SECONDS, ARTIFACTS_DIR
from config.browsers import create_driver


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=DEFAULT_BROWSER)
    parser.addoption("--headless", action="store_true", default=HEADLESS)


@pytest.fixture
def browser(request):
    browser_name = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    driver = create_driver(browser_name, headless)
    driver.implicitly_wait(0)
    yield driver
    _capture_artifacts_on_failure(request, driver)
    driver.quit()


def _capture_artifacts_on_failure(request, driver):
    # If the test failed, capture screenshot and page source
    if request.node.rep_call.failed:  # type: ignore[attr-defined]
        test_name = request.node.nodeid.replace("::", "-").replace("/", "_")
        out_dir = pathlib.Path(ARTIFACTS_DIR) / test_name
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        driver.save_screenshot(str(out_dir / f"screenshot-{ts}.png"))
        with open(out_dir / f"page-{ts}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    # Embed screenshot into pytest-html report on failure/skipped-xfail
    try:
        pytest_html = item.config.pluginmanager.getplugin("html")
    except Exception:
        pytest_html = None
    if not pytest_html:
        return

    extras = getattr(rep, "extras", [])

    if rep.when in ("setup", "call"):
        xfail = hasattr(rep, "wasxfail")
        if (rep.skipped and xfail) or (rep.failed and not xfail):
            # Resolve driver from our fixture name
            drv = item.funcargs.get("browser", None)
            if drv is not None:
                safe_name = (
                    item.nodeid
                    .replace("::", "_")
                    .replace("/", "_")
                    .replace("\\", "_")
                    .replace("[", "_")
                    .replace("]", "_")
                    .replace(" ", "_")
                )
                out_dir = pathlib.Path(ARTIFACTS_DIR) / "report_screens"
                out_dir.mkdir(parents=True, exist_ok=True)
                ts = time.strftime("%Y%m%d-%H%M%S")
                file_path = out_dir / f"{safe_name}-{ts}.png"
                try:
                    drv.save_screenshot(str(file_path))
                    extras.append(pytest_html.extras.image(str(file_path), mime_type="image/png"))
                except Exception:
                    pass

    rep.extras = extras


@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, EXPLICIT_WAIT_SECONDS)


@pytest.fixture
def base_url():
    return BASE_URL

