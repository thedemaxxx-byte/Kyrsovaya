import pytest
import requests
from playwright.sync_api import Page, expect


# 1. UI E2E Test: Availability and presence of "Котософт" text
def test_ui_kotosoft_availability(page: Page):
    """Проверяет доступность сайта и наличие текста 'Котософт'."""
    print("Navigating to котософт.рф...")
    page.goto("http://xn--j1aiaaoedp.xn--p1ai", wait_until="domcontentloaded")

    body_text = page.locator("body").text_content()
    assert "Котософт" in body_text, "Text 'Котософт' was not found on the page"
    print("UI Test passed: Website is available and contains 'Котософт'")


# 2. Smoke API Test: Check HTTP response status
def test_api_kotosoft_status():
    """Проверяет HTTP-статус ответа сервера (200 OK)."""
    print("Sending GET request to котософт.рф...")
    response = requests.get("http://xn--j1aiaaoedp.xn--p1ai", timeout=15)
    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}"
    )
    print("API Test passed: HTTP status is 200")


# Дополнительные тесты генерируются Dify AI на основе requirements_text
# и записываются в test_dynamic.py при запуске через repository_dispatch.
