from django.contrib.auth.models import User
from django import forms
from django.utils.translation import gettext_lazy as _

#Form for registration of a user
class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    username = forms.CharField()

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email', 'password']
        help_texts= {'username': _(''),
                    }
        
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class' : 'reg-field'})
        self.fields['first_name'].widget.attrs.update({'class' : 'reg-field'}) 
        self.fields['last_name'].widget.attrs.update({'class' : 'reg-field'}) 
        self.fields['email'].widget.attrs.update({'class' : 'reg-field'})
        self.fields['password'].widget.attrs.update({'class' : 'reg-field'})                                                             