# Supabase backend (optional)

The book is a static site, and every page works without this backend. The backend adds two **insert-only** channels for readers, and nothing else:

| Table | Public may | Visible to the public |
|---|---|---|
| `errata_reports` | insert (page, anchor, kind, message, optional contact) | nothing; triage happens in the dashboard |
| `independent_checks` | insert (reproduction or proof check: subject, outcome, details, optional environment, fingerprint, name) | only rows where `reviewed = true`, and never the `reviewed` flag itself |

Updates and deletes are reserved for the project owner (dashboard or service role). The full schema, with its constraints, column-level grants and row-level-security policies, is in `migrations/`.

## Hosted project

- Project `computational-grammar-theory`, ref `viyuzjhvjivhdvbrcnwh`, region `us-east-1`, organization `abedkadaan` (free plan).
- API URL `https://viyuzjhvjivhdvbrcnwh.supabase.co`.
- The **publishable** key is in `book/content/backend.json`. It is public by design. **Never** commit a secret or service-role key; the book build refuses to ship one.

## Researcher workflow

1. **Triage errata:** Table Editor → `errata_reports` → set `status` (`confirmed`, `fixed`, `rejected` or `duplicate`) and `resolution`. Every confirmed erratum also goes into the errata table of `RESULTS.md` §D.
2. **Publish a check:** Table Editor → `independent_checks` → set `reviewed = true`. It then appears on the book's status page, whatever its outcome.
3. **Change the schema:** add a new file under `migrations/`, then run `supabase db push` (or apply it with the Supabase MCP connector). Never edit an applied migration.

## Configuration

- **Different project:** set `CGT_SUPABASE_URL` and `CGT_SUPABASE_PUBLISHABLE_KEY` at build time, for example in Vercel's environment variables.
- **No backend:** set `CGT_BACKEND=off`. The forms are then replaced by a pointer to the repository's issue tracker.

## Verified at setup (2026-10-08)

Checked against the live API with the publishable key:
- inserts succeed (HTTP 201);
- reading `errata_reports` is denied;
- setting `status` or `reviewed` on insert is denied;
- an invalid `subject` is rejected by its check constraint;
- deletes are denied;
- unreviewed checks are invisible, and reviewed ones are visible.

The Supabase security advisor reported no findings.

Setup left test rows: two in `errata_reports` (messages starting "RLS self-test" and "End-to-end self-test") and one unreviewed, invisible row in `independent_checks`. Delete them in the Table Editor.
