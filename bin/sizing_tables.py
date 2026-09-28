#!/usr/bin/env python3
"""Generate the operations-update tables from tagged lsst/rubin-sizing-model.

    python bin/sizing_tables.py              # every model in sizing-models.toml
    python bin/sizing_tables.py --check      # exit 1 if committed tables are stale
    python bin/sizing_tables.py --only NAME --local PATH   # untagged working copy

For each model: fetch the pinned tag, run its generate_model.py --emit-tex,
then check that the output is stamped with that tag, that every table and
macro the document uses exists, and that no two models define the same name.
Output replaces the model's directory only if all checks pass.

Needs git, uv and Python 3.11+.
"""

from __future__ import annotations

import argparse
import filecmp
import glob
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    sys.exit(f"ERROR: {message}")


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def fetch(model: dict, dest: Path) -> None:
    """Shallow checkout of the pinned tag."""
    run(["git", "init", "--quiet", str(dest)])
    run(["git", "-C", str(dest), "fetch", "--quiet", "--depth", "1", model["repo"],
         f"refs/tags/{model['ref']}:refs/tags/{model['ref']}"])
    run(["git", "-C", str(dest), "-c", "advice.detachedHead=false",
         "checkout", "--quiet", model["ref"]])


def generate(model: dict, checkout: Path, output: Path) -> None:
    output.mkdir(parents=True)
    run(["uv", "run", "--quiet", "--project", str(checkout), "python",
         str(checkout / "generate_model.py"),
         "--params", str(checkout / model["params"]),
         "--output", str(output.parent / "model.xlsx"),
         "--emit-tex", str(output)], cwd=checkout)


def produced(output: Path, prefix: str) -> tuple[str, set, set, set]:
    ref, macros, labels, tables = "", set(), set(), set()
    for path in output.glob("*.tex"):
        text = path.read_text(encoding="utf-8")
        ref = ref or next(iter(re.findall(r"@ (\S+)\. Do not edit", text)), "")
        macros |= set(re.findall(rf"\\newcommand\{{\\({prefix}[A-Z][A-Za-z]*)\}}", text))
        labels |= set(re.findall(r"\\label\{(tab:[^}]+)\}", text))
        tables.add(path.stem)
    return ref, macros, labels, tables


def used(model: dict) -> tuple[set, set]:
    prefix, out = model["macro_prefix"], model["output"].rstrip("/")
    macros, tables = set(), set()
    for pattern in model["consumers"]:
        for name in glob.glob(str(ROOT / pattern)):
            text = re.sub(r"(?<!\\)%.*", "", Path(name).read_text(encoding="utf-8"))
            macros |= set(re.findall(rf"\\({prefix}[A-Z][A-Za-z]*)", text))
            tables |= set(re.findall(rf"\\input\{{{re.escape(out)}/([^}}]+)\}}", text))
    return macros, tables


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, default=ROOT / "sizing-models.toml")
    parser.add_argument("--only", help="only the model with this name")
    parser.add_argument("--local", type=Path, help="use this working copy, not the tag")
    parser.add_argument("--check", action="store_true",
                        help="compare with the committed tables; change nothing")
    args = parser.parse_args()

    models = tomllib.loads(args.config.read_text(encoding="utf-8"))["model"]
    if args.only:
        models = [m for m in models if m["name"] == args.only] or fail(
            f"no model named '{args.only}'")
    if args.local and len(models) != 1:
        fail("--local needs exactly one model: add --only NAME")

    owners: dict[str, str] = {}
    stale = []
    with tempfile.TemporaryDirectory() as tmp:
        for model in models:
            name, prefix = model["name"], model["macro_prefix"]
            if not re.fullmatch(r"[A-Za-z]+", prefix):
                fail(f"{name}: macro_prefix must be letters only")
            print(f"{name}: {model['repo']} @ {model['ref']}"
                  + (f" (local copy {args.local})" if args.local else ""))

            checkout = args.local.resolve() if args.local else Path(tmp) / name / "src"
            if not args.local:
                fetch(model, checkout)
            output = Path(tmp) / name / "tables"
            generate(model, checkout, output)

            ref, macros, labels, tables = produced(output, prefix)
            if not args.local and ref != model["ref"]:
                fail(f"{name}: output stamped '{ref}', expected '{model['ref']}'")
            need_macros, need_tables = used(model)
            missing = sorted(need_tables - tables) + sorted(need_macros - macros)
            if missing:
                fail(f"{name} @ {ref} does not produce: {', '.join(missing)}. "
                     f"Tag a model version that does and update `ref`.")
            for item in macros | labels:
                if item in owners:
                    fail(f"'{item}' is produced by both {owners[item]} and {name}")
                owners[item] = name

            committed = ROOT / model["output"]
            if args.check:
                diff = filecmp.dircmp(committed, output)
                changed = diff.diff_files + diff.left_only + diff.right_only
                if changed:
                    stale.append(f"{name}: {', '.join(sorted(changed))}")
            else:
                shutil.rmtree(committed, ignore_errors=True)
                shutil.copytree(output, committed)
            print(f"  ok: {len(tables)} files, {len(macros)} macros, stamped {ref}")

    for line in stale:
        print(f"STALE {line}. Run `make sizing-tables` and commit.")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
