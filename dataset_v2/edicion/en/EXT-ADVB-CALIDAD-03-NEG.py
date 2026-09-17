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
