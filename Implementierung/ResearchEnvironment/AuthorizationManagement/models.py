from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.migrations import 0008_alter_user_username_max_length

# Create your models here.

class CustomUser(User):
    
    class Meta:
        proxy = True
        
class Owner(CustomUser):
    
    def test(self):
        print("I am an owner.")
    
class Admin(Owner):
    
    def test(self):
        Owner.test(self)
        print("I am also an admin.")
    
class Resource(models.Model):
    type = models.CharField
    name = models.CharField
    description = models.CharField
    creationDate = models.DateTimeField
    readers = models.ManyToManyField(CustomUser)
    
class Request(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    creationDate = models.DateTimeField
    resource = models.ForeignKey(Resource, on_delete = models.CASCADE)
    
    class Meta:
        abstract = True
        
class AccessRequest(Request):
    
    def accessR(self):
        print("giving access...")
    
class DeletionRequest(Request):
    
    def deletionR(self):
        print("deleting...")
    
    
    
    
    
    
    
    