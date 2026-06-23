#!/usr/bin/env python3
"""Print a readable view of a Jupyter notebook.

Usage:
    python scripts/read_notebook.py v2-matrix-kvs.ipynb
    python scripts/read_notebook.py v2-matrix-kvs.ipynb --outputs
    python scripts/read_notebook.py v2-matrix-kvs.ipynb --cell 3
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "".join(str(x) for x in value)
    return str(value)


def print_source(cell: dict[str, Any], index: int, max_lines: int | None) -> None:
    kind = cell.get("cell_type", "unknown")
    print(f"\n--- cell {index} {kind} ---")
    source = as_text(cell.get("source", ""))
    lines = source.splitlines()
    shown = lines if max_lines is None else lines[:max_lines]
    for line_no, line in enumerate(shown, start=1):
        print(f"{line_no:03}: {line}")
    if max_lines is not None and len(lines) > max_lines:
        print(f"... ({len(lines) - max_lines} more source lines)")


def print_outputs(cell: dict[str, Any], index: int, max_chars: int | None) -> None:
    outputs = cell.get("outputs", [])
    if not outputs:
        return

    print(f"\n--- cell {index} outputs ({len(outputs)}) ---")
    for output_index, output in enumerate(outputs):
        print(f"\n[output {output_index}] {output.get('output_type', 'unknown')}")

        if "ename" in output:
            print(f"{output.get('ename')}: {output.get('evalue')}")
            text = "\n".join(output.get("traceback", []))
        elif "text" in output:
            text = as_text(output.get("text"))
        elif "data" in output:
            data = output.get("data", {})
            text = as_text(data.get("text/plain", data))
        else:
            text = str(output)

        if max_chars is not None and len(text) > max_chars:
            print(text[-max_chars:])
            print(f"... (truncated to last {max_chars} chars)")
        else:
            print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read a Jupyter notebook as plain text.")
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--outputs", action="store_true", help="Print cell outputs too.")
    parser.add_argument("--only-outputs", action="store_true", help="Print outputs without source.")
    parser.add_argument("--cell", type=int, help="Only print one cell by zero-based index.")
    parser.add_argument("--max-lines", type=int, default=160, help="Max source lines per cell. Use 0 for unlimited.")
    parser.add_argument("--max-output-chars", type=int, default=5000, help="Max output chars per output. Use 0 for unlimited.")
    args = parser.parse_args()

    max_lines = None if args.max_lines == 0 else args.max_lines
    max_output_chars = None if args.max_output_chars == 0 else args.max_output_chars

    notebook = json.loads(args.notebook.read_text())
    cells = notebook.get("cells", [])

    indexes = [args.cell] if args.cell is not None else range(len(cells))
    for index in indexes:
        cell = cells[index]
        if not args.only_outputs:
            print_source(cell, index, max_lines)
        if args.outputs or args.only_outputs:
            print_outputs(cell, index, max_output_chars)


if __name__ == "__main__":
    main()
