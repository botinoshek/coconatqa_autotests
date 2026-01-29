import requests
from constants import BASE_URL, HEADERS, LOGIN_ENDPOINT
import pytest
import psycopg2
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
from Modul_4.Cinescope.api.movies_api import MoviesAPI

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

@pytest.fixture(scope="session")
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

@pytest.fixture(scope="session")
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

@pytest.fixture(scope="session")
def movies_api(super_admin):
    return MoviesAPI(super_admin.api.session)

@pytest.fixture(scope="session")
def created_movie(movies_api):
    resp = movies_api.post_create_movies(expected_status=201)
    movie_id = resp.json().get("id")
    assert movie_id, f"В ответе нет id. Ответ: {resp.text}"

    yield movie_id

    try:
        movies_api.delete_movies_id(movie_id, expected_status=200)
    except Exception:
        pass