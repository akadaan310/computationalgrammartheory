#!/usr/bin/env sh
# Reproduce every experiment and regenerate results/SUMMARY.md.
# Requirements: Python >= 3.10, standard library only.  Deterministic seeds.
# EXP-008..010 use the SDK in ../sdk/src (no installation needed).
set -e
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/../sdk/src:$(pwd)${PYTHONPATH:+:$PYTHONPATH}"
python3 check_theorems.py
for e in exp001_binary_tree exp002_reachability exp003_constrained \
         exp004_forest_dag exp005_dynamic exp006_solution_grammar exp007_grammar_shape \
         exp008_compiled_words exp009_pagerank exp010_constrained_ranking; do
  echo "== $e"; python3 "$e.py"
done
python3 analyze.py > /dev/null
echo "wrote results/SUMMARY.md"
