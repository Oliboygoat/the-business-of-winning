# Proposed public inventory

**Owner-authorized 62-file real-data release. Permission confirmation recorded November 6, 2026; see `PUBLICATION_RIGHTS.md`.**

This candidate contains **62 tracked files**. `publication/public_inventory.json` supplies their exact SHA-256 digests (except its self-entry); the private preparation receipt seals that inventory. File inclusion follows the owner-approved candidate; it does not itself grant a license.

## Exact proposed file list

| Path | Purpose |
|---|---|
| `.env.example` | Non-secret configuration, dependencies or original styling |
| `.github/workflows/checks.yml` | Non-secret configuration, dependencies or original styling |
| `.gitignore` | Non-secret configuration, dependencies or original styling |
| `.python-version` | Non-secret configuration, dependencies or original styling |
| `.streamlit/config.toml` | Non-secret configuration, dependencies or original styling |
| `.streamlit/secrets.example.toml` | Non-secret configuration, dependencies or original styling |
| `AI_ANALYST.md` | Original documentation |
| `DATA_SOURCES.md` | Original documentation |
| `MULTISEASON_SOURCES.md` | Original documentation |
| `PUBLICATION_INVENTORY.md` | Original documentation |
| `PUBLICATION_RIGHTS.md` | Original documentation |
| `README.md` | Original documentation |
| `VERIFICATION.md` | Original documentation |
| `analyst/__init__.py` | Original runtime and Analyst code |
| `analyst/demo.py` | Original runtime and Analyst code |
| `analyst/openai_service.py` | Original runtime and Analyst code |
| `analyst/security.py` | Original runtime and Analyst code |
| `analyst/tools.py` | Original runtime and Analyst code |
| `analyst/ui.py` | Original runtime and Analyst code |
| `analytics.py` | Original runtime and Analyst code |
| `app.py` | Original runtime and Analyst code |
| `assets/style.css` | Non-secret configuration, dependencies or original styling |
| `audit/results.json` | Original statistical diagnostics |
| `charts.py` | Original runtime and Analyst code |
| `data/multiseason/cpi_march.csv` | Verified numerical input |
| `data/multiseason/provenance.json` | Source citations and historical hashes |
| `data/multiseason/teams_2021_2026.csv` | Verified numerical input |
| `data/provenance.json` | Source citations and historical hashes |
| `data/teams_2025.csv` | Verified numerical input |
| `executive.py` | Original runtime and Analyst code |
| `multi_analytics.py` | Original runtime and Analyst code |
| `multi_ui.py` | Original runtime and Analyst code |
| `publication/private_exclusions.json` | Provenance, rights status, verification or inventory |
| `publication/public_inventory.json` | Provenance, rights status, verification or inventory |
| `publication/rights_status.json` | Provenance, rights status, verification or inventory |
| `publication/validation.json` | Provenance, rights status, verification or inventory |
| `publication/verification_baseline.json` | Provenance, rights status, verification or inventory |
| `pytest.ini` | Non-secret configuration, dependencies or original styling |
| `requirements-ai-test.txt` | Non-secret configuration, dependencies or original styling |
| `requirements-dev.txt` | Non-secret configuration, dependencies or original styling |
| `requirements-lock.txt` | Non-secret configuration, dependencies or original styling |
| `requirements.txt` | Non-secret configuration, dependencies or original styling |
| `research_ui.py` | Original runtime and Analyst code |
| `scripts/audit_release.py` | Automated verification |
| `scripts/check_publication.py` | Automated verification |
| `scripts/smoke_public.py` | Automated verification |
| `scripts/verify_public_data.py` | Automated verification |
| `sections.py` | Original runtime and Analyst code |
| `tests/test_2022_research.py` | Automated verification |
| `tests/test_accessible_content.py` | Automated verification |
| `tests/test_analyst_ai.py` | Automated verification |
| `tests/test_analyst_demo.py` | Automated verification |
| `tests/test_analytics.py` | Automated verification |
| `tests/test_app.py` | Automated verification |
| `tests/test_audit.py` | Automated verification |
| `tests/test_executive.py` | Automated verification |
| `tests/test_facts_only_package.py` | Automated verification |
| `tests/test_multiseason.py` | Automated verification |
| `tests/test_multiseason_ui.py` | Automated verification |
| `tests/test_public_release.py` | Automated verification |
| `tests/test_redesign.py` | Automated verification |
| `ui.py` | Original runtime and Analyst code |

## Remains private

- Complete original repository and all of its historical commits; no ancestor is imported into this repository.
- All eight publisher HTML/text captures and fourteen raw MLB JSON responses, including duplicate audit captures. Exact excluded source paths/blob IDs are in `publication/private_exclusions.json`.
- Ignored newspaper PDFs and syndicated HTML, the full 2022 AP research dossier, rounded comparison records, the 2025 AP/TBC comparison dataset, source acquisition/rebuild scripts and historical source-reconciliation tests.
- Existing screenshots, old audit reports and development research intermediates not necessary to run this candidate.
- Recovery bundles, local environments, secrets/credential locations, runtime ledgers and other ignored files. No actual secret values are included in this inventory.

The original private project retains every original file, including the original versions of candidate-adapted documentation/tests. A private file-by-file export receipt distinguishes unchanged, adapted and unexported originals. Source URLs and hashes can be retained publicly without distributing source contents.

## Proposed numerical scope and review status

Only three CSV inputs are proposed: 180 unique team-season records, the required 30-row duplicate 2025 input, and six CPI observations. TBC supplies only 30 payroll values for 2022; no extra TBC 2025 dataset or AP 2022 narrative figures are exported. Calculated outputs in the diagnostics/baseline are project-generated results.

Read `PUBLICATION_RIGHTS.md` and `publication/rights_status.json`: the owner-provided permission and GitHub release approval are recorded separately from the historical legal assessment. The confirmation was not independently verified. Streamlit deployment remains unapproved.
