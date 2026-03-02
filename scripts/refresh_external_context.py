#!/usr/bin/env python3
"""Refresh external Cortical Labs context used by this skill."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen


CL_API_DOC_REPO = "https://github.com/Cortical-Labs/cl-api-doc.git"
CL_SDK_REPO = "https://github.com/Cortical-Labs/cl-sdk.git"
WHITEPAPER_DOI = "https://doi.org/10.48550/arXiv.2602.11632"
ARXIV_ABS = "https://arxiv.org/abs/2602.11632"
ARXIV_PDF = "https://arxiv.org/pdf/2602.11632.pdf"


def run(cmd: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr}")
    return proc.stdout.strip()


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "codex-corticallabs-context-refresh/1.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_bytes(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "codex-corticallabs-context-refresh/1.0"})
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def clone_or_pull(repo_url: str, target: Path) -> str:
    if (target / ".git").exists():
        run(["git", "fetch", "--depth=1", "origin"], cwd=target)
        run(["git", "reset", "--hard", "origin/HEAD"], cwd=target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth=1", repo_url, str(target)])
    return run(["git", "rev-parse", "HEAD"], cwd=target)


def parse_arxiv_abs(html: str) -> tuple[str, str, str, str]:
    def extract(pattern: str) -> str:
        m = re.search(pattern, html, re.S)
        if not m:
            return ""
        txt = re.sub("<[^>]+>", " ", m.group(1))
        txt = re.sub(r"\s+", " ", txt).strip()
        return unescape(txt)

    title = extract(r'<h1 class="title mathjax">\s*<span[^>]*>Title:</span>\s*(.*?)\s*</h1>')
    abstract = extract(r'<blockquote class="abstract mathjax">\s*<span[^>]*>Abstract:</span>\s*(.*?)\s*</blockquote>')
    authors = extract(r'<div class="authors">\s*<span[^>]*>Authors:</span>\s*(.*?)\s*</div>')
    subject = extract(r'<span class="primary-subject">(.*?)</span>')
    return title, authors, subject, abstract


def build_notebook_index(cl_api_doc: Path, out_file: Path) -> None:
    import json as _json

    lines = [
        "# cl-api-doc Notebook Index",
        "",
        f"Source: `{cl_api_doc}`",
        "",
    ]
    for nb in sorted(cl_api_doc.glob("CL-*.ipynb")):
        data = _json.loads(nb.read_text(encoding="utf-8"))
        md, code = [], []
        for cell in data.get("cells", []):
            src = "".join(cell.get("source", [])).strip()
            if not src:
                continue
            one_line = src.replace("\n", " ")[:220]
            if cell.get("cell_type") == "markdown" and len(md) < 2:
                md.append(one_line)
            if cell.get("cell_type") == "code" and len(code) < 2:
                code.append(one_line)

        lines.append(f"## {nb.name}")
        if md:
            lines.append(f"- Notebook focus: {md[0]}")
        if len(md) > 1:
            lines.append(f"- Additional note: {md[1]}")
        for idx, snippet in enumerate(code, 1):
            lines.append(f"- Example code {idx}: `{snippet}`")
        lines.append("")

    out_file.write_text("\n".join(lines), encoding="utf-8")


def try_extract_pdf_text(pdf_path: Path, out_file: Path, skill_root: Path) -> bool:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        # Fallback to a local tools venv if available.
        venv_python = skill_root / ".venv-tools" / "bin" / "python"
        if not venv_python.exists():
            return False
        proc = subprocess.run(
            [
                str(venv_python),
                "-c",
                (
                    "from pypdf import PdfReader\n"
                    "from pathlib import Path\n"
                    f"pdf=Path(r'''{pdf_path}''')\n"
                    f"out=Path(r'''{out_file}''')\n"
                    "reader=PdfReader(str(pdf))\n"
                    "parts=[]\n"
                    "for i,p in enumerate(reader.pages,1):\n"
                    "  parts.append(f'\\n\\n===== PAGE {i} =====\\n\\n{(p.extract_text() or '').strip()}')\n"
                    "out.write_text(''.join(parts),encoding='utf-8')\n"
                ),
            ],
            text=True,
            capture_output=True,
        )
        return proc.returncode == 0

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for idx, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        pages.append(f"\n\n===== PAGE {idx} =====\n\n{text}")
    out_file.write_text("".join(pages), encoding="utf-8")
    return True


def read_sdk_version(pyproject_path: Path) -> str:
    pyproject = pyproject_path.read_text(encoding="utf-8")
    m = re.search(r'^\s*version\s*=\s*"([^"]+)"', pyproject, re.M)
    return m.group(1) if m else "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Path to the skill root directory.",
    )
    args = parser.parse_args()

    skill_root = Path(args.skill_root).resolve()
    refs = skill_root / "references" / "external"
    refs.mkdir(parents=True, exist_ok=True)

    cl_api_doc_dir = refs / "cl-api-doc"
    cl_sdk_dir = refs / "cl-sdk"
    whitepaper_dir = refs / "whitepaper"
    whitepaper_dir.mkdir(parents=True, exist_ok=True)

    cl_api_doc_sha = clone_or_pull(CL_API_DOC_REPO, cl_api_doc_dir)
    cl_sdk_sha = clone_or_pull(CL_SDK_REPO, cl_sdk_dir)

    doi_head = fetch_text(WHITEPAPER_DOI)
    arxiv_abs_html = fetch_text(ARXIV_ABS)
    arxiv_pdf_bytes = fetch_bytes(ARXIV_PDF)

    (whitepaper_dir / "doi-head.txt").write_text(doi_head, encoding="utf-8")
    (whitepaper_dir / "arxiv-abs.html").write_text(arxiv_abs_html, encoding="utf-8")
    pdf_path = whitepaper_dir / "arxiv-2602.11632.pdf"
    pdf_path.write_bytes(arxiv_pdf_bytes)

    title, authors, subject, abstract = parse_arxiv_abs(arxiv_abs_html)
    (whitepaper_dir / "whitepaper-abstract.txt").write_text(
        f"Title: {title}\nAuthors: {authors}\nPrimary subject: {subject}\n\nAbstract:\n{abstract}\n",
        encoding="utf-8",
    )

    fulltext_path = whitepaper_dir / "whitepaper-fulltext.txt"
    fulltext_extracted = try_extract_pdf_text(pdf_path, fulltext_path, skill_root)

    build_notebook_index(cl_api_doc_dir, refs / "cl-api-doc-index.md")

    run(
        [
            sys.executable,
            str(skill_root / "scripts" / "extract_sdk_signatures.py"),
            "--sdk-root",
            str(cl_sdk_dir),
            "--out",
            str(refs / "sdk-signatures.md"),
        ]
    )

    lock = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": {
            "docs_site": "https://docs.corticallabs.com/",
            "cl_api_doc_repo": {"url": CL_API_DOC_REPO, "commit": cl_api_doc_sha},
            "cl_sdk_repo": {
                "url": CL_SDK_REPO,
                "commit": cl_sdk_sha,
                "version": read_sdk_version(cl_sdk_dir / "pyproject.toml"),
            },
            "whitepaper": {
                "doi_url": WHITEPAPER_DOI,
                "arxiv_abs": ARXIV_ABS,
                "arxiv_pdf": ARXIV_PDF,
                "fulltext_extracted": fulltext_extracted,
            },
        },
    }
    (refs / "source-lock.json").write_text(json.dumps(lock, indent=2), encoding="utf-8")

    print("Refreshed external context.")
    print(f"cl-api-doc: {cl_api_doc_sha}")
    print(f"cl-sdk: {cl_sdk_sha}")
    print(f"whitepaper fulltext extracted: {fulltext_extracted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
