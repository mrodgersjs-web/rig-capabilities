# 20 GitHub Repos for RIG Signal Detection Stack

Mapped to the 7 signal layers of the V10 Idea Engine.

---

## Weak Signal & Horizon Scanning (S1, S3)

| # | Repo | Signal Layer | What It Does |
|---|------|-------------|---------------|
| 1 | [gautamHCSCV/Detecting-Emerging-Technologies](https://github.com/gautamHCSCV/Detecting-Emerging-Technologies-and-their-Evolution-using-Deep-Learning-and-Weak-Signal-Analysis-) | S1, S3 | Multi-layer quantitative approach: identifies future signs from scientific publications using deep learning + weak signal analysis |
| 2 | [KamranNiroomand/TechnologyEmergenceDetection](https://github.com/KamranNiroomand/TechnologyEmergenceDetection) | S1, S3 | BERT-based emerging tech detection + evolution tracking — identifies vocabulary drift before it becomes consensus |
| 3 | [DesignThinkingJapan/future-signals-2026-report](https://github.com/DesignThinkingJapan/future-signals-2026-report) | S1, S7 | Future Signals architecture: 5 signals reshaping enterprise AI, 390+ references, multi-model scanning methodology |
| 4 | [manthanK1/Open-Source-Signal-Intelligence-Early-Anomaly-Detection-Platform](https://github.com/manthanK1/Open-Source-Signal-Intelligence-Early-Anomaly-Detection-Platform) | S1, S5 | Early anomaly detection using news, prediction markets, shipping flows, geo-economic signals |

## Social Discourse & Wound Detection (S2, S6)

| # | Repo | Signal Layer | What It Does |
|---|------|-------------|---------------|
| 5 | [AbhayAyare/Social-Media-Trend-Tracker](https://github.com/AbhayAyare/Social-Media-Trend-Tracker) | S2, S6 | Analyzes social media trends, sentiment, emerging topics using NLP — tracks Twitter/Reddit for real-time wound signals |
| 6 | [davidjosipovic/news-trend-analysis](https://github.com/davidjosipovic/news-trend-analysis) | S1, S2 | Automated NLP pipeline: sentiment detection + topic modeling + summarization with daily GitHub Actions updates |
| 7 | [giangnguyen2412/TrendAnalysis-and-IssueTracking-in-NLP](https://github.com/giangnguyen2412/TrendAnalysis-and-IssueTracking-in-NLP) | S2, S4 | Trend analysis + issue tracking from newspaper collections — identifies recurring wound patterns over time |
| 8 | [momo-shogun/Trends-Tracker](https://github.com/momo-shogun/Trends-Tracker) | S2, S6 | Real-time dashboard visualizing trending topics: frequent words, sentiment, engagement patterns |

## Deep Research & Proof Mining (S5, S7)

| # | Repo | Signal Layer | What It Does |
|---|------|-------------|---------------|
| 9 | [stanford-oval/storm](https://github.com/stanford-oval/storm) (28.2k stars) | S5, S7 | Multi-perspective research — generates full reports with citations. Powers proof gap detection |
| 10 | [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) | S5, S7 | Fully automated data synthesis pipeline — deep research at scale for evidence mining |
| 11 | [HKUDS/AI-Researcher](https://github.com/HKUDS/AI-Researcher) | S3, S7 | Academic research agent: literature discovery, novelty assessment, hypothesis generation |
| 12 | [Ed1sonChen/DailyArxiv](https://github.com/Ed1sonChen/DailyArxiv) | S3, S7 | Daily arXiv paper tracking — catches vocabulary drift and new frameworks from academic frontier |

## Multi-Agent Orchestration (Tournament + Writing)

| # | Repo | Signal Layer | What It Does |
|---|------|-------------|---------------|
| 13 | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | Tournament | Multi-agent orchestration — run Red Team vs Blue Team debates, parallel writer agents, scorer agents |
| 14 | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | Tournament | Stateful graph-based workflows — model the idea tournament as a directed graph with conditional branching |
| 15 | [microsoft/autogen](https://github.com/microsoft/autogen) | Tournament | Multi-agent conversation framework — ensemble draft generation + adversarial evaluation |
| 16 | [camel-ai/owl](https://github.com/camel-ai/owl) | S5, Tournament | Multi-modal agent UI — orchestrate research agents across text, image, and data modalities |

## Anomaly Detection & Statistical Deviation (S1, S5)

| # | Repo | Signal Layer | What It Does |
|---|------|-------------|---------------|
| 17 | [yzhao062/anomaly-detection-resources](https://github.com/yzhao062/anomaly-detection-resources) | S1, S4 | 20+ outlier detection algorithms — adaptable for detecting content that deviates from median in any corpus |
| 18 | [tinybirdco/use-case-real-time-anomaly-detection](https://github.com/tinybirdco/use-case-real-time-anomaly-detection) | S1, S5 | Real-time anomaly detection: Z-score, IQR, rate-of-change — directly maps to MAD-Z scoring |

## Memory, Learning & Calibration

| # | Repo | Signal Layer | What It Does |
|---|------|-------------|---------------|
| 19 | [langfuse/langfuse](https://github.com/langfuse/langfuse) | All | LLM observability — trace every generation, score, and swarm prediction for Brier calibration over time |
| 20 | [Papr-ai/memory-opensource](https://github.com/Papr-ai/memory-opensource) | All | Open-source memory layer — store winning patterns, hook libraries, villain class registries, engagement data |

---

## Usage Pattern

For each pipeline stage:

**Signal Detection (S1-S7):** Repos 1-8 + 17-18 provide the raw signal pipeline. Combine STORM (9) or DeepResearch (10) for evidence mining. Use DailyArxiv (12) for vocabulary drift tracking.

**Idea Tournament:** CrewAI (13) for multi-agent orchestration. LangGraph (14) for the directed graph with conditional branching. AutoGen (15) for adversarial debate (Red Team vs Blue Team). CAMEL OWL (16) for multi-modal research integration.

**Memory & Learning:** Langfuse (19) traces every generation, score, and prediction. Papr (20) stores institutional memory. Combined they enable the Brier calibration loop — every shipped artifact makes the system smarter.
