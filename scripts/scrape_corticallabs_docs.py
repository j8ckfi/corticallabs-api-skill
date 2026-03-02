#!/usr/bin/env python3
"""Recursively scrape https://docs.corticallabs.com pages into local references."""

from __future__ import annotations

import argparse
import json
import queue
import re
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


BASE_URL = "https://docs.corticallabs.com/"
ALLOWED_HOST = "docs.corticallabs.com"


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.links.append(value)


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self._out: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = False
        if tag in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "br"}:
            self._out.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = data.strip()
        if text:
            self._out.append(text)

    def text(self) -> str:
        joined = " ".join(self._out)
        joined = re.sub(r"\s+\n", "\n", joined)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        return joined.strip() + "\n"


@dataclass
class PageResult:
    url: str
    status: int
    html_path: str | None
    text_path: str | None
    error: str | None
    fetched_at: str


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = "https"
    netloc = parsed.netloc or ALLOWED_HOST
    path = parsed.path or "/"
    path = re.sub(r"/{2,}", "/", path)
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunparse((scheme, netloc, path, "", "", ""))


def is_allowed(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if parsed.netloc and parsed.netloc != ALLOWED_HOST:
        return False
    path = parsed.path or "/"
    blocked_ext = (
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".css",
        ".js",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp4",
        ".mp3",
    )
    return not path.lower().endswith(blocked_ext)


def url_to_rel_path(url: str, suffix: str) -> Path:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path == "/":
        return Path(f"index{suffix}")
    if path.endswith(".html"):
        return Path(path.lstrip("/")).with_suffix(suffix)
    if "." not in Path(path).name:
        return Path(path.lstrip("/") + suffix)
    return Path(path.lstrip("/")).with_suffix(suffix)


def fetch(url: str, timeout: float) -> tuple[int, str, str]:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; codex-corticallabs-docs-scraper/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", 200)
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    return status, body.decode("utf-8", errors="replace"), ctype


def extract_links(base_url: str, html: str) -> Iterable[str]:
    parser = LinkExtractor()
    parser.feed(html)
    for href in parser.links:
        abs_url = urljoin(base_url, href)
        parsed = urlparse(abs_url)
        if parsed.fragment:
            abs_url = abs_url.split("#", 1)[0]
        if parsed.query:
            abs_url = abs_url.split("?", 1)[0]
        if is_allowed(abs_url):
            yield normalize_url(abs_url)


def html_to_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return parser.text()


def scrape(max_pages: int, timeout: float, out_dir: Path) -> list[PageResult]:
    html_root = out_dir / "upstream-html"
    text_root = out_dir / "upstream-text"
    html_root.mkdir(parents=True, exist_ok=True)
    text_root.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    q: queue.SimpleQueue[str] = queue.SimpleQueue()
    q.put(normalize_url(BASE_URL))
    results: list[PageResult] = []

    while not q.empty() and len(seen) < max_pages:
        url = q.get()
        if url in seen:
            continue
        seen.add(url)
        fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        try:
            status, html, ctype = fetch(url, timeout=timeout)
            if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
                results.append(
                    PageResult(
                        url=url,
                        status=status,
                        html_path=None,
                        text_path=None,
                        error=f"Skipped non-HTML content-type: {ctype}",
                        fetched_at=fetched_at,
                    )
                )
                continue

            html_path = html_root / url_to_rel_path(url, ".html")
            text_path = text_root / url_to_rel_path(url, ".txt")
            html_path.parent.mkdir(parents=True, exist_ok=True)
            text_path.parent.mkdir(parents=True, exist_ok=True)
            html_path.write_text(html, encoding="utf-8")
            text_path.write_text(html_to_text(html), encoding="utf-8")

            for link in extract_links(url, html):
                if link not in seen:
                    q.put(link)

            results.append(
                PageResult(
                    url=url,
                    status=status,
                    html_path=str(html_path.relative_to(out_dir)),
                    text_path=str(text_path.relative_to(out_dir)),
                    error=None,
                    fetched_at=fetched_at,
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                PageResult(
                    url=url,
                    status=0,
                    html_path=None,
                    text_path=None,
                    error=str(exc),
                    fetched_at=fetched_at,
                )
            )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[1] / "references"),
        help="Destination directory for scrape output.",
    )
    parser.add_argument("--max-pages", type=int, default=1500, help="Maximum pages to crawl.")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    results = scrape(max_pages=args.max_pages, timeout=args.timeout, out_dir=out_dir)
    manifest_path = out_dir / "scrape-manifest.json"
    manifest = {
        "base_url": BASE_URL,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "max_pages": args.max_pages,
        "count": len(results),
        "results": [r.__dict__ for r in results],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    ok = sum(1 for r in results if r.status == 200 and not r.error)
    failures = sum(1 for r in results if r.error or r.status == 0)
    print(f"Scrape complete. total={len(results)} ok={ok} failures={failures}")
    print(f"Manifest: {manifest_path}")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
