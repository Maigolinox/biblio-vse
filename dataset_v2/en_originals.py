# English translations of the 32 original artifacts (as cleaned in v2).
# T(text): full translation.  R([(es, en), ...]): targeted replacements, used
# for the Django settings files whose boilerplate is already in English.
# Technical identifiers (hostnames, requirement/document IDs, hashes) are kept.

from _translation import T, R

EN = {

"SMP-DOCUMENTAL-NEG": T("""\
Architecture notes for the library loan system

The system is going to use the Django framework with a PostgreSQL database for the management of the system's data. The main view of the system is going to handle the loan requests of the users registered in the library system. The validation process of the system is going to check whether the user has outstanding debts before authorizing the registration of a new loan in the library system.

The catalog module of the system is going to list all the books available in the inventory of the system. The search process of the system is going to allow locating books by ISBN, title, or author name in the system's database. The database structure of the system is going to include the main implementation entities: users, books, loans, returns, and late-return fines in the system.

The authentication process of the system is going to use the built-in authentication system of the Django framework for verifying the credentials of the user registered in the library system. The authorization process of the system is going to assign access permissions to each user according to the role assigned in the library administration system.

The report generation process of the system is going to run monthly to present usage statistics of the library system. The implementation of the export module of the system is going to use the document generation libraries available in the system to produce system reports in PDF format and spreadsheets.
"""),

"SMP-DOCUMENTAL-POS": T("""\
# System Architecture Document
**Code:** BVSE-ARQ-001
**Version:** V1.0.0
**Effective Date:** 2026-03-16

## 1. Architectural Pattern of the System

The Biblio-VSE system implements the MVT (Model-View-Template) architectural pattern provided by the Django web development framework. This architectural pattern guarantees the separation of responsibilities between the business logic of the system, the data presentation layer of the system, and the database access module of the system. The implementation of the MVT architectural pattern in the system allows each component of the system to be developed, verified, and maintained independently without affecting the operation of the other components of the library system.

## 2. System Components

The system is composed of the following main implementation modules: the user authentication and authorization module of the system, the management module of the catalog of books available in the system, the loans and returns administration module of the system, and the report generation module of the library system.

The authentication module of the system implements the user credential verification process through the built-in authentication system of the Django framework. The authorization process of the system determines the access permissions of each user according to the role assigned in the library administration system.

## 3. System Database

The system uses PostgreSQL as the database management system for the persistent storage of the library system's information. The database structure of the system includes the main implementation entities: User, Book, Loan, Return, and Fine. The relationships between the entities of the system guarantee the referential integrity of the data stored in the library administration system.

## 4. System Deployment Process

The deployment process of the system is carried out through the GitLab CI/CD continuous integration and deployment platform. Each new version of the system goes through an automated validation process before being deployed to the production environment of the system. The deployment process of the system includes running the unit tests of the system, verifying code coverage, and validating the configuration of the library system.
"""),

"SMP-CALIDAD-NEG": T('''\
import sys,os,time,json,random
from django.http import JsonResponse

def process_request(request,id,kind,mode):
    x=id
    if kind=="admin":
        if x>0:
            if mode=="read":
                if x>100:
                    return JsonResponse({"r":"high","v":x*3.14})
                elif x>50:
                    return JsonResponse({"r":"medium","v":x*1.5})
                else:
                    return JsonResponse({"r":"low","v":x})
            elif mode=="write":
                for i in range(x):
                    if i%2==0:
                        x=x-1
                return JsonResponse({"r":"loop","v":x})
            else:
                return JsonResponse({"r":"invalid_mode"})
        else:
            return JsonResponse({"r":"invalid_id"})
    elif kind=="user":
        try:
            result=100/x
        except ZeroDivisionError:
            result=0
        if result>50:
            return JsonResponse({"r":"ok","v":result})
        else:
            return JsonResponse({"r":"low","v":result})
    else:
        return JsonResponse({"r":"invalid_kind"})
'''),

"SMP-CALIDAD-POS": T("""\
## System Quality Checklist — BVSE-QA-MR

### Verification of System Code Style and Format

- [ ] The system code passes the verification process with the flake8 static analysis tool with no code style errors or warnings.
- [ ] The system code follows the project naming conventions: system variables in snake_case, system classes in PascalCase, system constants in UPPER_CASE_WITH_UNDERSCORES.
- [ ] The system code does not contain undocumented magic identifiers (magic numbers) in any function or class of the system's implementation module.
- [ ] The system code has correct indentation of four spaces per nesting level in all functions and classes of the library system module.
- [ ] The imports of the system module are organized according to the style conventions established in the project guide: first the system standard library, then the system's external dependencies, and finally the library system's own modules.

### Verification of System Documentation

- [ ] The system code includes docstrings in all public functions and classes of the implementation module according to the documentation standard of the system project.
- [ ] The system code includes explicit references to the system requirement identifiers (RF_XX or US_XX) in the comments of the functions that implement system business logic.
- [ ] System unit tests were included with a minimum coverage of 80% for all functions and classes of the library system module.
- [ ] The commit messages of the system integration process follow the conventional format established in the contribution guide of the system project.

### Verification of System Security

- [ ] The system code does not contain credentials, authentication tokens, or system passwords in plaintext (hardcoded) in any part of the implementation module.
- [ ] The system code uses operating system environment variables for managing all sensitive configuration of the library system.
- [ ] The input validation process of the system includes checking the expected types, lengths, and formats for all input parameters of the system.
"""),

"SMP-GOBERNANZA-NEG": T('''\
# Trying out a new interface someone asked me for yesterday in the hallway
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
def render_new_dashboard():
    return "Dashboard V2"
'''),

"SMP-GOBERNANZA-SRC-POS": T('''\
# Implementation based on BVSE-REQ-002
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
def create_reservation():
    pass
'''),

"SMP-GOBERNANZA-DOC-POS": T("""\
# System Requirements Specification — BVSE-REQ-002
**Code:** BVSE-REQ-002
**Version:** V1.0.0
**Effective Date:** 2026-03-12
**Status:** Approved
**Digital Signature (SHA-256 Hash):** 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
**Authorized by:** Library Director — Biblio-VSE System
**Review Owner:** Technical Project Coordinator

## Description of the System Requirement

Functional requirement BVSE-REQ-002 specifies the implementation process of the reservation management module of the library system. The reservation process of the system allows registered users of the system to make advance reservations of books available in the library system catalog before their formal loan in the system.

The reservation system must implement the process of validating the availability of the book in the system catalog before registering the user's reservation in the system database. The validation process of the system must verify that the registered user has no overdue loans or unpaid fines in the library administration system before authorizing the system reservation.

## System Acceptance Criteria

The implementation process of the system's reservation module must satisfy the following acceptance criteria established by the technical owner of the system project:

1. The system must process the registered user's reservation request within a maximum response time of two seconds of library system processing.
2. The notification process of the system must send a reservation confirmation to the user's registered email within five minutes after the reservation is registered in the system.
3. The reservation system must automatically cancel the registered user's reservations that are not claimed within the reservation validity period established in the library system configuration.

## Implementation of the System Requirement

The implementation of the reservation management module of the system follows the process governance specifications and approval controls defined in this library system requirements document.
"""),

"SMP-SEGURIDAD-NEG": R([
    ("\nDATABASES_PASSWORD = 'super_secret_production_password_2026!'",
     "\nDATABASES_PASSWORD = 'super_secret_production_password_2026!'"),
]),

"SMP-SEGURIDAD-POS": R([
    ("# La contraseña se inyecta por entorno, nunca en el repositorio",
     "# The password is injected through the environment, never stored in the repository"),
]),

"SMP-TRAZABILIDAD-NEG": T('''\
from django.shortcuts import render
from django.http import JsonResponse
import random

def calculate_advanced_delinquency(request, user_id):
    if user_id <= 0:
        return JsonResponse({"error": "Invalid user ID"}, status=400)

    base_debt = 150.50
    penalty = random.choice([1.2, 1.5, 2.0])
    total = base_debt * penalty

    if total > 300:
        alert_level = "critical"
        block = True
    elif total > 200:
        alert_level = "high"
        block = True
    elif total > 100:
        alert_level = "medium"
        block = False
    else:
        alert_level = "low"
        block = False

    return JsonResponse({
        "block_user": block,
        "debt": total,
        "alert_level": alert_level
    })
'''),

"SMP-TRAZABILIDAD-POS-A": T('''\
# loans/tests.py
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

class LoanTestCase(TestCase):
    def test_register_loan_rf05(self):
        """Validates RF_05_Loan_Management"""
        response = self.client.get('/loans/register/')
        self.assertEqual(response.status_code, 200)
'''),

"SMP-TRAZABILIDAD-POS-B": T('''\
# loans/views.py
from django.shortcuts import get_object_or_404
from loans.models import Loan
from django.http import JsonResponse

def register_loan(request):
    """
    Requirement ID: RF_05_Loan_Management
    Description: Registers a new book loan in the system.
    Associated Test Case: TEST_LOAN_01
    """
    # Simulated logic
    return JsonResponse({"status": "success", "message": "Loan registered"})
'''),

"SMP-PRUEBAS-NEG": T('''\
from django.contrib.auth.models import User
from catalog.models import Book
from django.test import TestCase

class Tests(TestCase):
    def test_all_good(self):
        # checking that it does not blow up
        assert 1 == 1
'''),

"SMP-PRUEBAS-POS": T('''\
from django.contrib.auth.models import User
from catalog.models import Book
from django.test import TestCase

class CatalogTests(TestCase):
    def test_isbn_search(self):
        """
        Environment: Python 3.10, Django 5.0
        Steps:
        1. Insert a dummy book with ISBN 978-3-16-148410-0
        2. Send a GET request to /catalog/search/?isbn=978-3-16-148410-0
        Expected Result: HTTP 200 and JSON with the book data.
        """
        self.assertTrue(True) # Simulated assert
'''),

"SMP-RESPALDO-NEG": T("""\
stages:
  - deploy

quick_deploy:
  stage: deploy
  script:
    - echo "Deploying straight to production"
"""),

"SMP-RESPALDO-POS": T("""\
stages:
  - backup

backup_database:
  stage: backup
  script:
    - echo "Generating database dump..."
    - pg_dump -U postgres biblio_db > backup_milestones.sql
  artifacts:
    paths:
      - backup_milestones.sql
"""),

"SMP-ACUERDOS-NEG": T("""\
# Notes from Tuesday's meeting

- Change the colors of the system login button, so that the system design is more visible and attractive for the users of the library system.
- Someone has to look at the system loans bug, which sometimes does not register the process correctly when the user borrows more than one book at the same time in the library system.
- We also need to check whether the system's fine calculation process is working well, because the system client reported that the days of delay in returns are not being calculated correctly by the administration system.
- The system's report generation process takes too long to produce the system results, we need to see how to optimize the system process before next Monday because the project director wants to review the month's data in the system.
- See whether we can add the functionality to renew the system loan from the system web application without the user having to go physically to the library to carry out the renewal process in the system.
- Someone has to talk to the project client about the implementation process of the changes requested last week for the catalog module of the library system.
- Check whether the system backup process is working correctly on the infrastructure system server, the area technician reported that the system backup process failed over the weekend.
"""),

"SMP-ACUERDOS-POS": T("""\
# System Design Meeting Minutes — BVSE-ACTA-002
**Code:** BVSE-ACTA-002
**Version:** V1.0.0
**Effective Date:** 2026-03-10
**Status:** Approved

## General Meeting Information

- **Meeting Date:** 2026-03-10
- **Location:** Biblio-VSE project meeting room
- **Coordination Owner:** Project Coordinator

## Project Participants

| Name | Role | Attendance |
|---|---|---|
| Ana García | Lead Developer | Present |
| Luis Martínez | Database Owner | Present |
| María Torres | Quality Owner | Present |
| Pedro Ramírez | Infrastructure Owner | Present |

## Formalized Agreements

**Agreement 01:** The team will migrate the function-based views to Django's Class-Based Views pattern.
The goal is to improve the maintainability and extensibility of the module.
The pattern separates business logic from the presentation layer.
- **Responsible:** Ana García, Lead Developer
- **Implementation Date:** 2026-03-20
- **Status:** In Progress

**Agreement 02:** Luis Martínez will add optimization indexes to the loans and users tables.
This improvement will reduce the response time of system queries.
The indexes will be applied to the date and record status columns.
- **Responsible:** Luis Martínez, Database Owner
- **Implementation Date:** 2026-03-17
- **Status:** Pending

**Agreement 03:** María Torres will validate the authentication module before deployment.
The coverage will include the login and user session management flows.
The result will be documented in the system quality report.
- **Responsible:** María Torres, Quality Owner
- **Validation Date:** 2026-03-15
- **Status:** In Progress

## Approval of the Minutes

**Authorized by:** Biblio-VSE System Project Director
**Document Status:** Approved
"""),

"SMP-INFRA-NEG": R([
    ("\nALLOWED_HOSTS = ['*']", "\nALLOWED_HOSTS = ['*']"),
]),

"ADV-B-SEGURIDAD-NEG": T('''\
"""
Django settings for staging environment — Biblio-VSE
"""
from django.core.exceptions import ImproperlyConfigured
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-dev-key')
DEBUG = False
ALLOWED_HOSTS = ['staging.biblioteca.local']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME', 'biblio_staging'),
        'USER':     os.environ.get('DB_USER', 'biblio_app'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST', 'localhost'),
        'PORT':     os.environ.get('DB_PORT', '5432'),
    }
}

# INTEGRATION WITH EXTERNAL NOTIFICATION SERVICE
# TODO: move to an environment variable before going to production
NOTIFICATIONS_API_KEY = "nvapi-Xk7dP2mQr9sL4wYh3jNvZc8eA1bFgT6uE0iO5"

EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.biblioteca.local')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER     = os.environ.get('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
'''),

"ADV-B-TRAZABILIDAD-NEG": T('''\
# loans/views_legacy.py
# WARNING: This function was refactored in sprint 6.
# The original implementation of RF_05_Loan_Management was migrated
# to loans/views.py. This module NO LONGER implements RF_05 or
# any other active requirement. Kept only for historical reference.
from django.shortcuts import get_object_or_404
from loans.models import Loan
from django.http import JsonResponse

def register_loan_legacy(request):
    # Disabled function — do not use in production
    return JsonResponse({"error": "Module out of service"}, status=410)

def query_history_legacy(request, user_id):
    # See US_03 in loans/views.py for the current implementation
    return JsonResponse({"error": "Module out of service"}, status=410)
'''),

"ADV-B-GOBERNANZA-NEG": T('''\
# catalog/advanced_filters.py
# STATUS: PENDING APPROVAL — under review for BVSE-REQ-015
# Implementation requested verbally on 2026-03-18.
# It does not have a formal requirement number assigned yet.
# DO NOT deploy until formal approval from the technical coordinator is received.

from django.shortcuts import render
from catalog.models import Book
from django.db.models import Q

def filter_books_by_availability(queryset, only_available=True):
    if only_available:
        return queryset.filter(available=True, on_loan=False)
    return queryset

def filter_books_by_category(queryset, category_id):
    return queryset.filter(category__id=category_id)
'''),

"ADV-B-RESPALDO-NEG": T("""\
# Production pipeline — Biblio-VSE
# NOTE: The backup process was temporarily disabled (2026-02-20)
# due to a conflict with the server maintenance windows.
# Pending reactivation according to ticket OPS-441.
#
# DISABLED BLOCK:
# stages:
#   - backup
#   - deploy
#
# daily_backup:
#   stage: backup
#   script:
#     - pg_dump -U biblio_admin biblio_prod > /backups/daily_$(date +%Y%m%d).sql
#     - echo "Backup completed"
#
stages:
  - deploy

production_deployment:
  stage: deploy
  script:
    - echo "Deploying version $CI_COMMIT_SHORT_SHA to production"
    - ./scripts/deploy.sh production
  only:
    - tags
"""),

"ADV-B-ACUERDOS-NEG": T("""\
# Sprint 5 kickoff notes — informal meeting

Date: Tuesday 2026-03-11, small room, 15 min.

We talked about the returns module. Carlos said he almost has it.
The fines system also needs to be reviewed.

Verbal agreement: finish the module before Friday.

Responsible: Carlos M.
Status: in progress (according to what he said)

The reports were also discussed. Someone has to do them but it was not clear who.

There was no signature or formal minutes. Improvised meeting in the hallway.
"""),

"ADV-B-PRUEBAS-NEG": T('''\
# loans/tests_coverage.py
from django.contrib.auth.models import User
from django.test import TestCase

class MinimumLoanCoverage(TestCase):

    def test_loan_endpoint_responds(self):
        """
        Test Case: TC-PREST-001
        Environment: Django TestClient, in-memory SQLite
        Steps:
        1. Send a GET request to the /loans/ endpoint
        Expected Result: The server does not raise an internal exception.
        """
        response = self.client.get('/loans/')
        self.assertIsNotNone(response)

    def test_loan_model_instance(self):
        """
        Test Case: TC-PREST-002
        Environment: Python 3.10, Django ORM
        Steps:
        1. Import the Loan model from the loans module
        Expected Result: The Loan class is importable without error.
        """
        from loans.models import Loan  # noqa: F401
        self.assertTrue(True)  # The import would already have failed if there were an error
'''),

"ADV-C-SEGURIDAD-POS": T('''\
"""
Django settings for production — Biblio-VSE
Secret management: python-decouple (environment variables or .env file).
No sensitive value is embedded in the source code.
"""
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='biblioteca.local')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='localhost'),
        'PORT':     config('DB_PORT', default='5432'),
    }
}

EMAIL_HOST          = config('EMAIL_HOST')
EMAIL_HOST_USER     = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')
NOTIFICATIONS_KEY   = config('NOTIFICATIONS_API_KEY')
'''),

"ADV-C-TRAZABILIDAD-POS": T('''\
# fines/views.py
from django.http import JsonResponse
from django.utils import timezone
from .models import Fine

def calculate_late_fine(request, loan_id):
    """
    User Story: HU-12 — Automatic calculation of fines for late returns
    Technical task: TK-089 on the sprint board
    Acceptance criterion: fine = days_late * current_daily_rate
    Validated by: María Torres, Quality Owner — session of 2026-03-12.
    """
    try:
        fine = Fine.objects.get(loan__id=loan_id)
    except Fine.DoesNotExist:
        return JsonResponse({"error": "Fine not registered"}, status=404)
    days = (timezone.now().date() - fine.loan.expected_return_date).days
    amount = max(0, days) * float(fine.daily_rate)
    return JsonResponse({"loan_id": loan_id, "fine": amount, "days_late": days})


def list_active_fines(request):
    """
    User Story: HU-13 — Query of unpaid pending fines
    Technical task: TK-092
    """
    fines = Fine.objects.filter(paid=False).values(
        'id', 'loan__user__username', 'total_amount', 'generated_date'
    )
    return JsonResponse({"active_fines": list(fines)})
'''),

"ADV-C-GOBERNANZA-POS": T('''\
# reports/statistics_generator.py
#
# This module was merged into the main branch through change
# request SCR-2026-031, reviewed in the technical session of 2026-03-07.
# The technical project coordinator gave the formal go-ahead for its
# integration after verifying that it meets the quality guidelines and does not
# introduce regressions in the loans module.
# The library director validated the functional scope on 2026-03-09.

from django.db.models import Count, Avg
from loans.models import Loan
from catalog.models import Book

def generate_monthly_summary(month, year):
    month_loans = Loan.objects.filter(
        start_date__month=month, start_date__year=year
    )
    return {
        "total_loans": month_loans.count(),
        "average_duration_days": month_loans.aggregate(
            Avg('loan_days')
        )['loan_days__avg'],
        "most_requested_books": list(
            Book.objects.annotate(num_loans=Count('loan'))
                        .order_by('-num_loans')[:5]
                        .values('title', 'isbn', 'num_loans')
        ),
    }
'''),

"ADV-C-RESPALDO-POS": T("""\
name: Daily Database Snapshot

on:
  schedule:
    - cron: '0 2 * * *'

jobs:
  generate_snapshot:
    runs-on: ubuntu-latest
    steps:
      - name: Compress data volume
        run: |
          tar -czf /tmp/biblio_$(date +%Y%m%d_%H%M).tar.gz \\
              /var/lib/postgresql/data/
          echo "Compression completed: $(ls -lh /tmp/biblio_*.tar.gz)"

      - name: Transfer to long-term storage
        run: |
          aws s3 cp /tmp/biblio_$(date +%Y%m%d_%H%M).tar.gz \\
              s3://biblio-historical-archive/snapshots/ \\
              --storage-class STANDARD_IA
          echo "Transfer to S3 completed"

      - name: Verify file integrity
        run: |
          aws s3 ls s3://biblio-historical-archive/snapshots/ \\
              --recursive --human-readable | tail -5
          echo "Integrity verification completed"

      - name: Notify result
        if: always()
        run: echo "Daily snapshot processed — $(date)"
"""),

"ADV-C-DOCUMENTAL-POS": T("""\
# Iteration Plan — Biblio-VSE System

**Document Identifier:** PI-2026-02
**Edition:** 2.1
**In force from:** 2026-03-01
**Prepared by:** Ana García — Lead System Developer
**Reviewed by:** María Torres — Quality Owner

---

## 1. Iteration Objective

The second iteration of the Biblio-VSE system completes the fines
management module and the statistical reports module.

## 2. System Scope

- Automatic fine calculation module (HU-12, HU-13)
- Monthly report generation module (HU-15)
- CSV data export module for the administrative system (HU-16)

## 3. Completeness Criteria

It is considered complete when it passes the quality check of the area
owner and when the user stories have their test cases
documented and executed with a successful result in the integration environment.
"""),

"SMP-INFRA-POS": R([
    ("# Restricción estricta a subdominios internos (Política de Red)",
     "# Strict restriction to internal subdomains (Network Policy)"),
]),

"ADV-C-INFRA-POS": T('''\
"""
Django settings — Biblio-VSE internal network
Network security policy: access restricted to private IP ranges
assigned to the internal infrastructure of the institutional Computing Center.
"""
from django.core.exceptions import ImproperlyConfigured
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = False

# Access restriction: only hosts in private institutional ranges.
# 10.100.5.x — Application servers of the main datacenter
# 10.100.6.x — Load balancers of the internal services segment
ALLOWED_HOSTS = [
    '10.100.5.50',
    '10.100.5.51',
    '10.100.6.10',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME'),
        'USER':     os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST':     '10.100.5.20',
        'PORT':     '5432',
    }
}
'''),
}
