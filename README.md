# Rapidusertests Playwright Assignment

**Repository:** https://github.com/softwaretesteravneet-sudo/testassingment-byAvneet

Python + Playwright suite for the Rapidusertests PRE auth application.

| Item | Value |
| --- | --- |
| App | https://auth.pre.stgrapidusertests.com/login |
| In scope | Customer registration (submit + field validation), standard login, SSO via Auth0 |
| Out of scope | Tester registration, clicking the email verification link |
| Browser | Google Chrome only (Playwright `chrome` channel, not bundled Chromium) |
| Suite folder | [`rapidtester-playwright/`](rapidtester-playwright/) |

A new clone should work after Python, Chrome, and a local `.env` are in place. Credentials stay out of git.

---

## Approach

The suite is built so a new engineer can read a test and understand the user journey without hunting for locators or passwords.

1. **Page Object Model.** Locators and clicks live in `pages/`. Tests describe the journey only.
2. **Test data is separate.** Accounts and registration payloads live in `testdata/`. Page objects never hardcode credentials.
3. **Secrets stay in `.env`.** Basic Auth, login, and optional SSO users are loaded at runtime. `.env` and `.env.example` are gitignored.
4. **One module per assignment flow.** `test_login.py`, `test_registration.py`, `test_sso.py`.
5. **Ready for parallel runs.** Default is four Chrome workers (`pytest -n 4`). Each registration uses a unique email so workers do not collide.
6. **Google Chrome, not Chromium.** `conftest.py` finds or installs Chrome. Reports label the browser as Google Chrome even though Playwright’s engine id is `chromium`.
7. **HTTP Basic Auth on the browser context.** The PRE environment is gated. Playwright sends the gate user on every request so tests never type that prompt.
8. **Honest SSO.** Auth0 is the external provider. The reachable part (redirect + OAuth/PKCE contract) always runs. Completing login is skipped unless an enterprise-directory user is configured — that skip is not treated as a pass.

---

## Architecture

Tests never own locators or credentials. Page objects never own test data. Configuration never lives in a test file.

```text
testassingment-byAvneet/
  README.md                         This guide
  .github/workflows/playwright.yml  CI: install Chrome, run pytest in parallel
  rapidtester-playwright/
    config/
      settings.py                   BASE_URL, APP_URL, Basic Auth, Auth0 host/client
      browser.py                    Chrome channel, launch args, timeouts, viewport
    testdata/
      users.py                      standard_user() and sso_user() from .env
      customers.py                  unique registration payloads (parallel-safe)
      sso.py                        Auth0 OAuth/PKCE contract constants
      models.py                     User and CustomerRegistrationData
    pages/
      base_page.py                  goto, get_by_test_id, wait for Vue
      login_page.py                 email/password login and SSO link
      registration_page.py          customer signup form and field errors
      auth0_page.py                 external SSO provider + /authorize checks
      two_factor_page.py            optional 2FA splash (Skip)
      dashboard_page.py             authenticated landing (/profiles or app host)
    tests/
      test_login.py                 standard login positive flow
      test_registration.py          submit + field validation
      test_sso.py                   Auth0 contract + optional full SSO login
    utils/
      chrome.py                     find or install Google Chrome
      logger.py                     suite.log on console + report folder
      reporting.py                  reports/<date>/<time>/report.html
    conftest.py                     fixtures, Chrome check, shared xdist report dir
    pytest.ini                      -n 4, --browser-channel chrome, markers
    .env.example                    placeholder keys only (gitignored)
    .env                            real values on your machine (gitignored)
```

**How the layers connect**

```text
pytest
  → conftest.py
       loads Settings from .env
       launches Google Chrome with Basic Auth on the context
  → tests/          “open login, sign in, expect dashboard”
       uses testdata/ for who to sign in as
       uses pages/   for how to click and assert
  → pages/          only locators and user actions
  → config/         only environment and browser policy
```

| Layer | Owns | Does not own |
| --- | --- | --- |
| `tests/` | Scenarios and assertions | Locators, passwords |
| `pages/` | Locators and clicks | Emails, passwords, URLs |
| `testdata/` | Users and registration payloads | Playwright calls |
| `config/` | URLs, env, Chrome launch | Test logic |
| `.env` | Secrets | Anything committed to git |

---

## Setup on your machine (step by step)

Do these in order on a new laptop or a fresh clone.

### Step 1 — Install prerequisites

1. Install **Python 3.10 or newer** from https://www.python.org/downloads/  
   On Windows, tick **Add python.exe to PATH**.
2. Install **Google Chrome**.
3. Install **Git**, then clone this repository:

```powershell
git clone https://github.com/softwaretesteravneet-sudo/testassingment-byAvneet.git
cd testassingment-byAvneet
```

### Step 2 — Open the suite folder

All install and run commands below are from `rapidtester-playwright/`:

```powershell
cd rapidtester-playwright
```

### Step 3 — Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activate script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should show `(.venv)`.

### Step 4 — Install Python packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs Playwright, pytest, pytest-xdist (parallel), pytest-html (reports), python-dotenv, and Faker.

### Step 5 — Install the Playwright Chrome driver

```powershell
python -m playwright install chrome
```

This is the Playwright browser driver for the installed Google Chrome. You do not need Playwright’s bundled Chromium.

### Step 6 — Create your local `.env`

```powershell
copy .env.example .env
```

macOS / Linux: `cp .env.example .env`

Open `rapidtester-playwright/.env` in an editor. Fill every required key from the **assignment PDF**. Do not commit this file.

| Variable | What to paste from the PDF |
| --- | --- |
| `BASIC_AUTH_USERNAME` | Environment Access username |
| `BASIC_AUTH_PASSWORD` | Environment Access password |
| `LOGIN_EMAIL` | Standard login email |
| `LOGIN_PASSWORD` | Standard login password |
| `AUTH0_HOST` | Auth0 host used by SSO (if listed / observed) |
| `AUTH0_CLIENT_ID` | Auth0 client id used by SSO (if listed / observed) |
| `SSO_EMAIL` / `SSO_PASSWORD` | Leave empty unless you have an enterprise-directory user |

`BASE_URL` and `APP_URL` can stay as in `.env.example` unless the assignment URL changes.

### Step 7 — Confirm Chrome and the env file

```powershell
python -c "from utils.chrome import ensure_google_chrome; print(ensure_google_chrome())"
```

If this prints a `chrome.exe` (or `google-chrome`) path, the browser is ready. If `.env` is missing a required value, the first test run will say which variable to add.

### Step 8 — Run the suite

**Headless (default, four Chrome workers):**

```powershell
pytest
```

**Headed (watch one Chrome window):**

```powershell
pytest -n 0 --headed
```

**One flow only:**

```powershell
pytest -n 0 --headed tests/test_login.py
pytest -n 0 --headed tests/test_registration.py
pytest -n 0 --headed tests/test_sso.py
```

### Step 9 — Open the report

After a run, open:

`rapidtester-playwright/reports/<YYYY-MM-DD>/<HH-MM-SS>/report.html`  
and the live run log:

`rapidtester-playwright/reports/<YYYY-MM-DD>/<HH-MM-SS>/suite.log`

During the run, INFO lines print in the terminal (test start/pass/skip/fail, page opens, login, submit). Failures include the page URL and the full error. DEBUG detail stays in `suite.log`. Passwords are never written to the log.

You should see **4 passed, 1 skipped** on the assignment account. The skip is the SSO completion test (see Flows below).

### Step 10 — Deactivate when you are done

```powershell
deactivate
```

Next time you only need:

```powershell
cd testassingment-byAvneet\rapidtester-playwright
.\.venv\Scripts\Activate.ps1
pytest
```

---

## Browser

| Setting | Default | Why |
| --- | --- | --- |
| Product | Google Chrome | Assignment is a real-user Chrome suite |
| Playwright channel | `chrome` (`BROWSER_CHANNEL`) | Uses the installed browser, not Chromium |
| Headless | Yes, unless you pass `--headed` | Fast CI / default local run |
| Headed | `pytest -n 0 --headed` | Watch the UI; one browser, no workers |
| Workers | 4 (`-n 4`) | Parallel-ready without extra spawn cost |
| Locale | `de-DE` | Matches the PRE app locale |
| Viewport | 1280×720 | Stable desktop layout |
| Action timeout | 12s | Fail fast on missing controls |
| Navigation timeout | 25s | Auth0 and app redirects are slower |
| Screenshots | On failure only | Smaller artifacts |
| Video / tracing | Off | Keeps the suite fast |

`utils/chrome.py` reuses Chrome if it is already installed. If it is missing, the session tries to install it before tests start.

Launch flags skip extensions, sync, first-run dialogs, and other Chrome noise so parallel workers stay quiet.

---

## Pytest markers (comments on each test)

Markers are the labels in `pytest.ini`. They are how you group and explain tests.

| Marker | Meaning | Used on |
| --- | --- | --- |
| `smoke` | Critical happy path — run this first | Login, registration submit, SSO contract |
| `login` | Standard email/password login | `test_standard_login_positive_flow` |
| `registration` | Customer signup only (not tester signup) | Both registration tests |
| `sso` | External provider (Auth0) | Both SSO tests |

```powershell
pytest -m smoke
pytest -m login
pytest -m registration
pytest -m sso
pytest -m "smoke and not sso"
```

---

## Flows

All flows start behind HTTP Basic Auth. The browser context already has those credentials, so the first page you see is the app, not the gate.

### 1. Customer registration — submit

**File:** `tests/test_registration.py` → `test_customer_registration_submits_form`  
**Markers:** `smoke`, `registration`  
**Page:** `/customer/signup` (customer only; tester signup is not opened)

```text
Open customer signup
  → form is ready, Create Account is disabled
  → fill first name, last name, company, unique email, password, accept terms
  → submit
  → assert the “resend confirmation email” link is visible
```

Email-link verification is out of scope. A unique email (`your.email+rt<token>@gmail.com`) is generated so parallel workers never register the same user twice.

### 2. Customer registration — field validation

**File:** `tests/test_registration.py` → `test_customer_registration_field_validation`  
**Markers:** `registration`  
**Same page load** for every check (faster than opening the form four times).

```text
Fill name, company, email          → submit stays disabled (no password, no terms)
Fill password                      → submit still disabled (terms unchecked)
Check terms                        → submit becomes enabled
Clear first name / last name /
  company / email and submit       → matching field error
Type an invalid email              → email error
Type a weak password               → password error
```

### 3. Standard login — positive flow

**File:** `tests/test_login.py` → `test_standard_login_positive_flow`  
**Markers:** `smoke`, `login`  
**Page:** `/login`  
**User:** `LOGIN_EMAIL` / `LOGIN_PASSWORD` from `.env` (assignment standard account)

```text
Open login
  → email, password, Login, and SSO link are visible
  → sign in with the standard account
  → if the optional 2FA splash appears, click Skip
  → assert the URL is /profiles or the app host
```

### 4. SSO — open Auth0 and check the contract (always runs)

**File:** `tests/test_sso.py` → `test_sso_opens_auth0_with_valid_authorize_contract`  
**Markers:** `smoke`, `sso`  
**External provider:** Auth0 Universal Login

```text
Open login
  → click the SSO link
  → capture the Auth0 /authorize request
  → assert HTTPS, Auth0 host, client id, redirect /sso/callback
  → assert response_type=code, response_mode=query, PKCE S256
  → assert scopes openid, profile, email, plus state and nonce
  → assert the Auth0 “Welcome” identifier screen
```

This is the positive SSO start the assignment asked for: the app hands the user to the external provider with a valid OAuth/PKCE request.

### 5. SSO — finish login when Auth0 accepts the email (often skipped)

**File:** `tests/test_sso.py` → `test_sso_completes_login_when_provider_accepts_identifier`  
**Markers:** `sso`

```text
Open login → start SSO → Auth0 Welcome screen
  → type SSO_EMAIL (defaults to the standard login email)
  → if the password field appears:
        type password → wait for callback → skip 2FA if shown
        → assert authenticated app URL
  → if Auth0 shows “Email does not match any enterprise directory”:
        skip (do not fail, do not pass)
```

**Why it skips today**

This Auth0 tenant only accepts emails that belong to a configured **enterprise directory** (company IdP). The assignment account is a normal database user. Auth0 therefore never shows the password field, so the test cannot complete a full SSO session.

That is a tenant / data limit, not a broken click path. The contract test above still proves SSO starts correctly.

**How a new user would finish it**

Put an enterprise-directory email and password in `.env` as `SSO_EMAIL` and `SSO_PASSWORD`. Re-run `pytest -m sso`. The skip goes away and the test asserts the same authenticated landing as standard login.

---

## Configuration (`.env`)

`.env` is optional. If a variable is missing, the suite uses the values from the assignment PDF so CI and a fresh clone can run `pytest` without GitHub secrets. A local `.env` still overrides those defaults and is gitignored.

| Variable | Required | Purpose |
| --- | --- | --- |
| `BASE_URL` | Yes (has a default URL) | Auth origin |
| `APP_URL` | Yes (has a default URL) | App origin after login |
| `BASIC_AUTH_USERNAME` | Yes | PRE environment gate |
| `BASIC_AUTH_PASSWORD` | Yes | PRE environment gate |
| `LOGIN_EMAIL` | Yes | Standard login |
| `LOGIN_PASSWORD` | Yes | Standard login |
| `SSO_EMAIL` | Optional | Enterprise SSO user; falls back to login email |
| `SSO_PASSWORD` | Optional | Enterprise SSO user; falls back to login password |
| `AUTH0_HOST` | Yes | Host checked on `/authorize` |
| `AUTH0_CLIENT_ID` | Yes | Client id checked on `/authorize` |
| `BROWSER_CHANNEL` | Optional | Default `chrome` |
| `BROWSER_LOCALE` | Optional | Default `de-DE` |

GitHub Actions does not need repository secrets for the assignment account. Optional secrets still override the PDF defaults when you set them.

---

## Expected result

On this assignment account, both headless and headed runs look like:

```text
4 passed, 1 skipped
```

| Test | Typical result |
| --- | --- |
| `test_standard_login_positive_flow` | Passed |
| `test_customer_registration_submits_form` | Passed |
| `test_customer_registration_field_validation` | Passed |
| `test_sso_opens_auth0_with_valid_authorize_contract` | Passed |
| `test_sso_completes_login_when_provider_accepts_identifier` | Skipped until an enterprise SSO user is provided |

CI (`.github/workflows/playwright.yml`) runs the same headless command from `rapidtester-playwright/` and uploads the HTML report.
