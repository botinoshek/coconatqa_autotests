import allure, pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from models.page_object_models import CinescopRegisterPage
from utils.data_generator import DataGenerator

@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Register")
@pytest.mark.ui
class TestRegisterPage:
    @allure.title("Проведение успешной регистрации")
    def test_register_by_ui(self, page):
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        random_password = DataGenerator.generate_random_password()

        register_page = CinescopRegisterPage(page) # Создаем объект страницы регистрации cinescope
        register_page.open()
        register_page.register(random_name, random_email, random_password, random_password)# Выполняем регистрацию

        with allure.step("Проверка редиректа на /login (если есть)"):
            try:
                page.wait_for_url(f"{register_page.home_url}login", timeout=5000)
            except PlaywrightTimeoutError:
                register_page.assert_stay_on_register_page()
        register_page.make_screenshot_and_attach_to_allure() # Прикрепляем скриншот
        register_page.assert_alert_was_pop_up() # Проверка появления и исчезновения алерта

    @allure.title("Негативный тест: Пустые поля регистрации")
    def test_register_empty_fields_negative(self, page):
        register_page = CinescopRegisterPage(page)
        register_page.open()
        register_page.register("", "", "", "")

        with allure.step("Проверить, что регистрация не прошла"):
            register_page.assert_stay_on_register_page()
            register_page.assert_success_alert_not_visible()
            errors = register_page.get_error_texts()
            assert any("Неверная почта" in e for e in errors), "Ожидалась ошибка про email"
            assert any("Пароль должен содержать не менее 8 символов" in e for e in errors), \
                "Ожидалась ошибка про минимальную длину пароля"

    @allure.title("Негативный тест: Некорректный email")
    def test_register_invalid_email_negative(self, page):
        random_name = DataGenerator.generate_random_name()
        strong_password = "Aa1!aaaa"

        register_page = CinescopRegisterPage(page)
        register_page.open()
        register_page.register(random_name, "not-an-email", strong_password, strong_password)
        page.locator("input[name='email']").blur()

        register_page.assert_stay_on_register_page()
        register_page.assert_success_alert_not_visible()
        errors = register_page.get_error_texts()
        if errors:
            assert any("Неверная почта" in e for e in errors) or any("email" in e.lower() for e in errors), \
                "Ожидалась ошибка про email"

    @allure.title("Негативный тест: Пароли не совпадают")
    def test_register_password_mismatch_negative(self, page):
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        password = "Aa1!aaaa"
        password_repeat = "Aa1!aaab"

        register_page = CinescopRegisterPage(page)
        register_page.open()
        register_page.register(random_name, random_email, password, password_repeat)

        register_page.assert_stay_on_register_page()
        register_page.assert_success_alert_not_visible()
        errors = register_page.get_error_texts()
        assert any("Пароль не соответствует требованиям" in e or "Пароли не совпадают" in e for e in errors), \
            "Ожидалась ошибка про несовпадение паролей"
