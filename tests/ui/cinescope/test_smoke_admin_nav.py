import allure, pytest
from playwright.sync_api import expect
from config import settings


@allure.epic("Тестирование UI")
@allure.feature("Smoke: Admin Navigation")
@pytest.mark.ui
class TestSmokeAdminNav:
    @allure.title("Smoke: Навигация в админ-панели")
    def test_admin_side_menu_navigation(self, admin_page):
        page = admin_page
        page.goto(f"{settings.base_url}dashboard")

        page.get_by_role("link", name="Фильмы").click()
        expect(page).to_have_url(f"{settings.base_url}dashboard/movies")

        page.get_by_role("link", name="Пользователи").click()
        expect(page).to_have_url(f"{settings.base_url}dashboard/users")

        page.get_by_role("link", name="Жанры").click()
        expect(page).to_have_url(f"{settings.base_url}dashboard/genres")

        page.get_by_role("link", name="Платежи").click()
        expect(page).to_have_url(f"{settings.base_url}dashboard/payments")
