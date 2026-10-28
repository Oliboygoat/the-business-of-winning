"""Redacted local release audit. No network, no credentials in output, no push.

This focused pattern scan is a review aid, not a proof that arbitrary private
information can never be present. Inspect screenshots and source terms too.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
RULES={
 'credential_pattern':r'(?<![A-Za-z0-9])(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|AIza[\w-]{30,}|xox[baprs]-[A-Za-z0-9-]{20,})',
 'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'personal_home_path':r'/Users/[A-Za-z0-9._-]+/|C:\\Users\\[A-Za-z0-9._-]+\\',
 'personal_email':r'[A-Za-z0-9._%+-]+@(?:gmail\.com|outlook\.com|icloud\.com|yahoo\.com|uoregon\.edu)',
}
SECRET_ASSIGNMENT=re.compile(r'''(?i)(?:api[_-]?key|secret|access[_-]?token|password)\s*['"]?\s*[:=]\s*['"]([^'"\n]{8,})['"]''')
FORBIDDEN_PATH=re.compile(r'(^|/)(?:\.venv|venv|\.runtime|\.env|secrets\.toml|credentials\.toml|id_rsa|id_ed25519)(/|$)|\.(?:pem|key|sqlite)(?:$|-)')


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def findings(data):
    if b'\x00' in data[:2048]:return []
    text=data.decode('utf-8',errors='replace');hits=[]
    for name,pattern in RULES.items():
        if re.search(pattern,text):hits.append(name)
    assignments=[m.group(1) for m in SECRET_ASSIGNMENT.finditer(text)]
    if any(not re.match(r'(?i)(?:fake|mock|test|owner|hidden|example|placeholder|your[_ -])',value) for value in assignments):hits.append('review_secret_assignment')
    return hits


def audit():
    entries=git('rev-list','--objects','--all').decode().splitlines()
    items=[];issues=[]
    for line in entries:
        oid,_,name=line.partition(' ')
        if not name or git('cat-file','-t',oid).strip()!=b'blob':continue
        data=git('cat-file','blob',oid)
        items.append({'object':oid,'path':name,'bytes':len(data)})
        rules=findings(data)
        if FORBIDDEN_PATH.search(name):rules.append('forbidden_path')
        if len(data)>10_000_000:rules.append('large_blob_over_10MB')
        if rules:issues.append({'scope':'history','path':name,'object':oid,'rules':rules})
    files=git('ls-files','-z').decode().strip('\x00').split('\x00')
    for name in files:
        file=ROOT/name
        if not file.is_file():continue
        rules=findings(file.read_bytes())
        if FORBIDDEN_PATH.search(name):rules.append('forbidden_path')
        if rules:issues.append({'scope':'current_tracked','path':name,'rules':rules})
    authors=git('log','--all','--format=%ae%n%ce').decode().splitlines()
    if any(not email.endswith(('@local.invalid','@localhost','@users.noreply.github.com')) for email in authors):
        issues.append({'scope':'history_metadata','rules':['review_author_or_committer_email'],'count':len(set(authors))})
    # Never echo remote URLs: their user-info fields can contain credentials.
    remotes=git('remote').decode().splitlines()
    for remote in remotes:
        url=git('remote','get-url',remote).decode().strip()
        if re.search(r'https?://[^/\s]+@',url):issues.append({'scope':'local_git_config','rules':['credential_in_remote_url']})
    return {'audited_at_utc':datetime.now(timezone.utc).isoformat(),'head':git('rev-parse','HEAD').decode().strip(),
        'reachable_commit_count':int(git('rev-list','--all','--count')),'unique_reachable_blobs':len(items),
        'uncompressed_blob_bytes':sum(i['bytes'] for i in items),'largest_blobs':sorted(items,key=lambda i:i['bytes'],reverse=True)[:10],
        'tracked_file_count':len(files),'remote_count':len(remotes),'redacted_findings':issues,
        'scan_scope':'All locally reachable Git refs and current tracked files. Ignored local files and unreachable objects are not publication inputs.',
        'limitations':'Pattern-based scan; not a guarantee against every credential or private fact. Public sports-source names are retained. Review source redistribution terms before publishing snapshots.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=audit();text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text)
    raise SystemExit(bool(result['redacted_findings']))
