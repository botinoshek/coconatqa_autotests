import time, pytest, allure
from playwright.sync_api import sync_playwright
from Modul_4.Cinescope.models.page_object_models import CinescopCommentPage
from conftest import registered_user


@allure.epic("Тестирование UI")
@allure.feature("Тестирование функционала комментирования")
@pytest.mark.ui
class TestCommentPage:
        @allure.title("Проведение успешного комментирования")
        def test_comment_by_ui(self, authorized_page):
                page = authorized_page
                comment_page = CinescopCommentPage(page)
                comment_page.open()
                comment_page.write_a_comment("Автотест-UI")
                comment_page.assert_aller_was_pop_up()
                comment_page.make_screenshot_and_attach_to_allure()