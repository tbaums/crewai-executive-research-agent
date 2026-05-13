# CrewAI Executive Research Agent

A multi-agent research system that generates executive-ready HTML reports for B2B market and strategy research topics.

This project was built as a take-home exercise for a Sales Engineering / Field Engineering interview process.

## Quickstart

Create a virtual environment, install dependencies, copy the example environment file, add an OpenAI API key, and run the report generator.

Commands:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python -m executive_research.main "finance - procure-to-pay"

Generated reports are written to the reports directory.

## Assignment Fit

The system accepts a high-level research topic, coordinates multiple specialized agents, gathers public web context, synthesizes findings, and produces an executive-facing report suitable for customer discussion.

## Architecture

The system uses a small CrewAI crew with specialized agents:

1. Research Planner: turns the user topic into focused research questions.
2. Industry Researcher: identifies market trends, pain points, buyer context, and operational drivers.
3. Startup / Vendor Researcher: identifies relevant startup and vendor activity.
4. Executive Synthesizer: turns research into a concise executive narrative.
5. Quality Reviewer: checks clarity, source usage, and customer-readiness.

The output is rendered as both Markdown and HTML.

## Design Decisions

### Agent framework: CrewAI

CrewAI was selected because the assignment asks for a multi-agent research system, and CrewAI is purpose-built for defining agents, tasks, crews, tools, and workflows. This maps directly to the exercise requirement for role-specialized research and synthesis agents.

Sources reviewed:
- https://docs.crewai.com/
- https://docs.crewai.com/en/concepts/agents
- https://docs.crewai.com/en/quickstart

### LLM: GPT-4.1

GPT-4.1 was selected as the default LLM because this project benefits more from strong instruction following, long-context synthesis, and reliable structured output than from maximum speed or minimum cost. The evaluator provided an OpenAI API key, so using a current OpenAI model reduces integration risk.

The model is configurable through environment variables so the system can be changed later without rewriting application code.

Sources reviewed:
- https://platform.openai.com/docs/models
- https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety

### Data sources: public web search and webpage extraction

The prototype uses public web search and lightweight webpage extraction so it can run with minimal setup. This is sufficient for a take-home exercise because it demonstrates the agent workflow, research process, source handling, and report generation.

For production customer deployments, the data-source layer should be swapped or expanded to include approved enterprise sources such as internal knowledge bases, CRM notes, financial filings, procurement system exports, industry research subscriptions, curated news APIs, and commercial company databases.

### Output format: HTML report

HTML was selected because it is easy to open locally, easy to style, easy to share in a demo, and more executive-friendly than raw terminal output. Markdown is also saved as an intermediate artifact for debugging and portability.

### Implementation philosophy

This project intentionally prioritizes a small, reliable, explainable system over an elaborate demo. The goal is to show practical field-engineering judgment: clear architecture, reasonable defaults, working code, reproducible setup, and an output that can support a customer-facing conversation.
