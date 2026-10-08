"""Execute every ```python run``` block in the book and compare its stdout
with the ```output``` block that immediately follows it.

Each block runs in a fresh interpreter with the SDK on the path
(PYTHONPATH=sdk/src), so examples cannot depend on each other.  Exit status
is non-zero if any block fails or any output differs; the book must not show
output that its code does not produce.

Usage:  python3 book/tools/check_examples.py [chapter-slug ...]
        python3 book/tools/check_examples.py --write slug   (authoring aid: fill
        the output blocks of one chapter from actual execution; the author must
        then re-read the surrounding prose against the real output)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
REPO = os.path.dirname(BOOK)
CH = os.path.join(BOOK, "content", "chapters")
BLOCK = re.compile(r"```python run\n(.*?)```\s*\n```output\n(.*?)```", re.S)


def write(slug):
    env = dict(os.environ, PYTHONPATH=os.path.join(REPO, "sdk", "src"), PYTHONHASHSEED="0")
    path = os.path.join(CH, slug + ".md")
    src = open(path, encoding="utf8").read()

    def fill(m):
        p = subprocess.run([sys.executable, "-c", m.group(1)], capture_output=True, text=True, env=env, timeout=300)
        if p.returncode:
            raise SystemExit(f"block failed:\n{m.group(1)}\n{p.stderr}")
        return f"```python run\n{m.group(1)}```\n\n```output\n{p.stdout.rstrip()}\n```"
    src = re.sub(r"```python run\n(.*?)```\s*\n```output\n(.*?)```", fill, src, flags=re.S)
    open(path, "w", encoding="utf8").write(src)
    print(f"filled outputs in {slug}")
    return 0


def main(only=()):
    env = dict(os.environ, PYTHONPATH=os.path.join(REPO, "sdk", "src"), PYTHONHASHSEED="0")
    total = failed = 0
    for f in sorted(os.listdir(CH)):
        slug = f[:-3]
        if only and slug not in only:
            continue
        src = open(os.path.join(CH, f), encoding="utf8").read()
        runs = src.count("```python run")
        blocks = BLOCK.findall(src)
        if runs != len(blocks):
            print(f"FAIL {slug}: {runs} run blocks but {len(blocks)} have an output block right after")
            failed += 1
        for i, (code, expected) in enumerate(blocks, 1):
            total += 1
            p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=300)
            got = p.stdout.rstrip()
            if p.returncode != 0 or got != expected.rstrip():
                failed += 1
                print(f"FAIL {slug} block {i} (exit {p.returncode})")
                print("--- expected ---\n" + expected.rstrip() + "\n--- got ---\n" + got + ("\n--- stderr ---\n" + p.stderr if p.stderr else ""))
    print(f"{total - failed + (0)}/{total} examples reproduce their printed output" if not failed else f"{failed} failure(s) in {total} examples")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--write":
        sys.exit(write(sys.argv[2]))
    sys.exit(main(sys.argv[1:]))
