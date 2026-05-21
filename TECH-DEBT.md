## Web library cleanup and upgrades

### Remove (unused or legacy)

- **Semantic UI 2.4** — no active call sites, CSS loaded but nothing uses it
- **iCheck 1.0.1** — initialization explicitly commented out in `app.js`, plugin code dead
- **jQuery Inputmask** — vendored but never imported or called
- **jQuery placeholder** — vendored but never called
- **Ionicons 1.4.0** — superseded by Font Awesome, zero icon classes in use
- **html5shiv 3.7.0** — IE8 conditional load, can be dropped
- **Respond.js** — IE8 media query polyfill, can be dropped alongside html5shiv

### Upgrade or replace

- **jQuery 3.6.0** → upgrade to latest 3.x
- **Bootstrap 3.0.3** → upgrade to Bootstrap 5 (breaking: grid/component class renames)
- **Bootstrap Datepicker 1.9.0** → replace with [Flatpickr](https://flatpickr.js.org/) (actively maintained, no jQuery dependency)
- **ECharts 5.3.3** → upgrade to latest 5.x
- **Font Awesome Free 7.1.0** → already recent; verify latest
- **Moment.js 2.29.4** → replace with [Day.js](https://day.js.org/) (same API, ~2 KB vs 70 KB, actively maintained)
- **jQuery slimScroll 1.3.0** → replace with CSS `overflow: auto` + `::-webkit-scrollbar` styling (only 2 call sites)
- **jQuery ba-resize** → replace with native `ResizeObserver` API (1 call site)
