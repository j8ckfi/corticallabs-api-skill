#!/usr/bin/env python3
"""Extract public class/function signatures from cl-sdk source files."""

from __future__ import annotations

import ast
import argparse
from pathlib import Path


TARGET_MODULES = [
    "src/cl/__init__.py",
    "src/cl/neurons.py",
    "src/cl/recording.py",
    "src/cl/data_stream.py",
    "src/cl/_stim_plan.py",
    "src/cl/util/recording_view.py",
    "src/cl/app/base.py",
    "src/cl/app/model/model.py",
    "src/cl/analysis/__init__.py",
    "src/cl/visualisation/visualisation.py",
    "src/cl/visualisation/jupyter.py",
]


def ann_to_str(node: ast.AST | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node)


def arg_to_str(arg: ast.arg, default: ast.expr | None = None) -> str:
    a = arg.arg
    ann = ann_to_str(arg.annotation)
    if ann:
        a += f": {ann}"
    if default is not None:
        a += f" = {ast.unparse(default)}"
    return a


def format_signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = fn.args
    parts: list[str] = []

    posonly = args.posonlyargs
    reg = args.args
    defaults = [None] * (len(posonly) + len(reg) - len(args.defaults)) + list(args.defaults)
    all_pos = posonly + reg

    for idx, arg in enumerate(all_pos):
        parts.append(arg_to_str(arg, defaults[idx]))
        if idx == len(posonly) - 1 and posonly:
            parts.append("/")

    if args.vararg:
        parts.append("*" + arg_to_str(args.vararg))
    elif args.kwonlyargs:
        parts.append("*")

    for kwarg, kwdefault in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(arg_to_str(kwarg, kwdefault))

    if args.kwarg:
        parts.append("**" + arg_to_str(args.kwarg))

    returns = ann_to_str(fn.returns)
    sig = f"{fn.name}({', '.join(parts)})"
    if returns:
        sig += f" -> {returns}"
    return sig


def first_doc_line(node: ast.AST) -> str:
    doc = ast.get_docstring(node) or ""
    doc = doc.strip()
    if not doc:
        return ""
    return doc.splitlines()[0].strip()


def is_public(name: str) -> bool:
    return not name.startswith("_")


def render_module(module_path: Path, root: Path) -> str:
    rel = module_path.relative_to(root)
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    out: list[str] = []
    out.append(f"## {rel}")
    out.append("")

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(node.name):
            out.append(f"- `def {format_signature(node)}`")
            doc = first_doc_line(node)
            if doc:
                out.append(f"  - {doc}")
        elif isinstance(node, ast.ClassDef) and is_public(node.name):
            out.append(f"- `class {node.name}`")
            cdoc = first_doc_line(node)
            if cdoc:
                out.append(f"  - {cdoc}")
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(child.name):
                    out.append(f"  - `def {format_signature(child)}`")
                    doc = first_doc_line(child)
                    if doc:
                        out.append(f"    - {doc}")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", required=True, help="Path to cloned cl-sdk repo root.")
    parser.add_argument("--out", required=True, help="Output markdown path.")
    args = parser.parse_args()

    root = Path(args.sdk_root).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# cl-sdk Public Signatures")
    lines.append("")
    lines.append(f"Source root: `{root}`")
    lines.append("")

    missing: list[str] = []
    for rel in TARGET_MODULES:
        module_path = root / rel
        if not module_path.exists():
            missing.append(rel)
            continue
        lines.append(render_module(module_path, root))

    if missing:
        lines.append("## Missing modules")
        lines.append("")
        for rel in missing:
            lines.append(f"- `{rel}`")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
