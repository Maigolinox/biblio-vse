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
