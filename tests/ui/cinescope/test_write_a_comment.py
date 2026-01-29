import pytest, allure
from Modul_4.Cinescope.models.page_object_models import CinescopCommentPage
from Modul_4.Cinescope.config.settings import settings



@allure.epic("Тестирование UI")
@allure.feature("Тестирование функционала комментирования")
@pytest.mark.ui
class TestCommentPage:
    @allure.title("Проведение успешного комментирования")
    def test_comment_by_ui(self, authorized_page, created_movie):
        page = authorized_page
        page.goto(f"{settings.base_url}movies/{created_movie}")
        comment_page = CinescopCommentPage(page)
        #comment_page.click_button_more_detailed()
        comment_page.write_a_comment()
        comment_page.click_button_submit()
        comment_page.assert_alert_was_pop_up()
        comment_page.assert_check_comment()
        comment_page.make_screenshot_and_attach_to_allure()