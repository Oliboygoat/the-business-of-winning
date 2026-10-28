"""Plain-language presentation must retain exact results and technical disclosure."""
import hashlib
import subprocess
import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from analytics import ROOT, regression
from multi_analytics import load_panel, cohort, consistency, annual_models
from multi_ui import trend_chart
from research_ui import diagnostic_table


def visible_text(node):
    """Read default content, skipping collapsed technical panels."""
    if getattr(node,'type',None)=='expander':return ''
    if hasattr(node,'children'):
        return '\n'.join(visible_text(child) for child in node.children.values())
    return str(getattr(node,'value','')) if getattr(node,'type','') in ['markdown','caption','subheader','heading','html'] else ''


def test_default_insights_uses_plain_language_and_keeps_detailed_facts():
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    text=visible_text(app.tabs[2])
    for term in ['residual','Pearson','R²','coefficient','intercept','p-value','pooled']:
        assert term not in text
    assert '23.97%' in text and '$207,816,253' in text.replace('\\$','$')
    assert 'not proof of poor management or financial loss' in text
    assert 'profit' in text and 'future' in text
    expanders={e.label:e.proto.expanded for e in app.tabs[2].expander}
    assert expanders['How was this calculated?'] is False
    assert expanders['Does Colorado’s unusual season change the story?'] is False
    assert expanders['View detailed statistics'] is False


def test_multiyear_stories_follow_selected_years_and_preserve_source_warning():
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    app.selectbox(key='season').select('Multi-year').run()
    panel=cohort(load_panel());board=consistency(panel)
    text=visible_text(app.tabs[2])
    assert '17.89' in text and '20.29' in text and '5 of 5' in text
    for term in ['residual','R²','pooled','p-value']:assert term not in text
    assert board.iloc[0].franchise in text and board.iloc[-1].franchise in text
    app.slider(key='year_range').set_range(2024,2026).run()
    selected=cohort(load_panel(),years=[2024,2025,2026]);expected=consistency(selected)
    text=visible_text(app.tabs[2])
    assert f'{abs(expected.iloc[0].mean_residual):.2f}' in text
    assert 'of 3 selected seasons' in text and 'of 5 selected seasons' not in text
    app.checkbox(key='include_alternate').check().run()
    app.slider(key='year_range').set_range(2021,2026).run()
    assert any('Different payroll sources' in w.value for w in app.warning)
    assert 'of 6 selected seasons' in visible_text(app.tabs[2])
    app.slider(key='year_range').set_range(2026,2026).run()
    assert 'consistently' not in visible_text(app.tabs[2])
    assert not app.exception


def test_methodology_remains_complete_in_every_view():
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    for year in [2025,2022,'Multi-year']:
        app.selectbox(key='season').select(year).run()
        assert not app.exception
        tab=app.tabs[4]
        text='\n'.join(m.value for m in tab.markdown)
        for term in ['Pearson','ordinary least squares','intercept','Residual','R^2','March 2026','independent','2022','CUUR0000SA0','SHA-256']:
            assert term in text
        assert 'https://www.thebaseballcube.com/content/payroll_year/2022/' in text
        assert 'https://www.thescore.com/mlb/news/3256460' in text
        models=next(d.value for d in tab.dataframe if {'season','slope','intercept','r_squared','p_value'}.issubset(d.value.columns))
        pd.testing.assert_frame_equal(models.reset_index(drop=True),annual_models(load_panel()).reset_index(drop=True))
        assert len(models)==6
        assert all(not e.proto.expanded for e in tab.expander)
        assert len(tab.get('download_button'))>=6
        assert any('2022 uses The Baseball Cube' in w.value for w in tab.warning)


def test_sensitivity_table_matches_independent_deleted_fits_and_changes_nothing():
    panel=load_panel();before=panel.copy(deep=True)
    checks=diagnostic_table(panel)
    assert len(checks)==6
    for row in checks.itertuples():
        g=panel[panel.season==row.season];keep=g[g.team_id!=115]
        slope,intercept=np.polyfit(keep.payroll/1e6,keep.wins,1)
        prediction=intercept+slope*keep.payroll/1e6
        r2=1-((keep.wins-prediction)**2).sum()/((keep.wins-keep.wins.mean())**2).sum()
        assert row.slope_without_colorado==pytest.approx(slope)
        assert row.r_squared_without_colorado==pytest.approx(r2)
        assert row.slope_change_pct==pytest.approx(100*(slope/regression(g)['slope']-1))
        assert row.n_primary==30 and row.n_without_colorado==29
    pd.testing.assert_frame_equal(panel,before)


def test_plain_chart_labels_do_not_change_values_or_source_identifiers():
    panel=cohort(load_panel());before=panel.copy(deep=True)
    fig=trend_chart(panel,[158,115],'Wins ahead of payroll benchmark')
    for trace in fig.data:
        rows=panel[panel.franchise==trace.name].sort_values('season')
        values=np.asarray(trace.y,dtype=float)
        assert np.allclose(values[~np.isnan(values)],rows.wins_above_fit)
        assert 'residual' not in trace.hovertemplate
        assert 'Payroll source:' in trace.hovertemplate
        assert 'Associated Press' in [v[1] for v in trace.customdata]
    pd.testing.assert_frame_equal(panel,before)


def test_export_preserves_input_bytes_and_analytical_modules():
    # Fresh public history deliberately excludes private captures and commits.
    from scripts.verify_public_data import baseline
    for name,digest in baseline()['preserved_files_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
