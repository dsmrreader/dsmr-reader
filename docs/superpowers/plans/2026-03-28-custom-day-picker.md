# Custom Day Picker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the flatpickr inline day picker on Archive and Compare pages with a custom `.dsmr-picker` calendar grid matching the existing month/year picker pattern.

**Architecture:** Three JS files are modified (archive.js, compare.js) to add `render_day_picker()` following the exact same render-to-innerHTML pattern as `render_month_picker()` / `render_year_picker()`. Two HTML templates swap `<input type="hidden">` for `<div>` containers and drop flatpickr tags. CSS adds a 7-column grid modifier and weekday header style, and removes the flatpickr dark-mode overrides.

**Tech Stack:** Vanilla JS, jQuery, `Intl.DateTimeFormat` (already used by month/year pickers), existing `.dsmr-picker` CSS component, djlint (template formatter).

---

### Task 1: Add CSS for the day picker grid

**Files:**
- Modify: `dsmr_frontend/static/dsmr_frontend/css/dsmr-reader/global.css` (after line 187, inside the picker section)
- Modify: `dsmr_frontend/static/dsmr_frontend/css/dsmr-reader/dark.css` (lines 96–131 removed, one rule added)

- [ ] **Step 1: Add `.dsmr-picker-grid--days` and `.dsmr-picker-weekday` to global.css**

  In `/app/src/dsmr_frontend/static/dsmr_frontend/css/dsmr-reader/global.css`, insert after the `.dsmr-picker-cell:disabled` block (after line 187):

  ```css
  .dsmr-picker-grid--days {
      grid-template-columns: repeat(7, 1fr);
  }

  .dsmr-picker-weekday {
      text-align: center;
      padding: 4px;
      font-size: 11px;
      color: #999;
      font-weight: 600;
  }
  ```

- [ ] **Step 2: Remove flatpickr dark-mode overrides and add weekday dark rule in dark.css**

  In `/app/src/dsmr_frontend/static/dsmr_frontend/css/dsmr-reader/dark.css`, replace the entire flatpickr block (lines 96–131):

  ```css
  /**
  * Flatpickr dark mode
  */
  .dark-mode .flatpickr-calendar {
      background: var(--dark-panel-background);
      box-shadow: none;
      border-color: var(--dark-border-color);
  }
  .dark-mode .flatpickr-months .flatpickr-month,
  .dark-mode .flatpickr-weekdays,
  .dark-mode span.flatpickr-weekday {
      background: var(--dark-panel-background);
      color: var(--dark-font-color);
      fill: var(--dark-font-color);
  }
  .dark-mode .flatpickr-day {
      color: var(--dark-font-color);
  }
  .dark-mode .flatpickr-day:hover,
  .dark-mode .flatpickr-day.prevMonthDay:hover,
  .dark-mode .flatpickr-day.nextMonthDay:hover {
      background: var(--dark-table-background);
      border-color: var(--dark-table-background);
  }
  .dark-mode .flatpickr-day.selected,
  .dark-mode .flatpickr-day.selected:hover {
      background: #428bca;
      border-color: #428bca;
  }
  .dark-mode .flatpickr-day.today {
      border-bottom-color: var(--dark-font-color);
  }
  .dark-mode .flatpickr-months .flatpickr-prev-month svg,
  .dark-mode .flatpickr-months .flatpickr-next-month svg {
      fill: var(--dark-font-color);
  }
  ```

  with:

  ```css
  /**
  * Day grid picker dark mode
  */
  .dark-mode .dsmr-picker-weekday {
      color: #666;
  }
  ```

- [ ] **Step 3: Commit**

  ```bash
  cd /app && git -C /app status
  git add src/dsmr_frontend/static/dsmr_frontend/css/dsmr-reader/global.css \
          src/dsmr_frontend/static/dsmr_frontend/css/dsmr-reader/dark.css
  git commit -m "style: add day picker grid CSS, remove flatpickr dark-mode overrides"
  ```

---

### Task 2: Replace flatpickr day picker in archive.js

**Files:**
- Modify: `dsmr_frontend/static/dsmr_frontend/js/dsmr-reader/archive/archive.js`

- [ ] **Step 1: Replace the top-level variables and flatpickr init**

  Replace the entire contents of `/app/src/dsmr_frontend/static/dsmr_frontend/js/dsmr-reader/archive/archive.js` with the following. The key changes are:
  - Remove `g_day_picker` and its flatpickr init
  - Add `g_day_picker_month = null`
  - Update `switch_mode()` days branch
  - Add `render_day_picker()`

  ```javascript
  let g_datepicker_view_mode = 'months';
  let g_selected_date = null;
  let g_day_picker_month = null;
  let g_month_picker_year = null;
  let g_year_picker_decade_start = null;
  let summary_xhr_request = null;
  let g_graph_xhr_request = null;


  $(document).ready(function () {
      $("#datepicker_trigger_days").click(function () {
          g_datepicker_view_mode = 'days';
          switch_mode();
      });

      $("#datepicker_trigger_months").click(function () {
          g_datepicker_view_mode = 'months';
          switch_mode();
      });

      $("#datepicker_trigger_years").click(function () {
          g_datepicker_view_mode = 'years';
          switch_mode();
      });

      /* Initial mode. */
      switch_mode();
  });

  /**
   * Shows the appropriate picker for the current mode and triggers a view update.
   */
  function switch_mode() {
      $('.datepicker-trigger').removeClass('st-green').addClass('st-gray');
      $('#datepicker_trigger_' + g_datepicker_view_mode).removeClass('st-gray').addClass('st-green');

      var startDate = new Date(DATEPICKER_START_DATE);
      var endDate = new Date(DATEPICKER_END_DATE);

      if (g_datepicker_view_mode === 'days') {
          $('#datepicker-day').show();
          $('#datepicker-month').hide();
          $('#datepicker-year').hide();
          if (!g_selected_date) {
              g_selected_date = endDate;
          }
          g_day_picker_month = {year: g_selected_date.getFullYear(), month: g_selected_date.getMonth()};
          render_day_picker();
      } else if (g_datepicker_view_mode === 'months') {
          $('#datepicker-day').hide();
          $('#datepicker-month').show();
          $('#datepicker-year').hide();

          if (!g_selected_date) {
              g_selected_date = new Date(endDate.getFullYear(), endDate.getMonth(), 1);
          }
          g_month_picker_year = Math.max(startDate.getFullYear(),
              Math.min(endDate.getFullYear(), g_selected_date.getFullYear()));
          render_month_picker();
      } else {
          $('#datepicker-day').hide();
          $('#datepicker-month').hide();
          $('#datepicker-year').show();

          if (!g_selected_date) {
              g_selected_date = new Date(endDate.getFullYear(), 0, 1);
          }
          g_year_picker_decade_start = Math.floor(g_selected_date.getFullYear() / 10) * 10;
          render_year_picker();
      }

      update_view(g_selected_date);
  }

  /**
   * Renders the day-grid calendar picker into #datepicker-day.
   * Reads / mutates: g_day_picker_month, g_selected_date.
   */
  function render_day_picker() {
      var startDate = new Date(DATEPICKER_START_DATE);
      var endDate = new Date(DATEPICKER_END_DATE);
      var year = g_day_picker_month.year;
      var month = g_day_picker_month.month;
      var locale = DATEPICKER_LANGUAGE_CODE.startsWith('nl') ? 'nl-NL' : 'en-GB';

      /* Weekday header row — Monday first (Jan 1 2024 is a Monday) */
      var weekdays = '';
      for (var d = 0; d < 7; d++) {
          var name = new Intl.DateTimeFormat(locale, {weekday: 'short'}).format(new Date(2024, 0, 1 + d));
          weekdays += '<div class="dsmr-picker-weekday">' + name + '</div>';
      }

      /* Number of days in this month; weekday of the 1st (0=Mon … 6=Sun) */
      var daysInMonth = new Date(year, month + 1, 0).getDate();
      var firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7;

      var cells = '';

      /* Spillover days from previous month */
      var prevMonthDays = new Date(year, month, 0).getDate();
      for (var p = firstWeekday - 1; p >= 0; p--) {
          cells += '<button class="dsmr-picker-cell muted" disabled>' + (prevMonthDays - p) + '</button>';
      }

      /* Days of current month */
      var minDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      var maxDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
      for (var day = 1; day <= daysInMonth; day++) {
          var cellDate = new Date(year, month, day);
          var isDisabled = cellDate < minDate || cellDate > maxDate;
          var isActive = g_selected_date
              && g_selected_date.getFullYear() === year
              && g_selected_date.getMonth() === month
              && g_selected_date.getDate() === day;
          var cls = 'dsmr-picker-cell' + (isActive ? ' active' : '');
          if (isDisabled) {
              cells += '<button class="' + cls + '" disabled>' + day + '</button>';
          } else {
              cells += '<button class="' + cls + '" data-day="' + day + '">' + day + '</button>';
          }
      }

      /* Trailing spillover to complete the last row */
      var totalCells = firstWeekday + daysInMonth;
      var trailingCells = (7 - (totalCells % 7)) % 7;
      for (var n = 1; n <= trailingCells; n++) {
          cells += '<button class="dsmr-picker-cell muted" disabled>' + n + '</button>';
      }

      /* Nav disabled logic */
      var prevMonthDate = new Date(year, month - 1, 1);
      var nextMonthDate = new Date(year, month + 1, 1);
      var prevDisabled = prevMonthDate < new Date(startDate.getFullYear(), startDate.getMonth(), 1);
      var nextDisabled = nextMonthDate > new Date(endDate.getFullYear(), endDate.getMonth(), 1);

      var titleStr = new Intl.DateTimeFormat(locale, {month: 'long', year: 'numeric'}).format(new Date(year, month, 1));

      document.getElementById('datepicker-day').innerHTML =
          '<div class="dsmr-picker">' +
          '<div class="dsmr-picker-nav">' +
          '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
          '<span class="dsmr-picker-title">' + titleStr + '</span>' +
          '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
          '</div>' +
          '<div class="dsmr-picker-grid dsmr-picker-grid--days">' + weekdays + cells + '</div>' +
          '</div>';

      var container = document.getElementById('datepicker-day');

      container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
          g_day_picker_month = {year: prevMonthDate.getFullYear(), month: prevMonthDate.getMonth()};
          render_day_picker();
      });
      container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
          g_day_picker_month = {year: nextMonthDate.getFullYear(), month: nextMonthDate.getMonth()};
          render_day_picker();
      });
      container.querySelectorAll('.dsmr-picker-cell[data-day]').forEach(function (cell) {
          cell.addEventListener('click', function () {
              g_selected_date = new Date(year, month, parseInt(this.getAttribute('data-day')));
              update_view(g_selected_date);
              render_day_picker();
          });
      });
  }

  /**
   * Renders the month-grid picker into #datepicker-month.
   * Reads / mutates: g_month_picker_year, g_selected_date.
   */
  function render_month_picker() {
      var startDate = new Date(DATEPICKER_START_DATE);
      var endDate = new Date(DATEPICKER_END_DATE);
      var year = g_month_picker_year;
      var locale = DATEPICKER_LANGUAGE_CODE.startsWith('nl') ? 'nl-NL' : 'en-GB';

      var months = [];
      for (var i = 0; i < 12; i++) {
          months.push(new Intl.DateTimeFormat(locale, {month: 'short'}).format(new Date(2024, i, 1)));
      }

      var prevDisabled = year - 1 < startDate.getFullYear();
      var nextDisabled = year + 1 > endDate.getFullYear();

      var cells = '';
      for (var m = 0; m < 12; m++) {
          var cellDate = new Date(year, m, 1);
          var minMonth = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
          var maxMonth = new Date(endDate.getFullYear(), endDate.getMonth(), 1);
          var isDisabled = cellDate < minMonth || cellDate > maxMonth;
          var isActive = g_selected_date
              && g_selected_date.getFullYear() === year
              && g_selected_date.getMonth() === m;
          var cls = 'dsmr-picker-cell' + (isActive ? ' active' : '');
          if (isDisabled) {
              cells += '<button class="' + cls + '" disabled>' + months[m] + '</button>';
          } else {
              cells += '<button class="' + cls + '" data-month="' + m + '">' + months[m] + '</button>';
          }
      }

      document.getElementById('datepicker-month').innerHTML =
          '<div class="dsmr-picker">' +
          '<div class="dsmr-picker-nav">' +
          '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
          '<span class="dsmr-picker-title">' + year + '</span>' +
          '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
          '</div>' +
          '<div class="dsmr-picker-grid">' + cells + '</div>' +
          '</div>';

      var container = document.getElementById('datepicker-month');

      container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
          g_month_picker_year--;
          render_month_picker();
      });
      container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
          g_month_picker_year++;
          render_month_picker();
      });
      container.querySelectorAll('.dsmr-picker-cell[data-month]').forEach(function (cell) {
          cell.addEventListener('click', function () {
              g_selected_date = new Date(g_month_picker_year, parseInt(this.getAttribute('data-month')), 1);
              update_view(g_selected_date);
              render_month_picker();
          });
      });
  }

  /**
   * Renders the year-grid picker into #datepicker-year.
   * Reads / mutates: g_year_picker_decade_start, g_selected_date.
   * Shows 12 years (decadeStart−1 … decadeStart+10) like Bootstrap Datepicker.
   */
  function render_year_picker() {
      var startDate = new Date(DATEPICKER_START_DATE);
      var endDate = new Date(DATEPICKER_END_DATE);
      var ds = g_year_picker_decade_start;

      /* Prev disabled when the previous decade contains no valid years. */
      var prevDisabled = (ds - 1) < startDate.getFullYear();
      var nextDisabled = (ds + 10) > endDate.getFullYear();

      var cells = '';
      for (var y = ds - 1; y <= ds + 10; y++) {
          var isOutOfDecade = y < ds || y > ds + 9;
          var isDisabled = y < startDate.getFullYear() || y > endDate.getFullYear();
          var isActive = g_selected_date && g_selected_date.getFullYear() === y;
          var cls = 'dsmr-picker-cell'
              + (isOutOfDecade && !isDisabled ? ' muted' : '')
              + (isActive ? ' active' : '');
          if (isDisabled) {
              cells += '<button class="' + cls + '" disabled>' + y + '</button>';
          } else {
              cells += '<button class="' + cls + '" data-year="' + y + '">' + y + '</button>';
          }
      }

      document.getElementById('datepicker-year').innerHTML =
          '<div class="dsmr-picker">' +
          '<div class="dsmr-picker-nav">' +
          '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
          '<span class="dsmr-picker-title">' + ds + '\u2013' + (ds + 9) + '</span>' +
          '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
          '</div>' +
          '<div class="dsmr-picker-grid">' + cells + '</div>' +
          '</div>';

      var container = document.getElementById('datepicker-year');

      container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
          g_year_picker_decade_start -= 10;
          render_year_picker();
      });
      container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
          g_year_picker_decade_start += 10;
          render_year_picker();
      });
      container.querySelectorAll('.dsmr-picker-cell[data-year]').forEach(function (cell) {
          cell.addEventListener('click', function () {
              g_selected_date = new Date(parseInt(this.getAttribute('data-year')), 0, 1);
              update_view(g_selected_date);
              render_year_picker();
          });
      });
  }

  /**
   * Shortcut for updating both XHR views.
   */
  function update_view(selected_date) {
      update_summary(selected_date);
      update_graphs(selected_date);
  }

  /**
   * Updates the upper view, which is the summary table.
   */
  function update_summary(selected_date) {
      $("#summary-loader").show();
      $("#summary-holder").hide();

      /* Prevent queueing multiple updates when a user clicks multiple selections too quickly. */
      if (summary_xhr_request !== null) {
          summary_xhr_request.abort();
      }

      summary_xhr_request = $.ajax({
          url: ARCHIVE_XHR_SUMMARY_URL,
          data: {
              'date': dayjs(selected_date).format(DATEPICKER_LOCALE_FORMAT.toUpperCase()),
              'level': g_datepicker_view_mode
          },
      }).done(function (data) {
          $("#summary-holder").html(data).show();
      }).always(function () {
          $("#summary-loader").hide();
          summary_xhr_request = null;
      });
  }

  /**
   * Updates the lower view, which are the graphs displayed.
   */
  function update_graphs(selected_date) {
      /* Prevent queueing multiple updates when a user clicks multiple selections too quickly. */
      if (g_graph_xhr_request !== null) {
          g_graph_xhr_request.abort();
      }

      if (echarts_electricity_graph !== undefined) {
          echarts_electricity_graph?.showLoading('default', LOADING_OPTIONS)
          echarts_electricity_graph?.clear();
      }

      if (echarts_electricity_returned_graph !== undefined) {
          echarts_electricity_returned_graph?.showLoading('default', LOADING_OPTIONS)
          echarts_electricity_returned_graph?.clear();
      }

      if (echarts_gas_graph !== undefined) {
          echarts_gas_graph?.showLoading('default', LOADING_OPTIONS)
          echarts_gas_graph?.clear();
      }

      g_graph_xhr_request = $.ajax({
          url: ARCHIVE_XHR_GRAPHS_URL,
          dataType: "json",
          data: {
              'date': dayjs(selected_date).format(DATEPICKER_LOCALE_FORMAT.toUpperCase()),
              'level': g_datepicker_view_mode
          }
      }).done(function (response) {
          if (response.electricity) {
              render_electricity_graph(response.electricity);
          }

          if (response.electricity_returned) {
              render_electricity_returned_graph(response.electricity_returned);
          }

          if (response.gas) {
              render_gas_graph(response.gas);
          }
      }).always(function () {
          g_graph_xhr_request = null;
          $("#chart-loader").hide();
      });
  }
  ```

- [ ] **Step 2: Commit**

  ```bash
  cd /app && git -C /app status
  git add src/dsmr_frontend/static/dsmr_frontend/js/dsmr-reader/archive/archive.js
  git commit -m "feat: replace flatpickr day picker with custom grid in archive.js"
  ```

---

### Task 3: Update archive.html

**Files:**
- Modify: `dsmr_frontend/templates/dsmr_frontend/archive.html`

- [ ] **Step 1: Replace the day picker input with a div**

  In `/app/src/dsmr_frontend/templates/dsmr_frontend/archive.html`, replace:

  ```html
                          <input id="datepicker-day" type="hidden">
  ```

  with:

  ```html
                          <div id="datepicker-day" style="display:none;"></div>
  ```

- [ ] **Step 2: Remove flatpickr CSS link**

  Remove this block from the `{% block stylesheets %}` section:

  ```html
      <link href="{% static 'dsmr_frontend/css/flatpickr.min.css' %}?r=v{{ dsmr_version }}"
            rel="stylesheet"
            type="text/css" />
  ```

- [ ] **Step 3: Remove flatpickr JS scripts**

  Remove these three lines from the `{% block javascript %}` section:

  ```html
      <script type="text/javascript"
              src="{% static 'dsmr_frontend/js/flatpickr.min.js' %}?r=v{{ dsmr_version }}"></script>
      {% if LANGUAGE_CODE == 'nl' %}
          <script type="text/javascript"
                  src="{% static 'dsmr_frontend/js/flatpickr-locale-nl.js' %}?r=v{{ dsmr_version }}"></script>
      {% endif %}
  ```

- [ ] **Step 4: Run djlint to reformat the template**

  ```bash
  cd /app/src && poetry run djlint --reformat dsmr_frontend/templates/dsmr_frontend/archive.html
  ```

  Expected: `1 file reformatted` (or `1 file left unchanged` if already clean).

- [ ] **Step 5: Commit**

  ```bash
  cd /app && git -C /app status
  git add src/dsmr_frontend/templates/dsmr_frontend/archive.html
  git commit -m "feat: remove flatpickr from archive template, use div day picker container"
  ```

---

### Task 4: Replace flatpickr day picker in compare.js

**Files:**
- Modify: `dsmr_frontend/static/dsmr_frontend/js/dsmr-reader/compare/compare.js`

- [ ] **Step 1: Replace the entire file**

  Replace the entire contents of `/app/src/dsmr_frontend/static/dsmr_frontend/js/dsmr-reader/compare/compare.js`:

  ```javascript
  let g_datepicker_view_mode = 'months';
  let g_datepicker_selections = {};
  let g_day_picker_month = {'1': null, '2': null};
  let g_month_picker_year = {'1': null, '2': null};
  let g_year_picker_decade_start = {'1': null, '2': null};


  $(document).ready(function () {
      $("#datepicker_trigger_days").click(function () {
          g_datepicker_view_mode = 'days';
          switch_mode();
      });

      $("#datepicker_trigger_months").click(function () {
          g_datepicker_view_mode = 'months';
          switch_mode();
      });

      $("#datepicker_trigger_years").click(function () {
          g_datepicker_view_mode = 'years';
          switch_mode();
      });

      /* Initial mode. */
      switch_mode();
  });

  /**
   * Shows the appropriate pickers for the current mode and resets selections.
   */
  function switch_mode() {
      /* Reset selections so both dates must be re-chosen in the new mode. */
      g_datepicker_selections = {};

      $('.datepicker-trigger').removeClass('st-green').addClass('st-gray');
      $('#datepicker_trigger_' + g_datepicker_view_mode).removeClass('st-gray').addClass('st-green');

      var startDate = new Date(datepicker_start_date);
      var endDate = new Date(datepicker_end_date);

      ['1', '2'].forEach(function (postfix) {
          if (g_datepicker_view_mode === 'days') {
              $('#datepicker' + postfix + '-day').show();
              $('#datepicker' + postfix + '-month').hide();
              $('#datepicker' + postfix + '-year').hide();

              if (!g_day_picker_month[postfix]) {
                  g_day_picker_month[postfix] = {year: endDate.getFullYear(), month: endDate.getMonth()};
              }
              render_day_picker(postfix);
          } else if (g_datepicker_view_mode === 'months') {
              $('#datepicker' + postfix + '-day').hide();
              $('#datepicker' + postfix + '-month').show();
              $('#datepicker' + postfix + '-year').hide();

              if (!g_month_picker_year[postfix]) {
                  g_month_picker_year[postfix] = endDate.getFullYear();
              }
              g_month_picker_year[postfix] = Math.max(startDate.getFullYear(),
                  Math.min(endDate.getFullYear(), g_month_picker_year[postfix]));
              render_month_picker(postfix);
          } else {
              $('#datepicker' + postfix + '-day').hide();
              $('#datepicker' + postfix + '-month').hide();
              $('#datepicker' + postfix + '-year').show();

              if (!g_year_picker_decade_start[postfix]) {
                  g_year_picker_decade_start[postfix] = Math.floor(endDate.getFullYear() / 10) * 10;
              }
              render_year_picker(postfix);
          }
      });
  }

  /**
   * Renders the day-grid calendar picker for the given postfix.
   * Reads / mutates: g_day_picker_month[postfix], g_datepicker_selections[postfix].
   */
  function render_day_picker(postfix) {
      var startDate = new Date(datepicker_start_date);
      var endDate = new Date(datepicker_end_date);
      var year = g_day_picker_month[postfix].year;
      var month = g_day_picker_month[postfix].month;
      var locale = datepicker_language_code.startsWith('nl') ? 'nl-NL' : 'en-GB';

      /* Weekday header row — Monday first (Jan 1 2024 is a Monday) */
      var weekdays = '';
      for (var d = 0; d < 7; d++) {
          var name = new Intl.DateTimeFormat(locale, {weekday: 'short'}).format(new Date(2024, 0, 1 + d));
          weekdays += '<div class="dsmr-picker-weekday">' + name + '</div>';
      }

      /* Number of days in this month; weekday of the 1st (0=Mon … 6=Sun) */
      var daysInMonth = new Date(year, month + 1, 0).getDate();
      var firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7;

      var cells = '';

      /* Spillover days from previous month */
      var prevMonthDays = new Date(year, month, 0).getDate();
      for (var p = firstWeekday - 1; p >= 0; p--) {
          cells += '<button class="dsmr-picker-cell muted" disabled>' + (prevMonthDays - p) + '</button>';
      }

      /* Days of current month */
      var minDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      var maxDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
      for (var day = 1; day <= daysInMonth; day++) {
          var cellDate = new Date(year, month, day);
          var isDisabled = cellDate < minDate || cellDate > maxDate;
          var sel = g_datepicker_selections[postfix];
          var isActive = sel
              && sel.getFullYear() === year
              && sel.getMonth() === month
              && sel.getDate() === day;
          var cls = 'dsmr-picker-cell' + (isActive ? ' active' : '');
          if (isDisabled) {
              cells += '<button class="' + cls + '" disabled>' + day + '</button>';
          } else {
              cells += '<button class="' + cls + '" data-day="' + day + '">' + day + '</button>';
          }
      }

      /* Trailing spillover to complete the last row */
      var totalCells = firstWeekday + daysInMonth;
      var trailingCells = (7 - (totalCells % 7)) % 7;
      for (var n = 1; n <= trailingCells; n++) {
          cells += '<button class="dsmr-picker-cell muted" disabled>' + n + '</button>';
      }

      /* Nav disabled logic */
      var prevMonthDate = new Date(year, month - 1, 1);
      var nextMonthDate = new Date(year, month + 1, 1);
      var prevDisabled = prevMonthDate < new Date(startDate.getFullYear(), startDate.getMonth(), 1);
      var nextDisabled = nextMonthDate > new Date(endDate.getFullYear(), endDate.getMonth(), 1);

      var titleStr = new Intl.DateTimeFormat(locale, {month: 'long', year: 'numeric'}).format(new Date(year, month, 1));

      document.getElementById('datepicker' + postfix + '-day').innerHTML =
          '<div class="dsmr-picker">' +
          '<div class="dsmr-picker-nav">' +
          '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
          '<span class="dsmr-picker-title">' + titleStr + '</span>' +
          '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
          '</div>' +
          '<div class="dsmr-picker-grid dsmr-picker-grid--days">' + weekdays + cells + '</div>' +
          '</div>';

      var container = document.getElementById('datepicker' + postfix + '-day');

      container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
          g_day_picker_month[postfix] = {year: prevMonthDate.getFullYear(), month: prevMonthDate.getMonth()};
          render_day_picker(postfix);
      });
      container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
          g_day_picker_month[postfix] = {year: nextMonthDate.getFullYear(), month: nextMonthDate.getMonth()};
          render_day_picker(postfix);
      });
      container.querySelectorAll('.dsmr-picker-cell[data-day]').forEach(function (cell) {
          cell.addEventListener('click', function () {
              g_datepicker_selections[postfix] = new Date(year, month, parseInt(this.getAttribute('data-day')));
              update_summary();
              render_day_picker(postfix);
          });
      });
  }

  /**
   * Renders the month-grid picker for the given postfix.
   */
  function render_month_picker(postfix) {
      var startDate = new Date(datepicker_start_date);
      var endDate = new Date(datepicker_end_date);
      var year = g_month_picker_year[postfix];
      var locale = datepicker_language_code.startsWith('nl') ? 'nl-NL' : 'en-GB';

      var months = [];
      for (var i = 0; i < 12; i++) {
          months.push(new Intl.DateTimeFormat(locale, {month: 'short'}).format(new Date(2024, i, 1)));
      }

      var prevDisabled = (year - 1) < startDate.getFullYear();
      var nextDisabled = (year + 1) > endDate.getFullYear();

      var cells = '';
      for (var m = 0; m < 12; m++) {
          var cellDate = new Date(year, m, 1);
          var minMonth = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
          var maxMonth = new Date(endDate.getFullYear(), endDate.getMonth(), 1);
          var isDisabled = cellDate < minMonth || cellDate > maxMonth;
          var sel = g_datepicker_selections[postfix];
          var isActive = sel && sel.getFullYear() === year && sel.getMonth() === m;
          var cls = 'dsmr-picker-cell' + (isActive ? ' active' : '');
          if (isDisabled) {
              cells += '<button class="' + cls + '" disabled>' + months[m] + '</button>';
          } else {
              cells += '<button class="' + cls + '" data-month="' + m + '">' + months[m] + '</button>';
          }
      }

      document.getElementById('datepicker' + postfix + '-month').innerHTML =
          '<div class="dsmr-picker">' +
          '<div class="dsmr-picker-nav">' +
          '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
          '<span class="dsmr-picker-title">' + year + '</span>' +
          '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
          '</div>' +
          '<div class="dsmr-picker-grid">' + cells + '</div>' +
          '</div>';

      var container = document.getElementById('datepicker' + postfix + '-month');

      container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
          g_month_picker_year[postfix]--;
          render_month_picker(postfix);
      });
      container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
          g_month_picker_year[postfix]++;
          render_month_picker(postfix);
      });
      container.querySelectorAll('.dsmr-picker-cell[data-month]').forEach(function (cell) {
          cell.addEventListener('click', function () {
              g_datepicker_selections[postfix] = new Date(
                  g_month_picker_year[postfix], parseInt(this.getAttribute('data-month')), 1
              );
              update_summary();
              render_month_picker(postfix);
          });
      });
  }

  /**
   * Renders the year-grid picker for the given postfix.
   * Shows 12 years (decadeStart−1 … decadeStart+10) like Bootstrap Datepicker.
   */
  function render_year_picker(postfix) {
      var startDate = new Date(datepicker_start_date);
      var endDate = new Date(datepicker_end_date);
      var ds = g_year_picker_decade_start[postfix];

      var prevDisabled = (ds - 1) < startDate.getFullYear();
      var nextDisabled = (ds + 10) > endDate.getFullYear();

      var cells = '';
      for (var y = ds - 1; y <= ds + 10; y++) {
          var isOutOfDecade = y < ds || y > ds + 9;
          var isDisabled = y < startDate.getFullYear() || y > endDate.getFullYear();
          var sel = g_datepicker_selections[postfix];
          var isActive = sel && sel.getFullYear() === y;
          var cls = 'dsmr-picker-cell'
              + (isOutOfDecade && !isDisabled ? ' muted' : '')
              + (isActive ? ' active' : '');
          if (isDisabled) {
              cells += '<button class="' + cls + '" disabled>' + y + '</button>';
          } else {
              cells += '<button class="' + cls + '" data-year="' + y + '">' + y + '</button>';
          }
      }

      document.getElementById('datepicker' + postfix + '-year').innerHTML =
          '<div class="dsmr-picker">' +
          '<div class="dsmr-picker-nav">' +
          '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
          '<span class="dsmr-picker-title">' + ds + '\u2013' + (ds + 9) + '</span>' +
          '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
          '</div>' +
          '<div class="dsmr-picker-grid">' + cells + '</div>' +
          '</div>';

      var container = document.getElementById('datepicker' + postfix + '-year');

      container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
          g_year_picker_decade_start[postfix] -= 10;
          render_year_picker(postfix);
      });
      container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
          g_year_picker_decade_start[postfix] += 10;
          render_year_picker(postfix);
      });
      container.querySelectorAll('.dsmr-picker-cell[data-year]').forEach(function (cell) {
          cell.addEventListener('click', function () {
              g_datepicker_selections[postfix] = new Date(
                  parseInt(this.getAttribute('data-year')), 0, 1
              );
              update_summary();
              render_year_picker(postfix);
          });
      });
  }

  /**
   * Updates the summary table when both pickers have a selection.
   */
  function update_summary() {
      if (!g_datepicker_selections['1'] || !g_datepicker_selections['2']) {
          return;
      }

      let base_selection = dayjs(g_datepicker_selections['1']).format(datepicker_locale_format.toUpperCase());
      let comparison_selection = dayjs(g_datepicker_selections['2']).format(datepicker_locale_format.toUpperCase());

      $("#summary-holder").hide();
      $("#summary-loader").show();

      $.ajax({
          url: compare_xhr_summary_url,
          data: {
              'base_date': base_selection,
              'comparison_date': comparison_selection,
              'level': g_datepicker_view_mode
          },
      }).done(function (data) {
          $("#summary-holder").html(data).show();
      }).always(function () {
          $("#summary-loader").hide();
      });
  }
  ```

- [ ] **Step 2: Commit**

  ```bash
  cd /app && git -C /app status
  git add src/dsmr_frontend/static/dsmr_frontend/js/dsmr-reader/compare/compare.js
  git commit -m "feat: replace flatpickr day picker with custom grid in compare.js"
  ```

---

### Task 5: Update compare.html

**Files:**
- Modify: `dsmr_frontend/templates/dsmr_frontend/compare.html`

- [ ] **Step 1: Replace day picker inputs with divs**

  In `/app/src/dsmr_frontend/templates/dsmr_frontend/compare.html`, replace:

  ```html
                  <input id="datepicker1-day" type="hidden">
  ```

  with:

  ```html
                  <div id="datepicker1-day" style="display:none;"></div>
  ```

  And replace:

  ```html
                  <input id="datepicker2-day" type="hidden">
  ```

  with:

  ```html
                  <div id="datepicker2-day" style="display:none;"></div>
  ```

- [ ] **Step 2: Remove flatpickr CSS link**

  Remove:

  ```html
      <link href="{% static 'dsmr_frontend/css/flatpickr.min.css' %}?r=v{{ dsmr_version }}"
            rel="stylesheet"
            type="text/css" />
  ```

- [ ] **Step 3: Remove flatpickr JS scripts**

  Remove:

  ```html
      <script type="text/javascript"
              src="{% static 'dsmr_frontend/js/flatpickr.min.js' %}?r=v{{ dsmr_version }}"></script>
      {% if LANGUAGE_CODE == 'nl' %}
          <script type="text/javascript"
                  src="{% static 'dsmr_frontend/js/flatpickr-locale-nl.js' %}?r=v{{ dsmr_version }}"></script>
      {% endif %}
  ```

- [ ] **Step 4: Run djlint to reformat the template**

  ```bash
  cd /app/src && poetry run djlint --reformat dsmr_frontend/templates/dsmr_frontend/compare.html
  ```

  Expected: `1 file reformatted` (or `1 file left unchanged`).

- [ ] **Step 5: Commit**

  ```bash
  cd /app && git -C /app status
  git add src/dsmr_frontend/templates/dsmr_frontend/compare.html
  git commit -m "feat: remove flatpickr from compare template, use div day picker containers"
  ```

---

### Task 6: Run quality checks

- [ ] **Step 1: Run the full quality pipeline**

  ```bash
  cd /app/src && poetry run black . && poetry run djlint --reformat . && poetry run mypy /app/src && poetry run flake8 && poetry run pytest -v
  ```

  All steps must pass. JS/CSS changes are not covered by the Python test suite — manual browser verification is the test for this feature (see below).

- [ ] **Step 2: Manual browser verification checklist**

  Start the dev server and open the Archive page (`/archive/`):
  - [ ] Days button shows a calendar grid with Mon–Sun headers and correct month/year title
  - [ ] Clicking a day highlights it (blue) and loads the summary + graphs below
  - [ ] Prev/next nav arrows change the displayed month
  - [ ] Prev arrow disabled when at the first valid month; next arrow disabled at the last
  - [ ] Days outside the valid range are greyed out and unclickable
  - [ ] Spillover days from prev/next months are shown muted and unclickable
  - [ ] Switching between Days/Months/Years modes works without errors
  - [ ] Dark mode: calendar renders correctly with dark colours
  - [ ] Dutch locale (`?lang=nl`): weekday names appear in Dutch

  Open the Compare page (`/compare/`):
  - [ ] Both "Compare from" and "Compare to" panels show independent day grids
  - [ ] Selecting a day in each panel triggers the summary once both are chosen
  - [ ] Nav arrows work independently per panel

- [ ] **Step 3: Commit quality-check result (if djlint made additional changes)**

  ```bash
  cd /app && git -C /app status
  # Only commit if there are changes
  git add -p
  git commit -m "style: apply djlint formatting after quality check"
  ```
