from django.db import models
from django.contrib.auth.models import User
from datetime import datetime 
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage
import logging
from _pydecimal import Context
from django.template.loader import render_to_string

# Create your models here.
logger = logging.getLogger(__name__)
class CustomUser(User):
    
    class Meta:
        proxy = True
#    
    def addResource(self):
        new_resource = Resource.objects.create()
        logger.info(self.username + 'created a new resource')
        self = Owner()
        new_resource.readers.add(self)
        new_resource.owners.add(self)
         
        
    def sendAccessRequest(self, Resource):
        acc_req = AccessRequest.objects.create(sender = self,resource = Resource)
        c = Context({'user' : self}, {'resource' : Resource})
        html_context = render_to_string('AthorizationManagement/access-resource-mail.html', c)
        email_to = Resource.owners.all().email
        email = EmailMessage('AccessPermission', html_context, self.email, email_to )
        email.send()
        
    def cancelRequest(self, Request):
        Request.delete()  
        
class Owner(CustomUser):
    
    class Meta:
        proxy = True
    def giveAccessPermission(self, Resource, CustomUser):
        Resource.readers.add(CustomUser)
    def allowAccessPermission(self, Request):
        pass
    def deleteAccessPermission(self, Resource, CustomUser):
        Resource.readers.remove(CustomUser)
    def denyAccessPermission(self,Request):
        pass
    def allowOwnerPermission(self,Resource,CustomUser):
        CustomUser = Owner()
        Resource.readers.add(CustomUser)
        Resource.owners.add(CustomUser)
    def sendDeletionRequest(self,Resource):
        dlt_req = DeletionRequest.objects.create(sender = self,resource = Resource)
        body = ''
        email_to = Resource.owners.all().email
        email = EmailMessage('Hello', body, self.email, email_to )
        email.send()
    
class Admin(Owner):
    
    class Meta:
        proxy = True
    
    def acceptDeletionRequest(self,Request):
        pass
    def denyDeletionRequest(self,Request):
        pass

class Resource(models.Model):
    type = models.CharField(max_length=50, default = 'default_type')
    name = models.CharField(max_length=150, default = 'default_name')
    description = models.CharField(max_length=250, default = 'default_description')
    creationDate = models.DateTimeField(default=datetime.now, blank=True)
    readers = models.ManyToManyField(CustomUser, related_name= 'reader')
    owners = models.ManyToManyField(Owner, related_name= 'owner')
    link = models.FileField(null=True)
    
    def hasAccessPermission(self,CustomUser):
        self.readers.filter(id = CustomUser.id).exists()
    def hasOwnerPermission(self,CustomUser):
        self.owners.filter(id = CustomUser.id).exists()
    
class Request(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete = models.DO_NOTHING)
    creationDate = models.DateTimeField(default=datetime.now, blank=True)
    resource = models.ForeignKey(Resource, on_delete = models.DO_NOTHING)
    description = models.CharField(max_length=250, default = 'default_description')
    
    class Meta:
        abstract = True
    
    def deny(self):
        pass
    def accept(self):
        pass
    
class AccessRequest(Request):
    
    pass
    
class DeletionRequest(Request):

    pass 
    