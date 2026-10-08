// Apply the reader's saved theme before first paint (loaded synchronously in <head>;
// external rather than inline so the site can run under a strict CSP).
try { const t = localStorage.getItem("cgt-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) { /* storage unavailable */ }
