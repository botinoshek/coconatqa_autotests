import pytest, allure
from Modul_4.Cinescope.models.page_object_models import CinescopLoginPage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestloginPage:
    @allure.title("Проведение успешного входа в систему")
    def test_login_by_ui(self, registered_user, page):
        login_page = CinescopLoginPage(page)# Создаем объект страницы Login

        login_page.open()
        login_page.login(registered_user.email, registered_user.password) # Осуществяем вход

        login_page.assert_was_redirect_to_home_page() # Проверка редиректа на домашнюю страницу
        login_page.make_screenshot_and_attach_to_allure() # Прикрепляем скриншот
        login_page.assert_alert_was_pop_up() # Проверка появления и исчезновения алерта
