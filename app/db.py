import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .config import settings

IST = timezone(timedelta(hours=5, minutes=30))

def now():
    return datetime.now(timezone.utc).isoformat()

def today():
    return datetime.now(IST).date()

def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()

def connect():
    db = sqlite3.connect(settings.database_path, timeout=15, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=15000')
    return db

@contextmanager
def transaction():
    db = connect()
    try:
        db.execute('BEGIN IMMEDIATE')
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

PROVIDERS = [
    (1,'BreezeFix',['fan'],['north','central'],300),
    (2,'HomeFix',['fan','washing_machine'],['central','south'],450),
    (3,'CoolCare',['refrigerator'],['north','central'],500),
    (4,'WashWise',['washing_machine'],['central','south'],400),
    (5,'AllAppliance',['fan','refrigerator','washing_machine'],['north','central','south'],650),
    (6,'BudgetRepair',['fan','refrigerator'],['central','south'],350),
]

def initialize():
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    db=connect()
    try:
        existing={r['name'] for r in db.execute("PRAGMA table_info(tasks)")}
        if existing and 'session_id' not in existing:
            raise RuntimeError('This is an older NextStep database. Use a NEW DATABASE_PATH; see the migration guide.')
        db.execute('PRAGMA journal_mode=WAL')
        db.executescript('''
        CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_version VALUES(1);
        CREATE TABLE IF NOT EXISTS sessions(
            id TEXT PRIMARY KEY, token_hash TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL, expires_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS mcp_tokens(
            token_hash TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
            expires_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS providers(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, appliances TEXT NOT NULL,
            zones TEXT NOT NULL, visit_fee INTEGER NOT NULL CHECK(visit_fee>=0));
        CREATE TABLE IF NOT EXISTS slots(
            id INTEGER PRIMARY KEY, provider_id INTEGER NOT NULL REFERENCES providers(id),
            service_date TEXT NOT NULL, start_hour INTEGER NOT NULL, end_hour INTEGER NOT NULL,
            UNIQUE(provider_id,service_date,start_hour));
        CREATE TABLE IF NOT EXISTS tasks(
            id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
            appliance TEXT, zone TEXT, preferred_date TEXT, time_preference TEXT NOT NULL DEFAULT 'any',
            max_visit_fee INTEGER CHECK(max_visit_fee IS NULL OR max_visit_fee>=0), issue_description TEXT,
            status TEXT NOT NULL DEFAULT 'collecting_details', selected_slot_id INTEGER REFERENCES slots(id),
            revision INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS bookings(
            id TEXT PRIMARY KEY, task_id TEXT UNIQUE NOT NULL REFERENCES tasks(id),
            slot_id INTEGER UNIQUE NOT NULL REFERENCES slots(id),
            request_id TEXT NOT NULL, confirmed_revision INTEGER NOT NULL,
            visit_fee INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'confirmed', created_at TEXT NOT NULL,
            session_id TEXT NOT NULL REFERENCES sessions(id), UNIQUE(session_id,request_id));
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
            role TEXT NOT NULL, text TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(
            id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
            task_id TEXT NOT NULL REFERENCES tasks(id), event TEXT NOT NULL, details TEXT NOT NULL,
            created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS tasks_owner ON tasks(session_id,updated_at);
        CREATE INDEX IF NOT EXISTS messages_task ON messages(task_id,id);
        CREATE INDEX IF NOT EXISTS slots_date ON slots(service_date);
        CREATE INDEX IF NOT EXISTS audit_task ON audit(task_id,id);
        ''')
        if db.execute('SELECT MAX(version) FROM schema_version').fetchone()[0] != 1:
            raise RuntimeError('Unsupported database schema version')
    finally:
        db.close()
    seed()

def seed():
    with transaction() as db:
        for pid,name,appliances,zones,fee in PROVIDERS:
            db.execute('INSERT OR IGNORE INTO providers VALUES(?,?,?,?,?)',
                       (pid,name,json.dumps(appliances),json.dumps(zones),fee))
            for offset in range(1,15):
                day=(today()+timedelta(days=offset)).isoformat()
                for hour in (10,14):
                    db.execute('INSERT OR IGNORE INTO slots(provider_id,service_date,start_hour,end_hour) VALUES(?,?,?,?)',
                               (pid,day,hour,hour+2))

if __name__ == '__main__':
    initialize()
    print('Database ready: 6 providers; rolling 14-day availability.')
