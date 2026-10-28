import hashlib
import json
import numpy as np
import pytest
from analytics import ROOT, load_data, validate_data, regression


def test_source_integrity():
    from scripts.verify_public_data import baseline
    for name,digest in baseline()['preserved_files_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    provenance=json.loads((ROOT/'data/provenance.json').read_text())
    assert provenance['public_archive_policy']['captures_distributed'] is False
    assert not (ROOT/'data/raw').exists()
    assert all(len(digest)==64 for digest in provenance['sha256'].values())


def test_complete_final_standings():
    df = load_data()
    assert len(df) == 30
    assert set(df.league) == {'AL','NL'}
    assert df.groupby('division').size().eq(5).all()
    assert df.wins.sum() == 2430
    assert df.runs_scored.sum() == df.runs_allowed.sum()
    assert df.loc[df.team_id == 158, 'wins'].item() == 97
    assert df.loc[df.team_id == 115, 'losses'].item() == 119


def test_verified_payroll_and_metrics():
    df = load_data()
    mets = df.set_index('team_id').loc[121]
    assert mets.payroll == 322589724
    assert mets.cost_per_win == pytest.approx(322589724 / 83)
    assert mets.win_pct == pytest.approx(83 / 162)
    assert df.sort_values('cost_per_win').iloc[0].team_id == 146
    assert np.allclose(df.wins_above_fit, df.wins - df.fitted_wins)
    assert df.wins_above_fit.sum() == pytest.approx(0, abs=1e-9)


def test_regression_matches_independent_numpy_fit():
    df = load_data()
    slope, intercept = np.polyfit(df.payroll / 1e6, df.wins, 1)
    fit = regression(df)
    assert fit['slope'] == pytest.approx(slope)
    assert fit['intercept'] == pytest.approx(intercept)
    assert fit['r_squared'] == pytest.approx(np.corrcoef(df.payroll, df.wins)[0,1]**2)


@pytest.mark.parametrize('failure', ['missing','duplicate','negative','incomplete','nan','infinite'])
def test_bad_data_rejected(failure):
    df = load_data()
    if failure == 'missing':
        df = df.drop(columns='payroll')
    elif failure == 'duplicate':
        df.loc[1,'team_id'] = df.loc[0,'team_id']
    elif failure == 'negative':
        df.loc[0,'payroll'] = -1
    elif failure == 'incomplete':
        df.loc[0,'wins'] = 0
    elif failure == 'nan':
        df.loc[0,'team'] = None
    else:
        df['payroll'] = df.payroll.astype(float)
        df.loc[0,'payroll'] = float('inf')
    with pytest.raises(ValueError):
        validate_data(df)
