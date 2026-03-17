import pytest, allure
from models.page_object_models import CinescopLoginPage


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

    @allure.title("Негативный тест: Пустые поля логина")
    def test_login_empty_fields_negative(self, page):
        login_page = CinescopLoginPage(page)
        login_page.open()
        login_page.login("", "")

        login_page.assert_stay_on_login_page()
        login_page.assert_success_alert_not_visible()
        errors = login_page.get_error_texts()
        assert any("Поле email не может быть пустым" in e for e in errors), "Ожидалась ошибка про email"
        assert any("Поле пароль не может быть пустым" in e for e in errors), "Ожидалась ошибка про пароль"

    @allure.title("Негативный тест: Некорректный email")
    def test_login_invalid_email_negative(self, page):
        login_page = CinescopLoginPage(page)
        login_page.open()
        login_page.login("not-an-email", "Qwerty123!")
        page.locator("input[name='email']").blur()

        login_page.assert_stay_on_login_page()
        login_page.assert_success_alert_not_visible()

    @allure.title("Негативный тест: Неверный пароль")
    def test_login_wrong_password_negative(self, page):
        login_page = CinescopLoginPage(page)
        login_page.open()
        login_page.login("user{}@mail.com".format(1), "WrongPass1!")
        page.locator("input[name='password']").blur()

        login_page.assert_stay_on_login_page()
        login_page.assert_success_alert_not_visible()
