import allure, pytest
from playwright.sync_api import expect
from config import settings


@allure.epic("Тестирование UI")
@allure.feature("Smoke: Header")
@pytest.mark.ui
class TestSmokeHeaderGuest:
    @allure.title("Smoke: Переходы в хедере для гостя")
    def test_header_links_guest(self, page):
        page.goto(settings.base_url)

        # Cinescope -> главная
        page.get_by_role("link", name="Cinescope").click()
        expect(page).to_have_url(settings.base_url)

        # Все фильмы -> /movies
        page.get_by_role("link", name="Все фильмы").click()
        expect(page).to_have_url(f"{settings.base_url}movies")

        # Войти -> /login (если ссылка отображается)
        login_link = page.get_by_role("link", name="Войти")
        if login_link.is_visible():
            login_link.click()
            expect(page).to_have_url(f"{settings.base_url}login")


@allure.epic("Тестирование UI")
@allure.feature("Smoke: Header")
@pytest.mark.ui
class TestSmokeHeaderAdmin:
    @allure.title("Smoke: Профиль и админка из хедера")
    def test_header_links_admin(self, admin_page):
        page = admin_page
        page.goto(settings.base_url)

        # Профиль -> /profile
        page.get_by_role("link", name="Профиль").click()
        expect(page).to_have_url(f"{settings.base_url}profile")

        # Админ панель -> /dashboard
        page.get_by_role("link", name="Админ панель").click()
        expect(page).to_have_url(f"{settings.base_url}dashboard")

        # Вернуться на главную -> /
        page.get_by_role("link", name="Вернуться на главную").click()
        expect(page).to_have_url(settings.base_url)
