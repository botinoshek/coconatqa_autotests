from random import randint
import allure
from playwright.sync_api import Page, expect, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from utils.data_generator import DataGenerator
from config import settings

class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator: str, text: str):
        self.page.fill(locator, text)

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator: str):
        self.page.click(locator)

    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url: str):
        self.page.wait_for_url(url)
        assert self.page.url == url, "Редирект на домашнюю старницу не произошел"

    @allure.step("Получение текста элемента: {locator}")
    def get_element_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content()

    @allure.step("Ожидание появления или исчезновения элемента: {locator}, state = {state}")
    def wait_for_element(self, locator: str, state: str = "visible"):
        self.page.locator(locator).wait_for(state=state)

    @allure.step("Скриншот текущей страиницы")
    def make_screenshot_and_attach_to_allure(self):
        screenshot_path = "screenshot.png"
        self.page.screenshot(path=screenshot_path, full_page=True)  # full_page=True для скриншота всей страницы

        # Прикрепление скриншота к Allure-отчёту
        with open(screenshot_path, "rb") as file:
            allure.attach(file.read(), name="Screenshot after redirect", attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения c текстом: {text}")
    def check_pop_up_element_with_text(self, text: str) -> bool:

        with allure.step("Проверка появления алерта с текстом: '{text}'"):
            notification_locator = self.page.get_by_text(text)
            # Ждем появления элемента
            notification_locator.wait_for(state="visible")
            assert notification_locator.is_visible(), "Уведомление не появилось"

        with allure.step("Проверка исчезновения алерта с текстом: '{text}'"):
            # Ждем, пока алерт исчезнет
            notification_locator.wait_for(state="hidden")
            assert notification_locator.is_visible() == False, "Уведомление не исчезло"

class BasePage(PageAction): #Базовая логика доспустимая для всех страниц на сайте
    def __init__(self, page: Page):
        super().__init__(page)
        self.home_url = settings.base_url

        # Общие локаторы для всех страниц на сайте
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

    @allure.step("Переход на главную страницу, из шапки сайта")
    def go_to_home_page(self):
        self.click_element(self.home_button)
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Переход на страницу 'Все фильмы, из шапки сайта'")
    def go_to_all_movies(self):
        self.click_element(self.all_movies_button)
        self.wait_redirect_for_url(f"{self.home_url}movies")

class CinescopRegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        # Локаторы элементов
        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[type='submit']"
        self.sign_button = "a[href='/login' and text()='Войти']"

        # Локальные action методы
    def open(self):
        self.open_url(self.url)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        self.enter_text_to_element(self.full_name_input, full_name)
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.repeat_password_input, confirm_password)

        self.click_element(self.register_button)

    def assert_was_redirect_to_login_page(self):
        self.wait_redirect_for_url(f"{self.home_url}login")

    def assert_alert_was_pop_up(self):
        self.check_pop_up_element_with_text("Подтвердите свою почту")


class CinescopLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        # Локаторы элементов
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"

        self.login_button = "button[type='submit']"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"


    # Локальные action методы
    def open(self):
        self.open_url(self.url)

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.email_input, email)
        self.click_element(self.login_button)

    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    def assert_alert_was_pop_up(self):
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")

class CinescopCommentPage(BasePage):
    """Page Object для страницы фильма с функционалом комментирования"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.random_score = randint(1, 5)
        self.comment = DataGenerator.generate_random_comment()

        # Локаторы для комментариев
        self.input_comment = self.page.get_by_placeholder("Написать отзыв")
        self.score_combobox = self.page.get_by_role("combobox")
        self.score_select = self.page.locator("select[aria-hidden='true']")
        self.button_submit = self.page.get_by_role("button", name="Отправить")
        
        # Локаторы для проверки
        self.comment_text_locator = "p.line-clamp-8"
        self.error_message = "span.text-red-500"
        self.success_alert = "[role='alert']:has-text('Отзыв успешно создан')"

    def navigate_to_movie(self, movie_id: int):
        """Переход на страницу фильма"""
        movie_url = f"{self.home_url}movies/{movie_id}"
        with allure.step(f"Переход на страницу фильма ID: {movie_id}"):
            self.open_url(movie_url)

    def fill_comment_text(self, comment: str = None):
        """Ввод текста комментария с явным ожиданием элемента"""
        comment_text = comment if comment is not None else self.comment
        with allure.step(f"Ввод комментария: '{comment_text}'"):
            self.input_comment.wait_for(state="visible")
            self.input_comment.fill(comment_text)

    def select_score(self, score: int = None):
        """Выбор оценки из dropdown"""
        score_value = score if score is not None else self.random_score
        
        # Валидация оценки
        assert 1 <= score_value <= 5, f"Оценка должна быть от 1 до 5, получено: {score_value}"
        
        with allure.step(f"Выбор оценки: {score_value}/5"):
            # Кликаем на combobox для открытия
            self.score_combobox.wait_for(state="visible")
            self.score_combobox.click()

            # Кликаем по нужной оценке напрямую
            option = self.page.get_by_role("option", name=str(score_value))
            option.wait_for(state="visible")
            option.click()

    def submit_comment(self):
        """Отправка комментария"""
        with allure.step("Клик по кнопке 'Отправить'"):
            self.button_submit.click()
            
    def write_a_comment(self, comment: str = None, score: int = None):
        """Полный цикл: ввод комментария + выбор оценки (без отправки)"""
        comment_text = comment if comment is not None else self.comment
        score_value = score if score is not None else self.random_score
        
        with allure.step(f"Заполнение формы комментария: текст='{comment_text}', оценка={score_value}"):
            self.fill_comment_text(comment_text)
            self.select_score(score_value)

    def clear_comment_field(self):
        """Очистить поле комментария"""
        with allure.step("Очистка поля комментария"):
            self.input_comment.wait_for(state="visible")
            self.input_comment.clear()

    def is_submit_button_disabled(self) -> bool:
        """Проверить, отключена ли кнопка отправки"""
        with allure.step("Проверка статуса кнопки отправки (disabled)"):
            return self.button_submit.is_disabled()

    def is_submit_button_enabled(self) -> bool:
        """Проверить, активна ли кнопка отправки"""
        with allure.step("Проверка статуса кнопки отправки (enabled)"):
            return self.button_submit.is_enabled()

    def get_comment_field_value(self) -> str:
        """Получить текущее значение коммента из поля ввода"""
        with allure.step("Получение значения из поля комментария"):
            return self.input_comment.input_value()

    def get_selected_score(self) -> str:
        """Получить выбранную оценку из селекта"""
        with allure.step("Получение выбранной оценки"):
            return self.score_combobox.text_content().strip()

    def assert_alert_was_pop_up(self):
        """Проверка появления и исчезновения алерта об успешном создании"""
        self.check_pop_up_element_with_text("Отзыв успешно создан")

    def assert_success_alert_not_visible(self, timeout_ms: int = 1500):
        """Проверка отсутствия алерта об успешном создании"""
        with allure.step("Проверка, что алерт об успешном создании не появился"):
            locator = self.page.get_by_text("Отзыв успешно создан")
            expect(locator).not_to_be_visible(timeout=timeout_ms)

    def assert_check_comment(self, expected_comment: str = None):
        """Проверка отображения комментария на странице"""
        comment_to_check = expected_comment if expected_comment else self.comment
        with allure.step(f"Проверка отображения комментария: '{comment_to_check}'"):
            comment_locator = self.page.get_by_text(comment_to_check, exact=True)
            comment_locator.first.wait_for(state="visible")
            assert comment_locator.is_visible(), f"Комментарий '{comment_to_check}' не найден на странице"

    def assert_error_message_displayed(self, error_text: str = None):
        """Проверить наличие сообщения об ошибке"""
        with allure.step(f"Проверка сообщения об ошибке"):
            if error_text:
                self.check_pop_up_element_with_text(error_text)
            else:
                error_locator = self.page.locator(self.error_message)
                error_locator.wait_for(state="visible")
                assert error_locator.is_visible(), "Сообщение об ошибке не отображается"
