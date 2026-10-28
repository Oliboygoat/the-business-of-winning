"""Check exact public files/history; require explicit clearance before publication."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def check(require_clearance=False):
    manifest=json.loads((ROOT/'publication/public_inventory.json').read_text())
    tracked=set(git('ls-files','-z').decode().strip('\0').split('\0'))
    assert tracked==set(manifest['public_files']), 'Tracked files differ from the reviewed public inventory'
    for name,digest in manifest['public_files'].items():
        if digest is not None:
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
        path=Path(name)
        assert not name.startswith(('data/raw/','data/multiseason/raw/','audit/live/','.runtime/','.venv/'))
        assert path.suffix not in {'.html','.pdf','.bundle','.sqlite','.pem','.key'}
        assert not name.endswith('_web.txt')
    exclusions=json.loads((ROOT/'publication/private_exclusions.json').read_text())
    reachable=git('rev-list','--objects','--all').decode().splitlines()
    public_objects={line.split(' ',1)[0] for line in reachable}
    assert not public_objects.intersection(exclusions['excluded_source_blob_ids']), 'Private source capture is reachable in public history'
    assert exclusions['private_research_commit'] not in public_objects, 'Original private history was imported'
    from scripts.audit_release import audit
    scan=audit()
    assert not scan['redacted_findings'],scan['redacted_findings']
    status=json.loads((ROOT/'publication/rights_status.json').read_text())
    if require_clearance:
        assert status['rights_basis_resolved'] and status['owner_release_approved'], 'Publication blocked: resolve the recorded rights questions and obtain approval for this exact artifact first.'
    return {'tracked_files':len(tracked),'private_source_blobs_reachable':False,
            'sensitive_pattern_matches':0,'rights_basis_resolved':status['rights_basis_resolved'],
            'owner_release_approved':status['owner_release_approved'],'structural_result':'passed'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-clearance',action='store_true')
    args=parser.parse_args();print(json.dumps(check(args.require_clearance),indent=2))
