# Verification boundary for the facts-only export

The original verified project and complete source archive remain private. This public candidate has fresh Git history and deliberately contains no source captures. A missing private file is never converted into a skipped or silently passing source audit.

## What is unchanged

All three CSV inputs, original runtime/Analyst modules, analytical functions, chart builders, CSS and saved 2025 diagnostics match their private baseline SHA-256 values. `research_ui.py` retains the same calculations and layout; only reproducibility instructions were corrected for the absence of captures. Source documentation is the project's own explanation with the same definitions, qualifications and direct citations, corrected to identify private archives honestly.

Before export, all 180 source rows were rebuilt from the original private captures and compared to the verified CSV. Their canonical row hashes, source identifiers and saved analytical outputs were frozen in `publication/verification_baseline.json`. Hashes detect a change relative to that baseline; they do not independently establish whether the publisher was correct, prove a license, or prevent someone deliberately changing both data and manifest.

## Test adaptation

The original **118-test suite remains intact in the private project**. In this isolated candidate, ten source-dependent test functions across six test files were adapted:

- `test_analytics.py`: raw capture hash checks become retained input/code hashes and explicit no-capture checks.
- `test_multiseason.py`: two source-coverage/rebuild checks become manifest-scope and all-180-row fingerprint checks. Independent seasonal math, mappings, invalid-input and cohort tests remain.
- `test_audit.py`: the fresh-source check becomes a correctly labeled export-fidelity check. Independent formula, filter and influence assertions remain.
- `test_accessible_content.py`: an old private-commit lookup becomes the frozen exported-input/module fingerprint check.
- `test_redesign.py`: preservation hashes refer to retained files, not omitted capture files.
- `test_2022_research.py`: four checks over the unshipped rounded-AP research comparison/history become 2022 TBC row fidelity, absence of a fabricated AP replacement, absence of unneeded narrative figures and explicit source-rule/Analyst permission checks. Private research arithmetic tests remain available privately.

No test is skipped because its capture is missing. The public suite retains 118 baseline test cases after these transparent adaptations and adds six package-specific cases: complete numerical output reconciliation, detection of a changed payroll record, exact inventory/history exclusion, unresolved-rights gating the minimal CSV footprint and direct command-line execution without pytest path setup. The final run result is recorded in `publication/validation.json`.

## Reproduce locally

```bash
python scripts/verify_public_data.py
python -m pytest -q
python scripts/check_publication.py
```

Verification recomputes annual models, Colorado sensitivity and both AP-only/mixed-source consistency tables with unchanged analytical functions. Original interface tests exercise selectors, chart values, rankings, comparisons, methodology and chat/source restrictions. The no-SDK runtime smoke test runs independently of the development SDK. The closed inventory enumerates every proposed public file and all hashes except the inventory's own self-entry; a private receipt seals that inventory's hash.

Source re-extraction requires separately obtained source access and the private reproducibility pipeline. The original private captures, PDFs, full source comparison data, historical source-dependent tests, historical Git objects and recovery bundles are excluded from this repository. Metadata hashes/URLs identify them without reproducing them.

`python scripts/check_publication.py --require-clearance` is expected to fail while rights questions or final owner approval remain unresolved. That expected refusal is distinct from a failed functional test. GitHub-hosted CI, public network behavior and Community Cloud deployment have not run; no push or deployment has been performed.
