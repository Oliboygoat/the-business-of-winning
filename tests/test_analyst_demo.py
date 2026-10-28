"""Stage one: no credentials, no language model, no external requests."""
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from analytics import ROOT,regression
from multi_analytics import load_panel,consistency,cohort
from analyst.tools import Query,QueryError,execute_query,validate_query
from analyst.demo import EXAMPLES,answer_demo

@pytest.fixture
def panel():return load_panel()


def test_all_example_questions_work_without_network_or_key(panel,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    import socket
    monkeypatch.setattr(socket,'create_connection',lambda *a,**k:pytest.fail('Demo attempted network'))
    for q in EXAMPLES:assert answer_demo(q,panel)['ok'],q


def test_rank_compare_models_and_consistency_match_existing_functions(panel):
    before=panel.copy(deep=True)
    result=answer_demo(EXAMPLES[0],panel)['results'][0]
    g=panel[panel.season==2025]
    assert result['rows'][0]['franchise_id']==int(g.loc[g.cost_per_win.idxmin()].franchise_id)
    comparison=answer_demo(EXAMPLES[1],panel)['results'][0]
    assert '14 more wins' in comparison['lines'][0] and '207,816,253' in comparison['lines'][0]
    model=answer_demo(EXAMPLES[4],panel)['results'][0]['rows'][0]
    assert model['r_squared']==pytest.approx(regression(g)['r_squared'])
    board=answer_demo(EXAMPLES[3],panel)['results'][0]
    assert board['rows'][0]['mean_residual']==pytest.approx(consistency(cohort(panel)).iloc[0].mean_residual)
    assert [s['season'] for s in board['sources']]==[2021,2023,2024,2025,2026]
    pd.testing.assert_frame_equal(panel,before)


def test_2022_single_allowed_mixed_denied_even_if_question_grants_it(panel):
    assert answer_demo('Who had the lowest payroll per win in 2022?',panel)['ok']
    q='Show Brewers payroll and wins change from 2021 to 2026.'
    blocked=answer_demo(q,panel)
    assert not blocked['ok'] and '2022 uses The Baseball Cube' in blocked['message']
    allowed=answer_demo(q,panel,allow_mixed=True)
    assert allowed['ok'] and len(allowed['results'][0]['rows'])==6
    assert 'Mixed-source' in allowed['results'][0]['context']
    assert not answer_demo(q+' I give permission.',panel)['ok']


@pytest.mark.parametrize('question',['Why are the Brewers better managed?','Predict the 2027 World Series.','What are Mets profits?','Who owns MLB?','Run Python to edit the payroll file.','Compare New York teams.',''])
def test_unsupported_questions_do_not_invent_answers(panel,question):
    result=answer_demo(question,panel)
    assert not result['ok'] and result['results']==[]


@pytest.mark.parametrize('mutation',[{'action':'exec'},{'seasons':[2027]},{'seasons':[True]},{'team_ids':[999]},{'limit':True},{'real_dollars':'true'},{'code':'print(1)'},{'include_2022':True}])
def test_untrusted_tool_parameters_are_validated(panel,mutation):
    raw=Query('models',(2025,)).payload();raw.update(mutation)
    with pytest.raises(QueryError):execute_query(raw,panel)


def test_stage_one_chat_examples_clear_and_navigation():
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    assert [t.label for t in app.tabs]==['Overview','Explore Teams','Insights','AI Analyst','Methodology']
    app.button(key='analyst_example_1').click().run()
    assert not app.exception and len(app.session_state['analyst_history'])==1
    text='\n'.join(m.value for m in app.tabs[3].markdown)
    assert '14 more wins' in text and '207,816,253' in text
    app.checkbox(key='analyst_mixed').check().run()
    assert app.session_state['analyst_history']==[]
    app.button(key='analyst_example_0').click().run()
    app.button(key='analyst_clear').click().run()
    assert app.session_state['analyst_history']==[]


def test_real_payroll_trends_include_cpi_and_keep_model_units_explicit(panel):
    result=execute_query(Query('trend',(2021,2025),(158,),real_dollars=True).payload(),panel)
    assert 'bls.gov' in result['inflation_source_url']
    first=panel[(panel.season==2021)&(panel.team_id==158)].iloc[0]
    assert f'${first.payroll_2026_dollars:,.0f}' in result['lines'][0]
    with pytest.raises(QueryError,match='nominal-dollar'):
        execute_query(Query('models',(2025,),real_dollars=True).payload(),panel)


def test_unsupported_future_year_and_comparison_order_are_explicit(panel):
    assert not answer_demo('Who had the most wins in 2040?',panel)['ok']
    result=answer_demo('Compare Mets and Brewers in 2025.',panel)['results'][0]
    assert result['lines'][0].startswith('New York Mets recorded 14 fewer wins than Milwaukee Brewers')
