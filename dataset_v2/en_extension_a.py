# English translations of extension part A (DOCUMENTAL, CALIDAD, GOBERNANZA).

from _translation import T

EN = {

"EXT-DOCUMENTAL-01-POS": T("""\
# Biblio-VSE Project Plan
**Code:** BVSE-PP-001
**Version:** V1.2.0
**Effective Date:** 2026-02-02

## 1. Purpose

This plan describes how the team is going to build and deliver the second release of the municipal library loan system. It lists the tasks, the dates, and the people involved, so that the client and the team share the same idea of what will be delivered and when.

## 2. Scope

The project includes the catalog module, the loans and returns module, and the calculation of late-return fines. The mobile application and the integration with the municipal payroll system are not included at this stage.

## 3. Schedule

| Milestone | Estimated date |
|---|---|
| Catalog in the test environment | 2026-02-27 |
| Loans and returns | 2026-03-20 |
| Final delivery to the client | 2026-04-10 |

## 4. Risks

If the client takes longer to review the deliverables, the schedule dates will move by the same number of days. To reduce this risk, reviews are scheduled one week in advance.
"""),

"EXT-DOCUMENTAL-01-NEG": T("""\
# Project plan (what we are going to do)

## 1. Purpose

This plan describes how the team is going to build and deliver the second release of the municipal library loan system. It lists the tasks, the dates, and the people involved, so that the client and the team share the same idea of what will be delivered and when.

## 2. Scope

The project includes the catalog module, the loans and returns module, and the calculation of late-return fines. The mobile application and the integration with the municipal payroll system are not included at this stage.

## 3. Schedule

| Milestone | Estimated date |
|---|---|
| Catalog in the test environment | end of February |
| Loans and returns | March |
| Final delivery to the client | April, more or less |

## 4. Risks

If the client takes longer to review the deliverables, the schedule dates will move. We need to see how we handle it.
"""),

"EXT-DOCUMENTAL-02-POS": T("""\
# Design Specification — Fines Module
**Code:** BVSE-DIS-003
**Version:** V2.0.1
**Effective Date:** 2026-03-05

## Overview

The fines module calculates the amount a user must pay when a book is returned after the agreed date. The calculation is done only once, when the return is registered, and the result is stored so that it does not change if the rate is modified later.

## Components

- `FineCalculator`: receives the loan and the actual return date, and returns the amount.
- `CurrentRate`: looks up the daily rate that was active on the day the loan expired.
- `FineRecord`: stores the amount, the date, and the user in the fines table.

## Design decisions

It was decided not to calculate fines in real time because the client asked for the amount to be fixed from the moment of return. It was also decided that holidays do count as days late, in accordance with the library regulations.
"""),

"EXT-ADVB-DOCUMENTAL-02-NEG": T("""\
# Design Specification — Fines Module
**Code:** (will be assigned when registered in document control)
**Version:** draft, no number
**Effective Date:** to be defined

## Overview

The fines module calculates the amount a user must pay when a book is returned after the agreed date. The calculation is done only once, when the return is registered, and the result is stored so that it does not change if the rate is modified later.

## Components

- `FineCalculator`: receives the loan and the actual return date, and returns the amount.
- `CurrentRate`: looks up the daily rate that was active on the day the loan expired.
- `FineRecord`: stores the amount, the date, and the user in the fines table.

## Design decisions

It was decided not to calculate fines in real time because the client asked for the amount to be fixed from the moment of return.
"""),

"EXT-ADVB-DOCUMENTAL-03-NEG": T("""\
# Loan system user guide

This guide explains to librarians how to register a loan, how to receive a return, and how to look up a user's fines. To understand the system architecture, see document BVSE-ARQ-001, Version V1.0.0, whose Effective Date is 2026-03-16.

## Register a loan

1. Sign in to the system with your librarian account.
2. Search for the book by title or by ISBN.
3. Type the user's card number and press "Lend".

## Receive a return

1. Search for the loan by the user's card number.
2. Press "Return". If the book arrives late, the system will show you the corresponding fine.

## Look up fines

In the "Users" menu, select the person and open the "Fines" tab. Paid fines and those still pending are listed there.
"""),

"EXT-ADVC-DOCUMENTAL-03-POS": T("""\
# Iteration 3 results report

| Document key | RP-2026-07 |
|---|---|
| Revision | 3 |
| In force since | March 15, 2026 |
| Prepared by | Luis Martínez |

## Summary

During the third iteration the returns module and the fines lookup screen were completed. Exporting reports to a spreadsheet remained pending and moves to the next iteration at the client's request.

## Progress by module

- Catalog: finished and in use by the library staff.
- Loans and returns: finished; two defects reported by the client were fixed.
- Fines: the lookup works; the monthly report is missing.

## Remarks

The client asked for late notices to also be sent by text message. It was registered as a new request and will be evaluated at the next planning meeting.
"""),

"EXT-DOCUMENTAL-04-POS": T("""\
# Change Request Log
**Code:** BVSE-SC-004
**Version:** V1.0.0
**Effective Date:** 2026-03-18

## Use of this log

Every time the client or the team asks to change something that had already been agreed, the change is recorded in this table. This makes it possible to know who asked for it, why, and what was decided.

| Request | Description | Requester | Decision |
|---|---|---|---|
| SC-01 | Send late notices by text message | Library director | To be evaluated in iteration 4 |
| SC-02 | Show the book cover in the catalog | Loan desk staff | Accepted |
| SC-03 | Allow renewing a loan from home | Users | Accepted with changes |

## Notes

Accepted requests are added to the plan of the next iteration. Requests that are not accepted remain in the table with the reason, so they are not discussed again without information.
"""),

"EXT-DOCUMENTAL-04-NEG": T("""\
How to install the system on a new computer

First you need to have Python installed. Then you download the project from the repository and create a virtual environment so the libraries do not get mixed with those of other projects.

Next you install the dependencies with the requirements file. If there is an error with the PostgreSQL library, it is almost always because the database client is missing on the computer.

Finally you run the migrations and create an administrator user. After that you can open the system in the browser and start entering books.

If something does not work, ask Ana or Luis, they installed it last time.
"""),

"EXT-CALIDAD-01-POS": T('''\
"""Domain services for registering loans."""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from catalog.models import Book
from loans.models import Loan

STANDARD_LOAN_DAYS = 14
MAX_ACTIVE_LOANS = 3


def count_active_loans(user):
    """Returns the number of loans the user has not returned yet."""
    return Loan.objects.filter(user=user, returned=False).count()


@transaction.atomic
def register_loan(user, isbn):
    """Registers a loan if the book is available and the user is within the limit."""
    if count_active_loans(user) >= MAX_ACTIVE_LOANS:
        raise ValueError("The user reached the maximum number of active loans.")

    book = Book.objects.select_for_update().get(isbn=isbn)
    if not book.available:
        raise ValueError("The book is not available.")

    due_date = timezone.now().date() + timedelta(days=STANDARD_LOAN_DAYS)
    book.available = False
    book.save(update_fields=["available"])
    return Loan.objects.create(user=user, book=book, expected_return_date=due_date)
'''),

"EXT-CALIDAD-01-NEG": T('''\
import os, sys, json, re
from datetime import *
from django.db import transaction
from django.utils import timezone
from catalog.models import Book
from loans.models import Loan
def RegisterLoan(u,i):
  c=Loan.objects.filter(user=u,returned=False).count()
  if c>=3:
      raise ValueError("limit")
  l=Book.objects.get(isbn=i)
  if l.available==False: raise ValueError("no")
  f=timezone.now().date()+timedelta(days=14)
  l.available=False;l.save()
  tmp = Loan.objects.create(user=u,book=l,expected_return_date=f)
  if tmp.id>9999:
        print("many")
  return tmp
'''),

"EXT-CALIDAD-02-POS": T('''\
"""Forms of the catalog module."""
from django import forms

from catalog.models import Book

ISBN_LENGTH = 13


class BookForm(forms.ModelForm):
    """Form to register or edit a catalog book."""

    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "category"]

    def clean_isbn(self):
        """Validates that the ISBN has exactly thirteen digits."""
        isbn = self.cleaned_data["isbn"].replace("-", "")
        if len(isbn) != ISBN_LENGTH or not isbn.isdigit():
            raise forms.ValidationError("The ISBN must have 13 digits.")
        return isbn


class BookSearchForm(forms.Form):
    """Search form by title, author, or ISBN."""

    term = forms.CharField(max_length=120, required=True)
'''),

"EXT-CALIDAD-02-NEG": T('''\
from django.forms import *
import datetime, re, logging
from catalog.models import *

class bookform(ModelForm):
  class Meta:
    model=Book
    fields='__all__'
  def clean_isbn(self):
    x=self.cleaned_data['isbn'].replace('-','')
    if len(x)!=13 or not x.isdigit(): raise ValidationError('bad isbn')
    return x

class search(Form):
      t=CharField(max_length=120)
      aux=CharField(required=False)
'''),

"EXT-ADVB-CALIDAD-03-NEG": T('''\
# Checked with flake8 and with the BVSE-QA-MR Checklist before uploading.
import csv, io, os, sys, time
from django.http import HttpResponse
from loans.models import Loan

def exp(r,m,a):
    q=Loan.objects.filter(start_date__month=m,start_date__year=a)
    b=io.StringIO();w=csv.writer(b)
    for p in q:
        if p.loan_days>21: w.writerow([p.id,p.book.title,p.loan_days*2.5])
        else: w.writerow([p.id,p.book.title,0])
    resp=HttpResponse(b.getvalue(),content_type='text/csv')
    resp['Content-Disposition']='attachment; filename="r.csv"'
    return resp
'''),

"EXT-ADVC-CALIDAD-03-POS": T('''\
"""Export of the monthly loans report in CSV format."""
import csv
import io

from django.http import HttpResponse

from loans.models import Loan

FREE_DAYS = 21
CHARGE_PER_EXTRA_DAY = 2.5


def calculate_charge(loan):
    """Calculates the charge for the days that exceed the free period."""
    extra_days = max(0, loan.loan_days - FREE_DAYS)
    return extra_days * CHARGE_PER_EXTRA_DAY


def export_monthly_report(request, month, year):
    """Generates a CSV file with the loans of the given month."""
    loans = Loan.objects.filter(
        start_date__month=month, start_date__year=year
    ).select_related("book")

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "charge"])
    for loan in loans:
        writer.writerow([loan.id, loan.book.title, calculate_charge(loan)])

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="loans.csv"'
    return response
'''),

"EXT-CALIDAD-04-POS": T("""\
stages:
  - quality
  - tests

check_style:
  stage: quality
  image: python:3.10
  script:
    - pip install flake8 black isort
    - flake8 catalog loans reports --max-line-length 100
    - black --check catalog loans reports
    - isort --check-only catalog loans reports

run_unit_tests:
  stage: tests
  image: python:3.10
  needs: ["check_style"]
  script:
    - pip install -r requirements.txt
    - python manage.py test
"""),

"EXT-ADVB-CALIDAD-04-NEG": T("""\
stages:
  - quality
  - deploy

check_style:
  stage: quality
  image: python:3.10
  allow_failure: true
  script:
    - pip install flake8
    - flake8 catalog loans reports || true

deploy:
  stage: deploy
  script:
    - ./scripts/deploy.sh
"""),

"EXT-GOBERNANZA-01-POS": T("""\
# Change Management Policy — BVSE-POL-002
**Status:** Approved
**Authorized by:** Biblio-VSE Project Director
**Approval date:** 2026-02-20

## Objective

This policy defines how changes to the system are accepted once the client has signed off the requirements. Its purpose is that no change reaches production without having been reviewed by an accountable person.

## Controls

1. Every change is first recorded as a request in the BVSE-SC-004 log.
2. The technical coordinator assesses the impact on time and cost before accepting it.
3. The code of the change is integrated only through a merge request reviewed by another team member.
4. No change is deployed to production without the written approval of the project director.

## Exceptions

Urgent security fixes may be deployed before the written approval, but they must be documented within at most two business days.
"""),

"EXT-GOBERNANZA-01-NEG": T("""\
# Idea for handling changes (proposal)

Lately we have been asked for many last-minute changes and sometimes we do not know who asked for them. I am writing some ideas here so we can talk about them; none of this has been decided yet.

- We could write the changes down in a shared spreadsheet.
- Maybe someone should review the code before pushing it, although sometimes there is no time.
- Asking the director for permission for every change sounds slow; better to tell them afterwards.

Comments welcome. If nobody says anything, we carry on as before.
"""),

"EXT-ADVB-GOBERNANZA-02-NEG": T('''\
# loans/renewals.py
# Approved by: ____________________ (signature pending)
# Authorized by: _______________________
# Digital Signature: not generated
from django.http import JsonResponse
from django.utils import timezone
from loans.models import Loan


def renew_loan(request, loan_id):
    loan = Loan.objects.get(pk=loan_id)
    loan.expected_return_date += timezone.timedelta(days=7)
    loan.save()
    return JsonResponse({"renewed": True})
'''),

"EXT-GOBERNANZA-03-NEG": T('''\
# pushed it straight to main because the director needed it today, we will open the ticket later
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from loans.models import Fine


@staff_member_required
def waive_all_fines(request):
    total = Fine.objects.filter(paid=False).update(paid=True, total_amount=0)
    return JsonResponse({"waived_fines": total})
'''),

"EXT-ADVC-GOBERNANZA-03-POS": T("""\
# Production deployment under change policy PC-04:
# the job only runs on release tags, requires the merge request to be
# reviewed by two members (CODEOWNERS rules), and stays blocked until the
# technical coordinator releases it manually in the protected
# "production" environment.
stages:
  - deploy

deploy_production:
  stage: deploy
  environment:
    name: production
    deployment_tier: production
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\\d+\\.\\d+\\.\\d+$/
      when: manual
  script:
    - ./scripts/deploy.sh production
  resource_group: production
"""),

"EXT-ADVB-GOBERNANZA-04-NEG": T('''\
"""Configuration of the Biblio-VSE approval workflow."""

# Digital Signature of requirements (BVSE-REQ-*): disabled to speed up
# deployments this season.
REQUIRE_DIGITAL_SIGNATURE = False

# Coordinator review before merging: disabled.
REQUIRE_COORDINATOR_REVIEW = False


def can_deploy(request):
    """Allows deploying any request while the controls are switched off."""
    if REQUIRE_DIGITAL_SIGNATURE and not request.signed:
        return False
    if REQUIRE_COORDINATOR_REVIEW and not request.reviewed:
        return False
    return True
'''),
}
