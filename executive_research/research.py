from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse
import sys
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

def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", file=sys.stderr, flush=True)


BLOCKED_DOMAINS = {
    "abcdocz.com",
    "bing.com",
    "brex.com",
    "cfoiquk.com",
    "coruzant.com",
    "deepseekimagegenerator.com",
    "desapandakgede.id",
    "dragonsourcing.com",
    "dualfinances.com",
    "en.wikipedia.org",
    "finance.yahoo.com",
    "finansys.com",
    "findarticles.com",
    "lassosupplychain.com",
    "linkedin.com",
    "mercury.com",
    "openpr.com",
    "placement-officer.com",
    "procurementtactics.com",
    "realpage.com",
    "shoppable.ph",
    "sitnshow.com",
    "startuphub.ai",
    "tesladigitalhq.com",
    "tiktok.com",
    "transparentglobal.com",
    "vsfpartners.com",
    "visasponsor.jobs",
}

PREFERRED_DOMAINS = {
    "bcg.com",
    "coupa.com",
    "deloitte.com",
    "futuremarketinsights.com",
    "gartner.com",
    "ibm.com",
    "kpmg.com",
    "learn.microsoft.com",
    "mckinsey.com",
    "oracle.com",
    "pwc.com",
    "sap.com",
}

GENERIC_RELEVANCE_TERMS = {
    "AI",
    "automation",
    "enterprise",
    "market",
    "platform",
    "software",
    "startup",
    "technology",
    "vendor",
}

def topic_relevance_terms(topic: str) -> set[str]:
    normalized_topic = topic.lower().replace("-", " ")
    terms = {
        normalized_topic.strip(),
        *[part.strip() for part in normalized_topic.split() if len(part.strip()) > 3],
        *GENERIC_RELEVANCE_TERMS,
    }
    return {term for term in terms if term}

def source_domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")

def domain_matches(domain: str, blocked_domain: str) -> bool:
    return domain == blocked_domain or domain.endswith(f".{blocked_domain}")


def is_ad_or_redirect_url(url: str) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.lower()
    return (
        domain in {"bing.com", "google.com", "doubleclick.net"}
        or "/aclick" in path
        or "doubleclick" in domain
    )


def is_allowed_source(url: str) -> bool:
    domain = source_domain(url)
    if not domain:
        return False
    if is_ad_or_redirect_url(url):
        return False
    return not any(domain_matches(domain, blocked_domain) for blocked_domain in BLOCKED_DOMAINS)

def is_relevant_source(topic: str, title: str, url: str, snippet: str) -> bool:
    haystack = " ".join([title, url, snippet]).lower().replace("-", " ")
    return any(term.lower() in haystack for term in topic_relevance_terms(topic))

def build_queries(topic: str) -> list[str]:
    base = topic.strip()
    return [
        f"{base} market trends 2025",
        f"{base} startups vendors AI automation",
        f"{base} enterprise pain points buyers",
        f"{base} analyst report enterprise software automation",
    ]


def search_web(topic: str, max_results_per_query: int = 8) -> list[Source]:
    results: list[Source] = []
    seen_urls: set[str] = set()

    log(f"Searching web for topic: {topic}")
    with DDGS() as ddgs:
        for query in build_queries(topic):
            log(f"Search query: {query}")
            try:
                for item in ddgs.text(query, max_results=max_results_per_query):
                    url = item.get("href") or item.get("url") or ""
                    if not url or url in seen_urls:
                        continue
                    title = item.get("title") or "Untitled source"
                    snippet = item.get("body") or ""
                    if not is_allowed_source(url):
                        log(f"Skipping blocked source: {url}")
                        continue
                    if not is_relevant_source(topic, title, url, snippet):
                        log(f"Skipping low-relevance source: {url}")
                        continue

                    seen_urls.add(url)
                    results.append(
                        Source(
                            title=title,
                            url=url,
                            snippet=snippet,
                        )
                    )
            except Exception as exc:
                log(f"Search failed for query: {query} ({exc})")
                results.append(
                    Source(
                        title=f"Search failed for query: {query}",
                        url="",
                        snippet=f"Search error: {exc}",
                    )
                )

            time.sleep(0.4)

    results.sort(
        key=lambda source: source_domain(source.url) not in PREFERRED_DOMAINS
    )
    log(f"Search complete: {len(results[:12])} unique sources selected")
    return results[:12]

def extract_page_text(url: str, timeout: int = 8) -> str:
    if not url:
        return ""

    start = time.monotonic()
    log(f"Fetching source: {url}")

    try:
        response = requests.get(
            url,
            timeout=(4, timeout),
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        extracted = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False,
        )
        elapsed = time.monotonic() - start
        if extracted:
            log(f"Fetched source in {elapsed:.1f}s ({len(extracted)} chars extracted)")
            return extracted[:3500]
        log(f"Fetched source in {elapsed:.1f}s (no extractable text)")
        return ""
    except Exception as exc:
        elapsed = time.monotonic() - start
        log(f"Skipped source after {elapsed:.1f}s: {exc}")
        return ""


def gather_research_context(topic: str) -> tuple[str, list[Source]]:
    sources = search_web(topic)
    log(f"Extracting text from {len(sources)} sources")
    enriched: list[Source] = []

    for idx, source in enumerate(sources, start=1):
        log(f"Processing source {idx}/{len(sources)}: {source.title}")
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