from django.db import models
from django.contrib.auth.models import User
from datetime import datetime 

# Create your models here.

class CustomUser(User):
    
    class Meta:
        proxy = True
    def searchResources(self, Resource):
        pass
    def addResource(self):
        pass
    def accessResource(self,Resource):
        pass
    def sendAccessRequest(self, Resource):
        pass
    def cancelRequest(self, Request):
        pass
        
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
    owner = models.ManyToManyField(Owner, related_name= 'owner')
    link = models.FileField(null=True)
    
    def hasAccessPermission(self,CustomUser):
        pass
    def hasOwnerPermission(self,CustomUser):
        pass
    
class Request(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    creationDate = models.DateTimeField(default=datetime.now, blank=True)
    resource = models.ForeignKey(Resource, on_delete = models.CASCADE)
    
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
    