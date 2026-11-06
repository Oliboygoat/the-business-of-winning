# The Business of Winning

**Understanding the economics of winning in Major League Baseball.**

A Python and Streamlit dashboard comparing verified Opening Day payroll and regular-season results for 30 franchises across 2021–2026. Explore payroll versus wins, team comparisons, annual trends, consistency, statistical diagnostics and a free deterministic Analyst demo.

**Facts-only real-data release, authorized by the project owner on November 6, 2026.** This package contains real numerical records, not synthetic data. Publisher article captures and raw API responses are deliberately excluded. Read [PUBLICATION_RIGHTS.md](PUBLICATION_RIGHTS.md) for the owner-provided permission confirmation, factual-data rationale and historical acquisition-term questions. The confirmation has not been independently verified. Source attribution is not treated as permission.

## Explore the dashboard

- **Overview:** season selector, key figures and an interactive payroll-versus-wins plot.
- **Explore Teams:** league/division filters, rankings, comparisons and franchise trends.
- **Insights:** evidence-based team stories and cautious business interpretation.
- **AI Analyst:** supported questions answered by verified Python functions, without a key or paid request. Unsupported questions are declined.
- **Methodology:** sources, formulas, annual regressions, Colorado sensitivity, assumptions and downloadable numerical results.

The minimalist design uses system typography, rounded cards, restrained colors and interactive Plotly charts. The Analyst is a limited question router, not a language model. Paid AI cannot be enabled through secrets, environment flags, prompt text or public controls.

## Research scope

The six-season panel contains exactly **180 records**. Payroll uses AP Opening Day figures in 2021 and 2023–2026; **2022 uses The Baseball Cube on a separately labeled basis**. Default multi-year analysis includes the five AP seasons. Including 2022 requires explicit opt-in, with a separate Analyst permission. This restriction is methodological, not removed by a publication-rights decision.

Each season has its own 30-team ordinary least squares model. Pearson correlation and R² describe association; residuals compare actual wins with that season's fitted payroll benchmark. Multi-year consistency averages annual residuals descriptively, without treating repeated franchises as independent experiments. Colorado remains in primary models; exclusion is a sensitivity check. March BLS CPI-U converts spending into March 2026 purchasing power when selected.

Payroll per win is payroll divided by all regular-season wins. It does not measure profit, revenue, total investment, management quality or a causal return to spending. Fits are not validated forecasts. Accounting differences, 161-game records, small samples, teams playing one another and omitted performance factors remain documented.

[Six-season sources and definitions](MULTISEASON_SOURCES.md) · [2025 source notes](DATA_SOURCES.md) · [Public verification boundary](VERIFICATION.md)

## Run locally

Use **Python 3.12**. Runtime packages are pinned in the root `requirements.txt`: Streamlit 1.66.1, pandas 3.1.0, NumPy 2.5.4, Plotly 7.1.0 and SciPy 1.18.1.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Windows activation: `.venv\Scripts\activate`. No API key, `.env` or Streamlit secret is needed. The app reads bundled numerical inputs with portable paths and makes no live source or provider request to answer demo questions.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/verify_public_data.py
python scripts/check_publication.py
```

Development dependencies include an SDK solely for mocked protocol tests. Public runtime requirements exclude it. In a separate runtime-only environment, run `python scripts/smoke_public.py --require-no-sdk` to exercise the seasonal views, filters and all demo examples while blocking outbound connections.

Public verification uses frozen input/row fingerprints established after a private source rebuild, plus independent mathematical tests. It does not claim fresh source re-extraction. Private captures and original historical commits are not needed to run this candidate or its tests.

## Project structure

```text
app.py                         Streamlit entrypoint
analytics.py, multi_analytics.py Original analytical functions
charts.py, ui.py, assets/       Charts and visual design
sections.py, multi_ui.py        Dashboard sections
research_ui.py                 Detailed methodology and diagnostics
analyst/                       Read-only demo and disabled API gateway
data/                         Three factual input CSVs and provenance
publication/                   Exact inventory, fingerprints and rights status
scripts/, tests/               Verification, smoke test and full test suite
```

## Publication status

This candidate is isolated from the private research history. The owner-authorized target is GitHub `main` and Streamlit `app.py`, Python 3.12, root `requirements.txt`, **Secrets empty**. No workflow deploys the app. `python scripts/check_publication.py --require-clearance` checks the recorded owner release decision; it does not independently verify a license. Streamlit deployment remains unapproved. See [PUBLICATION_RIGHTS.md](PUBLICATION_RIGHTS.md) for the narrow practical next steps.

This independent project is not affiliated with or endorsed by MLB, AP or the cited publishers. No publisher text, page layout, photograph or source capture is licensed through this repository. No blanket license is assigned over third-party rights. Source URLs and historical capture hashes remain for transparency.
