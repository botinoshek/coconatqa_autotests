from Modul_4.Cinescope.api.tools_api import Tools
from Modul_4.Cinescope.config import settings
import pytest, json

@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    browser = playwright.chromium.launch(headless=False)  # headless=True для CI/CD, headless=False для локальной разработки
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
def authorized_page(context, auth_api, test_user):
    # 1) register
    auth_api.register_user(test_user)

    # 2) login (в requests появится refresh_token cookie на auth домене)
    login_data = {"email": test_user.email, "password": test_user.password}
    resp = auth_api.login_user(login_data, expected_status=201)

    # 3) переносим cookies ИМЕННО на auth-домен
    pw_cookies = []
    for c in auth_api.session.cookies:
        pw_cookies.append({
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path or "/",
        })
    context.add_cookies(pw_cookies)

    assert pw_cookies, "После логина в requests не появилось ни одной cookie"
    context.add_cookies(pw_cookies)

    # 4) открываем UI
    token = resp.json().get("accessToken")
    assert token, "accessToken отсутствует"

    context.add_init_script(
        f"window.localStorage.setItem('accessToken', {json.dumps(token)});"
    )
    page = context.new_page()
    print("settings type:", type(settings))
    print("settings dir:", [a for a in dir(settings) if "url" in a.lower()])
    page.goto(settings.base_url)

    yield page
    page.close()