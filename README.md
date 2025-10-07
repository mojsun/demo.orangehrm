## OrangeHRM UI Automation (Selenium + Python + pytest)

End-to-end UI tests for the OrangeHRM demo app using Selenium WebDriver and pytest. Includes a ready-to-run test matrix, HTML reporting with embedded screenshots, and page objects.

### Features
- Chrome/Firefox support, headed or headless
- Page Object Model for `Login` and `PIM`
- Markers: `smoke`, `regression`, `negative`, `pim`
- HTML report with embedded screenshots on failure
- Artifacts (screenshots + page HTML) saved per failing test

### Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run a visible smoke login
HEADLESS=false python -m pytest tests/e2e/test_login.py::test_login_success --browser=chrome -vv -s \
  --html=report.html --self-contained-html
open report.html
```

### Common runs
- All smoke tests (headed):
```bash
HEADLESS=false python -m pytest -m smoke --browser=chrome -vv -s \
  --html=report.html --self-contained-html
```
- Full matrix (can be slow):
```bash
HEADLESS=false python -m pytest -m "smoke or regression or negative or pim" --browser=chrome -vv -s \
  --html=report.html --self-contained-html
```

### Test matrix
Open in Excel:
```bash
open tests/data/test_matrix.csv
```

### Configuration (env vars)
- `BASE_URL` (default: OrangeHRM demo login)
- `BROWSER` = chrome|firefox (default: chrome)
- `HEADLESS` = true|false (default: true)
- `EXPLICIT_WAIT_SECONDS` (default: 15)
- `ARTIFACTS_DIR` (default: artifacts)

### Artifacts and reporting
- HTML: `report.html` (self-contained with images)
- On failure, per-test directory under `artifacts/<nodeid>/` contains:
  - `screenshot-<timestamp>.png`
  - `page-<timestamp>.html`
- Additionally, `conftest.py` attaches a screenshot to the report row for each failed test (stored under `artifacts/report_screens/`).

### Troubleshooting
- If Chrome window closes during teardown and screenshot fails, re-run headed and avoid closing the window manually.
- If `faker` not found, ensure you are using this project’s venv: `source .venv/bin/activate` then `pip install -r requirements.txt`.
- To avoid mixing with base conda Python, call `python -m pytest` from `.venv`.

### License
MIT
