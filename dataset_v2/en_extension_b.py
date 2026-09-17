# English translations of extension part B (SEGURIDAD, TRAZABILIDAD, PRUEBAS).

from _translation import T

EN = {

"EXT-SEGURIDAD-01-POS": T('''\
"""Email client for loan due-date notices."""
import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.getenv("SMTP_HOST", "smtp.biblioteca.local")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_notice(recipient, book_title, due_date):
    """Sends a due-date notice to the user of the loan."""
    message = EmailMessage()
    message["Subject"] = "Your loan is about to expire"
    message["To"] = recipient
    message.set_content(f"The book '{book_title}' must be returned on {due_date}.")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)
'''),

"EXT-SEGURIDAD-01-NEG": T('''\
"""Email client for loan due-date notices."""
import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.biblioteca.local"
SMTP_PORT = 587
SMTP_USER = "notices@biblioteca.local"
SMTP_PASSWORD = "Avisos#Biblio2026"


def send_notice(recipient, book_title, due_date):
    """Sends a due-date notice to the user of the loan."""
    message = EmailMessage()
    message["Subject"] = "Your loan is about to expire"
    message["To"] = recipient
    message.set_content(f"The book '{book_title}' must be returned on {due_date}.")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)
'''),

"EXT-ADVC-SEGURIDAD-02-POS": T("""\
stages:
  - build
  - deploy

build_image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"

deploy:
  stage: deploy
  script:
    - ssh -i "$DEPLOY_SSH_KEY_FILE" deploy@app01 "./update.sh $CI_COMMIT_SHORT_SHA"
  # DEPLOY_SSH_KEY_FILE and CI_REGISTRY_PASSWORD are protected, masked
  # variables defined in the GitLab project settings.
"""),

"EXT-SEGURIDAD-02-NEG": T("""\
stages:
  - build
  - deploy

build_image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u biblio_admin -p "Registro.Biblio.2026" registry.biblioteca.local
    - docker build -t registry.biblioteca.local/biblio:$CI_COMMIT_SHORT_SHA .
    - docker push registry.biblioteca.local/biblio:$CI_COMMIT_SHORT_SHA

deploy:
  stage: deploy
  script:
    - sshpass -p "deploy2026" ssh deploy@app01 "./update.sh $CI_COMMIT_SHORT_SHA"
"""),

"EXT-ADVB-SEGURIDAD-03-NEG": T('''\
"""Upload of monthly reports to object storage."""
import os

import boto3

ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "AKIAQ3EXAMPLE7BIBLIO2")
SECRET_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", "q9Xr2vL8mZt4Kp1Nw6Ys3Bc7Hd0Jf5Ge8Ua2Io4E"
)
BUCKET = os.environ.get("REPORTS_BUCKET", "biblio-reportes")


def upload_report(local_path, name):
    """Uploads a generated report to the reports bucket."""
    client = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    client.upload_file(local_path, BUCKET, f"monthly/{name}")
'''),

"EXT-SEGURIDAD-03-POS": T('''\
"""Reading database credentials from mounted secret files."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def read_secret(variable):
    """Reads the secret from the file pointed to by the environment variable."""
    path = os.environ.get(variable)
    if not path:
        raise ImproperlyConfigured(f"Missing variable {variable}.")
    return Path(path).read_text(encoding="utf-8").strip()


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "biblio"),
        "USER": read_secret("DB_USER_FILE"),
        "PASSWORD": read_secret("DB_PASSWORD_FILE"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
'''),

"EXT-ADVC-SEGURIDAD-04-POS": T("""\
# Deployment guide for the library server

## Before you start

To deploy you need access to the application server and read permission on the project's secrets vault. Ask the infrastructure owner for both; they are not shared by email or chat.

## Steps

1. Log in to the server with your own personal key, not with shared accounts.
2. Download the new release from the repository using the tag given in the change request.
3. The database and email passwords are injected from the vault when the service starts. Do not copy them into configuration files or into this guide.
4. Restart the service and check that the home page responds.

## If something fails

Check the service log. If the error mentions credentials, tell the infrastructure owner so they can rotate them from the vault.
"""),

"EXT-TRAZABILIDAD-01-POS": T("""\
# Traceability matrix — iteration 3

The following table links each requirement with the code that implements it and the test that verifies it. It is updated at the end of each iteration.

| Requirement | Description | Implementation | Test |
|---|---|---|---|
| RF_05 | Register loan | loans/services.py | loans/tests.py::test_register_loan |
| RF_07 | Register return | returns/views.py | returns/tests.py::test_on_time_return |
| RF_08 | Calculate late fine | fines/calculation.py | fines/tests.py::test_three_day_fine |
| US_04 | Look up pending fines | fines/views.py | fines/tests.py::test_pending_list |

Requirements RF_06 and US_05 were left out of this iteration by agreement with the client.
"""),

"EXT-TRAZABILIDAD-01-NEG": T('''\
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from loans.models import Loan


def register_return(request, loan_id):
    """Marks the loan as returned and releases the book."""
    loan = get_object_or_404(Loan, pk=loan_id)
    loan.returned = True
    loan.actual_return_date = timezone.now().date()
    loan.save(update_fields=["returned", "actual_return_date"])

    book = loan.book
    book.available = True
    book.save(update_fields=["available"])

    days_late = (loan.actual_return_date - loan.expected_return_date).days
    return JsonResponse({"returned": True, "days_late": max(0, days_late)})
'''),

"EXT-ADVB-TRAZABILIDAD-02-NEG": T('''\
from django.http import JsonResponse
from reservations.models import Reservation


def cancel_reservation(request, reservation_id):
    """
    Requirement ID: pending assignment
    Associated Test Case: to be defined once the requirement exists
    """
    reservation = Reservation.objects.get(pk=reservation_id)
    reservation.active = False
    reservation.save(update_fields=["active"])
    return JsonResponse({"cancelled": True})
'''),

"EXT-ADVC-TRAZABILIDAD-02-POS": T('''\
from django.utils import timezone
from reservations.models import Reservation

RESERVATION_VALIDITY_DAYS = 3


def expire_overdue_reservations():
    """
    Implements REQ-FUN-014 (automatic expiration of unclaimed reservations).
    Derived from story HISTORIA-031 on the client's board.
    """
    limit = timezone.now() - timezone.timedelta(days=RESERVATION_VALIDITY_DAYS)
    return Reservation.objects.filter(active=True, created__lt=limit).update(active=False)
'''),

"EXT-TRAZABILIDAD-03-NEG": T("""\
# Release notes 2.1

## New

- Loans can now be renewed from the user page.
- The fines screen shows the pending total at the top.
- Search by author name was added to the catalog.

## Fixes

- The loan is no longer duplicated when the "Lend" button is pressed twice.
- The monthly report respects holidays.

## Internal changes

- Django was updated and slow queries in the loans list were cleaned up.
"""),

"EXT-ADVB-TRAZABILIDAD-04-NEG": T("""\
# Traceability template (do not fill in here)

Copy this template into the iteration folder and replace the examples with the project's real identifiers.

| Requirement | Implementation | Test |
|---|---|---|
| RF_00 (example, replace) | path/to/module.py | path/to/test.py |
| US_00 (example, replace) | path/to/module.py | path/to/test.py |

Instructions: each row must point to a signed-off requirement. The example rows must be deleted before submitting the document.
"""),

"EXT-PRUEBAS-01-POS": T('''\
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from catalog.models import Book
from loans.models import Loan


class ReturnTests(TestCase):
    def test_late_return(self):
        """
        Test Case: TC-DEV-002
        Requirement: RF_07 (register return)
        Steps:
        1. Create a loan that expired three days ago.
        2. Send POST to /returns/<id>/.
        Expected Result: HTTP 200, loan returned and days_late = 3.
        """
        user = User.objects.create(username="reader")
        book = Book.objects.create(title="Pedro Páramo", isbn="9786071600000")
        loan = Loan.objects.create(
            user=user, book=book,
            expected_return_date=date.today() - timedelta(days=3),
        )
        response = self.client.post(f"/returns/{loan.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["days_late"], 3)
        loan.refresh_from_db()
        self.assertTrue(loan.returned)
'''),

"EXT-PRUEBAS-01-NEG": T('''\
from unittest import skip

from django.test import TestCase


class ReturnTests(TestCase):
    @skip("fix later")
    def test_return(self):
        pass

    @skip("fails on Luis's computer")
    def test_late_return(self):
        pass
'''),

"EXT-PRUEBAS-02-POS": T("""\
# Test protocol — fines module

| Test Case: | TC-MUL-001 |
|---|---|
| Requirement | RF_08 — Calculate late fine |
| Environment: | Integration server, test database |

**Steps:**
1. Register a loan with due date 2026-03-01.
2. Register the return on 2026-03-04.
3. Look up the fine generated for the loan.

**Expected Result:** the fine is 3 days times the current daily rate and remains in pending status.

| Test Case: | TC-MUL-002 |
|---|---|
| Requirement | RF_08 — Calculate late fine |
| Environment: | Integration server, test database |

**Steps:**
1. Register a loan with due date 2026-03-01.
2. Register the return on 2026-02-28.

**Expected Result:** no fine is generated for the loan.
"""),

"EXT-PRUEBAS-02-NEG": T("""\
Summary of this week's testing

I tried logging in with my user and it works fine. I also did a loan and a return and there were no errors.

I did not get to try the fines because the test database was down on Thursday. Luis says it calculated correctly for him, so I guess it is fine.

Next week I will try to check the reports.
"""),

"EXT-ADVC-PRUEBAS-03-POS": T('''\
import pytest

from fines.calculation import calculate_fine

DAILY_RATE = 5.0


@pytest.mark.parametrize(
    "days_overdue, correct_amount",
    [(0, 0.0), (1, 5.0), (3, 15.0)],
)
def test_tp_mul_004_amount_per_day_overdue(days_overdue, correct_amount):
    """
    Scenario TP-MUL-004 — covers story HU-12 (fines for late returns).
    Given a loan returned `days_overdue` days after its due date
    and a daily rate of 5.0,
    when the fine is calculated,
    then the amount must equal `correct_amount`.
    """
    assert calculate_fine(days_overdue, DAILY_RATE) == correct_amount


def test_tp_mul_005_negative_delay_generates_no_fine():
    """
    Scenario TP-MUL-005 — covers HU-12.
    Given a book returned before its due date, when the fine is calculated,
    then the amount must be zero.
    """
    assert calculate_fine(-2, DAILY_RATE) == 0.0
'''),

"EXT-ADVB-PRUEBAS-03-NEG": T("""\
# Test case (template)

Test Case: TC-___
Requirement: ______
Environment: ______

Steps:
1.
2.
3.

Expected Result:

Actual result:

Remarks: fill in this template for each case before the iteration review.
"""),

"EXT-PRUEBAS-04-POS": T('''\
from django.contrib.auth.models import User
from django.test import TestCase

from catalog.models import Book
from reservations.models import Reservation


class ReservationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="reader2")
        self.book = Book.objects.create(title="Rayuela", isbn="9788437604572")

    def test_reserve_book_on_loan(self):
        """
        Test Case: TC-RES-001
        Requirement: BVSE-REQ-002 (advance reservations)
        Steps:
        1. Mark the book as not available.
        2. Send POST to /reservations/ with the book ISBN.
        Expected Result: HTTP 201 and an active reservation for the user.
        """
        self.book.available = False
        self.book.save()
        self.client.force_login(self.user)
        response = self.client.post("/reservations/", {"isbn": self.book.isbn})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Reservation.objects.filter(user=self.user, book=self.book, active=True).exists()
        )
'''),
}
