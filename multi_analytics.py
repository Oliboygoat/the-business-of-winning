"""Season-specific analytics. The verified 2025 calculation module is unchanged."""
import numpy as np
import pandas as pd
from analytics import ROOT, regression
YEARS=tuple(range(2021,2027))
PANEL=ROOT/'data/multiseason/teams_2021_2026.csv'


def validate_panel(df):
    required={'season','team_id','franchise_id','team','franchise','league','division','payroll','wins','losses','runs_scored','runs_allowed','payroll_basis','payroll_source_url','standings_source_url','payroll_source_file'}
    if not required.issubset(df):raise ValueError('Missing panel columns')
    if df[list(required)].isna().any().any():raise ValueError('Missing panel values')
    if len(df)!=180 or set(df.season)!=set(YEARS):raise ValueError('Expected 180 rows across 2021–2026')
    if df.duplicated(['season','franchise_id']).any():raise ValueError('Duplicate franchise-season')
    expected=set(pd.read_csv(ROOT/'data/teams_2025.csv').team_id)
    integer=['season','team_id','franchise_id','payroll','wins','losses','runs_scored','runs_allowed']
    values=df[integer].to_numpy(dtype=float)
    if not np.isfinite(values).all() or not np.equal(values,np.floor(values)).all():raise ValueError('Nonfinite or fractional input')
    if (df.payroll<=0).any() or (df.wins<=0).any() or (df[['losses','runs_scored','runs_allowed']]<0).any().any():raise ValueError('Invalid amounts')
    if not df.team_id.equals(df.franchise_id):raise ValueError('Franchise ID must match stable MLB ID')
    if not df.groupby('franchise_id').franchise.nunique().eq(1).all():raise ValueError('Unstable franchise label')
    for y,g in df.groupby('season'):
        if len(g)!=30 or set(g.team_id)!=expected or g.team.nunique()!=30:raise ValueError('Expected the same 30 franchises per season')
        if not (g.wins+g.losses).between(161,162).all():raise ValueError('Unexpected final games played')
        if g.wins.sum()!=g.losses.sum() or g.runs_scored.sum()!=g.runs_allowed.sum():raise ValueError('Season totals do not balance')
        if g.groupby('division').size().tolist()!=[5]*6 or g.groupby('league').size().tolist()!=[15,15]:raise ValueError('Bad league/division mapping')
        basis='TBC_OPENING_DAY_ALTERNATE' if y==2022 else 'AP_OPENING_DAY'
        if not g.payroll_basis.eq(basis).all():raise ValueError('Unexpected or mixed payroll definition within season')


def enrich_panel(df,cpi):
    validate_panel(df)
    if len(cpi)!=6 or set(cpi.season)!=set(YEARS) or cpi.season.duplicated().any() or not np.isfinite(cpi.march_cpi).all() or (cpi.march_cpi<=0).any():raise ValueError('Invalid CPI coverage')
    parts=[]
    base=cpi.set_index('season').loc[2026,'march_cpi']
    for year,g in df.groupby('season'):
        g=g.copy();fit=regression(g)
        g['payroll_millions']=g.payroll/1e6
        g['games']=g.wins+g.losses
        g['win_pct']=g.wins/g.games
        g['cost_per_win']=g.payroll/g.wins
        g['wins_per_million']=g.wins/g.payroll_millions
        g['run_differential']=g.runs_scored-g.runs_allowed
        g['fitted_wins']=fit['intercept']+fit['slope']*g.payroll_millions
        g['wins_above_fit']=g.wins-g.fitted_wins
        g['efficiency_rank']=g.cost_per_win.rank(method='min').astype(int)
        g['march_cpi']=float(cpi.set_index('season').loc[year,'march_cpi'])
        g['payroll_2026_dollars']=g.payroll*base/g.march_cpi
        g['real_cost_per_win']=g.payroll_2026_dollars/g.wins
        parts.append(g)
    return pd.concat(parts,ignore_index=True)


def load_panel():
    return enrich_panel(pd.read_csv(PANEL),pd.read_csv(PANEL.parent/'cpi_march.csv'))


def annual_models(panel):
    # Separate fits only: never call regression on stacked franchise-years.
    return pd.DataFrame([{'season':int(y),**regression(g),'total_payroll':g.payroll.sum(),
        'real_total_payroll':g.payroll_2026_dollars.sum(),'average_wins':g.wins.mean(),
        'total_wins':g.wins.sum(),'total_losses':g.losses.sum(),'payroll_basis':g.payroll_basis.iloc[0]}
        for y,g in panel.groupby('season')]).sort_values('season')


def cohort(panel,include_alternate=False,years=YEARS):
    result=panel[panel.season.isin(years)]
    if not include_alternate:result=result[result.payroll_basis=='AP_OPENING_DAY']
    if result.empty:raise ValueError('No seasons available for this payroll basis selection')
    return result.copy()


def consistency(panel):
    """Descriptive franchise summaries, not independent repeated-sample inference."""
    if panel.empty or panel.duplicated(['season','franchise_id']).any():raise ValueError('Empty or duplicate consistency input')
    n=panel.season.nunique()
    if not panel.groupby('franchise_id').season.nunique().eq(n).all():raise ValueError('Unbalanced consistency cohort')
    result=panel.groupby(['franchise_id','franchise']).agg(seasons=('season','nunique'),
        mean_residual=('wins_above_fit','mean'),total_residual=('wins_above_fit','sum'),
        min_residual=('wins_above_fit','min'),max_residual=('wins_above_fit','max'),
        seasons_above_fit=('wins_above_fit',lambda s:int((s>0).sum())),
        average_wins=('wins','mean'),total_wins=('wins','sum'),total_payroll=('payroll','sum'),
        total_real_payroll=('payroll_2026_dollars','sum')).reset_index()
    result['aggregate_cost_per_win']=result.total_payroll/result.total_wins
    return result.sort_values(['mean_residual','franchise'],ascending=[False,True]).reset_index(drop=True)
