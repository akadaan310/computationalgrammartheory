# Design System

The book's website and print edition share one stylesheet (`book/site/assets/css/cgt.css`, about 24 kB, no framework). The design aims for a serious scholarly monograph: quiet paper tones, a serif text face, restrained colour that always *means* something, and no decoration that competes with mathematics.

## 1. Principles

1. **Reading first.** The text column is about 40rem wide (65–75 characters). Mathematics, tables and code may scroll inside their own containers, never the page.
2. **Colour carries meaning.** Each colour is tied to an evidence status or environment kind (§4). It is never used for decoration alone.
3. **Status is always visible.** Every chapter, formal environment and index row shows its evidence badge. Colour is never the only signal: the badge text always names the status.
4. **Strict CSP.** No inline scripts: the theme initializer is `assets/js/theme-init.js`, loaded synchronously in `<head>`. The production policy (`vercel.json`) is `script-src 'self'`. Styles allow `'unsafe-inline'` only because KaTeX emits style attributes.
5. **Works without JavaScript.** Math is rendered at build time. JavaScript adds search, the theme toggle, the table-of-contents highlight, filters and the laboratory widgets. Without it, each laboratory panel shows its author-written text alternative, which describes what the widget computes and its key result.
6. **One source, two media.** The print stylesheet turns the same HTML into the PDF (D-022).

## 2. Tokens

The tokens are CSS custom properties on `:root`. Dark values apply under `prefers-color-scheme: dark` unless the user picked light, and under `[data-theme="dark"]`. The choice is stored in `localStorage` (`cgt-theme`), and pages work if storage is blocked.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--paper`, `--paper-2`, `--paper-3`, `--card` | #f7f3ea, #efe8da, #e6dcc8, #fbf8f2 | #141516, #1b1d1f, #24272a, #191b1d | backgrounds |
| `--ink`, `--ink-2`, `--ink-3` | #1c1e21, #3c4045, #6a6e73 | #ece6d9, #cfc8b9, #9a9488 | text, secondary text, captions |
| `--rule`, `--rule-2` | #d6ccb8, #bfb39a | #33363a, #4a4e53 | hairlines, borders |
| `--emerald` (+ `-2`, `-tint`) | #0d6b52 | #5cc4a0 | links, focus, definitions, "proved here", primary actions |
| `--brass` (+ `-2`, `-tint`) | #8a6d2f | #d2b06a | chapter and section numbers, kickers, empirical status |
| `--claret` (+ `-tint`) | #8c2f39 | #e08a92 | rejected hypotheses, boundaries, negative results |
| `--slate` (+ `-tint`) | #3d5a80 | #9fb7d9 | established results, secondary data series |
| `--serif` | Source Serif 4 | | body text, headings |
| `--sans` | IBM Plex Sans | | navigation, labels, badges, tables of contents |
| `--mono` | JetBrains Mono | | code, identifiers, ledger IDs |
| `--measure`, `--gutter`, `--radius` | 40rem, 1rem, 6px | | layout |

All three typefaces are self-hosted from `@fontsource` packages (SIL Open Font License), so there are no third-party font requests. Text and background pairs were chosen for high contrast. A formal WCAG contrast audit has **not** been performed and is a release-checklist item.

## 3. Layout and breakpoints

| Width | Layout |
|---|---|
| ≥ 1180px | two columns: a sticky chapter table of contents (17rem) and the centred text column |
| < 1180px | single text column; the chapter table of contents is hidden (sections stay reachable through headings and the pager) |
| ≤ 900px | the header wraps; primary navigation becomes a horizontally scrollable row; the search field narrows |
| ≤ 560px | 1rem body text, the brand subtitle is hidden, environment paddings are reduced |

Release QA (D-021) treats horizontal page overflow at 390px width as a defect. Scroll containers (`.table-wrap`, `.equation`, code) are `position:relative`, so KaTeX's absolutely positioned MathML cannot escape them.

## 4. Components

- **Formal environments** (`.env-*`):
  - definition: emerald rule;
  - theorem, proposition, lemma, corollary: ink rule, italic body with upright math;
  - conjecture: dashed slate rule;
  - observation: slate rule on a slate tint;
  - algorithm: brass rule;
  - example, exercise and solution (`<details>`);
  - remark and history: quiet left rule;
  - proof: no box, with an end-of-proof ∎ that has an aria label;
  - boundary: claret, for the limits of a result;
  - objectives and summary: tinted cards;
  - demo: an interactive laboratory panel.

  Each environment header shows its kind, its number, an optional title, a status badge and a ledger link.
- **Status badges** (`.status-*`): `proved-here`, `standard` (shown as "Established"), `adapted`, `empirical`, `conjecture`, `rejected`, `definition`, `proposed`, `mixed`, `draft`, `note`. Each badge has a tooltip with the full meaning (`STATUS` in `build.mjs`).
- **Code figures**: a caption says how the code is used, for example "Python · executed by the book's example checker"; output blocks are captioned "Output (checked)".
- **Tables**: tabular numerals, hairline rules, and horizontal scrolling inside `.table-wrap`.
- **Navigation**:
  - header with brand, primary navigation, search and theme toggle;
  - a skip link to the content;
  - `aria-current` on the active page;
  - a chapter table of contents with section numbers;
  - previous/next pager.
- **Feedback forms** (`.feedback-form`): labelled fields in sans, serif text areas, an emerald submit button, and a polite live region for status, which turns emerald on success and claret on error. When the backend is unavailable, the forms are hidden and a claret notice points to the issue tracker.
- **Laboratory widgets**: a controls row, result cards with large numerals, bar charts in SVG or HTML, and monospace traces.

## 5. Accessibility

- `lang="en"` on every page.
- A skip link and visible `:focus-visible` outlines in the emerald focus colour.
- Landmark elements (`header`, `nav`, `main`, `footer`) and labelled navigation.
- MathML alongside every formula.
- Decorative glyphs are `aria-hidden`.
- The interactive laboratory panels are labelled regions.
- **Not tested:** keyboard-only navigation end to end, screen readers with real users, and a formal WCAG audit. All three are release-checklist items.

## 6. Print

`@media print`:
- white paper;
- header, footer, table of contents, pager, search and demos are hidden;
- 10.5pt body;
- each chapter starts on a new page, and environments avoid page breaks;
- solutions are expanded;
- code wraps at 8pt;
- display math is set at 95 %;
- scroll containers are switched off.

`tools/pdf.mjs` adds an A4 footer with title, author, edition and page numbers, and checks that nothing is wider than the text block.
