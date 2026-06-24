import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure Playwright browser launch arguments for CI."""
    return {
        **browser_type_launch_args,
        "headless": True,
    }
