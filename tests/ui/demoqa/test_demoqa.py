from playwright.sync_api import Page, expect
import time


def test_text_box(page: Page):
    page.goto('https://demoqa.com/text-box')

    username_locator = '#userName'
    page.fill(username_locator, 'testQa')
    page.fill('#userEmail', 'test@qa.com')
    page.fill('#currentAddress', 'Phuket, Thalang 99')
    page.fill('#permanentAddress', 'Moscow, Mashkova 1')

    page.click('button#submit')

    expect(page.locator('#output #name')).to_have_text('Name:testQa')
    expect(page.locator('#output #email')).to_have_text('Email:test@qa.com')
    expect(page.locator('#output #currentAddress')).to_have_text('Current Address :Phuket, Thalang 99')
    expect(page.locator('#output #permanentAddress')).to_have_text('Permananet Address :Moscow, Mashkova 1')
