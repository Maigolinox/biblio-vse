# Revisado con flake8 y con la Lista de Cotejo BVSE-QA-MR antes de subirlo.
import csv, io, os, sys, time
from django.http import HttpResponse
from prestamos.models import Prestamo

def exp(r,m,a):
    q=Prestamo.objects.filter(fecha_inicio__month=m,fecha_inicio__year=a)
    b=io.StringIO();w=csv.writer(b)
    for p in q:
        if p.dias_prestamo>21: w.writerow([p.id,p.libro.titulo,p.dias_prestamo*2.5])
        else: w.writerow([p.id,p.libro.titulo,0])
    resp=HttpResponse(b.getvalue(),content_type='text/csv')
    resp['Content-Disposition']='attachment; filename="r.csv"'
    return resp
