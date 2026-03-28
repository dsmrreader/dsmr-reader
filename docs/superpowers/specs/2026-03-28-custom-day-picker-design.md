# Custom Day Picker — Design Spec

**Date:** 2026-03-28
**Scope:** `archive.html`, `compare.html` and their JS/CSS

---

## Problem

The day-level date picker on the Archive and Compare pages uses flatpickr (inline calendar widget), while the month and year pickers are custom JS-rendered `.dsmr-picker` grids. The inconsistency means two visual styles, a third-party dependency, and extra dark-mode CSS overrides.

## Goal

Replace the flatpickr day picker with a custom calendar grid that matches the existing `.dsmr-picker` component pattern used by the month and year pickers.

---

## Design

### Day picker structure

The picker renders into `<div id="datepicker-day">` (replacing the `<input type="hidden">`). It follows the same render-to-innerHTML pattern as `render_month_picker` / `render_year_picker`.

Layout:

```
‹  March 2026  ›
Mo  Tu  We  Th  Fr  Sa  Su
                          1
 2   3   4   5   6   7   8
...
30  31
```

- **Nav row**: `‹` / `›` buttons; prev disabled when previous month has no valid days, next disabled when next month has no valid days.
- **Weekday header row**: 7 abbreviated names via `Intl.DateTimeFormat(locale, { weekday: 'short' })`, locale-aware (`nl-NL` or `en-GB`). Week starts Monday.
- **Day grid**: `grid-template-columns: repeat(7, 1fr)`. Spillover days from the previous/next month are shown muted and non-interactive (no `data-day` attribute, `disabled` attribute set).
- **Active cell**: selected day gets the `active` class (same blue highlight as month/year pickers).
- **Disabled cells**: days outside `DATEPICKER_START_DATE`–`DATEPICKER_END_DATE` are rendered with `disabled`.
- **State variable**: `g_day_picker_month` holds `{ year, month }` (0-indexed month) of the currently displayed calendar page. Initialized to the month containing `DATEPICKER_END_DATE`.

### CSS additions (`global.css`)

Add `.dsmr-picker-weekday` for the non-interactive header cells:

```css
.dsmr-picker-weekday {
    text-align: center;
    padding: 4px;
    font-size: 11px;
    color: #999;
    font-weight: 600;
}
```

Add `.dsmr-picker-grid--days` modifier to extend the grid to 7 columns:

```css
.dsmr-picker-grid--days {
    grid-template-columns: repeat(7, 1fr);
}
```

The existing month/year grid uses `repeat(3, 1fr)` — the day grid needs a different column count, achieved via the modifier class rather than changing the base class.

### CSS removals (`dark.css`)

Remove the ~25 lines of flatpickr dark-mode overrides (`.dark-mode .flatpickr-*`). Add:

```css
.dark-mode .dsmr-picker-weekday {
    color: #666;
}
```

---

## File-by-file changes

### `archive.js`

- Remove `g_day_picker` variable and flatpickr initialization.
- Add `g_day_picker_month = null`.
- Add `render_day_picker()` function.
- `switch_mode()`: replace `g_day_picker.calendarContainer.style.display` toggling with `$('#datepicker-day').show()` / `.hide()`.
- On days mode entry: initialize `g_day_picker_month` from `g_selected_date` or `DATEPICKER_END_DATE`, call `render_day_picker()`.

### `compare.js`

- Same changes, but parameterized by `postfix` (`'1'` or `'2'`).
- `g_day_picker_month = { '1': null, '2': null }`.
- `render_day_picker(postfix)`.

### `archive.html`

- Replace `<input id="datepicker-day" type="hidden">` with `<div id="datepicker-day" style="display:none;"></div>`.
- Remove `<link>` for `flatpickr.min.css`.
- Remove `<script>` for `flatpickr.min.js` and `flatpickr-locale-nl.js`.
- Keep `dayjs.min.js` (still used in XHR date formatting).

### `compare.html`

- Replace `<input id="datepicker1-day" type="hidden">` and `<input id="datepicker2-day" type="hidden">` with `<div>` equivalents.
- Remove flatpickr CSS/JS tags.
- Keep `dayjs.min.js`.

---

## Out of scope

- No changes to the XHR endpoints or date format sent to the server.
- No changes to the month or year pickers.
- No changes to the `flatpickr.*` static files on disk (they can be cleaned up separately).
