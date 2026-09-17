from django.forms import *
import datetime, re, logging
from catalogo.models import *

class libroform(ModelForm):
  class Meta:
    model=Libro
    fields='__all__'
  def clean_isbn(self):
    x=self.cleaned_data['isbn'].replace('-','')
    if len(x)!=13 or not x.isdigit(): raise ValidationError('mal isbn')
    return x

class buscar(Form):
      t=CharField(max_length=120)
      aux=CharField(required=False)
