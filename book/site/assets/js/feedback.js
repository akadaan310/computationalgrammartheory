// feedback.js — optional reader-feedback forms and the list of reviewed
// independent checks. Talks to Supabase's REST endpoint with the PUBLIC
// publishable key from assets/backend.json; the database's row-level-security
// policies (supabase/migrations) allow inserts and reading reviewed checks only.
// Without a configured backend the page explains how to report by other means.

const FIELDS = {
  errata_reports: ["page", "anchor", "kind", "message", "contact"],
  independent_checks: ["check_kind", "subject", "outcome", "environment", "fingerprint", "details", "checker_name"],
};
const EDITION = "working edition 0.1";

async function loadBackend(rel) {
  try {
    const r = await fetch(new URL(rel + "assets/backend.json", location.href));
    if (!r.ok) return null;
    const b = await r.json();
    return b && b.url && b.publishableKey ? b : null;
  } catch (e) {
    return null;
  }
}

function headers(b, extra = {}) {
  return { apikey: b.publishableKey, "Content-Type": "application/json", ...extra };
}

function setStatus(form, msg, kind) {
  const el = form.querySelector(".ff-status");
  el.textContent = msg;
  el.className = `ff-status ${kind || ""}`;
}

function wireForm(form, b) {
  const table = form.dataset.feedback;
  const params = new URLSearchParams(location.search);
  if (table === "errata_reports" && params.get("page")) form.elements.page.value = params.get("page").slice(0, 300);
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    if (form.elements.website && form.elements.website.value) return; // honeypot: silently ignore bots
    if (!form.checkValidity()) {
      form.reportValidity();
      setStatus(form, "Please complete the required fields.", "err");
      return;
    }
    const row = { edition: EDITION };
    for (const f of FIELDS[table]) {
      const v = (form.elements[f]?.value || "").trim();
      if (v) row[f] = v;
    }
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    setStatus(form, "Sending…");
    try {
      const r = await fetch(`${b.url}/rest/v1/${table}`, {
        method: "POST",
        headers: headers(b, { Prefer: "return=minimal" }),
        body: JSON.stringify(row),
      });
      if (r.status === 201) {
        form.reset();
        setStatus(form, table === "errata_reports"
          ? "Thank you. The report is in the researcher's review queue."
          : "Thank you. The check will be listed on the status page once it has been reviewed.", "ok");
      } else {
        let detail = "";
        try { detail = (await r.json()).message || ""; } catch (e) { /* no body */ }
        setStatus(form, `The service rejected the submission (${r.status}${detail ? ": " + detail : ""}).`, "err");
      }
    } catch (e) {
      setStatus(form, "The service could not be reached. Please try again later or open an issue on the repository.", "err");
    } finally {
      btn.disabled = false;
    }
  });
}

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const OUTCOME = { confirmed: "Confirmed", differs: "Results differ", "issue-found": "Issue found", failed: "Could not complete" };

async function listChecks(el, b, rel) {
  try {
    const cols = "created_at,edition,check_kind,subject,outcome,environment,fingerprint,details,checker_name";
    const r = await fetch(`${b.url}/rest/v1/independent_checks?select=${cols}&order=created_at.desc&limit=200`, { headers: headers(b) });
    if (!r.ok) return;
    const rows = await r.json();
    if (!Array.isArray(rows) || !rows.length) return;
    const ledgerLink = (s) => (/^CGT-/.test(s) ? `<a class="ledger-id" href="${rel}search.html?q=${encodeURIComponent(s)}">${esc(s)}</a>` : `<code>${esc(s)}</code>`);
    el.innerHTML = `<table class="checks-table"><thead><tr><th>Date</th><th>Check</th><th>Subject</th><th>Outcome</th><th>Details</th></tr></thead><tbody>${rows.map((x) =>
      `<tr><td>${esc(x.created_at.slice(0, 10))}</td><td>${x.check_kind === "proof-check" ? "Proof check" : "Reproduction"}</td><td>${ledgerLink(x.subject)}</td>` +
      `<td><span class="outcome outcome-${esc(x.outcome)}">${esc(OUTCOME[x.outcome] || x.outcome)}</span></td>` +
      `<td>${esc(x.details)}${x.environment ? `<br><small>${esc(x.environment)}</small>` : ""}${x.checker_name ? `<br><small>— ${esc(x.checker_name)}</small>` : ""}</td></tr>`).join("")}</tbody></table>`;
    el.classList.add("table-wrap");
  } catch (e) {
    /* keep the static "none yet" text */
  }
}

export async function mount(rel) {
  const forms = [...document.querySelectorAll("form[data-feedback]")];
  const list = document.querySelector("[data-independent-checks]");
  const b = await loadBackend(rel);
  if (!b) {
    forms.forEach((f) => { f.hidden = true; });
    document.querySelectorAll("[data-feedback-unavailable]").forEach((e) => { e.hidden = false; });
    return;
  }
  forms.forEach((f) => wireForm(f, b));
  if (list) listChecks(list, b, rel);
}
