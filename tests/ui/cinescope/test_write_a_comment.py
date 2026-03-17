import pytest
import allure
from models.page_object_models import CinescopCommentPage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование функционала комментирования")
@pytest.mark.ui
class TestCommentPage:
    """Тесты для проверки функционала написания комментариев к фильмам"""

    @allure.title("Позитивный тест: Успешное добавление комментария с оценкой")
    @allure.description("Проверка успешного добавления комментария с выбранной оценкой")
    def test_comment_by_ui_positive(self, authorized_page, created_movie):
        """Успешное комментирование с валидными данными"""
        comment_page = CinescopCommentPage(authorized_page)

        # Открыть страницу фильма
        comment_page.navigate_to_movie(created_movie)

        # Заполнить и отправить комментарий
        comment_page.write_a_comment()
        comment_page.submit_comment()

        # Проверки
        comment_page.assert_alert_was_pop_up()
        comment_page.assert_check_comment()
        comment_page.make_screenshot_and_attach_to_allure()

    @allure.title("Негативный тест: Попытка отправить пустой комментарий")
    @allure.description("Проверка, что пустой комментарий не отправляется")
    def test_comment_empty_text_negative(self, authorized_page, created_movie):
        """Не должно быть возможности отправить пустой комментарий"""
        comment_page = CinescopCommentPage(authorized_page)
        comment_page.navigate_to_movie(created_movie)

        comment_page.write_a_comment(comment="")

        with allure.step("Проверить, что кнопка отправки активна"):
            assert comment_page.is_submit_button_enabled(), \
                "Кнопка должна быть активна даже при пустом комментарии"

        comment_page.submit_comment()
        comment_page.assert_success_alert_not_visible()

    @allure.title("Негативный тест: Комментарий только с пробелами")
    @allure.description("Проверка, что комментарий только из пробелов не принимается")
    def test_comment_only_spaces_negative(self, authorized_page, created_movie):
        """Комментарий из одних пробелов должен быть отклонен"""
        comment_page = CinescopCommentPage(authorized_page)
        comment_page.navigate_to_movie(created_movie)

        comment_page.write_a_comment(comment="     ")

        with allure.step("Проверить, что кнопка отправки активна"):
            assert comment_page.is_submit_button_enabled(), \
                "Кнопка должна быть активна для пробелов"

        comment_page.submit_comment()
        comment_page.assert_success_alert_not_visible()

    @allure.title("Позитивный тест: Комментарий с минимальной длиной")
    @allure.description("Проверка приемки комментария минимальной валидной длины")
    def test_comment_min_length_positive(self, authorized_page, created_movie):
        """Минимальный валидный комментарий"""
        comment_page = CinescopCommentPage(authorized_page)
        comment_page.navigate_to_movie(created_movie)

        short_comment = "Хороший фильм!"
        comment_page.write_a_comment(comment=short_comment)

        assert comment_page.is_submit_button_enabled(), "Кнопка должна быть активна"
        comment_page.submit_comment()
        comment_page.assert_alert_was_pop_up()
        comment_page.make_screenshot_and_attach_to_allure()

    @allure.title("Позитивный тест: Комментарий со спецсимволами")
    @allure.description("Проверка приемки комментария со спецсимволами и эмодзи")
    def test_comment_with_special_chars_positive(self, authorized_page, created_movie):
        """Комментарий со спецсимволами и эмодзи должен быть принят"""
        comment_page = CinescopCommentPage(authorized_page)
        comment_page.navigate_to_movie(created_movie)

        comment_with_special = "Отличный фильм! 🎬 (10/10) [рекомендую]"
        comment_page.write_a_comment(comment=comment_with_special, score=5)

        assert comment_page.is_submit_button_enabled(), "Кнопка должна быть активна со спецсимволами"
        comment_page.submit_comment()
        comment_page.assert_alert_was_pop_up()

    @allure.title("Позитивный тест: Различные оценки (1-5)")
    @allure.description("Проверка всех возможных оценок от 1 до 5")
    @pytest.mark.parametrize("score", [1, 2, 3, 4, 5])
    def test_comment_all_scores_positive(self, authorized_page, created_movie, score):
        """Проверить все оценки от 1 до 5"""
        comment_page = CinescopCommentPage(authorized_page)
        comment_page.navigate_to_movie(created_movie)

        test_comment = f"Фильм с оценкой {score} звезд"

        with allure.step(f"Отправить комментарий с оценкой {score}"):
            comment_page.write_a_comment(comment=test_comment, score=score)
            assert comment_page.get_selected_score() == str(score), f"Оценка должна быть {score}"
            comment_page.submit_comment()
            comment_page.assert_alert_was_pop_up()

    @allure.title("Позитивный тест: Комментарий с многострочным текстом")
    @allure.description("Проверка приемки многострочного комментария")
    def test_comment_multiline_positive(self, authorized_page, created_movie):
        """Многострочный комментарий должен быть принят"""
        comment_page = CinescopCommentPage(authorized_page)
        comment_page.navigate_to_movie(created_movie)

        multiline_comment = "Отличный фильм!\nСюжет захватывает\nАкторы сыграли хорошо"
        comment_page.write_a_comment(comment=multiline_comment)

        assert comment_page.is_submit_button_enabled(), "Кнопка должна быть активна"
        comment_page.submit_comment()
        comment_page.assert_alert_was_pop_up()
        comment_page.make_screenshot_and_attach_to_allure()
