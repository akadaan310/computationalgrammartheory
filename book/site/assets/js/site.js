// site.js — theme, search, table-of-contents tracking, filters, lab mounting.
// Everything degrades gracefully: without JavaScript the book is fully
// readable (math is pre-rendered at build time), and every interactive
// demo carries a written text alternative.
(function () {
  "use strict";
  const root = document.documentElement;
  const rel = document.querySelector("#q")?.dataset.rel ?? "";

  // ---- theme
  const btn = document.querySelector(".theme-toggle");
  if (btn) btn.addEventListener("click", () => {
    const dark = root.dataset.theme === "dark" || (root.dataset.theme !== "light" && matchMedia("(prefers-color-scheme: dark)").matches);
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("cgt-theme", root.dataset.theme); } catch (e) { /* storage unavailable */ }
  });

  // ---- search
  let index = null;
  async function loadIndex() {
    if (index) return index;
    try { index = await (await fetch(rel + "assets/search-index.json")).json(); } catch (e) { index = []; }
    return index;
  }
  const norm = (s) => s.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "");
  function score(doc, terms) {
    const t = norm(doc.t), c = norm(doc.c || "");
    let s = 0;
    for (const q of terms) {
      if (t.includes(q)) s += t.startsWith(q) ? 6 : 4;
      else if (c.includes(q)) s += 1;
      else return 0;
    }
    if (["theorem", "definition", "proposition"].includes(doc.k)) s += 1;
    return s;
  }
  function search(q) {
    const terms = norm(q).split(/\s+/).filter((x) => x.length > 1);
    if (!terms.length) return [];
    return index.map((d) => [score(d, terms), d]).filter(([s]) => s > 0).sort((a, b) => b[0] - a[0]).slice(0, 40).map(([, d]) => d);
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const item = (d) => `<a href="${rel}${d.u}"><span class="k">${esc(d.k)}</span>${esc(d.t)}<span class="c">${esc(d.c || "")}</span></a>`;
  const input = document.querySelector("#q"), pop = document.querySelector(".search-pop");
  if (input && pop) {
    input.addEventListener("input", async () => {
      await loadIndex();
      const r = search(input.value).slice(0, 10);
      pop.innerHTML = r.length ? r.map(item).join("") : (input.value.trim() ? `<p class="c" style="padding:.5rem">No matches.</p>` : "");
      pop.hidden = !input.value.trim();
    });
    input.addEventListener("keydown", (e) => { if (e.key === "Escape") { pop.hidden = true; input.blur(); } });
    document.addEventListener("click", (e) => { if (!e.target.closest(".search")) pop.hidden = true; });
  }
  const results = document.querySelector("#search-results");
  if (results) {
    const q = new URLSearchParams(location.search).get("q") || "";
    if (input) input.value = q;
    loadIndex().then(() => {
      const r = search(q);
      results.innerHTML = `<p class="lede">${r.length} result${r.length === 1 ? "" : "s"} for “${esc(q)}”.</p><div class="search-pop" style="position:static;width:auto;max-height:none;box-shadow:none">${r.map(item).join("")}</div>`;
    });
  }

  // ---- TOC tracking
  const tocLinks = [...document.querySelectorAll(".chapter-toc a[href^='#']")];
  if (tocLinks.length && "IntersectionObserver" in window) {
    const map = new Map(tocLinks.map((a) => [a.getAttribute("href").slice(1), a]));
    const obs = new IntersectionObserver((ents) => {
      for (const e of ents) if (e.isIntersecting) { tocLinks.forEach((a) => a.classList.remove("active")); map.get(e.target.id)?.classList.add("active"); }
    }, { rootMargin: "0px 0px -70% 0px" });
    map.forEach((_, id) => { const el = document.getElementById(id); if (el) obs.observe(el); });
  }

  // ---- results index filter
  document.querySelectorAll(".filter button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".filter button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    const f = b.dataset.filter;
    document.querySelectorAll(".index-table tbody tr").forEach((tr) => { tr.hidden = f !== "all" && tr.dataset.kind !== f; });
  }));

  // ---- laboratory widgets
  const demos = document.querySelectorAll(".demo[data-demo]");
  if (demos.length) {
    import(new URL(rel + "assets/js/lab.js", location.href).href).then((lab) => demos.forEach((el) => lab.mount(el))).catch((e) => {
      demos.forEach((el) => { const p = document.createElement("p"); p.className = "lab-note"; p.textContent = "The interactive laboratory could not be loaded (" + e.message + "). The text description above remains authoritative."; el.appendChild(p); });
    });
  }
})();
