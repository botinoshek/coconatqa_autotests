from custom_requester.custom_requester import CustomRequester
from constants import LOGIN_ENDPOINT

class AdminAuthAPI(CustomRequester):
    """
      Класс для работы с аутентификацией админа.
      """
    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru/")
        self.session = session

    def login_admin_user(self, admin_user_data, expected_status=200):
        """
        Авторизация пользователя.
        :param admin_user_data: Данные для логина админом.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=admin_user_data,
            expected_status=expected_status
        )

    def authenticate_admin(self, admin_user_data):
        """
        Аутентификация администратора и установка токена.
        """
        response = self.login_admin_user(admin_user_data)

        if response.status_code != 200:
            raise ValueError(f"Authentication failed with status: {response.status_code}")

        response_json = response.json()

        if "accessToken" not in response_json:
            raise KeyError("Token is missing in admin authentication")

        token = response_json["accessToken"]
        self.session.headers.update({"authorization": "Bearer " + token})
        return token