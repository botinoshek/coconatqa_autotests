from api.tools_api import Tools
from config import settings
from models.page_object_models import CinescopLoginPage
from resources.user_creds import SuperAdminCreds
import pytest
import os

"""
Не фиксируем путь Playwright браузеров внутри репозитория.
Playwright использует стандартный кеш (~/.cache/ms-playwright),
что предотвращает попадание браузеров в git и раздувание проекта.
"""

@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    # Можно переопределить канал и headless через env:
    # PW_CHROMIUM_CHANNEL=chrome (использовать системный Chrome)
    # PW_HEADLESS=true
    channel = os.getenv("PW_CHROMIUM_CHANNEL")
    headless = os.getenv("PW_HEADLESS", "false").lower() == "true"
    launch_kwargs = {"headless": headless}
    if channel:
        launch_kwargs["channel"] = channel
    browser = playwright.chromium.launch(**launch_kwargs)  # headless=True для CI/CD, headless=False для локальной разработки
    yield browser  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    browser.close()  # Браузер закрывается после завершения всех тестов


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(settings.ui_timeout_ms)
    yield context
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir('playwright_trace', log_name)
    context.tracing.stop(path=trace_path)
    context.close()

@pytest.fixture(scope="function")  # Страница создается для каждого теста
def page(context):
    page = context.new_page()
    yield page  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    page.close()  # Страница закрывается после завершения теста

@pytest.fixture
def admin_page(page):
    if not SuperAdminCreds.USERNAME or not SuperAdminCreds.PASSWORD:
        pytest.skip("Не заданы SUPER_ADMIN_USERNAME/SUPER_ADMIN_PASSWORD в .env")

    login_page = CinescopLoginPage(page)
    login_page.open()
    login_page.login(SuperAdminCreds.USERNAME, SuperAdminCreds.PASSWORD)
    login_page.assert_was_redirect_to_home_page()

    return page

@pytest.fixture
def authorized_page(context, auth_api, test_user):
    # 1) register
    auth_api.register_user(test_user)

    # 2) login через UI (без прокидывания токена)
    page = context.new_page()
    page.goto(f"{settings.base_url}login")
    page.get_by_role("textbox", name="Email").fill(test_user.email)
    page.get_by_role("textbox", name="Пароль").fill(test_user.password)
    page.locator("form").get_by_role("button", name="Войти").click()
    page.get_by_role("link", name="Профиль").wait_for()

    yield page
    page.close()
