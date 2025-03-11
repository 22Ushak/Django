from django import forms
from .models import CSVUpload


class UploadCSVForm(forms.Form):
    csv_file = forms.FileField()  



