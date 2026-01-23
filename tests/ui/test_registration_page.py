from playwright.sync_api import Page
from random import randint
import time


def test_registration(page: Page):
    page.goto('https://dev-cinescope.coconutqa.ru/register')

    # вариант №1
    username_locator = 'input[name="fullName"]'
    email_loacor = 'input[name="email"]'
    password_locator = 'input[name="password"]'
    repeat_password_locator = 'input[name="passwordRepeat"]'

    user_email = f'autart{randint(1, 9999)}@emaiil.ru'
    page.fill(username_locator, 'Жмышенко Валерий Альбертович')
    page.fill(email_loacor, user_email)
    page.fill(password_locator, 'WHJ-WeU-EbS-W6L')
    page.fill(repeat_password_locator, 'WHJ-WeU-EbS-W6L')
    page.click('[type="submit"]')

    time.sleep(10)
