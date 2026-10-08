#!/usr/bin/env sh
# Reproduce every experiment and regenerate results/SUMMARY.md.
# Requirements: Python >= 3.10, standard library only.  Deterministic seeds.
set -e
cd "$(dirname "$0")"
python3 check_theorems.py
for e in exp001_binary_tree exp002_reachability exp003_constrained \
         exp004_forest_dag exp005_dynamic exp006_solution_grammar exp007_grammar_shape; do
  echo "== $e"; python3 "$e.py"
done
python3 analyze.py > /dev/null
echo "wrote results/SUMMARY.md"
