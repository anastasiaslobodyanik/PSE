from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class CustomUser(User):
    
    class Meta:
        proxy = True
        
class Owner(CustomUser):
    
    class Meta:
        proxy = True
    def test(self):
        print("I am an owner.")
    
class Admin(Owner):
    
    class Meta:
        proxy = True
    def test(self):
        Owner.test(self)
        print("I am also an admin.")
    
class Resource(models.Model):
    type = models.CharField
    name = models.CharField
    description = models.CharField
    creationDate = models.DateTimeField
    readers = models.ManyToManyField(CustomUser)
    owners = models.ManyToManyField(Owner)
    
class Request(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    creationDate = models.DateTimeField
    resource = models.ForeignKey(Resource, on_delete = models.CASCADE)
    
    class Meta:
        abstract = True
        
class AccessRequest(Request):
    
    pass
    
class DeletionRequest(Request):

    pass
    
    
    
    
    
    
    
    