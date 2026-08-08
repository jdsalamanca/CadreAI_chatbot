# Knowledge Gaps

Topics where public Cadre AI information is missing, insufficiently detailed, or ambiguous enough that the
chatbot must not fabricate an answer. Each gap below maps to a `status: "not_publicly_available"` item in
`cadre_knowledge_base.json` where one exists, plus additional gaps identified while organizing the research
into Phase 1 deliverables.

## Confirmed gaps (already encoded as `not_publicly_available` in the knowledge base)

1. **Service pricing** (`service_pricing`) — Cadre does not publish standard pricing for its core services.
   Required behavior: acknowledge pricing depends on the engagement and escalate to an AI strategist. Do
   not state or estimate a number.

2. **AI Maturity Index scoring methodology** (`ai_maturity_index_scoring_gap`) — the eight pillars are
   documented, but the exact scoring method, numeric thresholds, questionnaire length, and how a company
   actually obtains a score are not. Required behavior: describe the eight-pillar framework, but do not
   invent scoring mechanics.

3. **Client portal access / login** (`client_portal_access_gap`) — the portal's existence and purpose are
   documented, but login URL, password reset flow, authentication method, account creation, and
   client-specific permissions are not. Required behavior: confirm the portal exists, then escalate to
   hello@gocadre.ai for access issues.

## Additional gaps identified while structuring Phase 1 research

4. **No direct online scheduling link** — only a "Talk to an AI Strategist" CTA and general contact channels
   (email/phone/contact page) were found; no Calendly-style or similar direct booking URL. The chatbot
   should point users to the contact channels rather than implying a self-serve scheduling link exists.

5. **"AI Leadership & Facilitation" and "AI Agents" service lines lack dedicated deep-dive content** — both
   are named as one of Cadre's four core services, but no page-level detail on their specific scope,
   process, or deliverables was captured (unlike AI Strategy and AI Engineering, which have more supporting
   detail). The chatbot should describe them only at the level of what's documented and escalate for
   specifics.

6. **Five of nine listed industries lack dedicated sub-page detail** — Professional Services, Private
   Equity, Mortgage & Lending, Retail & E-commerce, and Hospitality appear on the industries list, and three
   of them (Hospitality, Professional Services, Mortgage & Lending) are represented by case studies, but
   none have the same kind of "AI opportunities" sub-page detail captured for Real Estate, Construction,
   Financial Services, and Manufacturing.

7. **No public FAQ page** was identified. General/common questions are handled by the topic areas in
   `cadre_research.md`, not a distinct FAQ source.

8. **Security certifications / compliance status** — Cadre's data-security approach (LLM selection,
   "black-boxing" data, discouraging personal-account use, secure tooling) is documented, but no
   certification (e.g., SOC 2), contractual guarantee, or specific technical control is documented. This is
   a hard boundary, not just a missing detail: the chatbot must not infer or imply certification/compliance
   status.

9. **Case study figures are self-reported** — the four case studies (Hospitality, Professional Services,
   Mortgage & Lending, Manufacturing) are published on Cadre's own site with no independent audit indicated.
   Not a "gap" in the sense of missing information, but a nuance the chatbot should preserve (these are
   Cadre's reported results, not independently verified figures) rather than presenting as flatly audited.

## Potentially conflicting / easily-confused information

10. **"~$30 per employee per month" figure** — this number is publicly associated with an AI command-center
    example, not with Cadre's own service pricing. Because it's easy to misread as a Cadre price point, it's
    explicitly excluded from the pricing answer and flagged here so it isn't reintroduced by a future
    research pass without the same caveat.

## How these gaps should be handled downstream

Per `CLAUDE.md`'s knowledge-integrity requirement, every gap above should result in the chatbot (a)
acknowledging the limitation rather than guessing, and (b) offering an escalation path (hello@gocadre.ai,
(619) 324-3223, the contact page, or "Talk to an AI Strategist") where relevant. This mapping is already
reflected in `cadre_knowledge_base.json`'s `response_policy` and `escalation` sections and should carry
through unchanged into the Phase 3 knowledge-service implementation.
