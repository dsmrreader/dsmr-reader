import datetime
import re
from pathlib import Path

import pytest
from django.urls import reverse
from playwright.sync_api import Page, expect

from dsmr_frontend.models.message import Notification
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.statistics import DayStatistics
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


def test_live_graphs_help_is_revealed_on_click(live_server, page: Page, frontend_data):
    page.goto("{}{}".format(live_server.url, reverse("frontend:live-graphs")))
    trigger = page.locator("a.graph_controls_help_trigger").first
    help_text = page.locator(".graph_controls_help").first
    expect(help_text).to_be_hidden()

    trigger.click()

    expect(help_text).to_be_visible()
    expect(trigger).to_be_hidden()
    expect(page).to_have_url(re.compile(r"/live$"))  # The empty href must not navigate away.


def test_energy_contract_details_are_revealed_on_click(live_server, page: Page, frontend_data):
    page.goto("{}{}".format(live_server.url, reverse("frontend:energy-contracts")))
    details = page.locator(".contract-details").first
    trigger = page.locator("a.show-contract-details").first
    expect(details).to_be_hidden()

    trigger.click()

    expect(details).to_be_visible()
    expect(trigger).to_be_hidden()


def test_configuration_search_shows_matching_results(live_server, page: Page, frontend_data, admin_credentials):
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:configuration"))
    results = page.locator(".search-results")
    expect(results).to_be_hidden()

    page.locator("#search").fill("mqtt")

    expect(results).to_be_visible()
    expect(results.locator("a").first).to_have_attribute("href", re.compile(r"^/admin/"))

    page.locator("#search").fill("")
    expect(results).to_be_hidden()

    page.locator("#search").fill("zzz-no-such-setting")
    expect(results).to_be_hidden()


def test_configuration_suggestion_fills_the_search(live_server, page: Page, frontend_data, admin_credentials):
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:configuration"))

    suggestion = page.locator("a.suggestion").first
    category = suggestion.inner_text()
    suggestion.click()

    expect(page.locator("#search")).to_have_value(category)
    expect(page.locator(".search-results")).to_be_visible()


def test_notifications_are_read_only_when_anonymous(live_server, page: Page, frontend_data):
    Notification.objects.all().delete()
    Notification.objects.create(message="E2E anonymous notification")

    page.goto("{}{}".format(live_server.url, reverse("frontend:notifications")))

    expect(page.get_by_text("E2E anonymous notification")).to_be_visible()
    expect(page.locator("button.mark-notification-read")).to_have_count(0)
    expect(page.locator("a[href*='/admin/login/']").first).to_be_visible()


def test_notification_can_be_marked_as_read(live_server, page: Page, frontend_data, admin_credentials):
    Notification.objects.all().delete()
    Notification.objects.create(message="E2E first notification")
    Notification.objects.create(message="E2E second notification")
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:notifications"))

    page.locator("button.mark-notification-read").first.click()

    expect(page.locator("button.mark-notification-read")).to_have_count(1)
    assert Notification.objects.unread().count() == 1


def test_all_notifications_can_be_marked_as_read(live_server, page: Page, frontend_data, admin_credentials):
    Notification.objects.all().delete()
    Notification.objects.create(message="E2E first notification")
    Notification.objects.create(message="E2E second notification")
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:notifications"))

    page.locator("button.mark-all-notifications-read").click()

    expect(page.locator("button.mark-notification-read")).to_have_count(0)
    assert Notification.objects.unread().count() == 0


@pytest.fixture
def multi_month_statistics(frontend_data):
    """Extends the fixture days (2016-01-01/02) with a day on either side, spanning a month and year boundary."""
    template = DayStatistics.objects.get(day=datetime.date(2016, 1, 1))

    for day in (datetime.date(2015, 12, 31), datetime.date(2016, 2, 1)):
        template.pk = None
        template.day = day
        template.save()


@pytest.mark.parametrize(
    "url_name,expected_text",
    [
        ("frontend:dashboard", "No data found yet"),
        ("frontend:live-graphs", "No data found yet"),
        ("frontend:statistics", "No data found yet"),
        ("frontend:archive", "No day statistics found yet"),
        ("frontend:energy-contracts", "No data or energy contracts found"),
    ],
)
def test_empty_database_shows_a_hint_without_errors(live_server, page: Page, transactional_db, url_name, expected_text):
    errors = track_console_errors(page)

    page.goto("{}{}".format(live_server.url, reverse(url_name)))

    expect(page.get_by_text(expected_text)).to_be_visible()
    assert errors == [], "Console errors on empty {}: {}".format(url_name, errors)


def test_empty_archive_has_no_pickers(live_server, page: Page, transactional_db):
    page.goto("{}{}".format(live_server.url, reverse("frontend:archive")))

    expect(page.locator("#datepicker_trigger_days")).to_have_count(0)
    expect(page.locator("#summary-holder")).to_have_count(0)


def test_empty_notifications_show_a_hint(live_server, page: Page, transactional_db):
    Notification.objects.all().delete()

    page.goto("{}{}".format(live_server.url, reverse("frontend:notifications")))

    expect(page.get_by_text("There are no unread notifications.")).to_be_visible()


def test_day_picker_is_limited_to_the_available_range(live_server, page: Page, frontend_data):
    page.goto("{}{}".format(live_server.url, reverse("frontend:archive")))
    page.locator("#datepicker_trigger_days").click()
    picker = page.locator("#datepicker-day")

    # Data only covers a single month, so there is nowhere to navigate to.
    expect(picker.locator(".dsmr-picker-prev")).to_be_disabled()
    expect(picker.locator(".dsmr-picker-next")).to_be_disabled()
    expect(picker.locator(".dsmr-picker-cell[data-day]")).to_have_count(2)


def test_day_picker_navigates_across_month_and_year_boundaries(live_server, page: Page, multi_month_statistics):
    page.goto("{}{}".format(live_server.url, reverse("frontend:archive")))
    page.locator("#datepicker_trigger_days").click()
    picker = page.locator("#datepicker-day")
    title = picker.locator(".dsmr-picker-title")

    # Starts at the newest day.
    expect(title).to_contain_text("2016")
    expect(picker.locator(".dsmr-picker-next")).to_be_disabled()
    expect(picker.locator(".dsmr-picker-cell.active")).to_have_text("1")

    picker.locator(".dsmr-picker-prev").click()
    expect(picker.locator(".dsmr-picker-next")).to_be_enabled()
    expect(picker.locator(".dsmr-picker-cell.active")).to_have_count(0)  # Selection lives in another month.
    expect(picker.locator(".dsmr-picker-cell[data-day]")).to_have_count(31)

    picker.locator(".dsmr-picker-prev").click()
    expect(title).to_contain_text("2015")
    expect(picker.locator(".dsmr-picker-prev")).to_be_disabled()
    expect(picker.locator(".dsmr-picker-cell[data-day]")).to_have_count(1)  # Only 31 December exists.

    picker.locator(".dsmr-picker-cell[data-day]").click()
    expect(picker.locator(".dsmr-picker-cell.active")).to_have_text("31")
    expect(page.locator("#summary-holder")).not_to_be_empty()


def test_month_picker_navigates_across_years(live_server, page: Page, multi_month_statistics):
    page.goto("{}{}".format(live_server.url, reverse("frontend:archive")))
    page.locator("#datepicker_trigger_months").click()
    picker = page.locator("#datepicker-month")
    title = picker.locator(".dsmr-picker-title")

    expect(title).to_have_text("2016")
    expect(picker.locator(".dsmr-picker-cell[data-month]")).to_have_count(2)  # January and February.
    expect(picker.locator(".dsmr-picker-next")).to_be_disabled()

    picker.locator(".dsmr-picker-prev").click()

    expect(title).to_have_text("2015")
    expect(picker.locator(".dsmr-picker-cell[data-month]")).to_have_count(1)  # December.
    expect(picker.locator(".dsmr-picker-prev")).to_be_disabled()

    picker.locator(".dsmr-picker-cell[data-month]").click()
    expect(picker.locator(".dsmr-picker-cell.active")).to_have_count(1)
    expect(page.locator("#summary-holder")).not_to_be_empty()


def _download_export_rows(page: Page) -> list[str]:
    with page.expect_download() as download_info:
        page.locator("#download_button").click()

    content = Path(download_info.value.path()).read_text()
    return [line for line in content.splitlines() if line.strip()]


def test_export_requires_login(live_server, page: Page, frontend_data):
    page.goto("{}{}".format(live_server.url, reverse("frontend:export")))

    expect(page).to_have_url(re.compile(r"/admin/login/"))


def test_export_preselects_the_full_available_range(live_server, page: Page, frontend_data, admin_credentials):
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:export"))

    expect(page.locator("#start_date")).not_to_have_value("")
    expect(page.locator("#start_datepicker .dsmr-picker-cell.active")).to_have_text("1")
    expect(page.locator("#end_datepicker .dsmr-picker-cell.active")).to_have_text("2")
    # Two days of data plus the header.
    assert len(_download_export_rows(page)) == 3


def test_export_follows_the_selected_date_range(live_server, page: Page, frontend_data, admin_credentials):
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:export"))
    start_before = page.locator("#start_date").input_value()

    page.locator("#end_datepicker .dsmr-picker-cell[data-day]").first.click()  # Same day as the start.

    expect(page.locator("#end_datepicker .dsmr-picker-cell.active")).to_have_text("1")
    assert page.locator("#end_date").input_value() == start_before
    assert len(_download_export_rows(page)) == 2


def test_export_switches_data_type(live_server, page: Page, frontend_data, admin_credentials):
    username, password = admin_credentials
    login(page, live_server.url, username, password, next_url=reverse("frontend:export"))
    day_rows = _download_export_rows(page)

    page.locator("#data_hour_totals").check()
    hour_rows = _download_export_rows(page)

    assert hour_rows[0] != day_rows[0]  # Different columns.


def test_trends_shows_a_day_picker_for_both_ends_of_the_period(live_server, page: Page, frontend_data):
    page.goto("{}{}".format(live_server.url, reverse("frontend:trends")))

    for side in ("start", "end"):
        expect(page.locator("#datepicker-{}-day".format(side))).to_be_visible()
        expect(page.locator("#datepicker-{}-day .dsmr-picker-cell.active".format(side))).to_have_count(1)


def test_trends_requests_new_data_for_the_selected_period(live_server, page: Page, frontend_data):
    errors = track_console_errors(page)
    page.goto("{}{}".format(live_server.url, reverse("frontend:trends")))
    expect(page.locator('[id^="echarts-"] canvas, [id^="echarts-"] svg').first).to_be_visible()
    start = page.locator("#datepicker-start-day .dsmr-picker-cell[data-day]").first

    with page.expect_response(re.compile(r"/trends/xhr/avg-consumption\?")) as response_info:
        start.click()

    response = response_info.value
    assert response.status == 200
    assert "start_date=" in response.url and "end_date=" in response.url
    expect(page.locator("#datepicker-start-day .dsmr-picker-cell.active")).to_have_count(1)
    assert errors == [], "Console errors on trends: {}".format(errors)


def test_dashboard_header_is_filled_through_xhr(live_server, page: Page, frontend_data):
    errors = track_console_errors(page)

    with page.expect_response(re.compile(r"/xhr/header")) as response_info:
        page.goto("{}{}".format(live_server.url, reverse("frontend:dashboard")))

    assert response_info.value.status == 200
    expect(page.locator("#latest_timestamp")).not_to_be_empty()
    expect(page.locator("#latest_electricity_delivered")).not_to_be_empty()
    expect(page.locator("#header-loader")).to_be_hidden()
    assert errors == [], "Console errors on dashboard: {}".format(errors)


@pytest.mark.parametrize("view_mode,picker,cell", [("months", "month", "data-month"), ("years", "year", "data-year")])
def test_compare_sends_the_selected_level(live_server, page: Page, frontend_data, view_mode, picker, cell):
    page.goto("{}{}".format(live_server.url, reverse("frontend:compare")))
    page.locator("#datepicker_trigger_{}".format(view_mode)).click()

    page.locator("#datepicker1-{} .dsmr-picker-cell[{}]".format(picker, cell)).first.click()
    with page.expect_response(re.compile(r"/compare/xhr/summary\?")) as response_info:
        page.locator("#datepicker2-{} .dsmr-picker-cell[{}]".format(picker, cell)).last.click()

    assert response_info.value.status == 200
    assert "level={}".format(view_mode) in response_info.value.url
    expect(page.locator("#summary-holder")).not_to_be_empty()


def test_compare_resets_selections_when_the_level_changes(live_server, page: Page, frontend_data):
    page.goto("{}{}".format(live_server.url, reverse("frontend:compare")))
    page.locator("#datepicker_trigger_days").click()
    page.locator("#datepicker1-day .dsmr-picker-cell[data-day]").first.click()
    expect(page.locator("#datepicker1-day .dsmr-picker-cell.active")).to_have_count(1)

    page.locator("#datepicker_trigger_months").click()
    page.locator("#datepicker_trigger_days").click()

    expect(page.locator("#datepicker1-day .dsmr-picker-cell.active")).to_have_count(0)


def test_compare_only_requests_data_once_both_sides_are_chosen(live_server, page: Page, frontend_data):
    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url) if "/compare/xhr/summary" in request.url else None)
    page.goto("{}{}".format(live_server.url, reverse("frontend:compare")))
    page.locator("#datepicker_trigger_days").click()

    page.locator("#datepicker1-day .dsmr-picker-cell[data-day]").first.click()
    page.wait_for_timeout(500)
    assert requests == []

    page.locator("#datepicker2-day .dsmr-picker-cell[data-day]").last.click()
    expect(page.locator("#summary-holder")).not_to_be_empty()
    assert len(requests) == 1


@pytest.mark.parametrize(
    "theme,color_scheme,expect_dark",
    [(0, "dark", False), (1, "light", True), (-1, "dark", True), (-1, "light", False)],
)
def test_theme_setting_controls_dark_mode(
    live_server, browser, frontend_data, theme: int, color_scheme: str, expect_dark: bool
):
    FrontendSettings.get_solo()
    FrontendSettings.objects.update(frontend_theme=theme)
    page = browser.new_page(color_scheme=color_scheme)

    page.goto("{}{}".format(live_server.url, reverse("frontend:dashboard")))

    if expect_dark:
        expect(page.locator("body")).to_have_class(re.compile(r"\bdark-mode\b"))
    else:
        expect(page.locator("body")).not_to_have_class(re.compile(r"\bdark-mode\b"))
    page.close()


def test_live_graphs_load_their_data_and_render(live_server, page: Page, frontend_data):
    errors = track_console_errors(page)

    with page.expect_response(re.compile(r"/xhr/electricity")) as response_info:
        page.goto("{}{}".format(live_server.url, reverse("frontend:live-graphs")))

    assert response_info.value.status == 200
    graphs = page.locator('[id^="echarts-"]')
    assert graphs.count() > 0

    for index in range(graphs.count()):
        expect(graphs.nth(index).locator("canvas, svg")).to_have_count(1)

    assert errors == [], "Console errors on live graphs: {}".format(errors)
