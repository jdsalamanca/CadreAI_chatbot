# Sources

All sources used to build `cadre_knowledge_base.json` / `cadre_research.md`. Primary (official Cadre AI)
sources are preferred throughout; there are no third-party sources in the current corpus.

## Official Cadre AI website (primary)

| URL | Topics covered | Knowledge item IDs |
|---|---|---|
| https://www.cadreai.com/ | Company overview, core services, workflow/automation approach, AI Maturity Index overview, AI Maturity Index scoring (absence of detail) | `company_overview`, `core_services`, `workflow_automation_and_custom_solutions`, `ai_maturity_index_overview`, `ai_maturity_index_scoring_gap` |
| https://www.cadreai.com/strategy | Getting started, AI Transformation Intensive & process, service pricing (absence of detail), AI Maturity Index pillars, client portal, client portal access gap, AI-Healthy Data Assessment | `getting_started`, `ai_transformation_intensive`, `ai_transformation_process`, `service_pricing`, `ai_maturity_index_pillars`, `client_portal`, `client_portal_access_gap`, `ai_healthy_data` |
| https://www.cadreai.com/contact | Strategy call / contact channels | `strategy_call` |
| https://www.cadreai.com/industries | Full industries list, manufacturing opportunities, "beyond the list" statement | `industries`, `industry_manufacturing`, `industry_outside_list` |
| https://www.cadreai.com/industries/real-estate | Real estate AI opportunities | `industry_real_estate` |
| https://www.cadreai.com/industries/construction | Construction AI opportunities | `industry_construction` |
| https://www.cadreai.com/industries/financial-services | Financial services AI opportunities | `industry_financial_services` |
| https://www.cadreai.com/ai-engineering | LLM selection approach, data security approach | `llm_selection`, `data_security` |
| https://www.cadreai.com/case-studies | Hospitality, Professional Services, Mortgage & Lending case studies | `case_study_hospitality`, `case_study_professional_services`, `case_study_mortgage` |
| https://www.cadreai.com/articles/your-systems-are-not-ready-for-ai | Manufacturing case study / "fix data before AI" narrative | `case_study_manufacturing` |

## Challenge-provided ground truth (primary, but not independently web-verifiable)

One source, referred to in the knowledge base as `challenge_ground_truth`, is a document provided directly
as part of this coding challenge rather than fetched from the live public web. It was used to corroborate
the four core service names and to source the technology-partner/ecosystem list.

| Source | Topics covered | Knowledge item IDs |
|---|---|---|
| Challenge ground-truth document | Core services (corroboration), technology partners/ecosystem | `core_services` (partial), `cadre_partners` |

**Note for the architecture/verification discussion**: this source is authoritative for the purposes of the
challenge, but it is not a URL a chatbot user (or a future automated re-verification process) could
independently re-check. It should be flagged as a distinct `source_type` (as it already is in
`cadre_knowledge_base.json`) so it isn't confused with a page that could silently go stale or 404.

## Sources considered but not found / not used

- No dedicated public FAQ page was located.
- No public pricing page was located.
- No public client-portal login page was located (only references to the portal's existence on
  `/strategy`).
- No direct online scheduling link (e.g., Calendly) was located; only the "Talk to an AI Strategist" CTA and
  general contact channels.

## Source policy applied

- Prefer official Cadre AI sources over third-party sources (none were needed or used).
- Do not infer facts not stated by a source.
- Record anything not found as a gap rather than guessing (see `knowledge_gaps.md`).
