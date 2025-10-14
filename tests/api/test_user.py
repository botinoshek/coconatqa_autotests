from Modul_4.Cinescope.models.base_models import (RegisterUserResponse,
                                                  LoginUserRequest,
                                                  LoginUserResponse,
                                                  CreateUserResponse,
                                                  DeleteUserResponse)
from Modul_4.Cinescope.api.api_manager import ApiManager
from conftest import creation_user_data


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
        assert login_response.refreshToken, "refreshToken отсутствует"

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