import re

import pytest
from django.urls import reverse
from playwright.sync_api import Page, expect

from dsmr_frontend.tests.e2e.helpers import login, track_console_errors

# Pages reachable without authentication by default (FrontendSettings.always_require_login=False).
PUBLIC_PAGES = [
    ("frontend:dashboard", "Dashboard"),
    ("frontend:live-graphs", "Live graphs"),
    ("frontend:archive", "Archive"),
    ("frontend:trends", "Trends"),
    ("frontend:statistics", "Statistics"),
    ("frontend:energy-contracts", "Energy contracts"),
    ("frontend:compare", "Compare"),
    ("frontend:about", "About"),
    ("frontend:notifications", "Notifications"),
]

# Pages that always require a logged-in user, regardless of FrontendSettings.
LOGIN_REQUIRED_PAGES = [
    ("frontend:support", "Support"),
    ("frontend:configuration", "Configuration"),
    ("frontend:export", "Export data"),
]

# Pages with an echarts container that should be populated with a rendered canvas/svg.
CHART_CONTAINERS = {
    "frontend:live-graphs": "#echarts-electricity-graph",
    "frontend:archive": "#echarts-electricity-graph",
    "frontend:trends": "#echarts-avg-electricity-graph",
}


pytestmark = pytest.mark.e2e


@pytest.mark.parametrize("url_name,title_contains", PUBLIC_PAGES)
def test_public_page_loads_without_errors(live_server, page: Page, frontend_data, url_name, title_contains):
    errors = track_console_errors(page)

    page.goto("{}{}".format(live_server.url, reverse(url_name)))

    expect(page).to_have_title(re.compile(re.escape(title_contains), re.IGNORECASE))
    expect(page.locator("#main-content")).to_be_visible()
    assert errors == [], "Console errors on {}: {}".format(url_name, errors)


@pytest.mark.parametrize("url_name,_title_contains", LOGIN_REQUIRED_PAGES)
def test_login_required_page_redirects_when_anonymous(
    live_server, page: Page, frontend_data, url_name, _title_contains
):
    page.goto("{}{}".format(live_server.url, reverse(url_name)))
    expect(page).to_have_url(re.compile(r"/admin/login/"))


@pytest.mark.parametrize("url_name,title_contains", LOGIN_REQUIRED_PAGES)
def test_login_required_page_loads_after_login(
    live_server, page: Page, frontend_data, admin_credentials, url_name, title_contains
):
    username, password = admin_credentials
    target_url = reverse(url_name)
    errors = track_console_errors(page)

    login(page, live_server.url, username, password, next_url=target_url)

    expect(page).to_have_title(re.compile(re.escape(title_contains), re.IGNORECASE))
    expect(page.locator("#main-content")).to_be_visible()
    assert errors == [], "Console errors on {}: {}".format(url_name, errors)


@pytest.mark.parametrize("url_name,chart_selector", CHART_CONTAINERS.items())
def test_chart_page_renders_a_graph(live_server, page: Page, frontend_data, url_name, chart_selector):
    page.goto("{}{}".format(live_server.url, reverse(url_name)))

    chart_container = page.locator(chart_selector)
    expect(chart_container).to_be_visible()
    expect(chart_container.locator("canvas, svg")).to_have_count(1)
