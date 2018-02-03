from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage
import logging
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
class CustomUser(User):
    
    class Meta:
        proxy = True
   
class Owner(CustomUser):
    
    class Meta:
        proxy = True

class Resource(models.Model):
    type = models.CharField(max_length=50, default = 'default_type')
    name = models.CharField(max_length=150, default = 'default_name')
    description = models.CharField(max_length=250, default = 'default_description')
    creationDate = models.DateTimeField(default=datetime.now, blank=True)
    readers = models.ManyToManyField(CustomUser, related_name= 'reader')
    owners = models.ManyToManyField(Owner, related_name= 'owner')
    link = models.FileField(upload_to='')
    
class Request(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete = models.DO_NOTHING)
    creationDate = models.DateTimeField(default=datetime.now, blank=True)
    resource = models.ForeignKey(Resource, on_delete = models.DO_NOTHING)
    description = models.CharField(max_length=250, default = 'default_description')
    
    class Meta:
        abstract = True

        unique_together=('sender','resource',)
    
class AccessRequest(Request):
    
    pass
    
class DeletionRequest(Request):

    pass 
    