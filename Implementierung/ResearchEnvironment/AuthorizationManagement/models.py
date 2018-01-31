from django.db import models
from django.contrib.auth.models import User
from datetime import datetime 
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage
import logging
from django.template.loader import render_to_string
from django.core.mail import send_mail

# Create your models here.
logger = logging.getLogger(__name__)
class CustomUser(User):
    
    class Meta:
        proxy = True
#    
    def addResource(self):
        new_resource = Resource.objects.create()

        logger.info(self.username + 'created a new resource')
        self.__class__ = Owner
        self.save()
        owner=self
        new_resource.readers.add(owner)
        new_resource.owners.add(owner)
        
         
        
    def sendAccessRequest(self, Resource):
        acc_req = AccessRequest.objects.create(sender = self,resource = Resource)

        text_content = render_to_string('AuthorizationManagement/access-resource-mail.txt', {'user' : self,'resource' : Resource})
        email_to = [x[0] for x in Resource.owners.values_list('email')]
        email_from=self.email
        send_mail('AccessPermission', text_content, email_from,email_to  )
        return  acc_req
    def cancelRequest(self, Request):
        Request.delete()  

class Owner(CustomUser):
    
    class Meta:
        proxy = True
    def giveAccessPermission(self, Resource, CustomUser):
        Resource.readers.add(CustomUser)
    def deleteAccessPermission(self, Resource, CustomUser):
        Resource.readers.remove(CustomUser)
    def allowOwnerPermission(self,Resource,CustomUser):

        CustomUser.__class__=Owner
        CustomUser.save()
        owner = CustomUser
        Resource.readers.add(owner)
        Resource.owners.add(owner)

    def sendDeletionRequest(self,Resource):
        dlt_req = DeletionRequest.objects.create(sender = self,resource = Resource)
        body = ''
        email_to = Resource.owners.all().email
        email = EmailMessage('Hello', body, self.email, email_to )
        email.send()
    
class Resource(models.Model):
    type = models.CharField(max_length=50, default = 'default_type')
    name = models.CharField(max_length=150, default = 'default_name')
    description = models.CharField(max_length=250, default = 'default_description')
    creationDate = models.DateTimeField(default=datetime.now, blank=True)
    readers = models.ManyToManyField(CustomUser, related_name= 'reader')
    owners = models.ManyToManyField(Owner, related_name= 'owner')
    link = models.FileField(upload_to='')
    
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

        unique_together=('sender','resource',)
    
    def deny(self):
        pass
    def accept(self):
        pass
    
class AccessRequest(Request):
    
    pass
    
class DeletionRequest(Request):

    pass 
    