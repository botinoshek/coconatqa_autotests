import allure, pytest
from models.page_object_models import CinescopAdminMoviesPage
from utils.data_generator import DataGenerator


@allure.epic("Тестирование UI")
@allure.feature("Создание фильма (Admin)")
@pytest.mark.ui
class TestCreateMoviePage:
    @allure.title("Позитивный тест: Создание фильма через UI")
    def test_create_movie_positive(self, admin_page):
        admin_page = CinescopAdminMoviesPage(admin_page)
        admin_page.open()
        admin_page.open_create_movie_dialog()

        name = f"auto_movie_{DataGenerator.generate_random_int(99999)}"
        description = "Автотестовое описание фильма"
        price = DataGenerator.generate_random_int(500) + 1
        image_url = "https://example.com/image.png"

        admin_page.fill_movie_form(name, description, price, image_url)
        admin_page.select_genre("Драма")
        admin_page.submit()

        admin_page.assert_dialog_closed()

    @allure.title("Негативный тест: Пустая форма создания фильма")
    def test_create_movie_empty_fields_negative(self, admin_page):
        admin_page = CinescopAdminMoviesPage(admin_page)
        admin_page.open()
        admin_page.open_create_movie_dialog()
        admin_page.submit()

        errors = admin_page.get_error_texts()
        assert any("Название не может быть пустым" in e for e in errors), "Ожидалась ошибка про название"
        assert any("Описание не может быть пустым" in e for e in errors), "Ожидалась ошибка про описание"
        assert any("Invalid url" in e or "url" in e.lower() for e in errors), "Ожидалась ошибка про ссылку"
        assert any("Жанр не может быть пустым" in e for e in errors), "Ожидалась ошибка про жанр"

    @allure.title("Негативный тест: Некорректная ссылка на изображение")
    def test_create_movie_invalid_image_url_negative(self, admin_page):
        admin_page = CinescopAdminMoviesPage(admin_page)
        admin_page.open()
        admin_page.open_create_movie_dialog()

        admin_page.fill_movie_form(
            name=f"auto_movie_{DataGenerator.generate_random_int(99999)}",
            description="Описание",
            price=100,
            image_url="not-a-url",
        )
        admin_page.select_genre("Драма")
        admin_page.submit()

        validation_message = admin_page.get_image_url_validation_message()
        assert "URL" in validation_message or "url" in validation_message.lower(), \
            "Ожидалась tooltip-ошибка про URL"

    @allure.title("Негативный тест: Не выбран жанр")
    def test_create_movie_missing_genre_negative(self, admin_page):
        admin_page = CinescopAdminMoviesPage(admin_page)
        admin_page.open()
        admin_page.open_create_movie_dialog()

        admin_page.fill_movie_form(
            name=f"auto_movie_{DataGenerator.generate_random_int(99999)}",
            description="Описание",
            price=100,
            image_url="https://example.com/image.png",
        )
        admin_page.submit()

        errors = admin_page.get_error_texts()
        assert any("Жанр не может быть пустым" in e for e in errors), "Ожидалась ошибка про жанр"
