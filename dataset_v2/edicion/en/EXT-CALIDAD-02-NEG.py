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
