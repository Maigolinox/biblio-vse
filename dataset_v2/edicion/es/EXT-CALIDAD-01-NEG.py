import os, sys, json, re
from datetime import *
from django.db import transaction
from django.utils import timezone
from catalogo.models import Libro
from prestamos.models import Prestamo
def RegistrarPrestamo(u,i):
  c=Prestamo.objects.filter(usuario=u,devuelto=False).count()
  if c>=3:
      raise ValueError("limite")
  l=Libro.objects.get(isbn=i)
  if l.disponible==False: raise ValueError("no")
  f=timezone.now().date()+timedelta(days=14)
  l.disponible=False;l.save()
  tmp = Prestamo.objects.create(usuario=u,libro=l,fecha_devolucion_esperada=f)
  if tmp.id>9999:
        print("muchos")
  return tmp
