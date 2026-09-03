"""DOCTRINE.md §9 — Baseline corpus per engine.

Each engine needs a generic baseline corpus to score against. The DOCTRINE
mandates 10 baseline types per engine (400 total). Day 3 ships representative
text samples for each type; Day 7 wires the weekly cron that scrapes fresh
samples from real LLM outputs + the web.

The baseline_scores_for_engine(slug) helper returns the engine's raw scores
across all 10 baseline samples. Robust-MAD-Z uses that as the comparison
distribution.
"""
from __future__ import annotations
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).parent.parent


# ── The 10 baseline types per DOCTRINE.md §9 ──────────────────────────────
BASELINE_TYPES = (
    "default_llm_output",      # 1. Default Claude/GPT/Gemini outputs
    "linkedin_top_post",       # 2. Top LinkedIn business post
    "medium_top_article",      # 3. Top Medium business article
    "generic_saas_landing",    # 4. Generic SaaS landing page
    "default_consultant_deck", # 5. Default consultant deliverable
    "wikipedia_summary",       # 6. Wikipedia-style summary
    "ai_agency_website",       # 7. AI agency website copy
    "generic_gtm_playbook",    # 8. Generic GTM playbook
    "default_agent_loop",      # 9. Default agent-loop output
    "template_default",        # 10. Off-the-shelf template
)


# ── Static representative samples per baseline type ───────────────────────
# Each is intentionally generic / median to anchor Robust-MAD-Z's baseline.
BASELINE_CORPUS: dict[str, str] = {

"default_llm_output": """
In today's rapidly evolving landscape, organizations must leverage AI to transform their operations and unlock new opportunities. This document outlines a holistic approach to integrating cutting-edge solutions that drive value across the enterprise.

Key benefits include enhanced productivity, improved customer experiences, and accelerated innovation. By harnessing the power of artificial intelligence, businesses can navigate the complexities of the modern marketplace and position themselves for sustained growth.

We recommend a phased rollout starting with pilot programs that demonstrate quick wins, building toward an enterprise-wide deployment. Stakeholder alignment, change management, and ongoing optimization will be critical success factors. Furthermore, establishing clear KPIs and governance frameworks ensures accountability and measurable impact.
""",

"linkedin_top_post": """
🚀 Excited to share my latest reflections on leadership and growth! After 20 years in the industry, here are 7 lessons I've learned that have transformed my approach to business:

1. People over processes
2. Listen more than you speak
3. Embrace failure as feedback
4. Invest in your team's development
5. Customer-centricity drives everything
6. Stay curious, stay humble
7. Take action — perfection is the enemy of progress

What lessons resonate with you? Drop a comment below and let's connect! ⬇️
#Leadership #Growth #Business #Mindset
""",

"medium_top_article": """
How I 10x'd My Productivity Using These 5 Simple Habits

Three years ago, I was drowning. Sixty-hour weeks. Constant overwhelm. The promise of "hustle culture" had become a slow-burning prison.

Then I changed five small habits. And everything shifted.

Here's what I discovered — and why most productivity advice fails you.

1. The 90-minute deep work block
2. The 2-minute rule for small tasks
3. Inbox zero (the right way)
4. Weekly review ritual
5. Saying no without guilt

Each of these took less than 15 minutes to implement, but the compound effects are real.
""",

"generic_saas_landing": """
The All-in-One Platform Built for Modern Teams

Unlock seamless collaboration, drive growth, and scale effortlessly with our powerful, intuitive platform. Trusted by thousands of teams worldwide, our cloud-based solution streamlines your workflows so you can focus on what matters most.

✓ Real-time collaboration
✓ Enterprise-grade security
✓ Integrations with 500+ tools
✓ AI-powered insights
✓ 24/7 world-class support

Get Started Free  ·  Book a Demo  ·  Learn More

Join 50,000+ teams already transforming their work. Start your 14-day free trial — no credit card required.
""",

"default_consultant_deck": """
Strategic Framework for Digital Transformation

EXECUTIVE SUMMARY
As organizations face unprecedented disruption, a comprehensive digital transformation strategy is no longer optional — it is imperative. This deck outlines our proven methodology for accelerating digital maturity across the enterprise.

KEY FINDINGS
- 78% of leading firms have accelerated digital initiatives
- AI adoption is expected to grow by 35% YoY
- Cloud-first organizations outperform peers by 2.4x
- Cybersecurity remains a top board-level concern

OUR APPROACH
Phase 1: Assess  ·  Phase 2: Design  ·  Phase 3: Build  ·  Phase 4: Scale
We bring deep industry expertise and best-in-class frameworks to deliver measurable outcomes.

NEXT STEPS
Schedule a discovery workshop with our senior leadership to align on priorities and define success criteria.
""",

"wikipedia_summary": """
Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by humans or animals. Leading AI textbooks define the field as the study of "intelligent agents": any system that perceives its environment and takes actions that maximize its chance of achieving its goals.

Some popular accounts use the term "artificial intelligence" to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving." However, this definition is rejected by major AI researchers.

AI applications include advanced web search engines, recommendation systems, understanding human speech, self-driving cars, automated decision-making, and competing at the highest level in strategic game systems.
""",

"ai_agency_website": """
We Build AI That Works.

At [Agency], we partner with forward-thinking businesses to design, deploy, and scale custom AI solutions that drive real ROI. From strategy to implementation, our team of seasoned experts brings deep domain knowledge and a passion for innovation.

OUR SERVICES
• AI Strategy & Roadmapping
• Custom Model Development
• Generative AI Integration
• MLOps & Production Deployment
• Training & Enablement

WHY US
✓ 50+ AI projects shipped
✓ Fortune 500 clients
✓ Award-winning team
✓ End-to-end capability

Let's build the future together. Schedule a free consultation today.
""",

"generic_gtm_playbook": """
Go-to-Market Playbook: B2B SaaS Edition

This playbook provides a comprehensive framework for launching a successful B2B SaaS product. It covers segmentation, positioning, channels, and metrics.

STEP 1: DEFINE YOUR ICP
Identify your ideal customer profile based on firmographics, technographics, and behavioral signals.

STEP 2: CRAFT YOUR VALUE PROP
Articulate the unique value your product delivers. Focus on outcomes, not features.

STEP 3: SELECT CHANNELS
Choose 2-3 channels (outbound, inbound, partnerships) where your ICP is most active.

STEP 4: BUILD THE FUNNEL
Design a multi-touch sequence to nurture leads through awareness, consideration, and decision.

STEP 5: MEASURE & ITERATE
Track CAC, LTV, payback period, and net revenue retention. Optimize ruthlessly.
""",

"default_agent_loop": """
Task received. Analyzing requirements...

Step 1: Understanding the user's intent. The query appears to be about [topic].
Step 2: Gathering relevant context from available sources.
Step 3: Synthesizing a response that addresses the core question.
Step 4: Verifying accuracy and clarity.
Step 5: Formatting the output for clear presentation.

Based on the analysis, here is the recommended approach:
- Consider multiple perspectives
- Identify key stakeholders
- Define success metrics
- Implement iteratively
- Measure outcomes

Let me know if you'd like me to elaborate on any of these points or explore additional angles.
""",

"template_default": """
[Title] — [Subtitle]

Introduction
[Insert introductory paragraph describing the topic and why it matters.]

Background
[Provide relevant background information and context.]

Key Points
1. [First main point with supporting details]
2. [Second main point with supporting details]
3. [Third main point with supporting details]

Recommendations
[Outline specific recommendations or next steps.]

Conclusion
[Summarize the key takeaways and call to action.]
""",
}


def get_baseline_samples() -> list[str]:
    """Return all 10 baseline text samples in canonical order."""
    return [BASELINE_CORPUS[t] for t in BASELINE_TYPES]


@lru_cache(maxsize=128)
def baseline_scores_for_engine(slug: str) -> tuple[float, ...]:
    """Return the raw scores of all 10 baseline samples for a given engine.

    Cached per-engine. Recompute by calling cache_clear() after baseline refresh.
    """
    from rig_lattice.adapters.criteria_runner import raw_score_from_criteria
    scores = []
    for sample in get_baseline_samples():
        try:
            score = raw_score_from_criteria(sample, slug)
        except FileNotFoundError:
            # No criteria pack yet — return median 50 for all
            score = 50.0
        scores.append(score)
    return tuple(scores)


def clear_baseline_cache() -> None:
    """Clear the LRU cache (e.g. after weekly recal cron updates samples)."""
    baseline_scores_for_engine.cache_clear()
