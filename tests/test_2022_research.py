"""The private AP search stays private; the published 2022 facts stay unchanged."""
import hashlib
import json
import pandas as pd
import pytest
from analytics import ROOT
from multi_analytics import load_panel,cohort
from scripts.verify_public_data import verify_rows,baseline
from analyst.demo import answer_demo


def test_all_thirty_2022_tbc_rows_match_export_baseline():
    panel=load_panel();before=panel.copy(deep=True)
    assert verify_rows()==180
    data=panel[panel.season==2022]
    assert len(data)==data.team_id.nunique()==30
    assert data.payroll_source_url.eq('https://www.thebaseballcube.com/content/payroll_year/2022/').all()
    pd.testing.assert_frame_equal(panel,before)


def test_2022_stays_tbc_without_an_invented_ap_replacement():
    data=load_panel().query('season == 2022')
    assert data.payroll_basis.eq('TBC_OPENING_DAY_ALTERNATE').all()
    assert 'ap_exact_payroll' not in data and 'ap_narrative_millions' not in data
    status=json.loads((ROOT/'publication/rights_status.json').read_text())
    assert status['tbc_payroll_records']==30
    assert status['ap_2022_replacement_recovered'] is False


def test_unneeded_narrative_comparisons_are_private_and_2022_guard_stays():
    # No indicative AP narrative comparisons enter this minimal release.
    assert not (ROOT/'research/2022_ap/ap_vs_tbc_partial_comparison.csv').exists()
    panel=load_panel()
    assert not answer_demo('Show Brewers payroll and wins change from 2021 to 2026.',panel)['ok']
    assert answer_demo('Who had the lowest payroll per win in 2022?',panel)['ok']
    assert answer_demo('Show Brewers payroll and wins change from 2021 to 2026.',panel,allow_mixed=True)['ok']


def test_production_bytes_cohort_and_source_rules_are_preserved():
    for name,digest in baseline()['preserved_files_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    panel=load_panel()
    assert len(panel)==180 and panel.groupby('season').size().eq(30).all()
    assert set(cohort(panel).season)=={2021,2023,2024,2025,2026}
    assert panel[panel.season==2022].payroll_basis.eq('TBC_OPENING_DAY_ALTERNATE').all()
