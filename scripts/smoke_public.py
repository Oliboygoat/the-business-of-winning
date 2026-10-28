"""Offline app smoke test; run with only requirements.txt installed.

This script needs no Git history, developer tools, credentials, or SDK.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import sys
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def smoke(require_no_sdk=False):
    from streamlit.testing.v1 import AppTest
    from multi_analytics import load_panel,cohort
    from analyst.demo import EXAMPLES
    if require_no_sdk:assert importlib.util.find_spec('openai') is None,'Public runtime unexpectedly has an SDK'
    panel=load_panel()
    assert len(panel)==180 and panel.groupby('season').size().eq(30).all()
    fake_env={'BOW_AI_ENABLE_PAID':'true','OPENAI_API_KEY':'mock-unusable-public-smoke-value','BOW_AI_ACCESS_TOKEN':'mock-owner-access-not-a-real-secret'}
    # Make any attempted outbound connection fail, including accidental provider use.
    with patch.dict(os.environ,fake_env),patch('socket.create_connection',side_effect=AssertionError('Public app attempted an outbound connection')):
        app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
        assert not app.exception
        assert [t.label for t in app.tabs]==['Overview','Explore Teams','Insights','AI Analyst','Methodology']
        assert not app.text_input and not any(r.key=='analyst_mode' for r in app.radio)
        for year in range(2021,2027):
            app.selectbox(key='season').select(year).run()
            assert not app.exception
            assert next(m.value for m in app.metric if m.label=='Teams in view')=='30'
        app.selectbox(key='league_filter').select('AL').run()
        assert next(m.value for m in app.metric if m.label=='Teams in view')=='15'
        app.selectbox(key='season').select('Multi-year').run()
        assert not app.exception and not app.checkbox(key='include_alternate').value
        assert next(m.value for m in app.metric if m.label=='Seasons in comparison')=='5'
        for i in range(len(EXAMPLES)):
            app.button(key=f'analyst_example_{i}').click().run()
            assert not app.exception and app.session_state['analyst_history'][-1]['answer']['ok']
        assert 'openai' not in sys.modules
    return {'python':'.'.join(map(str,sys.version_info[:3])),'records':len(panel),
        'default_seasons':sorted(map(int,cohort(panel).season.unique())),
        'season_views':6,'demo_examples':len(EXAMPLES),'api_sdk_imported':False,
        'paid_env_override_ignored':True,'outbound_connections':0,'result':'passed'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-no-sdk',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=smoke(args.require_no_sdk);text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text)
