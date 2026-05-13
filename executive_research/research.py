from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import time

import requests
import trafilatura
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

@dataclass
class Source:
    title: str
    url: str
    snippet: str
    extracted_text: str = ""


def build_queries(topic: str) -> list[str]:
    base = topic.strip()
    return [
        f"{base} market trends 2025",
        f"{base} startups vendors AI automation",
        f"{base} enterprise pain points CFO procurement",
        f"{base} analyst report procure to pay accounts payable automation",
    ]


def search_web(topic: str, max_results_per_query: int = 4) -> list[Source]:
    results: list[Source] = []
    seen_urls: set[str] = set()

    with DDGS() as ddgs:
        for query in build_queries(topic):
            try:
                for item in ddgs.text(query, max_results=max_results_per_query):
                    url = item.get("href") or item.get("url") or ""
                    if not url or url in seen_urls:
                        continue

                    seen_urls.add(url)
                    results.append(
                        Source(
                            title=item.get("title") or "Untitled source",
                            url=url,
                            snippet=item.get("body") or "",
                        )
                    )
            except Exception as exc:
                results.append(
                    Source(
                        title=f"Search failed for query: {query}",
                        url="",
                        snippet=f"Search error: {exc}",
                    )
                )

            time.sleep(0.4)

    return results[:12]

def extract_page_text(url: str, timeout: int = 12) -> str:
    if not url:
        return ""

    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
            )
            if extracted:
                return extracted[:3500]
    except Exception:
        pass

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        extracted = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False,
        )
        return (extracted or "")[:3500]
    except Exception:
        return ""


def gather_research_context(topic: str) -> tuple[str, list[Source]]:
    sources = search_web(topic)
    enriched: list[Source] = []

    for source in sources:
        text = extract_page_text(source.url)
        enriched.append(
            Source(
                title=source.title,
                url=source.url,
                snippet=source.snippet,
                extracted_text=text,
            )
        )

    context_blocks: list[str] = []
    for idx, source in enumerate(enriched, start=1):
        body = source.extracted_text or source.snippet or "No extract available."
        context_blocks.append(
            "\n".join(
                [
                    f"[{idx}] {source.title}",
                    f"URL: {source.url or 'n/a'}",
                    f"Snippet: {source.snippet}",
                    "Extract:",
                    body[:3000],
                ]
            )
        )

    return "\n\n---\n\n".join(context_blocks), enriched


def format_sources(sources: Iterable[Source]) -> str:
    lines: list[str] = []
    for idx, source in enumerate(sources, start=1):
        if source.url:
            lines.append(f"[{idx}] {source.title} - {source.url}")
    return "\n".join(lines)