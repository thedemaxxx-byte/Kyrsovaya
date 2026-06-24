import pytest
import requests
from playwright.sync_api import Page, expect


# 1. UI E2E Test: Availability and presence of "Котософт" text
def test_ui_kotosoft_availability(page: Page):
    """Проверяет доступность сайта и наличие текста 'Котософт'."""
    print("Navigating to котософт.рф...")
    page.goto("https://xn--b1aghb0bcheb.xn--p1ai", wait_until="domcontentloaded")

    body_text = page.locator("body").text_content()
    assert "Котософт" in body_text, "Text 'Котософт' was not found on the page"
    print("UI Test passed: Website is available and contains 'Котософт'")


# 2. Smoke API Test: Check HTTP response status
def test_api_kotosoft_status():
    """Проверяет HTTP-статус ответа сервера (200 OK)."""
    print("Sending GET request to котософт.рф...")
    response = requests.get("https://xn--b1aghb0bcheb.xn--p1ai", timeout=15)
    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}"
    )
    print("API Test passed: HTTP status is 200")


# 3. UI E2E Test: Check page title is not empty
def test_ui_page_title(page: Page):
    """Проверяет, что у страницы есть заголовок (title)."""
    page.goto("https://xn--b1aghb0bcheb.xn--p1ai", wait_until="domcontentloaded")

    title = page.title()
    assert title and len(title) > 0, "Page title is empty"
    print(f"Title Test passed: Page title is '{title}'")


# 4. UI E2E Test: Check for "Салют" (fireworks/greeting element)
def test_ui_salute_element(page: Page):
    """Проверяет наличие элемента или текста 'Салют' на сайте котософт.рф."""
    print("Navigating to котософт.рф to check for 'Салют'...")
    page.goto("https://xn--b1aghb0bcheb.xn--p1ai", wait_until="domcontentloaded")

    # Wait for page content to fully load
    page.wait_for_timeout(2000)

    # Get full page text content
    body_text = page.locator("body").text_content()
    page_html = page.content()

    # Check for "Салют" in visible text or in HTML (could be alt text, class name, etc.)
    salute_in_text = "Салют" in body_text or "салют" in body_text.lower()
    salute_in_html = "салют" in page_html.lower()

    assert salute_in_text or salute_in_html, (
        "Элемент или текст 'Салют' не найден на странице котософт.рф. "
        "Проверьте, что на сайте есть секция/элемент с упоминанием 'Салют'."
    )
    print("Salute Test passed: 'Салют' found on the page")


# 5. API Test: Check response contains HTML content
def test_api_response_has_html():
    """Проверяет, что ответ сервера содержит HTML-контент."""
    response = requests.get("https://xn--b1aghb0bcheb.xn--p1ai", timeout=15)
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type, (
        f"Expected Content-Type to contain 'text/html', got '{content_type}'"
    )
    assert len(response.text) > 100, "Response body is too short, page may not have loaded"
    print("HTML Content Test passed: Response contains valid HTML")
