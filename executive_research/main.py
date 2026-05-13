
from __future__ import annotations

import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv
import markdown as markdown_lib

from executive_research.research import gather_research_context, format_sources, log


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "research_report"


def make_llm() -> LLM:
    model = os.getenv("OPENAI_MODEL", "gpt-4.1")
    log(f"Initializing LLM: {model}")
    return LLM(model=model, temperature=0.2)


def build_crew(topic: str, research_context: str, source_list: str) -> Crew:
    log("Building CrewAI agents and tasks")
    llm = make_llm()

    planner = Agent(
        role="Research Planner",
        goal="Turn a broad executive research topic into a focused research plan.",
        backstory="You scope ambiguous B2B research questions quickly and clearly.",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    industry_researcher = Agent(
        role="Industry Researcher",
        goal="Extract market trends, buyer pain points, and operational implications from source material.",
        backstory="You understand enterprise operations, procurement, finance, and SaaS buying committees.",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    vendor_researcher = Agent(
        role="Startup and Vendor Researcher",
        goal="Identify vendor categories, startup activity, and competitive dynamics relevant to the topic.",
        backstory="You track B2B software markets and translate vendor noise into useful executive signal.",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    synthesizer = Agent(
        role="Executive Strategy Synthesizer",
        goal="Create an executive-ready Markdown report with clear recommendations and citations.",
        backstory="You write concise, board-ready research briefs for senior operators and technology buyers.",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    log("Defining CrewAI task: research plan")
    plan_task = Task(
        description=(
            f"Create a focused research plan for this topic: {topic}.\n\n"
            "Return 5 to 7 practical research questions for an executive audience."
        ),
        expected_output="A concise research plan with 5 to 7 research questions.",
        agent=planner,
    )

    log("Defining CrewAI task: industry analysis")
    industry_task = Task(
        description=(
            f"Using the source context below, analyze industry trends and buyer pain points for: {topic}.\n\n"
            f"Source context:\n{research_context}\n\n"
            "Use only the provided source context. Include citation markers like [1], [2] where useful."
        ),
        expected_output="A sourced industry analysis with trends, pain points, and executive implications.",
        agent=industry_researcher,
        context=[plan_task],
    )

    log("Defining CrewAI task: vendor landscape")
    vendor_task = Task(
        description=(
            f"Using the same source context, analyze vendor and startup activity for: {topic}.\n\n"
            f"Source context:\n{research_context}\n\n"
            "Group vendors by category when possible. Use citation markers like [1], [2] where useful."
        ),
        expected_output="A sourced vendor landscape summary with categories and competitive dynamics.",
        agent=vendor_researcher,
        context=[plan_task],
    )

    log("Defining CrewAI task: executive synthesis")
    synthesis_task = Task(
        description=(
            f"Write an executive-ready Markdown report on: {topic}.\n\n"
            "Use these sections:\n"
            "# Executive Research Report\n"
            "## Executive Summary\n"
            "## Market Context\n"
            "## Buyer Pain Points\n"
            "## Startup and Vendor Landscape\n"
            "## Strategic Opportunities\n"
            "## Risks and Open Questions\n"
            "## Recommendations\n"
            "## Sources\n\n"
            "Use citation markers such as [1], [2] in the body where claims depend on sources. "
            "In the Sources section, include this source list exactly as provided:\n"
            f"{source_list}"
        ),
        expected_output="A complete executive Markdown report with citations and recommendations.",
        agent=synthesizer,
        context=[industry_task, vendor_task],
    )

    crew = Crew(
        agents=[planner, industry_researcher, vendor_researcher, synthesizer],
        tasks=[plan_task, industry_task, vendor_task, synthesis_task],
        process=Process.sequential,
        verbose=True,
    )
    log("CrewAI crew ready: 4 agents, 4 sequential tasks")
    return crew


def run_crew_with_logging(crew: Crew) -> str:
    log("Starting CrewAI kickoff")
    start = time.monotonic()
    result = crew.kickoff()
    elapsed = time.monotonic() - start
    log(f"CrewAI kickoff complete in {elapsed:.1f}s")
    return str(result)


def render_html(topic: str, markdown_report: str) -> str:
    body = markdown_lib.markdown(markdown_report, extensions=["tables", "fenced_code"])
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Executive Research Report - {topic}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f6f7f9; color: #1f2937; }}
    main {{ max-width: 980px; margin: 40px auto; background: white; padding: 48px; border-radius: 16px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }}
    h1 {{ font-size: 2.2rem; margin-top: 0; color: #111827; }}
    h2 {{ margin-top: 2rem; color: #1f2937; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.4rem; }}
    h3 {{ color: #374151; }}
    p, li {{ line-height: 1.6; }}
    .meta {{ color: #6b7280; margin-bottom: 2rem; }}
  </style>
</head>
<body>
  <main>
    <div class="meta">Generated at {generated_at}</div>
    {body}
  </main>
</body>
</html>
"""


def main() -> int:
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Add it to .env or export it in your shell.")
        return 1

    topic = " ".join(sys.argv[1:]).strip() or "finance - procure-to-pay"
    print(f"Research topic: {topic}", flush=True)
    print("Gathering public web context...", flush=True)

    research_context, sources = gather_research_context(topic)
    source_list = format_sources(sources)

    print(f"Collected {len(sources)} source candidates.", flush=True)
    log(f"Research context length: {len(research_context)} chars")
    log(f"Source list length: {len(source_list)} chars")
    print("Running CrewAI agents...", flush=True)

    crew = build_crew(topic, research_context, source_list)
    markdown_report = run_crew_with_logging(crew)
    log(f"Markdown report length: {len(markdown_report)} chars")

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    slug = slugify(topic)
    markdown_path = reports_dir / f"{slug}.md"
    html_path = reports_dir / f"{slug}.html"

    log(f"Writing Markdown report: {markdown_path}")
    markdown_path.write_text(markdown_report)
    log(f"Writing HTML report: {html_path}")
    html_path.write_text(render_html(topic, markdown_report))

    print(f"Markdown report written to: {markdown_path}", flush=True)
    print(f"HTML report written to: {html_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())