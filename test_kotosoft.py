import pytest
import requests
from playwright.sync_api import Page, expect

# 1. UI E2E Test: Availability and presence of "Котософт" text
def test_ui_kotosoft_availability(page: Page):
    print("Navigating to котософт.рф...")
    # Go to target URL (Punycode format)
    page.goto("https://xn--b1aghb0bcheb.xn--p1ai")
    
    # Verify page title or body contains "Котософт"
    body_text = page.locator("body").text_content()
    assert "Котософт" in body_text, "Text 'Котософт' was not found on the page"
    print("UI Test passed: Website is available and contains 'Котософт'")

# 2. Smoke API Test: Check HTTP response status
def test_api_kotosoft_status():
    print("Sending GET request to котософт.рф...")
    response = requests.get("https://xn--b1aghb0bcheb.xn--p1ai", timeout=10)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    print("API Test passed: HTTP status is 200")
