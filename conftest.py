import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
import pytest
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from Modul_4.Cinescope.api.api_manager import ApiManager
from resources.user_creds import SuperAdminCreds
from Modul_4.Cinescope.entities.user import User
from constans.roles import Roles
from Modul_4.Cinescope.models.base_models import TestUser
from Modul_4.Cinescope.models.base_models import CreateUserRequests

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

# @pytest.fixture(scope="session")
# def test_login_user_data(test_user):
#     return {
#         "email": test_user["email"],
#         "password": test_user["password"]
#     }

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
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
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

# @pytest.fixture(scope="session")
# def super_admin():
#     return {
#         "email": "api1@gmail.com",
#         "password": "asdqwe123Q"
#     }

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
        creation_user_data['email'],
        creation_user_data['password'],
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