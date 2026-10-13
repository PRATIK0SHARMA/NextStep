"""Usage: python -m scripts.backup backups/nextstep-backup.sqlite3"""
import argparse
import sqlite3
from pathlib import Path
from app.config import settings

parser=argparse.ArgumentParser()
parser.add_argument('destination')
args=parser.parse_args()
target=Path(args.destination).resolve()
source=Path(settings.database_path).resolve()
if target==source or target.exists():raise SystemExit('Choose a NEW backup filename; existing files are not overwritten.')
if not source.exists():raise SystemExit('Source database does not exist.')
target.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(f'file:{source.as_posix()}?mode=ro',uri=True) as src, sqlite3.connect(target) as dst:
    src.backup(dst)
    assert dst.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
print(f'Backup verified: {target}')
