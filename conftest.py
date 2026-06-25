import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure Playwright browser launch arguments for CI."""
    return {
        **browser_type_launch_args,
        "headless": True,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure Playwright browser context arguments for CI."""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }
