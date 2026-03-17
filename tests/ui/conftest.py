from api.tools_api import Tools
from config import settings
import pytest, json
import os
import requests
import re

# Храним браузеры Playwright внутри репозитория, чтобы не упираться в права на ~/Library.
os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH",
    os.path.join(os.getcwd(), ".playwright-browsers"),
)

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
def created_movie(authorized_page):
    """
    UI-версия фикстуры: берем первый доступный фильм из /movies.
    Это обход для случаев, когда auth API недоступен по сети.
    """
    page = authorized_page
    page.goto(f"{settings.base_url}movies")
    first_link = page.get_by_role("link", name="Подробнее").first
    first_link.wait_for()
    href = first_link.get_attribute("href")
    assert href, "Ссылка на фильм не найдена на странице /movies"
    match = re.search(r"/movies/(\d+)", href)
    assert match, f"Не удалось извлечь movie_id из href: {href}"
    return int(match.group(1))

@pytest.fixture
def authorized_page(context, auth_api, test_user):
    # 1) register
    auth_api.register_user(test_user)

    page = context.new_page()
    # 2) login через UI, чтобы гарантированно появился блок комментариев
    page.goto(f"{settings.base_url}login")
    page.get_by_role("textbox", name="Email").fill(test_user.email)
    page.get_by_role("textbox", name="Пароль").fill(test_user.password)
    page.locator("form").get_by_role("button", name="Войти").click()
    page.get_by_role("link", name="Профиль").wait_for()

    yield page
    page.close()
