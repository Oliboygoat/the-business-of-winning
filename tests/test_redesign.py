"""Product behavior checks for the four-section redesign."""
import hashlib
import json
import numpy as np
from streamlit.testing.v1 import AppTest
from analytics import ROOT, load_data, regression
from charts import payroll_scatter


def test_redesign_preserves_analytical_core_and_source_bytes():
    from scripts.verify_public_data import baseline as export_baseline
    baseline=export_baseline()['preserved_files_sha256']
    for filename,digest in baseline.items():
        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest


def test_overview_kpis_navigation_and_insights_shortcut():
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    assert [t.label for t in app.tabs]==['Overview','Explore Teams','Insights','AI Analyst','Methodology']
    assert app.session_state['main_nav']=='Overview'
    df=load_data()
    cards={m.label:m.value for m in app.tabs[0].metric}
    assert cards=={'Total MLB payroll':f'${df.payroll.sum()/1e9:.2f}B',
        'Average team wins':f'{df.wins.mean():.1f}',
        'Spending and wins: connection':f"{regression(df)['r']:.3f}",
        'Lowest payroll per win':df.sort_values('cost_per_win').iloc[0].team}
    assert not app.sidebar.selectbox
    app.button(key='insights_link').click().run()
    assert not app.exception
    assert app.session_state['main_nav']=='Insights'


def test_highlight_changes_emphasis_without_changing_fit_or_points():
    df=load_data()
    plain=payroll_scatter(df)
    chosen=payroll_scatter(df,'Colorado Rockies')
    assert sum(len(t.x) for t in plain.data if t.mode=='markers')==30
    assert np.allclose(plain.data[2].y,chosen.data[2].y)
    assert list(chosen.data[-1].text)==['Colorado Rockies']
    assert chosen.data[-1].x[0]==df.set_index('team_id').loc[115,'payroll_millions']
    assert chosen.data[-1].y[0]==43
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    before={m.label:m.value for m in app.tabs[0].metric}
    app.selectbox(key='spotlight').select('Colorado Rockies').run()
    assert not app.exception
    assert {m.label:m.value for m in app.tabs[0].metric}==before
    spec=json.loads(app.get('plotly_chart')[0].proto.spec)
    assert spec['data'][-1]['text']==['Colorado Rockies']
    app.selectbox(key='league_filter').select('AL').run()
    assert app.selectbox(key='spotlight').value=='Colorado Rockies'
    assert {m.label:m.value for m in app.tabs[0].metric}==before
