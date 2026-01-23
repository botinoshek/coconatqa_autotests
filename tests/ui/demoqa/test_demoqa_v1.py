from playwright.sync_api import Page, expect
import time


def test_demoqa_a(page: Page):
    page.goto('https://demoqa.com/webtables')

    page.get_by_role("button", name="Add").click()
    modal_title_locator = page.locator('#registration-form-modal')
    expect(modal_title_locator).to_be_visible()
    page.get_by_placeholder("First Name").fill("Artem")
    page.locator('#lastName').fill("Grud")
    page.get_by_placeholder('name@example.com').fill('xuita@gm.co')
    page.get_by_placeholder('Age').fill("27")
    page.get_by_placeholder('Salary').fill('123')
    page.get_by_placeholder('Department').fill('1234')
    page.click('button#submit', force=True, timeout=5000)
