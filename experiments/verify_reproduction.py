"""Compare freshly generated results/*.json with a reference copy (default: the
committed version from git HEAD), ignoring wall-clock fields.  Exit code 0 iff
every counted (deterministic) field is identical.

Usage:  python3 experiments/verify_reproduction.py [git-ref]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
WALL = ("_s", "s_per_q", "breakeven_Q_wall")  # wall-clock fields


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items()
                if k != "env" and not any(k.endswith(s) for s in WALL)}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    bad = 0
    for f in sorted(os.listdir(R)):
        if not f.endswith(".json"):
            continue
        try:
            old = subprocess.run(["git", "show", f"{ref}:experiments/results/{f}"],
                                 capture_output=True, text=True, check=True).stdout
        except subprocess.CalledProcessError:
            print(f"{f}: no reference at {ref} (new file)"); continue
        a, b = strip(json.loads(old)), strip(json.load(open(os.path.join(R, f))))
        same = a == b
        bad += not same
        print(f"{f}: {'identical counted fields' if same else 'DIFFERS'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
