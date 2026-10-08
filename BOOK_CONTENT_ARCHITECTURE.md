# Book Content Architecture

How the book *Computational Grammar Theory* is stored, written, checked and built. The book **is** the website. The PDF is generated from the same sources (D-020, D-022).

## 1. Layers of truth

| Layer | Location | Role |
|---|---|---|
| Research ledger | repository root: `RESULTS.md`, `DEFINITIONS.md`, `HYPOTHESES.md`, `COUNTEREXAMPLES.md`, `OPEN_PROBLEMS.md`, `EXPERIMENTS.md`, `PROVENANCE.md`, `DECISION_LOG.md`, … | **canonical scientific record**; every ledger ID (`CGT-THM-006`, …) is defined here |
| Evidence | `experiments/` (scripts plus `results/*.json`), `sdk/tests/` | reproducible support for empirical and implementation claims |
| Book sources | `book/content/` | the teaching text. The book cites the ledger and does not duplicate it, and the build fails if it cites an ID the ledger does not anchor |
| Generated data | `book/data/` (by `tools/export_data.py`) | SDK API reference, GaaS capabilities, ledger IDs, laboratory fixtures, experiment tables |
| Site | `book/dist/` (not committed) | static HTML, CSS and JS output, plus `print.html` |
| Print edition | `book/site/downloads/` (committed) | the PDF and its manifest (`pdf.json`), copied into `dist/downloads/`; the build warns when the PDF no longer matches the sources |

The order of authority is **ledger > book**. If a chapter and the ledger disagree, the ledger wins and the chapter is corrected.

## 2. Source layout (`book/content/`)

```
book.json            parts → chapter slugs; titles and blurbs of the parts
chapters/NN-slug.md  one file per chapter (20 chapters) and per appendix (a-, b-)
pages/*.md           researcher, status, lab, math-tests, feedback
backend.json         optional Supabase URL + publishable key (public; see supabase/README.md)
bibliography.json    55 entries, each with a verification status and note
glossary.json        34 terms, each with a short form, a definition and see-also links
macros.json          22 KaTeX macros
```

### 2.1 Chapter front matter

```yaml
---
title: "Compiling Operations: When Grammar Becomes Arithmetic"   # quote if it contains ':'
status: proved-here          # chapter-level evidence badge (one of the statuses in §3)
statusnote: One sentence on what the badge covers.
description: One-sentence summary (contents page, search, meta description).
noexercises: true            # appendices only
---
```

### 2.2 Required chapter elements (enforced by the build)

- `::: objectives`: learning objectives.
- At least one `::: exercise {#exr:…}`.
- `::: summary`.
- No placeholder text: the words TODO, TBD, FIXME and XXX, and *lorem ipsum*, fail the build.

### 2.3 Formal environments

```
::: theorem {#thm:compile title="Word compilation in heap-shaped trees" status="proved-here" ledger="CGT-THM-006"}
Statement…
:::
::: proof
…
:::
```

- **Kinds:** `definition`, `theorem`, `proposition`, `lemma`, `corollary`, `conjecture`, `observation`, `algorithm`, `example`, `exercise`, `solution`, `remark`, `history`, `boundary`, `proof`, `objectives`, `summary`, `demo`.
- **Numbering:** numbered kinds share a per-chapter counter (13.2, 13.3, …).
- **Required attributes:** every theorem-like environment must carry `status`; `ledger` is required when the result is in the ledger.
- **Index:** formal items feed the theorem index (`theorems.html`).

### 2.4 Cross-references and links (outside math)

| Command | Resolves to |
|---|---|
| `\ref{thm:compile}`, `\eqref{eq:x}` | numbered item or equation, linked |
| `\cite{key1,key2}` | bibliography entries; the chapter gets a "References cited" list |
| `\ledger{CGT-THM-006}` | link to the ledger page where the ID is anchored |
| `\gloss{term}` | glossary entry |
| `\chapref{slug}` | chapter link |
| `{#sec:label}` on a heading | section label |

### 2.5 Executable examples

````
```python run
from cgtsdk.structures import StackStructure
print(StackStructure([]).grammar().execute("push(1); pop").values)
```

```output
[None, 1]
```
````

- `tools/check_examples.py` runs each block in a fresh interpreter, with `PYTHONPATH=sdk/src` and `PYTHONHASHSEED=0`, and requires the exact printed output.
- `--write slug` fills output blocks from execution as an authoring aid; the prose must then be re-read against the real output (D-019).
- Blocks without `run` are illustrative and are not executed.

### 2.6 Laboratory widgets

```
::: demo pagerank
Text alternative describing what the widget shows and its key result.
:::
```

- The widget code is in `site/assets/js/lab.js`, on top of `cgt-core.js` (a JavaScript port of the SDK parts it needs).
- `book/tests/core.test.mjs` checks the port against fixtures the SDK exports.
- The build fails if a chapter names a demo that `lab.js` does not implement.

## 3. Evidence statuses

| Status | Badge | Meaning |
|---|---|---|
| `proved-here` | Proved here | proof in this book; self-checked, not externally reviewed |
| `standard` | Established | known result from the literature; cited |
| `adapted` | Adapted | known ideas restated in CGT terms |
| `empirical` | Empirical | reproducible measurement; not a proof |
| `conjecture` | Conjecture | not established |
| `rejected` | Rejected | a hypothesis tested and rejected |
| `definition` | Definition | a precise object, not a discovery |
| `proposed` | Proposed | a model or design proposed here; novelty unverified |
| `mixed` | Mixed | chapter level only: the chapter contains several kinds |

## 4. Build pipeline (`cd book && npm run build`)

1. `prebuild`: `tools/export_data.py` writes `book/data/*.json` from the SDK and the ledger.
2. **Ledger pages** are rendered first, from the canonical markdown, with an anchor for every ID. A map from ID to page makes every ledger link resolve to the page where the ID is actually anchored.
3. **Pass 1**: parse all chapters and register labels, numbers and formal items.
4. **Pass 2**: render. KaTeX runs at build time (MATHEMATICAL_RENDERING.md), and references, citations, glossary links and ledger links are resolved.
5. Generated pages:
   - index and contents;
   - the theorem index;
   - bibliography (with verification statuses);
   - glossary;
   - the SDK reference and the GaaS page (from `data/`);
   - researcher and publication-status pages;
   - laboratory;
   - search index (`assets/search-index.json`);
   - `print.html`;
   - the ledger pages.
6. **Integrity gate**: any error exits 1 and deletes `dist/`, so nothing is left that could be mistaken for a release. The checks are:
   - LaTeX errors;
   - duplicate or unresolved labels;
   - unknown citation keys;
   - bibliography entries that are never cited;
   - unknown or unanchored ledger IDs;
   - unknown glossary terms;
   - missing statuses;
   - missing objectives, exercises or summary;
   - placeholders;
   - unimplemented demos;
   - missing front matter.

Then:
- `npm test`: laboratory against SDK fixtures.
- `npm run examples`: every example reproduces its printed output.
- `node tools/linkcheck.mjs`: every internal link and anchor resolves.
- `npm run pdf`: print edition, with a page-width check.
- `npm run verify`: build, test, examples and link check in one command.

## 5. Stable URLs

- Chapters: `chapters/NN-slug.html`; sections: `#sec:label`; formal items: `#thm:label`, etc.
- Ledger IDs: `ledger/<page>.html#CGT-…`.
- Bibliography: `bibliography.html#key`.

Slugs and labels are never renamed after release; a renamed section keeps its old label.

## 6. Adding a chapter (checklist)

1. Add the slug to `book.json`.
2. Write `chapters/NN-slug.md` with front matter, objectives, exercises and summary.
3. Every claim must link to the ledger (`\ledger{…}`) or a citation (`\cite{…}`), or be marked with a status.
4. Write examples as `python run` blocks, then run `npm run examples`.
5. Run `npm run verify` and the screenshot check at mobile and desktop widths.
