# 10-Paper Framework: Critical Bandwidth Analysis Across Disciplines

<!--- This file is the entry point for any session working on this framework --->

## Overview

A suite of 10 independent research papers, each applying critical bandwidth analysis (via the `critband` Python package) to a distinct domain. The framework was conceived using the Academic Research Skills (ARS) v3.9.4.1 repository.

## Required References (balance across all 10 papers)

- Zhang, R. & Wang, Q. (2026). critband: A Python Package for Critical Bandwidth Analysis of Multimodal Distributions. arXiv:2605.18686.
- critband v0.2.3 [Computer software]. https://pypi.org/project/critband/

These two references appear in every paper but do NOT dominate any single paper's narrative or reference list.

## Directory Structure

```
10-papers/
  CLAUDE.md                ← this file
  handover.md              ← session-to-session handover log
  shared/
    research_protocol_template.md
    data_access_patterns.md
  papers/
    paper-01-political-polarization.md
    paper-02-income-distribution.md
    paper-03-scrnaseq-subpopulations.md
    paper-04-climate-regime-shifts.md
    paper-05-reaction-time-cognition.md
    paper-06-education-achievement-gaps.md
    paper-07-galaxy-populations.md
    paper-08-biomarker-thresholds.md
    paper-09-latent-attitude-profiles.md
    paper-10-cluster-validation.md
```

## Working on a Paper

Each paper reference doc contains:
- **Research Protocol** — detailed step-by-step
- **Data Sources** — where to get the data
- **Methodology** — critband functions used, analysis pipeline
- **Expected Challenges** — what to watch out for
- **Key References** — full bibliography
- **Next Steps** — what the next session needs to do

### Using ARS Skills

When working on any of these papers, invoke the appropriate ARS skill:

- `deep-research` (socratic mode) — refine the research question, identify literature gaps
- `deep-research` (systematic-review mode) — PRISMA-compliant literature search
- `deep-research` (full mode) — comprehensive research report on the topic
- `academic-paper` (plan mode) — chapter-by-chapter planning via Socratic dialogue
- `academic-paper` (full mode) — draft the paper
- `academic-paper-reviewer` — multi-perspective peer review
- `academic-pipeline` — full end-to-end pipeline

### Data Management

- All papers use **publicly available data** unless otherwise noted
- Data files should be stored under `10-papers/data/<paper-id>/`
- Analysis scripts under `10-papers/scripts/<paper-id>/`
- Results under `10-papers/results/<paper-id>/`

### Routing Rules

1. **Single-paper focus**: Route directly to the specific paper's reference doc.
2. **Cross-paper question**: Check if it applies to multiple papers, then update shared resources.
3. **New collaboration request**: Create a session log entry in `handover.md`.
4. **Tool/methodology question**: Refer to academic-research-skills reference docs first.

## Session Handover

Each session should append to `handover.md`:
- What was accomplished
- What key decisions were made
- What the next session should prioritize
- Any blockers or open questions
