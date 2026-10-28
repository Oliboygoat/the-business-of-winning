"""The public candidate is self-contained without importing private research."""
from pathlib import Path
import hashlib
import json
import subprocess
import pytest
from analytics import ROOT
from scripts.check_publication import check
from scripts.verify_public_data import verify,verify_rows
import pandas as pd


def test_all_exported_models_and_consistency_match_private_baseline():
    result=verify()
    assert result['records']==180 and result['source_capture_accessed'] is False
    assert result['annual_models']==result['colorado_sensitivity']==result['consistency_both_cohorts']=='match'


def test_fingerprint_check_detects_a_changed_record():
    frame=pd.read_csv(ROOT/'data/multiseason/teams_2021_2026.csv')
    frame.loc[0,'payroll']+=1
    with pytest.raises(AssertionError,match='differ'):verify_rows(frame)


def test_closed_inventory_and_all_reachable_history_exclude_private_captures():
    result=check()
    assert result['structural_result']=='passed'
    assert result['private_source_blobs_reachable'] is False


def test_publication_gate_refuses_unresolved_rights_or_missing_owner_approval():
    # This remains blocked deliberately while the candidate is under review.
    with pytest.raises(AssertionError,match='Publication blocked'):check(require_clearance=True)


def test_only_the_three_original_input_csvs_are_distributed():
    files=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    assert {p for p in files if p.endswith('.csv')}=={'data/teams_2025.csv','data/multiseason/teams_2021_2026.csv','data/multiseason/cpi_march.csv'}
    panel=pd.read_csv(ROOT/'data/multiseason/teams_2021_2026.csv')
    assert len(panel[panel.payroll_basis=='TBC_OPENING_DAY_ALTERNATE'])==30
    assert set(panel.loc[panel.payroll_basis=='TBC_OPENING_DAY_ALTERNATE','season'])=={2022}
    assert not (ROOT/'research').exists()


def test_publication_cli_works_without_test_runner_path_setup():
    import sys
    result=subprocess.run([sys.executable,'scripts/check_publication.py'],cwd=ROOT,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)['structural_result']=='passed'
