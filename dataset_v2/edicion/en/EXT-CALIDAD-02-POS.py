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
