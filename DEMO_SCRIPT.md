# 5-Minute Demo Script

## Timing Assumptions

Target pace: 125-135 spoken words per minute.
Target spoken word count: roughly 600-650 words.
The remaining time is intentionally reserved for screen switching, scrolling, and short pauses.

Primary demo topic:

    finance - procure-to-pay

Primary sample report:

    reports/finance_procure_to_pay.html

Primary evaluation file:

    reports/finance_procure_to_pay_EVAL.md

## Run of Show

| Time | Screen | Goal |
|---|---|---|
| 0:00-0:45 | README / repo root | State what was built and why |
| 0:45-1:40 | `executive_research/main.py` | Explain the CrewAI agents and workflow |
| 1:40-2:25 | `executive_research/research.py` | Explain source gathering and filtering |
| 2:25-3:20 | terminal or generated report | Show how the system runs |
| 3:20-4:20 | `reports/finance_procure_to_pay.html` | Walk the executive report |
| 4:20-5:00 | eval file / README limitations | Explain evaluation and production hardening |

## Spoken Script

### 0:00-0:45 — Opening and Objective

For this take-home, I built a lightweight CrewAI executive research agent. The goal is to help a field team or business stakeholder quickly research a process area and produce a usable executive briefing, not just a pile of search results.

The app takes a topic like `finance - procure-to-pay`, gathers public web context, coordinates several specialized agents, and writes both Markdown and HTML reports. I kept the implementation intentionally small and explainable so the architecture, tradeoffs, and production gaps are easy to inspect.

### 0:45-1:40 — Agent Workflow

The main workflow lives in `executive_research/main.py`. I used four CrewAI agents because the assignment asked for a multi-agent system, and because the responsibilities map cleanly to how this research would be done by a field or strategy team.

The Research Planner turns the user topic into focused questions. The Industry Researcher analyzes market context, improvement areas, and buyer pain. The Startup and Vendor Researcher identifies relevant vendors, startups, and market entrants. Finally, the Executive Synthesizer turns the research into a concise report with citations, strategic opportunities, and recommendations.

That separation is important because it makes the workflow easier to reason about than one large prompt trying to do everything at once.

### 1:40-2:25 — Source Gathering and Filtering

The research layer lives in `executive_research/research.py`. It uses public web search, removes duplicate or obviously low-quality sources, applies topic-aware relevance checks, fetches page text with bounded timeouts, and falls back to snippets when a page cannot be extracted.

This is good enough for a prototype because it demonstrates real source integration without requiring a proprietary data contract. But it is not where I would stop for production. A production version should use approved sources, source scoring, recency checks, citation validation, caching, and ideally a funding-data connector for the VC-investment portion of the task.

### 2:25-3:20 — Run the System

The demo command is:

    python -m executive_research.main "finance - procure-to-pay"

If I run it live, the terminal shows progress through source search, skipped sources, extraction, CrewAI kickoff, and report writing. Those logs are intentional: long-running agent workflows are much easier to trust when users can see what is happening.

If time is tight, I would show the already generated report instead. The repo includes five sample reports across finance, HR, healthcare, cybersecurity, and supply chain so the reviewers can see that the input topic is not hardcoded to one domain.

### 3:20-4:20 — Walk the Primary Report

The strongest sample is `reports/finance_procure_to_pay.html`. I would use this as the primary artifact.

The report is structured for an executive reader: executive summary, market context, buyer pain points, startup and vendor landscape, strategic opportunities, recommendations, and sources. The goal is not to replace an analyst report. The goal is to produce a credible first draft that helps a business or field team prepare for a customer conversation.

I also kept Markdown output because it is easy to version, inspect, and evaluate. HTML is included because it is easier for nontechnical stakeholders to open and review.

### 4:20-5:00 — Evaluation and Production Hardening

I added companion evaluation files for each sample report. Those evals score the outputs against the assignment criteria: whether the system accepts a topic, produces an executive-ready report, covers industry improvements, leaders innovating, new companies, VC investment signals, real sources, clarity, and actionability.

The evals also call out limitations honestly. Source quality varies because public web search can return vendor blogs or SEO content. The prototype demonstrates the workflow, but production hardening should add approved data sources, stronger citation validation, source scoring, repeatable tests, and human review before customer-facing use.

## Backup Cuts If Running Long

- Skip the live run and open `reports/finance_procure_to_pay.html` directly.
- Summarize `research.py` in one sentence: public search, filtering, extraction, source formatting.
- Show only one eval file: `reports/finance_procure_to_pay_EVAL.md`.
- End with the production-hardening paragraph if interrupted.

## Backup Answers

### Why CrewAI?

CrewAI made the agent, task, and crew abstractions explicit, which was useful for demonstrating orchestration instead of hiding the workflow inside one monolithic prompt.

### Why HTML?

HTML is easy for nontechnical reviewers to open and read. Markdown remains useful for version control, debugging, and evaluation.

### Biggest known limitation?

Source quality. Public web search is enough for a prototype, but production should use approved sources, source scoring, recency checks, citation validation, and funding-data integrations.
