---
title: Reproducing This Book
status: definition
noexercises: true
description: How to rerun every experiment, test, example and build step, and what reproducibility means for each.
---

## What is reproducible, and how exactly {#sec:what}

| Artifact | Command (from the repository root) | Reproducibility |
|---|---|---|
| theorem checks (small-case exhaustive) | `python3 experiments/check_theorems.py` | exact |
| research experiments EXP-001 … EXP-010 | `sh experiments/run_all.sh` | counted steps bit-for-bit; wall-clock fields vary |
| comparison with committed results | `python3 experiments/verify_reproduction.py` | exits non-zero if any counted field differs |
| SDK test suite | `cd sdk && python3 -m unittest discover -s tests` | exact |
| book examples | `python3 book/tools/check_examples.py` | every printed output must match exactly |
| laboratory–SDK agreement | `cd book && npm test` | exact (floating point to $10^{-14}$) |
| site build with integrity checks | `cd book && npm install && npm run build` | deterministic HTML; fails on any integrity error |
| print edition (PDF) | `cd book && npm run pdf` | generated from the same sources via headless Chromium |

Requirements: Python 3.10 or later (standard library only) and, for the book build, Node.js 18 or later with the pinned packages of `book/package.json`. All random inputs are generated from fixed seeds.

## What reproducibility does not cover {#sec:repro-not}

Wall-clock times depend on the machine and are reported as secondary data only. The book's arguments rest on counted steps under stated cost models, which are machine-independent. The environment in which the recorded results were produced is listed in `REPRODUCIBILITY_REPORT.md` in the repository, together with the outcome of each command.
