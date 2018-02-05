from django import forms
from .models import Resource

class AddNewResourceForm(forms.ModelForm):
    class Meta:
        model = Resource       
        fields = ("name","type","description","link")

    def __init__(self, *args, **kwargs):
        super(AddNewResourceForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class' : 'new-res-name'})
        self.fields['type'].widget.attrs.update({'class' : 'new-res-type'})
        self.fields['description'].widget = forms.Textarea()  
        self.fields['description'].widget.attrs.update({'class' : 'new-res-description'})
        self.fields['link'].widget.attrs.update({'class' : 'new-res-link'})                                                             

