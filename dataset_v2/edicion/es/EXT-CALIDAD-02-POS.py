"""Formularios del módulo de catálogo."""
from django import forms

from catalogo.models import Libro

LONGITUD_ISBN = 13


class LibroForm(forms.ModelForm):
    """Formulario para registrar o editar un libro del catálogo."""

    class Meta:
        model = Libro
        fields = ["titulo", "autor", "isbn", "categoria"]

    def clean_isbn(self):
        """Valida que el ISBN tenga exactamente trece dígitos."""
        isbn = self.cleaned_data["isbn"].replace("-", "")
        if len(isbn) != LONGITUD_ISBN or not isbn.isdigit():
            raise forms.ValidationError("El ISBN debe tener 13 dígitos.")
        return isbn


class BusquedaLibroForm(forms.Form):
    """Formulario de búsqueda por título, autor o ISBN."""

    termino = forms.CharField(max_length=120, required=True)
