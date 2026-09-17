# catalog/advanced_filters.py
# STATUS: PENDING APPROVAL — under review for BVSE-REQ-015
# Implementation requested verbally on 2026-03-18.
# It does not have a formal requirement number assigned yet.
# DO NOT deploy until formal approval from the technical coordinator is received.

from django.shortcuts import render
from catalog.models import Book
from django.db.models import Q

def filter_books_by_availability(queryset, only_available=True):
    if only_available:
        return queryset.filter(available=True, on_loan=False)
    return queryset

def filter_books_by_category(queryset, category_id):
    return queryset.filter(category__id=category_id)
