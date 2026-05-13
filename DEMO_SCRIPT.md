# 5-Minute Customer-Facing Demo Script

## Timing Assumptions

Target audience: a VP of AI at a Fortune 500 company.
Target pace: 125-135 spoken words per minute.
Target spoken word count: roughly 600-650 words.
The remaining time is reserved for screen switching, scrolling, and short pauses.

Primary demo topic:

    finance - procure-to-pay

Primary rendered report:

    https://tbaums.github.io/crewai-executive-research-agent/reports/finance_procure_to_pay.html

Primary evaluation file:

    reports/finance_procure_to_pay_EVAL.md

## Run of Show

| Time | Screen | Goal |
|---|---|---|
| 0:00-0:35 | README / rendered report link | Frame the customer problem and business value |
| 0:35-1:45 | rendered finance report | Show the finished executive artifact first |
| 1:45-2:40 | `executive_research/main.py` | Explain CrewAI orchestration in customer terms |
| 2:40-3:25 | terminal / report generation | Show repeatability and operational visibility |
| 3:25-4:20 | `executive_research/research.py` / README | Explain source strategy, governance, and controls |
| 4:20-5:00 | eval file / limitations | Close with production path and enterprise next steps |

## Spoken Script

### 0:00-0:35 — Customer Problem and Value

The business problem is speed, trust, and repeatability. Your teams often need to understand a market, process area, competitor landscape, or customer initiative quickly, but the usual options are slow manual research or shallow AI summaries that are hard to verify.

This prototype shows how a CrewAI-based research workflow can turn a broad topic like `finance - procure-to-pay` into an executive-ready briefing that your strategy, sales, operations, or field teams could use before a customer conversation.

### 0:35-1:45 — Finished Executive Artifact

I will start with the finished report, because this is the artifact your users would actually consume.

The report opens with an executive summary, then covers market context, buyer pain points, startup and vendor landscape, strategic opportunities, recommendations, and sources. The intent is not to replace a final analyst report. It is to compress several hours of first-pass research into a briefing a senior stakeholder can review, challenge, and act on.

The same workflow has generated reports for HR onboarding, healthcare prior authorization, cybersecurity third-party risk, and supply chain demand forecasting. The system is not tied to one canned topic; it generalizes across business domains while keeping the output format consistent.

### 1:45-2:40 — Why CrewAI Fits the Use Case

This is a good fit for CrewAI because the work is naturally multi-step and role-based. A credible research workflow has to plan the question, gather industry context, identify vendors and new entrants, and synthesize findings for an executive audience.

CrewAI makes those roles explicit through agents, tasks, and crew-level orchestration. For an enterprise AI team, that makes the system inspectable: you can see which agent owns which responsibility, tune each role independently, and avoid burying the process inside one opaque prompt.

In this prototype, the crew has four roles: Research Planner, Industry Researcher, Startup and Vendor Researcher, and Executive Synthesizer.

### 2:40-3:25 — Repeatability and Operational Visibility

To generate a new report, the user provides a topic at the command line:

    python -m executive_research.main "finance - procure-to-pay"

The system then searches for source material, filters low-quality results, extracts page content, runs the CrewAI workflow, and writes both Markdown and HTML outputs.

The progress logs are intentional. In an enterprise environment, a long-running agent workflow should not feel like a black box. Users and operators need to see which stage is running, which sources are skipped, when extraction succeeds, and when the final report is written.

### 3:25-4:20 — Source Strategy and Enterprise Controls

The prototype uses public web search, relevance filtering, page extraction, bounded timeouts, and fallback snippets. That is enough to demonstrate real data-source integration while keeping the system easy to run and review.

For your production environment, the data layer is where I would harden first. The same workflow could connect to approved internal knowledge bases, CRM notes, procurement data, financial filings, market research subscriptions, curated news APIs, and commercial company databases. I would add source scoring, citation validation, recency checks, caching, observability, and human review for high-stakes outputs.

The key point is that the agent workflow can remain stable while the data sources and governance controls become enterprise-grade.

### 4:20-5:00 — Evaluation and Close

I also included companion evaluation files for the sample reports. They check whether each output accepts a topic, produces an executive-ready report, covers industry improvements, innovation leaders, new entrants, VC investment signals, real sources, clarity, and actionability.

The main limitation is source quality. Public web search can return vendor blogs or SEO-heavy content, so production should use approved data and stronger validation. But the core pattern is here: CrewAI coordinates specialized agents into a repeatable workflow that produces a useful executive artifact quickly, with a clear path to enterprise controls.

## Backup Cuts If Running Long

- Skip the live run and open the rendered finance report directly.
- Summarize the code in one sentence: CrewAI coordinates specialized research and synthesis agents over a lightweight web-research layer.
- Show only one evaluation file: `reports/finance_procure_to_pay_EVAL.md`.
- End with the production-hardening paragraph if interrupted.

## Backup Answers

### Why CrewAI?

CrewAI is a strong fit because the workflow naturally decomposes into specialized roles. It makes agent responsibilities and orchestration explicit, which is easier to inspect, explain, govern, and adapt than one monolithic prompt.

### Why show the report before the code?

For a VP of AI, the business artifact and operational value matter first. The code explains how the result is produced and how the workflow could be productionized.

### Biggest known limitation?

Source quality. Public web search is enough for a prototype, but production should use approved sources, source scoring, recency checks, citation validation, and funding-data integrations.