from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv
import markdown as markdown_lib

from executive_research.research import gather_research_context, format_sources


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "research_report"


def make_llm() -> LLM:
    model = os.getenv("OPENAI_MODEL", "gpt-4.1")
    return LLM(model=model, temperature=0.2)


def build_crew(topic: str, research_context: str, source_list: str) -> Crew:
    llm = make_llm()

    planner = Agent(
        role="Research Planner",
        goal="Turn a broad executive research topic into a focused research plan.",
        backstory=(
            "You are a pragmatic strategy consultant who scopes ambiguous B2B "
            "research questions quickly and clearly."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    industry_researcher = Agent(
        role="Industry Researcher",
        goal="Extract market trends, buyer pain points, and operational implications from source material.",
        backstory=(
            "You understand enterprise operations, procurement, finance, and SaaS buying committees."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    vendor_researcher = Agent(
        role="Startup and Vendor Researcher",
        goal="Identify vendor categories, startup activity, and competitive dynamics relevant to the topic.",
        backstory=(
            "You track B2B software markets and translate vendor noise into useful executive signal."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    synthesizer = Agent(
        role="Executive Strategy Synthesizer",
        goal="Create an executive-ready Markdown report with clear recommendations and citations.",
        backstory=(
            "You write concise, board-ready research briefs for senior operators and technology buyers."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    reviewer = Agent(
        role="Quality Reviewer",
        goal="Improve clarity, source discipline, and customer-readiness without adding unsupported claims.",
        backstory=(
            "You are a careful field engineering leader reviewing work before it goes to a customer."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    plan_task = Task(
        description=(
            f"Create a focused research plan for this topic: {topic}.\n\n"
            "Return 5 to 7 research questions. Keep them practical for an executive audience."
        ),
        expected_output="A concise research plan with 5 to 7 research questions.",
        agent=planner,
    )

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

    synthesis_task = Task(
        description=(
            f"Write an executive-ready Markdown report on: {topic}.\n\n"
            "The report must include these sections:\n"
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

    review_task = Task(
        description=(
            "Review the Markdown report. Improve clarity, executive tone, and source discipline. "
            "Do not add facts that are not supported by the prior research. Return only the final Markdown report."
        ),
        expected_output="The final polished Markdown report only.",
        agent=reviewer,
        context=[synthesis_task],
    )

    return Crew(
        agents=[planner, industry_researcher, vendor_researcher, synthesizer, reviewer],
        tasks=[plan_task, industry_task, vendor_task, synthesis_task, review_task],
        process=Process.sequential,
        verbose=False,
    )


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
    code {{ background: #f3f4f6; padding: 0.15rem 0.3rem; border-radius: 4px; }}
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
    print(f"Research topic: {topic}")
    print("Gathering public web context...")

    research_context, sources = gather_research_context(topic)
    source_list = format_sources(sources)

    if not source_list:
        print("WARNING: no web sources were found. The report may be weak.")

    print(f"Collected {len(sources)} source candidates.")
    print("Running CrewAI agents...")

    crew = build_crew(topic, research_context, source_list)
    result = crew.kickoff()
    markdown_report = str(result)

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    slug = slugify(topic)
    markdown_path = reports_dir / f"{slug}.md"
    html_path = reports_dir / f"{slug}.html"

    markdown_path.write_text(markdown_report)
    html_path.write_text(render_html(topic, markdown_report))

    print(f"Markdown report written to: {markdown_path}")
    print(f"HTML report written to: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())