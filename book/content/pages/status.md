# Publication status

This page summarizes what has and has not been verified about this publication. It is maintained by hand from the repository's `PUBLICATION_STATUS.md` at each release.

- **Peer review:** none. The book is a working research manuscript.
- **Proofs:** results marked <span class="status status-proved-here">Proved here</span> are self-checked and, where stated, checked exhaustively on small instances by `experiments/check_theorems.py` and the SDK tests. None has been independently reviewed.
- **Novelty:** most results proved here are elementary and several are probably folklore; each statement says what is known about its relationship to prior work. Candidate contributions are listed in the [provenance record](ledger/provenance.html).
- **Citations:** each bibliography entry states whether its metadata was verified against an authoritative record, found only in secondary sources, or not verified. Verification of metadata does not mean the full text was read.
- **Experiments:** all experiments are deterministic and reproducible with `sh experiments/run_all.sh`; counted steps reproduce bit-for-bit, wall-clock times do not.
- **Code examples:** every executable example in the book is run by `book/tools/check_examples.py` during verification, and its printed output must match.
- **Interactive laboratory:** every widget computes its numbers live with `cgt-core.js`, whose functions are tested against fixtures exported from the Python SDK.

Remaining limitations are listed in `PUBLICATION_AUDIT.md` and `PUBLICATION_STATUS.md` in the repository.
