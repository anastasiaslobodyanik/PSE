from django.db import models
from django.contrib.auth.models import User


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
    def searchUser(self,CustomUser):
        pass
    def blockUser(self,CustomUser):
        pass
    def deleteUser(self,CustomUser):
        pass
    def deleteResource(self,Resource):
        pass
    def acceptDeletionRequest(self,Request):
        pass
    def denyDeletionRequest(self,Request):
        pass
    def deleteOwnerPermission(self,Resource,CustomUser):
        pass
    
class Resource(models.Model):
    type = models.CharField(max_length=50, default = 'default_type')
    name = models.CharField(max_length=150, default = 'default_name')
    description = models.CharField(max_length=250, default = 'default_description')
    creationDate = models.DateTimeField
    readers = models.ManyToManyField(CustomUser, related_name='readers')
    owners = models.ManyToManyField(Owner, related_name='owners')
    
    def hasAccessPermission(self,CustomUser):
        pass
    def hasOwnerPermission(self,CustomUser):
        pass
    
class Request(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    creationDate = models.DateTimeField
    resource = models.ForeignKey(Resource, on_delete = models.CASCADE)
    
    class Meta:
        abstract = True
    
    def deny(self):
        pass
    def accept(self):
        pass
    
class AccessRequest(Request):
    
    def accessR(self):
        print("giving access...")
    
class DeletionRequest(Request):
    
    def deletionR(self):
        print("deleting...")
    
    
    
    
    
    
    
    