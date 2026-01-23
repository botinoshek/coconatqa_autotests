from playwright.sync_api import Page, expect

def test_find_element(page: Page):
    page.goto('https://demoqa.com/radio-button')
    page.wait_for_load_state()
    element_yes = page.get_by_label('Yes').is_enabled()
    assert element_yes == True
    element_no = page.get_by_role("radio", name='No').is_enabled()
    assert element_no == False
    element_impressive = page.locator('#impressiveRadio').is_enabled()
    assert element_impressive == True
    print(f'Y={element_yes},N={element_no},I={element_impressive}')

def test_find_element_q2(page: Page):
    page.goto('https://demoqa.com/checkbox')
    visible_finder_home = page.get_by_text('Home').is_visible()
    no_visible_finder_desktop = page.get_by_text('Desktop').is_hidden()
    print(f'Home{visible_finder_home}/Desctop{no_visible_finder_desktop}')
    assert visible_finder_home == True
    assert no_visible_finder_desktop == True
    page.get_by_role("button", name='Toggle').click()
    visible_finder_desktop = page.get_by_text('Desktop').is_visible()
    print(f'Home{visible_finder_home}/Desctop{visible_finder_desktop}')
    assert no_visible_finder_desktop == True

def test_find_element_q3(page: Page):
    page.goto('https://demoqa.com/dynamic-properties')
    no_visible = page.locator('#visibleAfter').is_hidden()
    print(no_visible)
    assert no_visible == True
    wait_selector = page.wait_for_selector('#visibleAfter', timeout=5100).is_visible()
    assert wait_selector == True
