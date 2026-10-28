# Facts-only real-data publication candidate

**October 27, 2026 · Local preparation only · Rights questions remain open.**

This package is proposed for a real MLB research dashboard, not a synthetic demonstration. It has fresh local Git history and excludes publisher articles/page extracts, raw MLB responses, newspaper issues, private recovery archives and unnecessary comparison datasets. Technical readiness does not itself establish legal clearance. No push or deployment is authorized by this document.

## Exactly which data is proposed

| File | Contents and reason retained |
|---|---|
| `data/multiseason/teams_2021_2026.csv` | 180 franchise-season rows: 30 clubs in each of six seasons. Fields are season, team/franchise IDs and names, league/division, nominal Opening Day payroll, regular-season wins/losses/runs, payroll-definition label and source identifiers/URLs. No player contracts, biographies, article narrative or page design. |
| `data/teams_2025.csv` | The original 30-row 2025 input, unchanged. Required by the existing single-season loader and panel cross-check. These are duplicate observations within the 180-row panel, not another 30 unique payrolls. |
| `data/multiseason/cpi_march.csv` | Six BLS March CPI-U observations. Used only for the existing inflation transformation. |
| `audit/results.json` | Original project-generated 2025 regression/influence diagnostics, plus historical source hashes. No raw responses. |
| `publication/verification_baseline.json` | Own input/code fingerprints, all 180 row digests, and project-generated annual/Colorado/consistency outputs used to demonstrate unchanged analysis. These are provenance and our mathematical outputs, not another publisher dataset. |
| Provenance JSONs and source notes | Bibliographic links, historical archive hashes, definitions and original methodological explanations. Historical source filenames identify private evidence; they do not promise that captures are included. |

There are **150 AP-based payroll observations** (2021, 2023–2026) and **30 TBC payroll observations** (2022). Standings and identity fields were extracted from MLB sources. No 2025 TBC comparison payrolls or rounded 2022 AP narrative figures are included. Calculations, fixture values, charts and download responses can disclose retained facts too; those uses are included in the proposed scope, not hidden by calling the inputs “minimal.”

All three input CSVs are byte-identical to the verified private baseline. The full current file list and hashes are in `publication/public_inventory.json`. `publication/private_exclusions.json` identifies excluded source paths/blob IDs without reproducing their contents. The original private repository retains the complete broader audit trail.

## Copyright basis being considered

Individual facts are generally outside copyright protection, while original writing and original selection/coordination/arrangement may be protected. A factual collection does not gain ownership of its numbers merely through collection effort. The proposed panel uses ordinary franchise-season identifiers and a project-designed schema rather than republishing article presentation. That supplies a credible facts-only rationale; lack of an open license is not by itself a copyright prohibition. It is not an adjudication of the particular source material. [Copyright Office](https://copyright.gov/help/faq/faq-protect.html), [Feist Publications v. Rural Telephone, 499 U.S. 340 (1991)](https://supreme.justia.com/cases/federal/us/499/340/), [17 U.S.C. §103](https://www.govinfo.gov/content/pkg/USCODE-2024-title17/html/USCODE-2024-title17-chap1-sec103.htm).

Recorded results and computed payroll aggregates should be examined separately from any genuinely judgmental valuation. The payroll accounting choices, and any claim to protected estimates/selection, need specific identification rather than a presumption either way. [CCC Information Services v. Maclean Hunter, 44 F.3d 61 (2d Cir. 1994)](https://law.justia.com/cases/federal/appellate-courts/F3/44/61/513081/) involved editorial vehicle valuations; it does not decide that these payroll totals are protected. Our regressions, formulas, original descriptions and visual layouts remain our analytical contribution. No fair-use claim is needed for an unprotected fact; this package does not rely on fair use to distribute full articles.

Attribution documents provenance and avoids misleading ownership claims. It is **not** treated as contractual permission, and this candidate does not purport to grant an open license over any third party's rights. Choosing a license for original code is a separate owner decision.

## Acquisition terms: precise open issues

Contractual limits are a separate inquiry from copyright. *ProCD* illustrates enforceable agreed limits on data use; *Nguyen* illustrates that notice and assent matter. Their circumstances and governing law must be applied, not assumed. Current terms do not by themselves prove what was accepted when the original captures were acquired. [ProCD v. Zeidenberg](https://law.justia.com/cases/federal/appellate-courts/F3/86/1447/538242/), [Nguyen v. Barnes & Noble](https://cdn.ca9.uscourts.gov/datastore/opinions/2014/08/18/12-56628.pdf).

| Source | Proposed use and evidence | Narrow question to resolve |
|---|---|---|
| AP, including syndications | Only 150 reported payroll amounts and original analytical outputs; source citations retained. [AP terms](https://www.ap.org/terms-and-conditions/) assert limits on distribution of covered material, including data. | What protected material, if any, is copied by this neutral factual panel? Did applicable AP terms bind the recorded acquisition, and would a binding restriction cover these uses? Identify whether any payroll number is a protected estimate rather than factual accounting. |
| Sun-Times 2021 | One 30-team factual extraction; no article or HTML. [Host terms](https://chicago.suntimes.com/legal/terms-of-use) separately assert personal-use, extraction and republication restrictions. | Establish terms presented, notice/assent and applicability to the particular source request, plus any relevant defenses/preemption. A host's AP syndication rights do not automatically license us. |
| theScore 2023–2025 | Three 30-team factual extractions; no pages. [Host terms §§3,6,7](https://thescoresupport.zendesk.com/hc/en-us/articles/13873292631949-Terms-of-Use) separately restrict reuse and automated downloading. | Same acquisition/assent/scope question for these requests, distinct from whether the underlying facts are copyrighted. |
| MLB standings and identities | Only club-season facts/identifiers, not entire API objects. The [legacy MLBAM notice](https://gdx.mlb.com/components/copyright.txt) restricts bulk and nonindividual uses; its referring-page scope must not automatically be assigned to another endpoint. | Which terms, if any, govern the saved StatsAPI requests and bind this use? Can these extracted records be distributed on that basis, or should equivalent permitted inputs be independently verified? |
| BLS CPI | Six observations; [BLS expressly identifies its material as public domain](https://www.bls.gov/bls/linksite.htm), with stated image exceptions. | Reuse supported with citation; no BLS emblem or third-party image is included. This does not clear payroll/MLB records. |

The private manifests distinguish HTTP capture from web retrieval and record unsuccessful requests. In particular, AP 2026/TBC web-tool retrieval followed direct HTTP 403 responses. No new access-control bypass was performed for this candidate. Those records do not establish whether terms were accepted or avoided. No account or clickwrap-assent evidence was established by the assessment; absence of that evidence is not proof no agreement exists. A focused reviewer can inspect the privately retained acquisition records with owner authorization. Simply changing the file format or obtaining the same numbers through a mirror does not resolve that question.

## The Baseball Cube: limited 2022 use

The [TBC FAQ](https://www.thebaseballcube.com/content/about/faq.asp) affirmatively allows use of parts of its data with reference/attribution, while drawing a boundary at using the entire database to support another site. This is permission evidence rather than an inference from public accessibility.

This uses all 30 rows of the 2022 team-payroll table, not just a handful of examples, but it is one bounded subsection of TBC’s much larger database. That plausibly fits the FAQ’s distinction between parts and the entire database; it is not an assertion of a universal safe quantity. The candidate names TBC, links the 2022 source and retains the different-definition warning. No TBC page, full database, player-level feed or additional TBC comparison dataset is distributed. The arithmetic outputs are our own.

The FAQ does not expressly define public GitHub cloning, CSV downloads or onward reuse. Confirm that this bounded extract and those distribution modes fit its permission, either through a narrowly worded clarification or qualified interpretation. Do not infer an unrestricted sublicensing grant or guarantee that TBC can license every upstream right. The 2022 analysis stays excluded by default even if reuse is resolved: permission does not reconcile its accounting with AP.

## Scope of a decision needed before publishing

Ask a qualified U.S. copyright/technology reviewer to evaluate **this candidate**, the factual CSV fields and the private acquisition records. A defensible conclusion may support factual use without obtaining every publisher's license. If a specific binding restriction remains, seek only the permission needed for this actual scope:

- public GitHub storage and cloning of the limited numerical records;
- a free public analytical app, charts, rankings, deterministic chat and CSV/result downloads;
- attribution, original transformations, retention and any onward-redistribution limits.

No contacts or purchases have been made. No broad archive, live feed or commercial data resale is proposed. Do not claim contractual certainty from the fact that the app is free or academically oriented.

`publication/rights_status.json` records unresolved questions and missing final owner approval. `python scripts/check_publication.py` validates packaging; **`python scripts/check_publication.py --require-clearance` intentionally fails** until those specific rights decisions and approval are documented. This is a review gate, not a legal determination or an unbypassable security control.

## Technical and research integrity

The original repository, source captures, complete audit/research work and verified recovery bundles remain local/private. The public candidate has no parent commit from that history and no remote. The original source-reconciliation tests remain private. Public source-dependent tests have been transparently adapted to frozen export fingerprints, with no skipped tests pretending to re-extract absent sources. All mathematical and interface assertions remain, and public verification independently recomputes annual models, both consistency cohorts and Colorado sensitivity.

The interface/layout is retained. Only the reproducibility expander's instructions and source notes were corrected to explain that captures are not distributed. The app's input CSVs, analytical functions, chart code, selectors, team comparisons and free Analyst code are unchanged. Paid AI stays disabled in code; runtime dependencies omit its SDK. No synthetic values, replacement payroll definitions or new AP 2022 figures are introduced.

This is a technically runnable local real-data candidate, **not a cleared public release**. Nothing should be pushed or deployed until the specific rights basis is resolved and the owner approves this exact artifact.
