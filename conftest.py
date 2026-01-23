import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
import pytest
import psycopg2
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from resources.db_creds import DataBaseCreds
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from Modul_4.Cinescope.api.api_manager import ApiManager, AuthAPI
from resources.user_creds import SuperAdminCreds
from Modul_4.Cinescope.entities.user import User
from constans.roles import Roles
from Modul_4.Cinescope.models.base_models import TestUser
from Modul_4.Cinescope.models.base_models import CreateUserRequests
from db_requester.db_helper import DBHelper
from Modul_4.Cinescope.api.tools_api import Tools
from urllib.parse import urlparse

@pytest.fixture
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER.value]
    )

@pytest.fixture
def registration_user_data() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER],
    )

@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture
def auth_api(session):
    return AuthAPI(session)

@pytest.fixture
def registered_user(auth_api, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = auth_api.register_user(test_user)
    response_data = response.json()

    registered_user = test_user
    registered_user.id = response_data["id"]
    test_user.verified = True
    return registered_user

@pytest.fixture(scope="session")
def auth_session(requester, registered_user):
    """
    Фикстура для создания авторизованной сессии.
    Использует уже зарегистрированного пользователя.
    """
    login_data = {
        "email": registered_user["email"],
        "password": registered_user["password"]
    }

    response = requester.send_request(
        method="POST",
        endpoint=LOGIN_ENDPOINT,
        data=login_data,
        expected_status=200
    )

    token = response.json().get("accessToken")
    assert token is not None, "Токен доступа отсутствует в ответе"

    # Создаем новую сессию с токеном авторизации
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers.update({"Authorization": f"Bearer {token}"})

    return session

@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    http_session.base_url = BASE_URL
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)

@pytest.fixture(scope="session")
def authenticated_admin_session(admin_auth_api, super_admin, session):
    """Возвращает сессию с аутентифицированным администратором"""
    admin_auth_api.authenticate_admin(super_admin)
    return session

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        session.base_url = BASE_URL
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.model_dump()
    updated_data.update({
        "verified": True,
        "banned": False
    })

    return CreateUserRequests(**updated_data)

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    """создание дефолтного пользователя администратором"""
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def admin(user_session, super_admin, creation_user_data):
    """создание админ пользователя супер администратором"""
    new_session = user_session()

    admin = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    admin.api.auth_api.authenticate(admin.creds)
    return admin

@pytest.fixture
def connection_db():
    conn = psycopg2.connect(
        host=DataBaseCreds.HOSTDB,
        port=DataBaseCreds.PORTDB,
        user=DataBaseCreds.USERNAMEDB,
        password=DataBaseCreds.PASSWORDDB,
        database=DataBaseCreds.NAMEDB
    )
    print("Подключение к БД успешно")
    yield conn
    print("Закрыто подключение к БД")
    conn.close()

@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

##UI test fixture
DEFAULT_UI_TIMEOUT = 30000  # Пример значения таймаута


@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    browser = playwright.chromium.launch(headless=False)  # headless=True для CI/CD, headless=False для локальной разработки
    yield browser  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    browser.close()  # Браузер закрывается после завершения всех тестов


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)
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

UI_URL = "https://dev-cinescope.coconutqa.ru/"
AUTH_URL = "https://auth.dev-cinescope.coconutqa.ru/"

@pytest.fixture
def authorized_page(context, auth_api, test_user):
    # 1) register
    auth_api.register_user(test_user)

    # 2) login (в requests появится refresh_token cookie на auth домене)
    login_data = {"email": test_user.email, "password": test_user.password}
    resp = auth_api.login_user(login_data, expected_status=200)

    # 3) переносим cookies ИМЕННО на auth-домен
    pw_cookies = []
    for c in auth_api.session.cookies:
        pw_cookies.append({
            "name": c.name,
            "value": c.value,
            "url": AUTH_URL,   # <-- ключевой момент: auth domain
        })

    assert pw_cookies, "После логина в requests не появилось ни одной cookie"
    context.add_cookies(pw_cookies)

    # 4) открываем UI
    token = resp.json().get("accessToken")
    assert token, "accessToken отсутствует"

    context.add_init_script(f"window.localStorage.setItem('accessToken', {token!r});")
    page = context.new_page()
    page.goto(UI_URL)

    # 5) быстрая проверка: если есть элемент, видимый только залогиненным — проверь его
    # пример (замени на реальный):
    # assert page.get_by_text("Выйти").is_visible()

    yield page
    page.close()