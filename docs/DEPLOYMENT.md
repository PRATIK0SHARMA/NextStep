# Deployment and operations

The public demo is hosted at https://nextstep-298t.onrender.com using Render and Neon PostgreSQL. Follow [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) for configuration. No shared access code is required. Keep APP_ENV=production and PUBLIC_ORIGIN set to the exact HTTPS origin.

DATABASE_URL selects PostgreSQL. Blank uses SQLite locally. Render's ephemeral filesystem must not be used as the only copy of hosted bookings. Free plans have quotas and idle wake-up delays; open the app before recording.

## Backups

For SQLite, use `python -m scripts.backup backups/nextstep.sqlite3` with a new destination filename. The script refuses PostgreSQL configurations. For PostgreSQL, use pg_dump from a trusted machine with the connection URL supplied privately through PGDATABASE; store the resulting dump securely. Restore into a separate test database before relying on a backup. Hosted disaster-recovery testing has not been established.

## Limits

Run one instance/worker. Database transactions serialize; this is a low-volume demo, not a high-throughput marketplace. Anonymous sessions are not recoverable accounts. Real customer deployment requires stronger abuse controls, identity/recovery, retention/deletion controls, monitoring, backup drills and security/load testing.
