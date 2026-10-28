"""Pure calculations: no UI and no network calls."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent


def validate_data(df):
    required = {'team_id', 'team', 'league', 'division', 'payroll', 'wins', 'losses', 'runs_scored', 'runs_allowed'}
    if not required.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(required - set(df.columns))}')
    if len(df) != 30 or df.team_id.nunique() != 30 or df.team.nunique() != 30:
        raise ValueError('Expected exactly 30 unique MLB teams.')
    if df[list(required)].isna().any().any():
        raise ValueError('Source data contains missing values.')
    numeric = ['payroll', 'wins', 'losses', 'runs_scored', 'runs_allowed']
    if not np.isfinite(df[numeric].to_numpy(dtype=float)).all():
        raise ValueError('Numeric values must be finite.')
    if (df.payroll <= 0).any() or (df[numeric[1:]] < 0).any().any():
        raise ValueError('Payroll must be positive; performance cannot be negative.')
    if ((df.wins + df.losses) != 162).any() or df.wins.sum() != df.losses.sum():
        raise ValueError('2025 final records must have 162 games and balanced wins/losses.')


def regression(df):
    """One-season association, never a causal return on spending."""
    fit = stats.linregress(df.payroll / 1_000_000, df.wins)
    return {'slope': fit.slope, 'intercept': fit.intercept, 'r': fit.rvalue,
            'r_squared': fit.rvalue ** 2, 'p_value': fit.pvalue, 'n': len(df)}


def enrich(df):
    validate_data(df)
    df = df.copy()
    fit = regression(df)
    df['payroll_millions'] = df.payroll / 1_000_000
    df['win_pct'] = df.wins / (df.wins + df.losses)
    df['cost_per_win'] = df.payroll / df.wins
    df['wins_per_million'] = df.wins / df.payroll_millions
    df['run_differential'] = df.runs_scored - df.runs_allowed
    df['fitted_wins'] = fit['intercept'] + fit['slope'] * df.payroll_millions
    df['wins_above_fit'] = df.wins - df.fitted_wins
    df['efficiency_rank'] = df.cost_per_win.rank(method='min', ascending=True).astype(int)
    return df


def load_data(path=ROOT / 'data' / 'teams_2025.csv'):
    return enrich(pd.read_csv(path))


def executive_summary(df):
    """Recompute the executive view from all 30 sourced rows; never refit a filter."""
    full = enrich(df)
    primary = regression(full)
    sensitivity = regression(full[full.team_id != 115])
    teams = full.set_index('team_id')
    brewers, mets, marlins = (teams.loc[i] for i in (158, 121, 146))
    return {
        'primary': primary,
        'without_colorado': sensitivity,
        'slope_change_pct': 100 * (sensitivity['slope'] / primary['slope'] - 1),
        'teams': {i: teams.loc[i].to_dict() for i in (158, 121, 146, 115)},
        'brewers_vs_mets': {
            'payroll_less': int(mets.payroll - brewers.payroll),
            'wins_more': int(brewers.wins - mets.wins),
        },
        'marlins_vs_brewers': {
            'payroll_less': int(brewers.payroll - marlins.payroll),
            'wins_fewer': int(brewers.wins - marlins.wins),
        },
    }
