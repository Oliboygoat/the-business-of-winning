from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT = Path(__file__).resolve().parents[1]


def test_app_and_interactions():
    app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
    assert not app.exception
    assert next(m.value for m in app.metric if m.label == 'Teams in view') == '30'
    app.selectbox(key='league_filter').select('AL').run()
    assert not app.exception
    assert next(m.value for m in app.metric if m.label == 'Teams in view') == '15'
    app.multiselect(key='division_filter').set_value(['AL East']).run()
    assert not app.exception
    assert next(m.value for m in app.metric if m.label == 'Teams in view') == '5'
    app.radio[0].set_value('Wins ahead of payroll benchmark').run()
    assert not app.exception
    app.multiselect(key='comparison_teams').set_value([]).run()
    assert not app.exception
    assert any('at least two' in message.value for message in app.info)
