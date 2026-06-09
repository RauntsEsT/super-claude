---
name: deep-research
description: Multi-source deep research using firecrawl and web search. Searches the web, synthesizes findings, and delivers cited reports with source attribution.
origin: ECC
---

# Deep Research

Produce thorough, cited research reports from multiple web sources.

## When to Activate

- User asks to research any topic in depth
- Competitive analysis, technology evaluation, market sizing
- Any question requiring synthesis from multiple sources
- User says "research", "deep dive", "investigate"

## Workflow

### Step 1: Plan Research
Break topic into 3-5 sub-questions.

### Step 2: Multi-Source Search
For each sub-question, search using available tools (firecrawl, web search).
- Use 2-3 keyword variations per sub-question
- Aim for 15-30 unique sources total
- Prioritize: academic, official, reputable news > blogs > forums

### Step 3: Deep-Read Key Sources
Fetch full content from 3-5 most promising URLs.

### Step 4: Synthesize Report

```markdown
# [Topic]: Research Report
*Generated: [date] | Sources: [N]*

## Executive Summary
[3-5 sentence overview]

## 1. [First Major Theme]
[Findings with inline citations]

## Key Takeaways
- [Insight 1]
- [Insight 2]

## Sources
1. [Title](url) — one-line summary
```

## Quality Rules

1. Every claim needs a source
2. Cross-reference — if only one source says it, flag it
3. Recency matters — prefer last 12 months
4. No hallucination — if unknown, say "insufficient data found"

## Parallel Research

For broad topics, launch 3 research agents in parallel, each covering different sub-questions.
