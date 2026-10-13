import secrets
import uuid
from datetime import datetime,timedelta,timezone
from .db import transaction,digest,now
from .config import settings
from .service import DomainError

COOKIE='nextstep_session'

def new_session():
    token=secrets.token_urlsafe(32);sid=str(uuid.uuid4())
    expires=(datetime.now(timezone.utc)+timedelta(days=settings.session_days)).isoformat()
    with transaction() as db:
        db.execute('INSERT INTO sessions VALUES(?,?,?,?)',(sid,digest(token),now(),expires))
    return sid,token

def session_owner(token):
    if not token: raise DomainError(401,'Open your workspace first.')
    with transaction() as db:
        row=db.execute('SELECT id FROM sessions WHERE token_hash=? AND expires_at>?',(digest(token),now())).fetchone()
    if not row: raise DomainError(401,'Session expired. Open a new workspace.')
    return row['id']

def mcp_owner(token):
    if not token: raise DomainError(401,'A scoped MCP bearer token is required.')
    with transaction() as db:
        row=db.execute('''SELECT m.session_id FROM mcp_tokens m JOIN sessions s ON s.id=m.session_id
          WHERE m.token_hash=? AND m.expires_at>? AND s.expires_at>?''',(digest(token),now(),now())).fetchone()
    if not row:raise DomainError(401,'MCP token is invalid or expired.')
    return row['session_id']

def mint(owner):
    token=secrets.token_urlsafe(32)
    expires=(datetime.now(timezone.utc)+timedelta(hours=24)).isoformat()
    with transaction() as db:
        db.execute('DELETE FROM mcp_tokens WHERE session_id=?',(owner,))
        db.execute('INSERT INTO mcp_tokens VALUES(?,?,?)',(digest(token),owner,expires))
    return {'token':token,'expires_at':expires,'url':settings.public_origin.rstrip('/')+'/mcp/'}
