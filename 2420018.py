import pytest
import time
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ═══════════════════════════════════════════════════════════════
# ENUMS & DATCLASSES
# ═══════════════════════════════════════════════════════════════

class PageName(Enum):
    CAMERAS = "cameras"
    LENSES = "lenses"
    CONTACT = "contact"


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class ContactData:
    name: str
    email: str
    phone: str
    message: str


# ═══════════════════════════════════════════════════════════════
# SELECTORS REGISTRY
# ═══════════════════════════════════════════════════════════════

class Selectors:
    """Centralized element selectors for all pages."""

    # Login Page
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BTN = (By.XPATH, "//div[@class='login-panel']//button")
    LOGIN_PAGE = (By.ID, "loginPage")
    LOGIN_ERROR = (By.ID, "loginError")
    USER_BADGE = (By.ID, "userBadge")

    # Main App
    APP = (By.ID, "app")
    LOGOUT_BTN = (By.XPATH, "//button[contains(@class, 'logout')]")

    # Navigation
    NAV_BUTTON = lambda page: (By.XPATH, f"//nav//button[@data-page='{page}']")

    # Pages
    CAMERAS_PAGE = (By.ID, "cameras")
    LENSES_PAGE = (By.ID, "lenses")
    CONTACT_PAGE = (By.ID, "contact")

    # Contact Form
    NAME_INPUT = (By.ID, "name")
    EMAIL_INPUT = (By.ID, "email")
    PHONE_INPUT = (By.ID, "phone")
    MESSAGE_INPUT = (By.ID, "message")
    SUBMIT_BTN = (By.XPATH, "//form//button[@type='submit']")

    # Error Messages
    NAME_ERROR = (By.ID, "nameError")
    EMAIL_ERROR = (By.ID, "emailError")
    PHONE_ERROR = (By.ID, "phoneError")
    FORM_SUCCESS = (By.ID, "formSuccess")


# ═══════════════════════════════════════════════════════════════
# PAGE OBJECT CLASSES
# ═══════════════════════════════════════════════════════════════

class BasePage:
    """Base page with common operations."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def find_element(self, locator):
        """Find element with explicit wait."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def is_displayed(self, locator) -> bool:
        """Check if element is displayed."""
        try:
            return self.find_element(locator).is_displayed()
        except:
            return False

    def get_text(self, locator) -> str:
        """Get element text."""
        return self.find_element(locator).text

    def click(self, locator):
        """Click element."""
        self.find_element(locator).click()

    def type_text(self, locator, text: str):
        """Type text into element."""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def clear_field(self, locator):
        element = self.find_element(locator)
        element.clear()
        # Force the field to be empty (workaround for stubborn inputs)
        element.send_keys("")

    def execute_js(self, script: str):
        """Execute JavaScript."""
        self.driver.execute_script(script)


class LoginPage(BasePage):
    """Page object for login functionality."""

    def is_login_page_visible(self) -> bool:
        return self.is_displayed(Selectors.LOGIN_PAGE)

    def login(self, credentials: Credentials):
        """Perform login with credentials."""
        self.type_text(Selectors.USERNAME_INPUT, credentials.username)
        self.type_text(Selectors.PASSWORD_INPUT, credentials.password)
        self.click(Selectors.LOGIN_BTN)
        time.sleep(0.5)

    def get_error_message(self) -> str:
        return self.get_text(Selectors.LOGIN_ERROR)

    def get_user_initials(self) -> str:
        return self.get_text(Selectors.USER_BADGE)


class AppPage(BasePage):
    """Page object for main application."""

    def is_app_visible(self) -> bool:
        return self.is_displayed(Selectors.APP)

    def navigate_to_page(self, page: PageName):
        """Navigate to a specific page."""
        self.click(Selectors.NAV_BUTTON(page.value))

    def is_page_visible(self, page: PageName) -> bool:
        """Check if a page is visible."""
        locator_map = {
            PageName.CAMERAS: Selectors.CAMERAS_PAGE,
            PageName.LENSES: Selectors.LENSES_PAGE,
            PageName.CONTACT: Selectors.CONTACT_PAGE,
        }
        return self.is_displayed(locator_map[page])

    def logout(self):
        """Click logout button."""
        self.click(Selectors.LOGOUT_BTN)


class ContactFormPage(BasePage):
    """Page object for contact form."""

    def fill_contact_form(self, data: ContactData):
        """Fill all contact form fields."""
        self.type_text(Selectors.NAME_INPUT, data.name)
        self.type_text(Selectors.EMAIL_INPUT, data.email)
        self.type_text(Selectors.PHONE_INPUT, data.phone)
        self.type_text(Selectors.MESSAGE_INPUT, data.message)

    def clear_all_fields(self):
        """Clear all form fields."""
        for locator in [Selectors.NAME_INPUT, Selectors.EMAIL_INPUT,
                        Selectors.PHONE_INPUT, Selectors.MESSAGE_INPUT]:
            self.clear_field(locator)

    def clear_error_messages(self):
        """Clear all displayed error messages."""
        self.execute_js(
            "document.getElementById('nameError').innerText='';"
            "document.getElementById('emailError').innerText='';"
            "document.getElementById('phoneError').innerText='';"
            "document.getElementById('formSuccess').innerText='';"
        )

    def submit_form(self):
        """Submit the contact form."""
        self.click(Selectors.SUBMIT_BTN)

    def get_field_error(self, field_name: str) -> str:
        """Get error message for a specific field."""
        error_map = {
            "name": Selectors.NAME_ERROR,
            "email": Selectors.EMAIL_ERROR,
            "phone": Selectors.PHONE_ERROR,
        }
        return self.get_text(error_map[field_name])

    def get_success_message(self) -> str:
        return self.get_text(Selectors.FORM_SUCCESS)


# ═══════════════════════════════════════════════════════════════
# TEST FIXTURES & HELPERS
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driver():
    """Set up Chrome WebDriver."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    drv = webdriver.Chrome(options=options)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"file:///{current_dir}/index.html"
    drv.get(file_path)
    drv.implicitly_wait(2)

    yield drv
    drv.quit()


@pytest.fixture
def login_page(driver):
    return LoginPage(driver)


@pytest.fixture
def app_page(driver):
    return AppPage(driver)


@pytest.fixture
def contact_form_page(driver):
    return ContactFormPage(driver)


@pytest.fixture
def valid_credentials():
    return Credentials(username="admin", password="@Dm1n")


@pytest.fixture
def valid_contact_data():
    return ContactData(
        name="Ivan Ivanov",
        email="ivan@example.com",
        phone="+359 888 000 111",
        message="Hello, I would like to ask about camera rentals."
    )


def ensure_logged_in(app_page, login_page, valid_credentials):
    """Helper to ensure user is logged in."""
    if not app_page.is_app_visible():
        login_page.login(valid_credentials)


# ═══════════════════════════════════════════════════════════════
# TEST CLASSES
# ═══════════════════════════════════════════════════════════════

class TestLogin:
    """Login functionality tests."""

    def test_login_page_visible_on_startup(self, login_page):
        assert login_page.is_login_page_visible(), \
            "Login page should be visible on startup"

    def test_invalid_credentials_error(self, login_page, driver):
        invalid_creds = Credentials(username="invalid", password="wrong")
        login_page.login(invalid_creds)
        error = login_page.get_error_message()
        assert error == "Incorrect username or password.", \
            f"Expected error message, got: {error}"

    def test_valid_login_shows_app(self, driver, app_page, login_page, valid_credentials):
        driver.get(driver.current_url)  # Reset
        login_page.login(valid_credentials)
        assert app_page.is_app_visible(), "App should be visible after login"
        assert not login_page.is_login_page_visible(), "Login page should be hidden"

    def test_user_initials_displayed(self, login_page, app_page, valid_credentials):
        ensure_logged_in(app_page, login_page, valid_credentials)
        initials = login_page.get_user_initials()
        assert initials == "AD", f"Expected initials 'AD', got '{initials}'"


class TestNavigation:
    """Navigation between pages tests."""

    @pytest.fixture(autouse=True)
    def setup(self, app_page, login_page, valid_credentials):
        ensure_logged_in(app_page, login_page, valid_credentials)

    def test_cameras_visible_by_default(self, app_page):
        assert app_page.is_page_visible(PageName.CAMERAS), \
            "Cameras page should be visible by default"

    def test_navigate_to_lenses(self, app_page):
        app_page.navigate_to_page(PageName.LENSES)
        assert app_page.is_page_visible(PageName.LENSES), \
            "Lenses page should be visible after navigation"

    def test_navigate_to_contact(self, app_page):
        app_page.navigate_to_page(PageName.CONTACT)
        assert app_page.is_page_visible(PageName.CONTACT), \
            "Contact page should be visible after navigation"

    def test_navigate_back_to_cameras(self, app_page):
        app_page.navigate_to_page(PageName.CAMERAS)
        assert app_page.is_page_visible(PageName.CAMERAS), \
            "Should be able to navigate back to cameras"

    def test_only_one_page_visible(self, app_page):
        app_page.navigate_to_page(PageName.LENSES)
        assert not app_page.is_page_visible(PageName.CAMERAS), \
            "Cameras should be hidden when Lenses is active"
        assert not app_page.is_page_visible(PageName.CONTACT), \
            "Contact should be hidden when Lenses is active"


class TestContactFormValidation:
    """Contact form validation tests."""

    @pytest.fixture(autouse=True)
    def setup(self, app_page, login_page, contact_form_page, valid_credentials):
        ensure_logged_in(app_page, login_page, valid_credentials)
        app_page.navigate_to_page(PageName.CONTACT)
        contact_form_page.clear_all_fields()
        contact_form_page.clear_error_messages()

    def test_name_required(self, contact_form_page):
        # Принудительно очищаем поле имени через JavaScript
        contact_form_page.driver.execute_script("document.getElementById('name').value = '';")
        # (Опционально) убедимся, что значение действительно пустое
        value = contact_form_page.driver.execute_script("return document.getElementById('name').value;")
        assert value == "", f"Name field is not empty: '{value}'"
        # Отправляем форму
        contact_form_page.submit_form()
        # Ждём появления сообщения об ошибке
        WebDriverWait(contact_form_page.driver, 3).until(
            EC.text_to_be_present_in_element(Selectors.NAME_ERROR, "Name is required.")
        )
        error = contact_form_page.get_field_error("name")
        assert error == "Name is required."

    def test_email_required_when_empty(self, contact_form_page):
        contact_form_page.type_text(Selectors.EMAIL_INPUT, "a")
        contact_form_page.find_element(Selectors.EMAIL_INPUT).send_keys(Keys.BACKSPACE)
        error = contact_form_page.get_field_error("email")
        assert error == "Email address is required.", f"Got error: {error}"

    def test_email_invalid_format(self, contact_form_page):
        contact_form_page.type_text(Selectors.EMAIL_INPUT, "not_an_email")
        error = contact_form_page.get_field_error("email")
        assert "valid email" in error, f"Expected format error, got: {error}"

    def test_email_valid_clears_error(self, contact_form_page):
        contact_form_page.type_text(Selectors.EMAIL_INPUT, "test@example.com")
        error = contact_form_page.get_field_error("email")
        assert error == "", f"Error should be cleared, but got: {error}"

    def test_phone_required_when_empty(self, contact_form_page):
        contact_form_page.type_text(Selectors.PHONE_INPUT, "1")
        contact_form_page.find_element(Selectors.PHONE_INPUT).send_keys(Keys.BACKSPACE)
        error = contact_form_page.get_field_error("phone")
        assert error == "Phone number is required.", f"Got error: {error}"

    def test_phone_too_short(self, contact_form_page):
        contact_form_page.type_text(Selectors.PHONE_INPUT, "123")
        error = contact_form_page.get_field_error("phone")
        assert "7–15 digits" in error, f"Expected length error, got: {error}"

    def test_phone_valid_clears_error(self, contact_form_page):
        contact_form_page.type_text(Selectors.PHONE_INPUT, "+359 888 123456")
        error = contact_form_page.get_field_error("phone")
        assert error == "", f"Error should be cleared, but got: {error}"


class TestContactFormSubmission:
    """Contact form submission tests."""

    @pytest.fixture(autouse=True)
    def setup(self, app_page, login_page, contact_form_page, valid_credentials):
        ensure_logged_in(app_page, login_page, valid_credentials)
        app_page.navigate_to_page(PageName.CONTACT)

    def test_successful_submission(self, contact_form_page, valid_contact_data):
        contact_form_page.fill_contact_form(valid_contact_data)
        contact_form_page.submit_form()
        success_msg = contact_form_page.get_success_message()
        assert success_msg == "Message sent successfully!", \
            f"Expected success message, got: {success_msg}"


class TestLogout:
    """Logout functionality tests."""

    def test_logout_returns_to_login(self, app_page, login_page, valid_credentials):
        ensure_logged_in(app_page, login_page, valid_credentials)
        app_page.logout()
        time.sleep(0.5)
        WebDriverWait(app_page.driver, 5).until(
            EC.visibility_of_element_located(Selectors.LOGIN_PAGE)
        )
        assert login_page.is_login_page_visible(), \
            "Should return to login page after logout"