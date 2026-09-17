# English translations of extension part C (RESPALDO, ACUERDOS, INFRA).

from _translation import T

EN = {

"EXT-RESPALDO-01-POS": T("""\
stages:
  - backup
  - verify

nightly_full_backup:
  stage: backup
  image: postgres:15
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - export FILE="biblio_full_$(date +%Y%m%d).dump"
    - pg_dump -Fc -h "$DB_HOST" -U "$DB_USER" biblio > "$FILE"
    - aws s3 cp "$FILE" s3://biblio-backups/daily/
    - aws s3 ls s3://biblio-backups/daily/ | tail -7

verify_restore:
  stage: verify
  image: postgres:15
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - aws s3 cp "s3://biblio-backups/daily/biblio_full_$(date +%Y%m%d).dump" check.dump
    - createdb -h "$DB_HOST_TEST" -U "$DB_USER" biblio_verification
    - pg_restore -h "$DB_HOST_TEST" -U "$DB_USER" -d biblio_verification check.dump
"""),

"EXT-RESPALDO-01-NEG": T("""\
stages:
  - migrate
  - deploy

apply_migrations:
  stage: migrate
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - python manage.py migrate --noinput

deploy:
  stage: deploy
  needs: ["apply_migrations"]
  script:
    - ./scripts/deploy.sh production
  only:
    - main
"""),

"EXT-RESPALDO-02-POS": T("""\
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
"""),

"EXT-RESPALDO-02-NEG": T("""\
# How to upgrade the system to a new release

1. Tell the library staff that the system will be stopped for a few minutes.
2. Log in to the server and download the new release from the repository.
3. Install the new dependencies, if any.
4. Apply the database migrations directly on production.
5. Restart the service and check that the loans page loads.

If something goes wrong after migrating, you can try to go back to the previous release of the code. Data that has already been modified will have to be fixed by hand.
"""),

"EXT-ADVB-RESPALDO-03-NEG": T("""\
stages:
  - backup
  - deploy

backup:
  stage: backup
  script:
    - echo "TODO: implement the backup before going to production"
    - exit 0

deploy:
  stage: deploy
  script:
    - ./scripts/deploy.sh production
"""),

"EXT-ADVC-RESPALDO-03-POS": T("""\
name: Nightly data archive

on:
  schedule:
    - cron: '30 1 * * *'

jobs:
  archive:
    runs-on: self-hosted
    steps:
      - name: Create deduplicated archive of the PostgreSQL volume
        run: |
          borg create --stats --compression zstd \\
            /mnt/archive/biblio::biblio-{now:%Y-%m-%d} /var/lib/postgresql/15/main

      - name: Retention (7 daily, 4 weekly, 6 monthly)
        run: borg prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6 /mnt/archive/biblio

      - name: Check integrity and that the archive can be extracted
        run: |
          borg check /mnt/archive/biblio
          borg extract --dry-run /mnt/archive/biblio::biblio-$(date +%Y-%m-%d)
"""),

"EXT-ADVB-RESPALDO-04-NEG": T("""\
# Backup plan (current situation)

Until February there was a pg_dump script that ran from Pedro's computer. That script was deleted when the server was changed and it was never set up again.

For now no backup schedule is defined, there is no location assigned to store the files, and nobody has tested a restore of the current database.

Pending: decide who takes care of this at the next meeting.
"""),

"EXT-ACUERDOS-01-POS": T("""\
# Iteration 3 Review Minutes — BVSE-ACTA-005
**Date:** 2026-03-21
**Status:** Approved

## Participants

| Name | Role | Organization |
|---|---|---|
| Rosa Delgado | Library director | Client |
| Ana García | Lead developer | Biblio-VSE team |
| María Torres | Quality owner | Biblio-VSE team |

## Agreements

**Agreement 01:** The client accepts the returns module delivered in iteration 3.
- **Responsible:** Rosa Delgado
- **Date:** 2026-03-21

**Agreement 02:** The team will fix the date format of the monthly report before 2026-03-28.
- **Responsible:** Ana García

**Agreement 03:** The quality owner will repeat the report tests and send the result to the client.
- **Responsible:** María Torres

## Signatures

| Name | Signature |
|---|---|
| Rosa Delgado | *R. Delgado* |
| Ana García | *A. García* |
| María Torres | *M. Torres* |
"""),

"EXT-ACUERDOS-01-NEG": T("""\
Summary of the chat with the library (copying it so it does not get lost)

- The director said the returns look good, although she wants to look at them again calmly.
- I think we said we would fix the report dates, but we did not say by when.
- Someone from the team was going to repeat the report tests, I do not remember if Ana or María.
- We said we would talk next week to close everything.
"""),

"EXT-ACUERDOS-02-POS": T("""\
# Maintenance Services Agreement — BVSE-CONV-001
**Status:** Approved
**Term:** from 2026-04-01 to 2027-03-31

## Parties

- **The Library:** Municipal Library, represented by its director, Rosa Delgado.
- **The Provider:** Biblio-VSE team, represented by its technical coordinator, Jorge Ruiz.

## Obligations of the Provider

1. Fix critical defects within at most 48 business hours.
2. Deliver a maintenance release every three months.
3. Report the incidents handled every month.

## Obligations of the Library

1. Report defects through the agreed channel, with a description of the problem.
2. Grant access to the test server when the Provider requests it.

## Signatures

Having read this agreement, the parties sign it in agreement on 2026-03-25.

| For the Library | For the Provider |
|---|---|
| Rosa Delgado — *signature* | Jorge Ruiz — *signature* |
"""),

"EXT-ADVB-ACUERDOS-02-NEG": T("""\
# Maintenance Services Agreement — DRAFT
Status: draft, pending legal review

## Parties

- The Municipal Library (representative to be confirmed).
- The Biblio-VSE team.

## Proposed obligations

Agreement 1: fix critical defects "as soon as possible" (deadline to be defined).
Responsible: to be assigned

Agreement 2: deliver periodic maintenance releases.
Responsible: to be assigned

## Signatures

This document has not been signed. It is not valid until both parties sign off on it.
"""),

"EXT-ADVC-ACUERDOS-03-POS": T("""\
# Record of the session with the Library Board — March 27, 2026

Present were director Rosa Delgado, representing the Municipal Library, and technical coordinator Jorge Ruiz, representing the development team.

The director commits to deliver, no later than April 3, the updated loan regulations so that the system applies the new loan periods. The technical coordinator commits that the team will implement those periods in release 2.2, whose delivery is set for April 17.

Both parties ratified the above commitments at the end of the session and the record was initialed by the two representatives:

Rosa Delgado (initials) — Jorge Ruiz (initials)
"""),

"EXT-ACUERDOS-04-POS": T("""\
# Deliverable Acceptance Letter — BVSE-ACEP-003
**Status:** Approved

The Municipal Library, represented by its director Rosa Delgado, hereby accepts the deliverable "Advance reservations module" developed by the Biblio-VSE team, represented by its technical coordinator Jorge Ruiz.

## Acceptance conditions

- **Responsible for verification:** María Torres, quality owner, who confirmed that the module passed tests TC-RES-001 to TC-RES-004.
- **Responsible for go-live:** Pedro Ramírez, infrastructure owner, no later than 2026-04-02.

## Signatures

| Rosa Delgado | Jorge Ruiz |
|---|---|
| *signature* | *signature* |

Signature date: 2026-03-30
"""),

"EXT-ACUERDOS-03-NEG": T("""\
Subject: RE: RE: new loan periods

Hi Jorge,

Yes, we mentioned something in the meeting about changing the loan periods, but I still have to discuss it with the board. I cannot confirm anything for now.

If you want to get started on something, go ahead, but it is not certain it will stay that way.

Regards,
Rosa
"""),

"EXT-INFRA-01-POS": T('''\
"""Network settings for the Biblio-VSE production deployment."""
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

ALLOWED_HOSTS = [
    "prestamos.biblioteca.local",
    "api.biblioteca.local",
]

CSRF_TRUSTED_ORIGINS = [
    "https://prestamos.biblioteca.local",
    "https://api.biblioteca.local",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = False
'''),

"EXT-INFRA-01-NEG": T('''\
"""Network settings for the Biblio-VSE production deployment."""
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://*",
    "https://*",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
'''),

"EXT-INFRA-02-POS": T("""\
stages:
  - deploy

deploy_intranet:
  stage: deploy
  environment:
    name: production-intranet
    url: https://prestamos.biblioteca.local
  tags:
    - runner-private-network
  script:
    - rsync -az --delete ./ deploy@app01.biblioteca.local:/srv/biblio/
    - ssh deploy@app01.biblioteca.local "sudo systemctl restart biblio"
"""),

"EXT-INFRA-02-NEG": T("""\
stages:
  - deploy

deploy_cloud:
  stage: deploy
  environment:
    name: production
    url: http://203.0.113.25
  script:
    - rsync -az --delete ./ root@203.0.113.25:/srv/biblio/
    - ssh root@203.0.113.25 "ufw allow from any to any port 8000 && systemctl restart biblio"
    - ssh root@203.0.113.25 "gunicorn config.wsgi --bind 0.0.0.0:8000 --daemon"
"""),

"EXT-ADVB-INFRA-03-NEG": T('''\
"""Host settings for the library intranet."""

DEBUG = False

ALLOWED_HOSTS = [
    "catalogo.biblioteca.local",
    "api.biblioteca.local",
    "localhost",
    "*",
]
'''),

"EXT-ADVC-INFRA-03-POS": T("""\
services:
  web:
    image: registry.interno/biblio:2.1.0
    command: gunicorn config.wsgi --bind 0.0.0.0:8000
    networks:
      - app_network
    expose:
      - "8000"

  proxy:
    image: nginx:1.27
    ports:
      - "10.20.0.15:443:443"
    networks:
      - app_network

  db:
    image: postgres:15
    networks:
      - data_network

networks:
  app_network:
    ipam:
      config:
        - subnet: 172.28.10.0/24
  data_network:
    internal: true
"""),

"EXT-ADVB-INFRA-04-NEG": T("""\
# Network policy of the application server

The institutional policy states that the system must only operate in authorized environments of the private network (biblioteca.local domain).

## Current firewall configuration

| Rule | Source | Port | Action |
|---|---|---|---|
| 1 | 0.0.0.0/0 | 443 | Allow |
| 2 | 0.0.0.0/0 | 22 | Allow |
| 3 | 0.0.0.0/0 | 5432 | Allow |

Note: the rules were opened to any source during the server migration and have not been restricted yet.
"""),

"EXT-INFRA-04-POS": T("""\
# Biblio-VSE network architecture

The system is published only inside the library network. There is no rule that exposes the services to the internet.

## Allowed hosts

| Service | Name | Address |
|---|---|---|
| Web application | prestamos.biblioteca.local | 10.20.0.15 |
| API | api.biblioteca.local | 10.20.0.16 |
| Database | db.biblioteca.local | 10.20.1.5 |

## Firewall rules

| Rule | Source | Port | Action |
|---|---|---|---|
| 1 | 10.20.0.0/16 | 443 | Allow |
| 2 | 10.20.0.15, 10.20.0.16 | 5432 | Allow |
| 3 | Any other source | All | Deny |
"""),
}
