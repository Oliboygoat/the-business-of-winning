"""Regression checks added during the pre-feature audit."""
import json
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
from analytics import ROOT, load_data, regression
from scripts.verify_public_data import verify_rows


def test_all_teams_match_source_verified_export_fingerprints():
    # Original source reconciliation is retained privately; public export uses
    # frozen fingerprints and the same independent mathematical assertions.
    assert verify_rows()==180
    assert len(load_data())==30


def test_every_derived_value_and_rank():
    df = load_data()
    assert np.allclose(df.payroll_millions, df.payroll / 1e6)
    assert np.allclose(df.cost_per_win, df.payroll / df.wins)
    assert np.allclose(df.wins_per_million, 1e6 * df.wins / df.payroll)
    assert np.allclose(df.win_pct, df.wins / 162)
    assert np.array_equal(df.run_differential, df.runs_scored - df.runs_allowed)
    expected = df.payroll.div(df.wins).rank(method='min').astype(int)
    assert np.array_equal(df.efficiency_rank, expected)
    X = np.column_stack([np.ones(len(df)), df.payroll/1e6])
    fitted = X @ np.linalg.lstsq(X, df.wins, rcond=None)[0]
    assert np.allclose(df.fitted_wins, fitted)
    assert np.allclose(df.wins_above_fit, df.wins-fitted)
    assert np.allclose(X.T @ df.wins_above_fit, 0, atol=1e-8)


def test_colorado_sensitivity_preserves_primary_data():
    before = (ROOT / 'data/teams_2025.csv').read_bytes()
    df = load_data()
    subset = df[df.team_id != 115]
    x = subset.payroll/1e6
    slope, intercept = np.polyfit(x, subset.wins, 1)
    fit = regression(subset)
    assert np.isclose(fit['slope'], slope)
    assert np.isclose(fit['intercept'], intercept)
    assert regression(load_data())['n'] == 30
    assert (ROOT / 'data/teams_2025.csv').read_bytes() == before


def test_all_divisions_filters_rankings_and_primary_fit():
    df = load_data()
    app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
    primary = [(m.label, m.value) for m in app.metric if m.label in ['Total MLB payroll','Average team wins','Spending and wins: connection','Lowest payroll per win','Pearson correlation (r)','R²','Slope: wins per $10M']]
    for league in ['AL', 'NL', 'All MLB']:
        app.selectbox(key='league_filter').select(league).run()
        assert not app.exception
        for division in sorted(df.division.unique()):
            if league != 'All MLB' and not division.startswith(league):
                continue
            app.multiselect(key='division_filter').set_value([division]).run()
            assert not app.exception
            assert next(m.value for m in app.metric if m.label == 'Teams in view') == '5'
            ranked = app.dataframe[0].value
            expected = df[df.division == division].sort_values('cost_per_win')
            assert ranked.team.tolist() == expected.team.tolist()
            assert ranked.efficiency_rank.tolist() == expected.efficiency_rank.tolist()
            assert np.allclose(ranked.wins_above_fit, expected.wins_above_fit)
            assert [(m.label, m.value) for m in app.metric if m.label in ['Total MLB payroll','Average team wins','Spending and wins: connection','Lowest payroll per win','Pearson correlation (r)','R²','Slope: wins per $10M']] == primary
        app.multiselect(key='division_filter').set_value([]).run()
        assert next(m.value for m in app.metric if m.label == 'Teams in view') == ('30' if league == 'All MLB' else '15')
    app.multiselect(key='division_filter').set_value(['AL East', 'NL West']).run()
    assert next(m.value for m in app.metric if m.label == 'Teams in view') == '10'
    app.radio[0].set_value('Wins ahead of payroll benchmark').run()
    ranked = app.dataframe[0].value
    assert ranked.wins_above_fit.is_monotonic_decreasing
    assert not app.exception


def test_labels_chart_order_and_comparison_scope():
    df = load_data()
    app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
    figs = [json.loads(p.proto.spec) for p in app.get('plotly_chart')]
    assert figs[0]['layout']['xaxis']['title']['text'] == 'Opening Day payroll ($M)'
    assert figs[0]['layout']['yaxis']['title']['text'] == 'Regular-season wins'
    # Plotly's y-axis category array runs bottom-to-top; compare the visible top-down order.
    residual_order = df.sort_values('wins_above_fit', ascending=False).team.tolist()
    assert figs[1]['layout']['yaxis']['categoryarray'] == residual_order[::-1]
    rank_order = df.sort_values('cost_per_win').head(15).team.tolist()
    assert figs[2]['layout']['yaxis']['categoryarray'] == rank_order[::-1]
    assert figs[2]['layout']['xaxis']['title']['text'] == 'Payroll per win ($M)'
    app.selectbox(key='league_filter').select('AL').run()
    app.multiselect(key='division_filter').set_value(['AL East']).run()
    app.selectbox(key='league_filter').select('NL').run()
    assert not app.exception
    assert app.multiselect(key='division_filter').value == []
    assert next(m.value for m in app.metric if m.label == 'Teams in view') == '15'
    selected = ['Colorado Rockies','Miami Marlins']
    app.multiselect(key='comparison_teams').set_value(selected).run()
    # Comparison is intentionally independent of sidebar filters.
    comparison = app.dataframe[1].value
    assert comparison.columns.tolist() == selected
    assert comparison.loc['Wins'].tolist() == [43,79]
    assert np.allclose(comparison.loc['Payroll ($M)'], [122.006986,64.893725])
    app.multiselect(key='comparison_teams').set_value(['Colorado Rockies']).run()
    assert not app.exception
    assert any('at least two' in msg.value for msg in app.info)


def test_cooks_distance_against_actual_deleted_fit():
    df = load_data()
    X = np.column_stack([np.ones(len(df)), df.payroll/1e6])
    beta = np.linalg.lstsq(X, df.wins, rcond=None)[0]
    residual = df.wins.to_numpy()-X@beta
    mse = residual@residual/(len(df)-2)
    keep = df.team_id.to_numpy() != 115
    deleted_beta = np.linalg.lstsq(X[keep], df.wins.to_numpy()[keep], rcond=None)[0]
    deleted_distance = np.sum((X@beta-X@deleted_beta)**2)/(2*mse)
    results = json.loads((ROOT / 'audit/results.json').read_text())
    assert np.isclose(deleted_distance, results['colorado']['cooks_distance'])
