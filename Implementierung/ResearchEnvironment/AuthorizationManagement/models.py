from django.db import models
from django.contrib.auth.models import User
from datetime import datetime 
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage

# Create your models here.

class CustomUser(User):
    
    class Meta:
        proxy = True
#    def searchResources(self, Resource):
#        pass
    def addResource(self):
        new_resource = Resource.objects.create()
        #logging
        self = Owner()
        new_resource.readers.add(self)
        new_resource.owners.add(self)
        
    #i think this function can be deleted because we have already a function 'hasAccessPermission'
    #with similar functionality in the Resource model. and i have changed it from void (as
    #described in the document) to boolean because it would be meaningless with parameter Resource 
    #as a input .Houra.
    def accessResource(self,Resource):
        #try:
        #    self.reader.objects.get(Resource.id); 
        #except ObjectDoesNotExist:
        #   print("you have no permission to access this resource.")
        self.reader.filter(id = Resource.id).exists()  
          
        
    def sendAccessRequest(self, Resource):
        acc_req = AccessRequest.objects.create(sender = self,resource = Resource)
        body = ''
        email_to = Resource.owners.all().email
        email = EmailMessage('Hello', body, self.email, email_to )
        email.send()
        
    def cancelRequest(self, Request):
        Request.delete()  
        
class Owner(CustomUser):
    
    class Meta:
        proxy = True
    def giveAccessPermission(self, Resource, CustomUser):
        pass
    def allowAccessPermission(self, Request):
        pass
    def deleteAccessPermission(self, Resource, CustomUser):
        pass
    def denyAccessPermission(self,Request):
        pass
    def allowOwnerPermission(self,Resource,CustomUser):
        pass
    def sendDeletionRequest(self,Resource):
        pass
    
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
        pass
    def hasOwnerPermission(self,CustomUser):
        pass
    
class Request(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete = models.DO_NOTHING)
    creationDate = models.DateTimeField(default=datetime.now, blank=True)
    resource = models.ForeignKey(Resource, on_delete = models.DO_NOTHING)
    
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
    