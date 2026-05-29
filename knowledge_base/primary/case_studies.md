# Ioanna Renta — Case Studies & Proof Points

## Case Study 1: AUDI A8 Navigation Programme Recovery
**Company:** HERE Technologies
**Role:** AUTO SDK Team Lead
**Situation:** The AUDI A8 navigation programme was at risk. The customer relationship was strained, software delivery was behind, and the production line date was fixed — missing it would have been a significant commercial failure.
**Actions:**
- Stabilised the customer relationship through direct engagement and transparent communication
- Restructured the delivery timeline with the engineering team
- Kept the programme on track through to the production line date
**Outcome:** Software shipped on the AUDI A8 production line date. Customer relationship preserved.
**Navigation performance:** As part of the broader engineering work, the team reduced navigation cold-start time from 55 seconds to 5 seconds through tile caching and rendering pipeline optimisation.
**Leadership lesson:** Transparency with customers during difficulty builds more trust than silence during success.

## Case Study 2: Quality Maturity Index at Delivery Hero
**Company:** Delivery Hero
**Domain:** Restaurants (240+ engineers)
**Situation:** A large, distributed engineering organisation with inconsistent quality standards, no shared language for improvement, and quality conversations that felt subjective and political.
**Actions:**
- Designed the Quality Maturity Index (QMI) — an eight-dimension engineering health framework
- Piloted within the Restaurants domain
- Made scoring transparent and non-punitive
- Created peer validation process to reduce gaming
**Outcome:**
- Within six months, 50% of the broader organisation voluntarily adopted QMI
- Provided a shared language for quality conversations across teams and leadership
- Became the baseline for engineering health reporting
**Leadership lesson:** Voluntary adoption is the only honest signal that a framework works. If people adopt it because they find it useful, not because they fear consequences, the data is trustworthy.

## Case Study 3: ML Recommendations at Delivery Hero
**Company:** Delivery Hero
**Domain:** Restaurants
**Situation:** Restaurant discovery was based on basic ranking signals. The opportunity was to use ML to personalise recommendations and increase organic order growth.
**Actions:**
- Built and scaled the ML recommendations capability within the engineering organisation
- Aligned product, data science, and engineering around a shared outcome metric
**Outcome:**
- 35% organic growth in restaurant orders
- 60% improvement in customer retention
**Leadership lesson:** The hardest part of ML in production is not the model — it is the alignment between product, data, and engineering around what success looks like.

## Case Study 4: Incident Reduction at sennder
**Company:** sennder
**Role:** VP Engineering, Platform & Data (150+ engineers)
**Situation:** P1 incidents were occurring at a rate of approximately 20 per week, causing significant operational disruption and eroding team confidence.
**Actions:**
- Established 24/7 on-call processes with clear escalation paths
- Implemented structured post-mortem culture (blameless, action-oriented)
- Built observability infrastructure to detect issues before they became incidents
- Created incident severity classification to reduce alert fatigue
**Outcome:** P1 incidents reduced from 20/week to 2/month — a 90%+ reduction.
**Leadership lesson:** Incident reduction is primarily a culture and process problem, not a technology problem. Most organisations have the tools. They lack the discipline.

## Case Study 5: Distributed Monolith Migration at sennder
**Company:** sennder
**Role:** VP Engineering, Platform & Data
**Situation:** A distributed monolith — the worst of both worlds. Tightly coupled services with the operational complexity of a distributed system. Moving to a properly decoupled architecture was a prerequisite for scaling.
**Actions:**
- Defined the target architecture with the engineering leads
- Used the strangler fig pattern — replacing components incrementally rather than rewriting
- Maintained business continuity throughout (no big-bang cutover)
- Completed the migration in six months
**Outcome:** Distributed monolith successfully exited in six months with zero major incidents during migration.
**Leadership lesson:** Big-bang rewrites almost always fail. Incremental migration with clear seams is slower to start but faster to finish.

## Case Study 6: AI Tooling Adoption at sennder
**Company:** sennder
**Role:** VP Engineering, Platform & Data
**Situation:** The organisation needed to adopt AI tooling at scale without creating security risks, governance gaps, or a two-tier system where some teams had AI and others didn't.
**Actions:**
- Deployed LibreChat as the internal AI interface — giving engineers access to LLM capabilities within a governed environment
- Built MCP server integration for commercial email parsing (OCR pipeline)
- Established AI usage guidelines as part of the Engineering Manifesto
- Rolled out AI tooling consistently across all teams
**Outcome:** Organisation-wide AI tooling adoption with governance in place from day one.
**Leadership lesson:** AI adoption without governance creates technical debt at AI speed. Define how you use AI before you use it everywhere.

## Quantified Impact Summary
| Metric | Before | After | Context |
|--------|--------|-------|---------|
| P1 incidents | 20/week | 2/month | sennder |
| Navigation cold-start | 55 seconds | 5 seconds | HERE/AUDI A8 |
| QMI adoption | 0% | 50% of org | Delivery Hero |
| Organic order growth | baseline | +35% | Delivery Hero (ML) |
| Customer retention | baseline | +60% | Delivery Hero (ML) |
| Monolith migration | in progress | complete | sennder (6 months) |
| Regrettable attrition | — | 0 | All organisations |


---

<!-- Added: 2026-05-29 16:53 | Category: Case Study | Source: KB Management tab -->

When Product Management struggled to create prototypes because Engineering did not give them Priority, instead of just accepting the situation, Ioanna has introduced librechat as an OSS interface and formulated a small task force to find a way to create an easy way for PMs to query DBs and start with that. the team established MCP servers and agents fed with the figma files required to match the look and feel of the company and the first prototype was able to be achieved without engineering involvement within one week.
