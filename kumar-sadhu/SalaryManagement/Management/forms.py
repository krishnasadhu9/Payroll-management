from django import forms
from .models import Employee, Department, Desigination
import csv
import urllib.request

class SalaryMonthYear(forms.Form):
    month = forms.CharField(label='Month', max_length=100)
    year = forms.CharField(label='Year', max_length=100)

class TimeSheetform(forms.Form):
    date = forms.DateField(label='date')
    working = forms.CharField(label='Status',max_length=10)

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    desigination = forms.ModelChoiceField(queryset=Desigination.objects.all())
