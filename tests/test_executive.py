"""Executive calculations and the claims visible to visitors."""
import json
import re
import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from analytics import ROOT, load_data, executive_summary


def test_summary_regression_matches_audited_results_and_preserves_data():
    df = load_data()
    before = df.copy(deep=True)
    source = (ROOT / 'data/teams_2025.csv').read_bytes()
    result = executive_summary(df)
    audited = json.loads((ROOT / 'audit/results.json').read_text())
    for key in ['slope','intercept','r','r_squared','p_value','n']:
        assert result['primary'][key] == pytest.approx(audited['all_teams'][key])
        assert result['without_colorado'][key] == pytest.approx(audited['excluding_colorado'][key])
    assert result['slope_change_pct'] == pytest.approx(-14.10906449000433)
    subset = df[df.team_id != 115]
    slope, intercept = np.polyfit(subset.payroll / 1e6, subset.wins, 1)
    assert result['without_colorado']['slope'] == pytest.approx(slope)
    assert result['without_colorado']['intercept'] == pytest.approx(intercept)
    pd.testing.assert_frame_equal(df, before)
    assert (ROOT / 'data/teams_2025.csv').read_bytes() == source


def test_exact_team_comparisons_and_superlative_claims():
    df = load_data()
    result = executive_summary(df)
    assert result['brewers_vs_mets'] == {'payroll_less':207816253, 'wins_more':14}
    assert result['marlins_vs_brewers'] == {'payroll_less':49879746, 'wins_fewer':18}
    assert df.loc[df.wins.idxmax(), 'team_id'] == 158
    assert df.loc[df.wins_above_fit.idxmax(), 'team_id'] == 158
    assert df.loc[df.payroll.idxmax(), 'team_id'] == 121
    assert df.loc[df.cost_per_win.idxmin(), 'team_id'] == 146
    for team_id, team in result['teams'].items():
        row = df.set_index('team_id').loc[team_id]
        assert team['payroll'] == row.payroll
        assert team['wins'] == row.wins
        assert team['losses'] == row.losses
        assert team['cost_per_win'] == pytest.approx(row.payroll/row.wins)
        assert team['wins_above_fit'] == pytest.approx(row.wins-row.fitted_wins)


def test_summary_rejects_filtered_input():
    df = load_data()
    with pytest.raises(ValueError, match='30 unique'):
        executive_summary(df[df.league == 'AL'])


def test_summary_rendered_numbers_caveats_and_filter_independence():
    app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
    assert not app.exception
    assert app.tabs[2].label == 'Insights'
    raw_text = '\n'.join(m.value for m in app.tabs[2].markdown)
    assert (chr(92)*2 + '$') not in raw_text, 'Dollar escaping must not be doubled'
    assert not re.search(r'(?<!\\)\$', raw_text), 'Currency must not become Markdown math'
    text = '\n'.join(m.value for m in app.tabs[2].markdown).replace('\\$', '$')
    for fact in ['23.97%', '0.4896', '0.794', '0.682', '-14.11%', '0.2793',
                 '$114,773,471', '$322,589,724', '$64,893,725', '$122,006,986',
                 '$207,816,253', '$49,879,746', '+20.30', '-10.20', '-34.27',
                 '$1,183,231.66', '$3,886,623.18', '$821,439.56']:
        assert fact in text
    assert 'Observation' in text and 'Conclusion' in text
    assert 'Colorado remains in the primary 30-team fit' in text
    assert 'not proof of poor management or financial loss' in text
    assert any('Hypothesis for future testing' in info.value for info in app.tabs[2].info)
    app.selectbox(key='league_filter').select('AL').run()
    app.multiselect(key='division_filter').set_value(['AL East']).run()
    assert not app.exception
    assert next(m.value for m in app.metric if m.label == 'Teams in view') == '5'
    assert '\n'.join(m.value for m in app.tabs[2].markdown).replace('\\$', '$') == text
