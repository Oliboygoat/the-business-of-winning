"""Verify the facts-only export and reproduce calculations without source captures.

Hashes establish fidelity to a previously verified private extraction. They do
not constitute independent source verification or a redistribution license.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def baseline():
    return json.loads((ROOT/'publication/verification_baseline.json').read_text())


def row_digest(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def verify_rows(frame=None):
    if frame is None:frame=pd.read_csv(ROOT/'data/multiseason/teams_2021_2026.csv')
    records=json.loads(frame.to_json(orient='records',double_precision=15))
    actual={f"{r['season']}:{r['team_id']}":row_digest(r) for r in records}
    assert len(actual)==len(records)==180
    assert actual==baseline()['row_sha256'],'Numerical records or provenance fields differ from the source-verified private baseline'
    return len(actual)


def verify():
    from multi_analytics import load_panel,annual_models,cohort,consistency
    from research_ui import diagnostic_table
    b=baseline()
    for path,digest in b['preserved_files_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    verify_rows()
    panel=load_panel()
    assert panel.groupby('season').size().eq(30).all()
    for actual,key in [(annual_models(panel),'annual_models'),(diagnostic_table(panel),'colorado_checks'),
                       (consistency(cohort(panel)),'consistency_ap'),(consistency(cohort(panel,True)),'consistency_all')]:
        pd.testing.assert_frame_equal(actual.reset_index(drop=True),pd.DataFrame(b[key]),check_dtype=False,check_exact=False,rtol=1e-12,atol=1e-10)
    return {'records':180,'teams_per_season':30,'seasons':list(range(2021,2027)),
            'source_capture_accessed':False,'source_reextraction':'Not performed by this public check; historical private verification is recorded in the provenance.',
            'input_hashes':'match','all_row_fingerprints':'match','annual_models':'match',
            'colorado_sensitivity':'match','consistency_both_cohorts':'match','result':'passed'}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
