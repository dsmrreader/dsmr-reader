from playwright.sync_api import ConsoleMessage, Page


def track_console_errors(page: Page) -> list[str]:
    """Registers a console listener and returns the (mutated in place) list of error messages."""
    errors: list[str] = []

    def _on_console(message: ConsoleMessage) -> None:
        if message.type == "error":
            errors.append(message.text)

    page.on("console", _on_console)
    return errors


def login(page: Page, live_server_url: str, username: str, password: str, next_url: str) -> None:
    page.goto("{}/admin/login/?next={}".format(live_server_url, next_url))
    page.locator("#id_username").fill(username)
    page.locator("#id_password").fill(password)
    page.locator('input[type="submit"]').click()
    page.wait_for_url("{}{}".format(live_server_url, next_url))
