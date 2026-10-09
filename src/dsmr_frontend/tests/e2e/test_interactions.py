import re

import pytest
from django.urls import reverse
from playwright.sync_api import Page, expect

from dsmr_frontend.tests.e2e.helpers import login, track_console_errors

pytestmark = pytest.mark.e2e


NAVIGATION_TARGETS = [
    "frontend:live-graphs",
    "frontend:archive",
    "frontend:compare",
    "frontend:trends",
    "frontend:statistics",
    "frontend:energy-contracts",
    "frontend:dashboard",
]


@pytest.mark.parametrize("url_name", NAVIGATION_TARGETS)
def test_sidebar_navigation_opens_page_and_marks_it_current(live_server, page: Page, frontend_data, url_name):
    page.goto("{}{}".format(live_server.url, reverse("frontend:about")))
    target_path = reverse(url_name)

    page.locator('#sidebar-menu a[href="{}"]'.format(target_path)).click()

    expect(page).to_have_url(re.compile("{}$".format(re.escape(target_path))))
    expect(page.locator('#sidebar-menu a[aria-current="page"]')).to_have_attribute("href", target_path)


def test_archive_summary_is_loaded_through_xhr(live_server, page: Page, frontend_data):
    errors = track_console_errors(page)

    page.goto("{}{}".format(live_server.url, reverse("frontend:archive")))

    summary = page.locator("#summary-holder")
    expect(summary).to_be_visible()
    expect(summary).not_to_be_empty()
    expect(page.locator("#summary-loader")).to_be_hidden()
    assert errors == [], "Console errors on archive: {}".format(errors)


def test_compare_summary_is_loaded_after_selecting_two_days(live_server, page: Page, frontend_data):
    errors = track_console_errors(page)
    page.goto("{}{}".format(live_server.url, reverse("frontend:compare")))
    summary = page.locator("#summary-holder")
    expect(summary).to_be_empty()

    page.locator("#datepicker_trigger_days").click()
    page.locator("#datepicker1-day .dsmr-picker-cell[data-day]").first.click()
    expect(summary).to_be_empty()  # Both sides are needed.
    page.locator("#datepicker2-day .dsmr-picker-cell[data-day]").last.click()

    expect(summary).not_to_be_empty()
    expect(page.locator("#summary-loader")).to_be_hidden()
    assert errors == [], "Console errors on compare: {}".format(errors)


@pytest.mark.parametrize("view_mode", ["days", "months", "years"])
def test_archive_switches_view_mode(live_server, page: Page, frontend_data, view_mode):
    page.goto("{}{}".format(live_server.url, reverse("frontend:archive")))

    page.locator("#datepicker_trigger_{}".format(view_mode)).click()

    # Only the picker of the selected view mode is shown, and only its trigger is highlighted.
    for current in ("days", "months", "years"):
        picker = page.locator("#datepicker-{}".format(current[:-1]))
        trigger = page.locator("#datepicker_trigger_{}".format(current))

        if current == view_mode:
            expect(picker).to_be_visible()
            expect(trigger).to_have_class(re.compile(r"\bst-green\b"))
        else:
            expect(picker).to_be_hidden()
            expect(trigger).to_have_class(re.compile(r"\bst-gray\b"))

    expect(page.locator("#summary-holder")).not_to_be_empty()


def test_archive_graphs_are_redrawn_for_another_view_mode(live_server, page: Page, frontend_data):
    page.goto("{}{}".format(live_server.url, reverse("frontend:archive")))
    graph = page.locator("#echarts-electricity-graph")
    expect(graph.locator("canvas, svg")).to_have_count(1)

    page.locator("#datepicker_trigger_years").click()

    expect(graph).to_be_visible()
    expect(graph.locator("canvas, svg")).to_have_count(1)


def test_trends_renders_all_available_graphs(live_server, page: Page, frontend_data):
    errors = track_console_errors(page)

    page.goto("{}{}".format(live_server.url, reverse("frontend:trends")))

    graphs = page.locator('[id^="echarts-"]')
    assert graphs.count() > 0

    for index in range(graphs.count()):
        expect(graphs.nth(index).locator("canvas, svg")).to_have_count(1)

    assert errors == [], "Console errors on trends: {}".format(errors)


def test_statistics_page_loads_its_data(live_server, page: Page, frontend_data):
    errors = track_console_errors(page)

    page.goto("{}{}".format(live_server.url, reverse("frontend:statistics")))

    expect(page.locator("#main-content table").first).to_be_visible()
    assert errors == [], "Console errors on statistics: {}".format(errors)


def test_export_downloads_a_csv_file(live_server, page: Page, frontend_data, admin_credentials):
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:export"))

    page.locator("#data_day_totals").check()
    with page.expect_download() as download_info:
        page.locator("#download_button").click()

    download = download_info.value
    assert download.suggested_filename.endswith(".csv")
