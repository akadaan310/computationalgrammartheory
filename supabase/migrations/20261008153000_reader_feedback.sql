-- Computational Grammar Theory: reader feedback backend.
--
-- The book is a static site and never requires an account. This schema adds two
-- optional, insert-only channels that serve the research directly:
--
--   errata_reports      readers report errors, unclear passages, citation problems
--                       or gaps in proofs. Private: only the researcher (service
--                       role / dashboard) can read them, because a report may
--                       contain a contact address.
--   independent_checks  readers record an independent reproduction of an experiment
--                       or an independent check of a proof (publication blockers
--                       B-4 and reproducibility). Public once the researcher marks
--                       a row as reviewed; no personal data is stored.
--
-- Anonymous visitors may INSERT only, and only rows in the initial state. Nobody
-- but the service role may update or delete. All text fields are length-bounded.

create table public.errata_reports (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  edition     text not null default 'working edition 0.1' check (char_length(edition) <= 60),
  page        text not null check (char_length(page) between 1 and 300),
  anchor      text check (char_length(anchor) <= 200),
  kind        text not null check (kind in ('erratum', 'unclear', 'citation', 'proof-gap', 'other')),
  message     text not null check (char_length(message) between 10 and 4000),
  contact     text check (char_length(contact) <= 200),
  status      text not null default 'new'
              check (status in ('new', 'confirmed', 'fixed', 'rejected', 'duplicate')),
  resolution  text check (char_length(resolution) <= 2000)
);

comment on table public.errata_reports is
  'Reader-submitted errata for the CGT book. Insert-only for the public; read and triage via the dashboard.';

create table public.independent_checks (
  id           uuid primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  edition      text not null default 'working edition 0.1' check (char_length(edition) <= 60),
  check_kind   text not null check (check_kind in ('reproduction', 'proof-check')),
  subject      text not null check (subject ~ '^(CGT-[A-Z]+-[0-9]+[a-z]?|run_all|sdk_tests|examples|laboratory)$'),
  outcome      text not null check (outcome in ('confirmed', 'differs', 'issue-found', 'failed')),
  environment  text check (char_length(environment) <= 500),
  fingerprint  text check (fingerprint ~ '^[0-9a-f]{8,64}$'),
  details      text not null check (char_length(details) between 10 and 4000),
  checker_name text check (char_length(checker_name) <= 120),
  reviewed     boolean not null default false
);

comment on table public.independent_checks is
  'Independent reproductions and proof checks submitted by readers. Public once reviewed = true.';

create index independent_checks_reviewed_idx on public.independent_checks (reviewed, created_at desc);
create index errata_reports_status_idx on public.errata_reports (status, created_at desc);

alter table public.errata_reports enable row level security;
alter table public.independent_checks enable row level security;

-- Least privilege: the public roles get exactly what the policies allow.
revoke all on public.errata_reports from anon, authenticated;
revoke all on public.independent_checks from anon, authenticated;
grant insert (edition, page, anchor, kind, message, contact) on public.errata_reports to anon, authenticated;
grant insert (edition, check_kind, subject, outcome, environment, fingerprint, details, checker_name)
  on public.independent_checks to anon, authenticated;
grant select (id, created_at, edition, check_kind, subject, outcome, environment, fingerprint, details, checker_name)
  on public.independent_checks to anon, authenticated;

create policy "anyone may submit an erratum"
  on public.errata_reports for insert to anon, authenticated
  with check (status = 'new' and resolution is null);

create policy "anyone may submit an independent check"
  on public.independent_checks for insert to anon, authenticated
  with check (reviewed = false);

create policy "reviewed checks are public"
  on public.independent_checks for select to anon, authenticated
  using (reviewed);
