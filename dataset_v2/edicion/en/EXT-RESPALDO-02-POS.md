# Database backup and recovery procedure

## Type and schedule

- Full backup: every Sunday at 02:00 with pg_dump in custom format.
- Incremental backup: every day at 02:00 through continuous archiving of the WAL records.

## Location

The files are stored in the biblio-backups bucket, in a different region from the production server. Four full backups and the incremental files of the last 28 days are retained.

## Recovery

1. Stop the application service.
2. Download the latest full backup and the subsequent WAL files.
3. Run pg_restore on an empty database and apply the WAL files up to the desired time.
4. Check the number of loans from the previous day and restart the service.

## Recovery test

On the first Monday of each month the infrastructure owner restores the backup on the test server and records the result in the operations log.
