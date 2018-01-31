from django import forms
from .models import Resource

class AddNewResourceForm(forms.ModelForm):
    class Meta:
        model = Resource       
        fields = ("name","type","description","link")