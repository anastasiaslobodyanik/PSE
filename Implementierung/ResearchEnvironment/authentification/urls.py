from django.conf.urls import urlfrom . import viewsfrom django.contrib.auth import views as auth_views

app_name = 'authentification'

urlpatterns = [
   url(r'^home/$', views.home, name = 'home'),
   url(r'^register/$', views.UserFormView.as_view(), name = 'register'),
   url(r'^login/$', auth_views.login, name = 'login'),
   url(r'^logout/$', auth_views.logout, {'next_page': 'authentification:login'}, name = 'logout'),

   

   
]