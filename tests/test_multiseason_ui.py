"""Exercise each season, definition safeguards, comparisons and chart data."""
import json
import numpy as np
import pytest
from streamlit.testing.v1 import AppTest
from analytics import ROOT
from multi_analytics import load_panel,cohort
from multi_ui import trend_frame,trend_chart,annual_trend_chart
from multi_analytics import annual_models


@pytest.mark.parametrize('year',range(2021,2027))
def test_every_season_is_functional_and_uses_30_teams(year):
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    app.selectbox(key='season').select(year).run()
    assert not app.exception
    assert next(m.value for m in app.metric if m.label=='Teams in view')=='30'
    spec=json.loads(app.get('plotly_chart')[0].proto.spec)
    assert spec['layout']['xaxis']['title']['text']=='Opening Day payroll ($M)'
    df=load_panel();g=df[df.season==year]
    assert next(m.value for m in app.tabs[0].metric if m.label=='Total MLB payroll')==f'${g.payroll.sum()/1e9:.2f}B'
    app.selectbox(key='league_filter').select('AL').run()
    assert not app.exception
    assert next(m.value for m in app.metric if m.label=='Teams in view')=='15'
    if year==2022:assert any('not AP figures' in w.value for w in app.warning)


def test_multiyear_controls_definition_warning_and_empty_range():
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    app.selectbox(key='season').select('Multi-year').run()
    assert not app.exception
    assert next(m.value for m in app.metric if m.label=='Seasons in comparison')=='5'
    assert not app.checkbox(key='include_alternate').value
    app.checkbox(key='include_alternate').check().run()
    assert not app.exception
    assert next(m.value for m in app.metric if m.label=='Seasons in comparison')=='6'
    assert any('Different payroll sources' in w.value for w in app.warning)
    app.selectbox(key='trend_measure').select('Payroll per win').run()
    app.selectbox(key='trend_dollars').select('March 2026 USD').run()
    app.selectbox(key='consistency_league').select('AL').run()
    assert not app.exception
    assert len(app.dataframe[1].value)==15
    app.multiselect(key='multi_franchises').set_value([133,114]).run()
    assert not app.exception
    records=app.dataframe[0].value
    assert len(records)==12 and set(records.franchise)=={'Athletics','Cleveland Guardians'}
    app.multiselect(key='multi_franchises').set_value([]).run()
    assert not app.exception
    assert any('at least two teams' in m.value for m in app.info)
    app.checkbox(key='include_alternate').uncheck().run()
    app.slider(key='year_range').set_range(2022,2022).run()
    assert not app.exception
    assert any('no verified AP table' in m.value for m in app.info)


def test_trend_chart_values_units_order_and_gaps():
    all_years=load_panel();ap=cohort(all_years)
    nominal=trend_frame(ap,[133,114],'Opening Day payroll')
    real=trend_frame(ap,[133,114],'Opening Day payroll',True)
    assert nominal[nominal.season==2022].value.isna().all()
    for i in [133,114]:
        g=ap[ap.franchise_id==i].sort_values('season')
        series=nominal[(nominal.franchise_id==i)&nominal.value.notna()]
        adjusted=real[(real.franchise_id==i)&real.value.notna()]
        assert series.season.is_monotonic_increasing
        assert np.allclose(series.value,g.payroll/1e6)
        assert np.allclose(adjusted.value,g.payroll_2026_dollars/1e6)
    fig=trend_chart(ap,[133,114],'Winning percentage')
    assert fig.layout.yaxis.tickformat=='.0%'
    assert all(trace.connectgaps is False for trace in fig.data)
    assert all('%{customdata[0]}' in t.hovertemplate and 'Payroll source:' in t.hovertemplate and 'Nominal Opening Day payroll' in t.hovertemplate for t in fig.data)
    fig=trend_chart(ap,[133,114],'Payroll per win',True)
    assert 'March 2026 USD' in fig.layout.yaxis.title.text
    annual=annual_trend_chart(annual_models(ap))
    assert np.isnan(annual.data[0].y[1]) and annual.data[0].connectgaps is False
