# Web Accessibility Guidelines for AI Agents

## Core Principle
Every user must be able to perceive, operate, understand, and navigate all content regardless of disability. Follow WCAG 2.2 AA as the minimum standard.

---

## 1. Semantic HTML

- Use the correct element for the job: `<button>` for actions, `<a>` for navigation, `<h1>`–`<h6>` for hierarchy
- Never use `<div>` or `<span>` as interactive elements without ARIA roles
- One `<h1>` per page; heading levels must not skip (h1 → h2 → h3, never h1 → h3)
- Use `<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, `<section>` landmarks
- Use `<ul>`/`<ol>` for lists, `<table>` for tabular data (never for layout)
- Form controls must use `<label for="id">` or `aria-label` — never placeholder-only labels

---

## 2. Keyboard Navigation

- All interactive elements must be reachable and operable via keyboard alone
- Tab order must follow visual/logical reading order
- Never remove focus outline without replacing it with a visible custom style
- `tabindex="0"` to add to tab order; `tabindex="-1"` to allow programmatic focus only
- Never use `tabindex > 0`
- Implement keyboard shortcuts for complex widgets:
  - Menus: arrow keys to navigate, Escape to close
  - Dialogs: Tab cycles within modal, Escape closes
  - Tabs: arrow keys switch tabs
- Skip links: first focusable element must be `<a href="#main">Skip to main content</a>`

---

## 3. Focus Management

- When a modal opens, move focus to the first focusable element inside it
- When a modal closes, return focus to the element that triggered it
- After route changes (SPA), move focus to the new `<h1>` or `<main>`
- After dynamic content loads (search results, alerts), announce via `aria-live`

---

## 4. ARIA

Use ARIA only when native HTML semantics are insufficient.

- `role="dialog"` + `aria-modal="true"` + `aria-labelledby` on modals
- `aria-expanded` on toggles (menus, accordions)
- `aria-selected` on tabs and listbox options
- `aria-current="page"` on active nav link
- `aria-live="polite"` for non-urgent dynamic updates
- `aria-live="assertive"` for urgent alerts only (use sparingly)
- `aria-hidden="true"` on decorative icons/images
- `aria-describedby` to associate hints or error messages with inputs
- Never use `aria-label` on elements that already have visible text — use `aria-labelledby` instead

---

## 5. Images and Media

- Every `<img>` must have an `alt` attribute
  - Informative images: describe content and function
  - Decorative images: `alt=""`
  - Functional images (icons as buttons): describe the action, not the icon
- Complex images (charts, graphs): provide a text alternative via `aria-describedby` or adjacent prose
- Video must have captions; audio must have transcripts
- No autoplay audio or video with sound
- If autoplay is unavoidable, provide a pause control as the first focusable element

---

## 6. Color and Contrast

- Text contrast ratio: minimum 4.5:1 for normal text, 3:1 for large text (18pt / 14pt bold)
- UI components (borders, icons): minimum 3:1 against adjacent colors
- Never use color as the only means of conveying information (e.g. red = error must also have an icon or text)
- Do not rely on color alone to indicate focus, selection, or state

---

## 7. Forms

- Every input must have a visible, persistent label (not just placeholder)
- Group related inputs with `<fieldset>` and `<legend>`
- Error messages must:
  - Be specific ("Email must include @" not "Invalid input")
  - Be programmatically associated via `aria-describedby`
  - Not rely on color alone
  - Be announced via `aria-live` when injected dynamically
- Required fields: use `required` attribute + indicate visually (not asterisk-only — explain the convention)
- Autocomplete: use `autocomplete` attribute on personal data fields

---

## 8. Motion and Animation

- Respect `prefers-reduced-motion` media query — disable or reduce all non-essential animation
- No content that flashes more than 3 times per second
- Parallax, scroll animations, and carousels must have pause controls or be disabled under reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 9. Responsive and Zoom

- Content must be usable at 400% browser zoom without horizontal scrolling
- Do not use `user-scalable=no` in the viewport meta tag
- Touch targets: minimum 44×44px (WCAG 2.2 requires 24×24px minimum, 44×44px recommended)
- Spacing between touch targets: minimum 8px

---

## 10. Page Structure

- Every page must have a unique, descriptive `<title>`
- `<html lang="en">` (or appropriate language code) on every page
- Inline language changes: `<span lang="fr">Bonjour</span>`
- Logical reading order in DOM must match visual order

---

## 11. Links and Buttons

- Link text must describe the destination ("View pricing" not "click here")
- If link text is ambiguous, add `aria-label` with full context
- Distinguish links from buttons: links navigate, buttons perform actions
- External links: indicate they open in a new tab via `aria-label` or visible icon with text alternative

---

## 12. Testing Checklist

Run these before marking any feature complete:

- [ ] Tab through entire page — every element reachable and operable
- [ ] No keyboard traps
- [ ] Screen reader test (NVDA+Firefox or VoiceOver+Safari)
- [ ] All images have appropriate alt text
- [ ] Color contrast passes on all text and UI elements
- [ ] Zoom to 400% — no content loss or horizontal scroll
- [ ] Reduced motion enabled — no disruptive animation
- [ ] Forms: labels, errors, and required fields all correct
- [ ] Dynamic content announced via aria-live
- [ ] axe DevTools or Lighthouse accessibility audit passes with 0 critical violations

---

## Quick Reference: Common Mistakes to Avoid

| Wrong | Right |
|---|---|
| `<div onclick="...">` | `<button>` |
| `placeholder` as label | `<label>` element |
| `outline: none` | Custom visible focus style |
| `alt="image.png"` | `alt="Description of content"` |
| Color-only error state | Color + icon + text |
| `tabindex="2"` | `tabindex="0"` |
| Missing lang attribute | `<html lang="en">` |
| `aria-label` over visible text | `aria-labelledby` |
| Autoplaying video with sound | User-initiated playback |
| `<table>` for layout | CSS Grid or Flexbox |

---

## References

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/
- axe DevTools: https://www.deque.com/axe/
