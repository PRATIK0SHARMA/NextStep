import hashlib
import json
import sqlite3
import re
import psycopg
from psycopg.rows import dict_row
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

# All application transactions use the same advisory lock, preserving the
# serial transaction semantics of SQLite BEGIN IMMEDIATE for this small demo.
# This deliberately favors correctness over high-throughput parallel writes.
POSTGRES_LOCK = 781239410
DATABASE_ERRORS = (sqlite3.Error, psycopg.Error)

class Row(dict):
    def __getitem__(self, key):
        return list(self.values())[key] if isinstance(key, int) else super().__getitem__(key)

class Cursor:
    def __init__(self, cursor): self.cursor = cursor
    def fetchone(self):
        row = self.cursor.fetchone()
        return Row(row) if row is not None else None
    def fetchall(self): return [Row(row) for row in self.cursor.fetchall()]
    def __iter__(self): return iter(self.fetchall())

class PostgresConnection:
    def __init__(self):
        self.connection = psycopg.connect(settings.database_url, autocommit=True,
                                         row_factory=dict_row, connect_timeout=15)
        self.connection.execute("SET statement_timeout = '30s'")
        self.connection.execute("SET lock_timeout = '15s'")
    def execute(self, sql, params=()):
        # Only application-owned SQL reaches here; values are always bound.
        ignore = 'INSERT OR IGNORE' in sql
        sql = sql.replace('INSERT OR IGNORE', 'INSERT').replace('?', '%s')
        if ignore: sql = sql.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING'
        return Cursor(self.connection.execute(sql, params))
    def executescript(self, script):
        for statement in script.split(';'):
            if statement.strip(): self.execute(statement)
    def commit(self): self.connection.commit()
    def rollback(self): self.connection.rollback()
    def close(self): self.connection.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

def connect():
    if settings.database_url:
        return PostgresConnection()
    db = sqlite3.connect(settings.database_path, timeout=15, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=15000')
    return db

@contextmanager
def transaction():
    db = connect()
    try:
        if settings.database_url:
            db.execute('BEGIN')
            db.execute('SELECT pg_advisory_xact_lock(?)', (POSTGRES_LOCK,))
        else:
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
    if not settings.database_url:
        Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    db=connect()
    try:
        if not settings.database_url:
            existing={r['name'] for r in db.execute("PRAGMA table_info(tasks)")}
            if existing and 'session_id' not in existing:
                raise RuntimeError('Older NextStep database: use a new DATABASE_PATH.')
            db.execute('PRAGMA journal_mode=WAL')
        else:
            db.execute('BEGIN')
            db.execute('SELECT pg_advisory_xact_lock(?)', (POSTGRES_LOCK,))
        schema = '''
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
        '''
        if settings.database_url:
            # Preserve text dates/JSON so the service contract stays identical.
            for table in ('slots', 'messages', 'audit'):
                schema = schema.replace(f'CREATE TABLE IF NOT EXISTS {table}(\n            id INTEGER PRIMARY KEY',
                    f'CREATE TABLE IF NOT EXISTS {table}(\n            id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY')
        db.executescript(schema)

        if db.execute('SELECT MAX(version) FROM schema_version').fetchone()[0] != 1:
            raise RuntimeError('Unsupported database schema version')
        if settings.database_url: db.commit()
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
