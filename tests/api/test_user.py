from Modul_4.Cinescope.models.base_models import (RegisterUserResponse,
                                                  LoginUserRequest,
                                                  LoginUserResponse,
                                                  CreateUserResponse,
                                                  DeleteUserResponse,
                                                  TestUser)
from Modul_4.Cinescope.api.api_manager import ApiManager
from conftest import creation_user_data
import datetime, allure
from constans.roles import Roles
import pytest_check as check



class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, registration_user_data):
        response = api_manager.auth_api.register_user(user_data=registration_user_data.model_dump())

        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email == registration_user_data.email, "Email не совпадает"

    def test_login_user(self, api_manager: ApiManager, registration_user_data):
        api_manager.auth_api.register_user(user_data=registration_user_data.model_dump())
        login_data = LoginUserRequest(
            email=registration_user_data.email,
            password=registration_user_data.password
        )
        response = api_manager.auth_api.login_user(
            login_data=login_data.model_dump(exclude_none=True)
        )
        login_response = LoginUserResponse(**response.json())

        assert login_response.user.email == registration_user_data.email, "Email не совпадает"
        assert login_response.accessToken, "accessToken отсутствует"
        #assert login_response.refreshToken, "refreshToken отсутствует"

    def test_create_user(self,api_manager: ApiManager, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(
            user_data=creation_user_data.model_dump(exclude_none=True)
        )
        create_user_response = CreateUserResponse(**response.json())
        assert create_user_response.email == creation_user_data.email, "Email не совпадает"
        assert create_user_response.verified is True, "Пользователь должен быть верифицирован"
        assert "USER" in [role.value for role in create_user_response.roles], "Неверная роль"
        assert create_user_response.id is not None, "ID не должен быть пустым"

    def test_delete_user(self, api_manager: ApiManager, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(
            user_data=creation_user_data.model_dump(exclude_none=True)
        )
        create_user_response = CreateUserResponse(**response.json())
        user_id = create_user_response.id
        response = super_admin.api.user_api.delete_user(user_id)
        response = super_admin.api.user_api.get_user(user_id)
        assert response.json() == {}, "Респонс не пустой, пользователь не удален"
        #delete_user_response = DeleteUserResponse(**response.json())
        #print(response.json())

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: TestUser, mocker):
        with allure.step("Мокаем метод register_user в auth_api"):
            mock_response = RegisterUserResponse(
                id="id",
                email="email@email.com",
                fullName="fullName",
                verified=True,
                banned=False,
                roles=[Roles.SUPER_ADMIN],
                createdAt=str(datetime.datetime.now())
            )
            mocker.patch.object(api_manager.auth_api, 'register_user', return_value=mock_response)

        with allure.step("Вызываем метод, который должен быть замокан"):
            register_user_response = api_manager.auth_api.register_user(test_user)

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            check.equal(register_user_response.email, mock_response.email, "Email не совпадает")
            check.equal(register_user_response.fullName, mock_response.fullName, "Имя не совпадает")
            check.is_true(register_user_response.verified, "Пользователь должен быть верифицирован")
            check.equal(register_user_response.roles, mock_response.role, "Роли не совпадают")
            check.equal(register_user_response.banned, mock_response.banned, "Баннед не совпадает")