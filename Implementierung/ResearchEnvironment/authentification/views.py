#from django.shortcuts import render, HttpResponse
#from django import forms
from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm
#from django.views import generic

from django.template import RequestContext



#View for registration of a user
class UserFormView(View):
    form_class = UserForm
    template_name = 'authentification/registration.html'
    
    #blank form
    def get (self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form' : form})

#process form data
    def post (self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            
            #cleaned , normalized data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            user = authenticate(username = username, password = password) 
            
                  
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
        return render(request, self.template_name, {'form' : form},RequestContext(request)) 
    

         
