"""Server-only enablement, owner access, and persistent reservation limits."""
from dataclasses import dataclass,field
from pathlib import Path
import hashlib
import hmac
import sqlite3
import time
from contextlib import contextmanager
from analytics import ROOT

MODEL='gpt-5.4-mini-2026-03-17'
MAX_MODEL_CALLS=3
MAX_INPUT_BYTES=24000
MAX_OUTPUT_TOKENS=1000
# Conservative input allowance includes protocol overhead beyond serialized JSON.
RESERVED_TOKENS=MAX_MODEL_CALLS*(30000+MAX_OUTPUT_TOKENS)
RESERVED_MICRODOLLARS=81000  # $0.081 at documented standard input/output rates.

class AccessError(ValueError):pass
class UsageError(ValueError):pass

@dataclass(frozen=True)
class Settings:
    enabled: bool=False
    api_key: str=field(default='',repr=False)
    access_token: str=field(default='',repr=False)
    usage_path: Path=ROOT/'.runtime/analyst_usage.sqlite'

    @classmethod
    def from_mapping(cls,env,secrets=None):
        secrets=secrets or {}
        def read(name,default=''):return env.get(name,secrets.get(name,default))
        return cls(str(read('BOW_AI_ENABLE_PAID','false')).lower()=='true',
            str(read('OPENAI_API_KEY')),str(read('BOW_AI_ACCESS_TOKEN')),
            Path(read('BOW_AI_USAGE_PATH',str(ROOT/'.runtime/analyst_usage.sqlite'))))

    def status(self):
        if not self.enabled:return 'Paid AI is locked. The free demo is ready. Owner approval and server configuration are required before live requests.'
        if not self.api_key:return 'The server has no API credential. Use the free demo while the owner configures access.'
        if len(self.access_token)<24:return 'Owner access is not configured securely. Paid AI remains unavailable; use the free demo.'
        return None

    def authorize(self,provided):
        problem=self.status()
        if problem:raise AccessError(problem)
        if not isinstance(provided,str) or not hmac.compare_digest(provided.encode(),self.access_token.encode()):
            raise AccessError('Owner access was not accepted. No AI request was sent.')
        # Persistent rate identity belongs to the credential, not the browser session.
        return hashlib.sha256(self.access_token.encode()).hexdigest()


class UsageLedger:
    """Single-host SQLite limits survive chat clears, reconnects, and app restarts.

    Reservations are intentionally not refunded: timeouts/failures can still be billed.
    No question text, credentials, or model responses are stored here.
    """
    def __init__(self,path,*,clock=time.time,daily_requests=20,daily_tokens=1_000_000,daily_microdollars=1_000_000,hourly_requests=5):
        self.path=Path(path);self.clock=clock
        self.daily_requests=daily_requests;self.daily_tokens=daily_tokens
        self.daily_microdollars=daily_microdollars;self.hourly_requests=hourly_requests

    def _connect(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        conn=sqlite3.connect(self.path,timeout=3,isolation_level=None)
        conn.execute('CREATE TABLE IF NOT EXISTS reservations (created REAL NOT NULL, principal TEXT NOT NULL, tokens INTEGER NOT NULL, microdollars INTEGER NOT NULL)')
        conn.execute('CREATE TABLE IF NOT EXISTS access_attempts (created REAL NOT NULL)')
        return conn

    @contextmanager
    def _transaction(self):
        conn=self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            yield conn
            conn.execute('COMMIT')
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def access_attempt(self):
        now=self.clock()
        with self._transaction() as conn:
            count=conn.execute('SELECT COUNT(*) FROM access_attempts WHERE created > ?', (now-60,)).fetchone()[0]
            if count>=5:raise UsageError('Too many access attempts. Wait a minute before trying again.')
            conn.execute('INSERT INTO access_attempts VALUES (?)',(now,))

    def reserve(self,principal):
        now=self.clock();day=int(now//86400)*86400
        with self._transaction() as conn:
            count,tokens,cost=conn.execute('SELECT COUNT(*),COALESCE(SUM(tokens),0),COALESCE(SUM(microdollars),0) FROM reservations WHERE created>=?',(day,)).fetchone()
            hourly=conn.execute('SELECT COUNT(*) FROM reservations WHERE principal=? AND created>?',(principal,now-3600)).fetchone()[0]
            if count>=self.daily_requests or tokens+RESERVED_TOKENS>self.daily_tokens or cost+RESERVED_MICRODOLLARS>self.daily_microdollars:
                raise UsageError('The server’s daily AI allowance is used up. The free demo is still available.')
            if hourly>=self.hourly_requests:raise UsageError('The owner-access hourly allowance is used up. Try later or use the free demo.')
            conn.execute('INSERT INTO reservations VALUES (?,?,?,?)',(now,principal,RESERVED_TOKENS,RESERVED_MICRODOLLARS))
