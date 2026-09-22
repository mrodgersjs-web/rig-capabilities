# 20 Additional GitHub Repos — Writing, Behavioral Science & Communication Enhancement

Complementary to the 20 signal detection repos in SIGNAL_DETECTION.md. These repos cover writing quality, NLP evaluation, behavioral science, persuasion analysis, and communication effectiveness — direct inputs to the RIG V10/V15 scoring and generation pipeline.

---

## Writing Quality & NLP Evaluation

| # | Repo | What It Does | RIG Application |
|---|------|-------------|----------------|
| 1 | [**salaniz/pycocoevalcap**](https://github.com/salaniz/pycocoevalcap) | Python implementation of Microsoft COCO caption evaluation — BLEU, METEOR, ROUGE, CIDEr, SPICE metrics | Foundation for evaluating artifact quality relative to baseline |
| 2 | [**google-research/bleurt**](https://github.com/google-research/bleurt) (1.6k stars) | BLEURT: Learning robust metrics for text generation — BERT-based learned evaluation | Replace rule-based scoring with learned quality assessment |
| 3 | [**neulab/BARTScore**](https://github.com/neulab/BARTScore) | Text generation evaluation as text generation — BART-based zero-shot evaluation | Score deviation from median baseline using generation probability |
| 4 | [**salesforce/decaNLP**](https://github.com/salesforce/decaNLP) (5.8k stars) | The Natural Language Decathlon — 10 NLP tasks in one model | Multi-task evaluation framework for communication quality |
| 5 | [**textstat/textstat**](https://github.com/textstat/textstat) | Python package to calculate readability statistics — Flesch-Kincaid, Dale-Chall, SMOG, etc. | Readability gates for different audience sophistication levels |

---

## Persuasion & Behavioral Science

| # | Repo | What It Does | RIG Application |
|---|------|-------------|----------------|
| 6 | [**yangkevin2/emnlp22-persuasiveness**](https://github.com/yangkevin2/emnlp22-persuasiveness) | EMNLP 2022: Predicting and analyzing persuasiveness in text | Empirical models for persuasion scoring without manipulation |
| 7 | [**behavioral-ds/awesome-behavioral-data-science**](https://github.com/behavioral-ds/awesome-behavioral-data-science) | Curated list of behavioral data science resources — behavioral economics, cognitive biases, decision science | Evidence base for psychological reactance gate, autonomy protocols |
| 8 | [**facebookresearch/vizseq**](https://github.com/facebookresearch/vizseq) (1.4k stars) | Visual analysis toolkit for text generation — attention visualization, saliency maps | Visualize which words drive BDF30 scores |
| 9 | [**thoppe/Psychological-Questionnaire-Analysis**](https://github.com/thoppe/Psychological-Questionnaire-Analysis) | Statistical analysis of psychological questionnaires — factor analysis, reliability | Validate scoring inter-rater reliability (Krippendorff's alpha) |
| 10 | [**allenai/nlp-abcd**](https://github.com/allenai/nlp-abcd) | AllenNLP + behavioral change detection in text — discourse and rhetoric patterns | Feed rhetoric analysis into CatchphraseScore and CraftCoefficient |

---

## Linguistic Style & Voice Analysis

| # | Repo | What It Does | RIG Application |
|---|------|-------------|----------------|
| 11 | [**PrithivirajDamodaran/Styleformer**](https://github.com/PrithivirajDamodaran/Styleformer) (1.2k stars) | Neural text style transfer — casual↔formal, active↔passive | Detect and manipulate archetype voice (Eminem, Hemingway, Didion) |
| 12 | [**thoppe/Simple-ROUGE**](https://github.com/thoppe/Simple-ROUGE) | Simple ROUGE implementation — n-gram overlap scoring for text similarity | Measure catchphrase uniqueness against corpus |
| 13 | [**facebookresearch/fairseq**](https://github.com/facebookresearch/fairseq) (30k+ stars) | Sequence-to-sequence toolkit — translation, summarization, language modeling | Backbone for custom text scoring models |
| 14 | [**microsoft/DialoGPT**](https://github.com/microsoft/DialoGPT) (10k+ stars) | Large-scale pretrained dialogue response generation model | Baseline for "what generic AI would write" — compute median baseline |
| 15 | [**coqui-ai/TTS**](https://github.com/coqui-ai/TTS) (36k+ stars) | Deep learning text-to-speech — multi-speaker, voice cloning | Read drafts aloud for sonic edge testing (CatchphraseScore sonic dimension) |

---

## Content Analysis & Competitive Intelligence

| # | Repo | What It Does | RIG Application |
|---|------|-------------|----------------|
| 16 | [**explosion/spaCy**](https://github.com/explosion/spaCy) (30k+ stars) | Industrial-strength NLP — entity recognition, dependency parsing, text classification | Extract named entities, rhetorical structures, and wound patterns from competitor content |
| 17 | [**huggingface/transformers**](https://github.com/huggingface/transformers) (135k+ stars) | State-of-the-art ML for text — sentiment, classification, generation | Backend for all custom scoring models in V14 pipeline |
| 18 | [**microsoft/LMOps**](https://github.com/microsoft/LMOps) (3k+ stars) | General technology for enabling AI capabilities with LLMs and MLOps | Pipeline orchestration for automated scoring → generation → evaluation loops |
| 19 | [**allenai/allennlp**](https://github.com/allenai/allennlp) (12k+ stars) | Open-source NLP research library — built on PyTorch | Train custom models for wound detection, mirror accuracy scoring |
| 20 | [**thunlp/OpenPrompt**](https://github.com/thunlp/OpenPrompt) (4.4k stars) | Open-source framework for prompt-learning — template-based text generation | Generate 50 tournament angles from signal cards using structured prompts |

---

## Integration Map: Where Each Repo Feeds

```
SIGNAL DETECTION (20 repos from SIGNAL_DETECTION.md)
  ↓
IDEA TOURNAMENT (CrewAI + LangGraph + OpenPrompt)
  ↓
CONTENT EVALUATION (bleurt, BARTScore, textstat, Styleformer)
  ↓  ← WRITING QUALITY (pycocoevalcap, BLEURT, spaCy)
  ↓  ← BEHAVIORAL SCIENCE (emnlp22-persuasiveness, behavioral-ds)
  ↓  ← LINGUISTIC STYLE (Styleformer, fairseq, DialoGPT)
  ↓
GATE ENFORCEMENT (gates.py with reactance + entropy validation)
  ↓
PREDICTION SWARM (8 personas with Brier calibration)
  ↓
POST-SHIP LEARNING (Langfuse + Papr memory)
```

---

## Quick-Start Recommendations

**For V11 (signal detection):** STORM + Alibaba DeepResearch + spaCy + transformers for NLP pipeline
**For V12 (tournament):** CrewAI + LangGraph + OpenPrompt for angle generation
**For V13 (ensemble writing):** Styleformer + DialoGPT + DialoGPT for style transfer across archetypes
**For V14 (calibration):** BLEURT + BARTScore + textstat for automated quality scoring
**For V15 (studio):** Langfuse + Microsoft LMOps for full pipeline observability
