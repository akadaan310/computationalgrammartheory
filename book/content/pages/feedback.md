# Report an erratum or an independent check

<p class="lede">This book is an unreviewed research manuscript, and its most valuable readers are the ones who find its mistakes. Nothing here requires an account. Submissions go to the researcher's review queue and are not published automatically.</p>

<div class="feedback-unavailable" data-feedback-unavailable hidden><p><strong>The submission service is not available on this copy of the book</strong> (it may be disabled, unreachable, or JavaScript may be off). Please open an issue on the <a href="https://github.com/akadaan310/computationalgrammartheory/issues">repository</a> instead, naming the page and the section.</p></div>

<noscript><p class="feedback-unavailable"><strong>These forms need JavaScript.</strong> Please open an issue on the <a href="https://github.com/akadaan310/computationalgrammartheory/issues">repository</a> instead, naming the page and the section.</p></noscript>

## Report an erratum {#sec:fb-erratum}

Mathematical errors, unclear passages, wrong or missing citations and gaps in proofs are all welcome. Every confirmed erratum is corrected in the open and listed in the errata table of the [results ledger](ledger/results.html), with credit if you wish.

<form class="feedback-form" data-feedback="errata_reports" novalidate>
<div class="ff-row"><label for="er-page">Page</label><input id="er-page" name="page" required maxlength="300" placeholder="e.g. chapters/13-compilation.html"></div>
<div class="ff-row"><label for="er-anchor">Section, theorem or equation <span class="ff-opt">(optional)</span></label><input id="er-anchor" name="anchor" maxlength="200" placeholder="e.g. Theorem 13.2, proof, step 3"></div>
<div class="ff-row"><label for="er-kind">Kind</label><select id="er-kind" name="kind" required><option value="erratum">Error (mathematics, code, numbers)</option><option value="proof-gap">Gap in a proof</option><option value="citation">Citation or attribution</option><option value="unclear">Unclear passage</option><option value="other">Other</option></select></div>
<div class="ff-row"><label for="er-message">What is wrong, and what should it say?</label><textarea id="er-message" name="message" required minlength="10" maxlength="4000" rows="6"></textarea></div>
<div class="ff-row"><label for="er-contact">Contact for follow-up <span class="ff-opt">(optional, never published)</span></label><input id="er-contact" name="contact" maxlength="200" autocomplete="email"></div>
<div class="ff-hp" aria-hidden="true"><label for="er-website">Leave this empty</label><input id="er-website" name="website" tabindex="-1" autocomplete="off"></div>
<div class="ff-actions"><button type="submit">Submit erratum</button><p class="ff-status" role="status" aria-live="polite"></p></div>
</form>

## Record an independent check {#sec:fb-check}

Did you rerun an experiment, the SDK tests or the book's examples on your own machine, or check a proof marked *proved here* line by line? Record the outcome, **whether it confirmed the result or not**: disagreements are the most useful reports. Once reviewed, checks are listed on the [publication status](status.html) page. Instructions for reproducing everything are in [Appendix B](chapters/b-reproducibility.html).

<form class="feedback-form" data-feedback="independent_checks" novalidate>
<div class="ff-row"><label for="ic-kind">Kind of check</label><select id="ic-kind" name="check_kind" required><option value="reproduction">Reproduction (experiments, tests, examples)</option><option value="proof-check">Proof check</option></select></div>
<div class="ff-row"><label for="ic-subject">What did you check?</label><input id="ic-subject" name="subject" required list="ic-subjects" pattern="^(CGT-[A-Z]+-[0-9]+[a-z]?|run_all|sdk_tests|examples|laboratory)$" placeholder="CGT-THM-006, CGT-EXP-009, run_all, sdk_tests, examples, laboratory"><datalist id="ic-subjects"><option value="run_all"><option value="sdk_tests"><option value="examples"><option value="laboratory"><option value="CGT-THM-006"><option value="CGT-THM-007"><option value="CGT-THM-008"><option value="CGT-THM-002"><option value="CGT-PROP-005"><option value="CGT-PROP-010"></datalist></div>
<div class="ff-row"><label for="ic-outcome">Outcome</label><select id="ic-outcome" name="outcome" required><option value="confirmed">Confirmed</option><option value="differs">Results differ</option><option value="issue-found">Issue found in the proof</option><option value="failed">Could not run or complete</option></select></div>
<div class="ff-row"><label for="ic-env">Environment <span class="ff-opt">(optional)</span></label><input id="ic-env" name="environment" maxlength="500" placeholder="e.g. Python 3.12, macOS 15, Apple M2"></div>
<div class="ff-row"><label for="ic-fp">Experiment fingerprint <span class="ff-opt">(optional, hex)</span></label><input id="ic-fp" name="fingerprint" pattern="^[0-9a-f]{8,64}$" maxlength="64"></div>
<div class="ff-row"><label for="ic-details">Details</label><textarea id="ic-details" name="details" required minlength="10" maxlength="4000" rows="6" placeholder="Commands run, what matched, what did not, which step of the proof"></textarea></div>
<div class="ff-row"><label for="ic-name">Name to credit <span class="ff-opt">(optional, published with the check)</span></label><input id="ic-name" name="checker_name" maxlength="120"></div>
<div class="ff-hp" aria-hidden="true"><label for="ic-website">Leave this empty</label><input id="ic-website" name="website" tabindex="-1" autocomplete="off"></div>
<div class="ff-actions"><button type="submit">Record check</button><p class="ff-status" role="status" aria-live="polite"></p></div>
</form>

## Privacy {#sec:fb-privacy}

The database stores only what you type into these forms, with a timestamp and the book edition. The book sets no cookie and uses no analytics or account. Like any web service, the hosting infrastructure (Supabase) keeps short-lived request logs, which include IP addresses; this site does not use them. An erratum's contact field is visible only to the researcher. A check's details and the name you choose to credit are published only after review. The service runs on Supabase. Its access rules, in `supabase/migrations/` in the repository, allow the public to submit and to read reviewed checks, and nothing else.
