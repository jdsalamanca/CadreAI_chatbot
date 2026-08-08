# Cadre AI Research Notes

## Status

This document backfills Phase 1 ("Cadre AI Knowledge Research") from research already performed for this
project. The underlying claims were gathered from Cadre AI's public website and from a challenge-provided
ground-truth document, and were subsequently structured into `cadre_knowledge_base.json` at the repo root.
This file re-organizes those same claims by research topic, per `plan.md`, and separates **explicit claims**
(stated directly by a source) from **interpretation** (a reasonable reading that is not a direct quote).

Every claim below carries the `id` it maps to in `cadre_knowledge_base.json` so it can be traced back to its
structured form. See `sources.md` for the source list and `knowledge_gaps.md` for what is missing or
unverifiable.

---

## Company Overview / What Cadre AI Does

- **Explicit claim** (`company_overview`): Cadre AI is an AI strategy and implementation partner that helps
  businesses use AI to drive revenue growth, improve profitability/EBITDA, and scale more efficiently.
- **Interpretation** (`company_overview`): Cadre's approach emphasizes understanding the business problem
  first, then identifying a solution, implementing it, and measuring results — rather than starting from a
  specific tool or product.

## Core Services

- **Explicit claim** (`core_services`): Cadre's four core service lines are AI Strategy, AI Leadership &
  Facilitation, AI Engineering, and AI Agents. (Corroborated by both the public site and the challenge
  ground-truth document.)
- **Explicit claim** (`workflow_automation_and_custom_solutions`): Cadre's implementation work includes
  workflow automation and custom AI agents.
- **Interpretation** (`workflow_automation_and_custom_solutions`): Cadre does not default to building a
  custom solution for every problem — it appears to consider existing tools first, then automation/
  integration, and builds custom solutions only when that's the appropriate option.
- **Gap**: "AI Leadership & Facilitation" and "AI Agents" are named as service lines but no dedicated
  page-level detail on their scope was captured beyond the name itself. See `knowledge_gaps.md`.

## Industries Served

- **Explicit claim** (`industries`): Cadre publicly lists nine industries: Professional Services, Private
  Equity, Real Estate, Financial Services, Mortgage & Lending, Construction, Retail & E-commerce,
  Manufacturing & Logistics, and Hospitality.
- **Explicit claim** (`industry_outside_list`): Cadre states it has worked with companies beyond the
  industries listed publicly, including companies "one might not expect to use AI."
- **Interpretation** (`industry_outside_list`): If a prospective client is in an industry not on the public
  list, the chatbot should not assume Cadre can't help — it should ask about the business/problem and offer
  to connect the user with a strategist rather than declining outright.

### Industry detail captured (4 of 9 have dedicated sub-page content)

- **Real Estate** (`industry_real_estate`): property analysis, lead qualification, transaction coordination,
  market intelligence.
- **Construction** (`industry_construction`): takeoffs, estimating, project health, change orders, resource
  planning.
- **Financial Services** (`industry_financial_services`): KYC, client retention, regulatory tracking,
  portfolio recommendations, risk assessment.
- **Manufacturing** (`industry_manufacturing`): predictive maintenance, inventory optimization, production
  scheduling — with an explicit emphasis on fixing foundational data/process problems before applying AI.
- **Gap**: Professional Services, Private Equity, Mortgage & Lending, Retail & E-commerce, and Hospitality
  do not have dedicated industry sub-page detail captured (though 3 of them appear as case studies — see
  below).

## AI Strategy / Getting Started

- **Explicit claim** (`getting_started`): Cadre typically starts by understanding a company's business,
  teams, processes, technology, and AI opportunities before selecting tools.
- **Explicit claim** (`getting_started`): Prospective clients can speak with an AI strategist to discuss
  their situation and determine next steps.
- **Explicit claim** (`ai_transformation_intensive`): Cadre advertises an "AI Transformation Intensive," a
  structured 45-day program from "lack of clarity" to a "prioritized roadmap."
- **Explicit claim** (`ai_transformation_process`): The Intensive follows four stages — Discover Use Cases,
  Survey the Landscape, Implement Solutions, Scale with Confidence — with discovery involving team
  interviews, problem identification, ROI estimation, and prioritization by impact/feasibility.
- **Explicit claim** (`ai_healthy_data`): Cadre treats clean, structured data as a prerequisite for effective
  AI, and includes an "AI-Healthy Data Assessment" in its transformation framework.

## AI Engineering / LLM Selection

- **Explicit claim** (`llm_selection`): Cadre takes a use-case-driven approach to LLM selection rather than
  treating one model as universally best, and its materials reference ChatGPT, Microsoft Copilot, and
  Claude as example platforms.
- **Explicit claim** (`cadre_partners`, source: challenge ground truth): Cadre's technology partner/ecosystem
  list includes OpenAI, Anthropic (Claude), Google, Microsoft, AWS, Salesforce, Snowflake, and OpenRouter.
  This claim comes from the challenge-provided ground truth document, not the live public site — flagged
  distinctly in `sources.md`.

## Data Security

- **Explicit claim** (`data_security`): Cadre's materials describe selecting an LLM appropriate to the
  business/use case, "black-boxing" company data so it isn't used to train other models, discouraging
  employees from putting company secrets into personal LLM accounts, and moving teams onto secure, compliant
  AI tools.
- **Boundary (must not infer)**: No source supports specific certifications (e.g., SOC 2), contractual
  guarantees, or a claim that Cadre "guarantees" complete data security. The chatbot must not assert these.

## AI Maturity Index

- **Explicit claim** (`ai_maturity_index_overview`): The AI Maturity Index scores a company across an
  eight-pillar framework, providing a grade per pillar plus explanations and actionable insights.
- **Explicit claim** (`ai_maturity_index_pillars`): The eight pillars are: (1) Build your dedicated AI team,
  (2) Deploy your AI Command Center, (3) Create an AI-First Culture Shift, (4) Connect & Enable your Tech
  Stack, (5) AI-Healthy Data Assessment, (6) Build your Framework for AI Agent Readiness, (7) Departmental AI
  Deep Dives, (8) Find your 3-Year AI Vision.
- **Gap** (`ai_maturity_index_scoring_gap`): Exact scoring methodology, numeric thresholds, questionnaire
  length, and how a company actually obtains a score are not documented publicly. Must not be invented.

## Case Studies

- **Hospitality** (`case_study_hospitality`): AI-powered booking visibility replacing an Excel-based
  system, integrated with an existing CRM, preventing conflicting same-day bookings. Reported result:
  $420,000 in annual savings.
- **Professional Services** (`case_study_professional_services`): AI voice/chat agents handling consultation
  requests, availability checks, scheduling, and booking. Reported results: 1,500 hours saved annually;
  500–700 appointment requests processed automatically per month.
- **Mortgage & Lending** (`case_study_mortgage`): Custom AI chatbot unifying loan tools, guideline access,
  investor matching, borrower communications. Reported result: processing time reduced from 1–2 days to
  rapid approvals with real-time updates.
- **Manufacturing** (`case_study_manufacturing`): A $120M manufacturing company wanted predictive maintenance
  but had fragmented data (paper records, Excel, manual scheduling). Cadre addressed the foundational
  data/process problems first. Reported results: 15 hours/week saved in scheduling; 12% improvement in
  project profitability.
- **Interpretation**: All four reported case studies are self-published by Cadre (own site), not independently
  audited — treat reported figures as Cadre's own claims, not independently verified facts, when presenting
  them (this nuance should be preserved rather than stated as flatly "verified" fact).

## Service / Pricing Information

- **Gap** (`service_pricing`): Cadre does not appear to publish standard pricing for its core services;
  pricing depends on the engagement.
- **Potential source of confusion flagged during research**: A publicly-referenced figure of roughly
  "$30 per employee per month" relates to an AI command-center example, not to Cadre's own service pricing.
  This must not be presented as Cadre's price. See `knowledge_gaps.md`.

## How to Book a Strategy Call

- **Explicit claim** (`strategy_call`): Cadre offers a "Talk to an AI Strategist" call-to-action on its
  website. Contact is also available via hello@gocadre.ai, phone (619) 324-3223, or the contact page.
- **Gap**: No direct public scheduling URL (e.g., a Calendly-style link) was identified during research.

## Client Portal

- **Explicit claim** (`client_portal`): Cadre provides a centralized portal for tracking AI tools, agents,
  training, and results.
- **Gap** (`client_portal_access_gap`): Login URL, password reset, authentication method, account creation,
  and client-specific permissions are not publicly documented.

## FAQs

- **Gap**: No dedicated public FAQ page/content was identified during research. Common-question handling in
  the chatbot will rely on the topic areas above plus escalation, not a distinct FAQ source.
