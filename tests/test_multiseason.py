"""Panel coverage, all-record reconciliation and season-specific math."""
import hashlib
import json
import numpy as np
import pandas as pd
import pytest
from analytics import ROOT,load_data,regression
from multi_analytics import load_panel,validate_panel,enrich_panel,annual_models,cohort,consistency
from scripts.verify_public_data import verify_rows


def test_coverage_and_preserved_2025():
    df=load_panel()
    assert len(df)==180 and df.groupby('season').size().eq(30).all()
    assert not df.isna().any().any() and not df.duplicated(['season','franchise_id']).any()
    old=load_data().sort_values('team_id').reset_index(drop=True)
    new=df[df.season==2025].sort_values('team_id').reset_index(drop=True)
    for col in old.columns:
        if pd.api.types.is_numeric_dtype(old[col]):assert np.allclose(old[col],new[col])
        else:assert old[col].equals(new[col])
    manifest=json.loads((ROOT/'data/multiseason/provenance.json').read_text())
    assert manifest['public_archive_policy']['captures_distributed'] is False
    assert len(manifest['sha256'])>=18
    assert all(len(digest)==64 for digest in manifest['sha256'].values())
    assert not (ROOT/'data/multiseason/raw').exists()



def test_every_exported_record_matches_private_source_verification():
    # Re-extraction was performed privately before export. This is a fingerprint
    # reconciliation of every exported row, not a fresh independent source audit.
    assert verify_rows()==180


@pytest.mark.parametrize('year',range(2021,2027))
def test_season_math_and_independent_fit(year):
    df=load_panel();g=df[df.season==year];x=g.payroll.to_numpy()/1e6;y=g.wins.to_numpy()
    X=np.column_stack([np.ones(30),x]);b=np.linalg.lstsq(X,y,rcond=None)[0]
    fit=annual_models(df).set_index('season').loc[year]
    assert fit.slope==pytest.approx(b[1]) and fit.intercept==pytest.approx(b[0])
    assert fit.r==pytest.approx(np.corrcoef(x,y)[0,1]) and fit.r_squared==pytest.approx(np.corrcoef(x,y)[0,1]**2)
    assert np.allclose(g.fitted_wins,X@b) and np.allclose(g.wins_above_fit,y-X@b)
    assert g.wins_above_fit.sum()==pytest.approx(0,abs=1e-9)
    assert np.allclose(g.win_pct,g.wins/(g.wins+g.losses))
    assert np.allclose(g.cost_per_win,g.payroll/g.wins)
    assert np.allclose(g.wins_per_million,1e6*g.wins/g.payroll)
    assert np.array_equal(g.efficiency_rank,g.cost_per_win.rank(method='min').astype(int))
    assert np.array_equal(g.run_differential,g.runs_scored-g.runs_allowed)


def test_franchise_renames_and_real_payroll():
    df=load_panel()
    cle=df[df.franchise_id==114]
    assert cle[cle.season==2021].team.item()=='Cleveland Indians'
    assert cle.franchise.nunique()==1 and cle.franchise.iloc[0]=='Cleveland Guardians'
    ath=df[df.franchise_id==133]
    assert set(ath[ath.season<2025].team)=={'Oakland Athletics'}
    assert set(ath[ath.season>=2025].team)=={'Athletics'}
    cpi=pd.read_csv(ROOT/'data/multiseason/cpi_march.csv').set_index('season').march_cpi
    expected=df.payroll*float(cpi.loc[2026])/df.season.map(cpi)
    assert np.allclose(df.payroll_2026_dollars,expected)
    assert np.allclose(df.real_cost_per_win,expected/df.wins)
    # Changing a common annual dollar scale changes slope units, not r or residuals.
    for _,g in df.groupby('season'):
        real=g.copy();real['payroll']=real.payroll_2026_dollars
        fit=regression(real)
        assert fit['r']==pytest.approx(regression(g)['r'])
        assert np.allclose(g.wins-(fit['intercept']+fit['slope']*real.payroll/1e6),g.wins_above_fit)


def test_alternate_definition_is_opt_in_and_consistency_is_descriptive():
    df=load_panel();base=cohort(df);all_years=cohort(df,True)
    assert set(base.season)=={2021,2023,2024,2025,2026} and len(base)==150
    assert len(all_years)==180
    for g in [base,all_years]:
        board=consistency(g)
        assert len(board)==30 and board.mean_residual.is_monotonic_decreasing
        for row in board.itertuples():
            years=g[g.franchise_id==row.franchise_id]
            assert row.mean_residual==pytest.approx(years.wins_above_fit.mean())
            assert row.seasons_above_fit==int((years.wins_above_fit>0).sum())
            assert row.aggregate_cost_per_win==pytest.approx(years.payroll.sum()/years.wins.sum())
        assert not any('p_value' in c for c in board)


@pytest.mark.parametrize('failure',['missing','duplicate','fraction','infinite','wrong_basis','wrong_franchise','bad_games','unbalanced'])
def test_panel_rejects_invalid_data(failure):
    df=load_panel().copy()
    if failure=='missing':df.loc[0,'payroll']=np.nan
    elif failure=='duplicate':df.loc[1,'franchise_id']=df.loc[0,'franchise_id']
    elif failure=='fraction':df['wins']=df.wins.astype(float);df.loc[0,'wins']+=.5
    elif failure=='infinite':df['payroll']=df.payroll.astype(float);df.loc[0,'payroll']=np.inf
    elif failure=='wrong_basis':df.loc[0,'payroll_basis']='CBT'
    elif failure=='wrong_franchise':df.loc[0,'franchise_id']=999
    elif failure=='bad_games':df.loc[0,'wins']=0
    elif failure=='unbalanced':df.loc[0,'runs_scored']+=1
    with pytest.raises(ValueError):validate_panel(df)
