from playwright.sync_api import Page, expect

def test_demoqa_a(page: Page):
    page.goto('https://demoqa.com/automation-practice-form')
    page.type("input#firstName",'Artemchik')
    page.get_by_placeholder("Last Name").fill("Grudchik")
    page.fill("input#userEmail", "blabla@gm.co")
    page.get_by_text("Male", exact=True).check()
    page.get_by_placeholder("Mobile Number").type("88005553535")
    birth_day = page.get_attribute("#dateOfBirthInput", "value")
    assert birth_day == "11 Dec 2025"
    footer = page.locator("footer").text_content()
    assert  footer == "© 2013-2020 TOOLSQA.COM | ALL RIGHTS RESERVED."

