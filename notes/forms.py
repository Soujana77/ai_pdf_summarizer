from django import forms
from .models import UploadedFile

class UploadPDFForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
