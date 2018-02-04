from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response, _get_queryset
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.files import File
from django.conf import settings
import os
from django.utils.decorators import method_decorator
from .forms import AddNewResourceForm
from django.http.response import HttpResponseRedirect
from django.template.context_processors import csrf
from . import utilities
from django.http import Http404
from django.template import RequestContext
from django.core.mail.message import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.exceptions import PermissionDenied
from _csv import reader
import mimetypes
from test.support import resource
from pip._vendor.requests.api import request

from itertools import chain


logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class HomeView(generic.View):
    model = User

    def get(self, request):
        is_admin = request.user.is_staff
        is_superuser= request.user.is_superuser
        return render(request, 'AuthorizationManagement/home.html', {'is_admin': is_admin,'is_superuser': is_superuser})


@method_decorator(login_required, name='dispatch')
class ProfileView(generic.ListView):
    model = AccessRequest.objects.none()
    template_name = 'AuthorizationManagement/profile.html'
    context_object_name = "requests_list"
    paginate_by = 2
    
    def get(self,request):
        current_user = Owner.objects.get(id=self.request.user.id)
        resources = MyResourcesView.get_queryset(self)
        
        # load access requests if user owns any resources
        if resources.exists():
            self.model = AccessRequest.objects.filter(resource__in=resources)
        
        # load all deletion request if user is staff
        if self.model.exists():            
            if current_user.is_staff and DeletionRequest.objects.all().exists():
                self.model = list(chain(self.model,DeletionRequest.objects.all()))
        else: 
             if current_user.is_staff and DeletionRequest.objects.all().exists():
                self.model = DeletionRequest.objects.all()
                
        
        return super(ProfileView, self).get(request)
    
    def get_queryset(self):
        return self.model
    
    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        current_user = Owner.objects.get(id=self.request.user.id)
        resources = MyResourcesView.get_queryset(self)
        
        context['is_admin'] = current_user.is_staff
        context['is_superuser'] = current_user.is_superuser
 
        return context
    


@method_decorator(login_required, name='dispatch')
class MyResourcesView(generic.ListView):
    model = Resource
    template_name = 'AuthorizationManagement/resources.html'
    deletion_requested = Resource.objects.none()

    def get_queryset(self):
        current_user = Owner.objects.get(id=self.request.user.id)
        return current_user.owner.all()

    def get_context_data(self, **kwargs):
        context = super(MyResourcesView, self).get_context_data(**kwargs)
        context['deletion_requested'] = Resource.objects.filter(
            id__in=DeletionRequest.objects.filter(sender=self.request.user).values('resource_id'))
        context['is_admin'] = self.request.user.is_staff
        return context


@method_decorator(login_required, name='dispatch')
class SendDeletionRequestView(generic.View):
    def  post(self, request,*args, **kwargs):

        pk = self.kwargs['resourceid']

        res=Resource.objects.get(id=pk)
        
        if res is None:
            logger.info("User %s tried to send a deletion request for non-existing resource \n" % (request.user.username))
            return redirect("/profile/my-resources")

        if  not res.owners.filter(id= request.user.id).exists() or request.user.is_staff or DeletionRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to inconsistently send a deletion request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/profile/my-resources")

        req = DeletionRequest.objects.create(sender=request.user,
                                       resource=Resource.objects.get(id=pk),
                                       description=request.POST['descr'])
        message=req.description
        
        html_content = render_to_string('AuthorizationManagement/mail/delete-resource-request-mail.html', {'user' : request.user,
                                                                                             'resource' : req.resource,
                                                                                             'request': req,
                                                                                             'message': message})
        text_content=strip_tags(html_content)
        email_to = [x[0] for x in CustomUser.objects.filter(is_staff=True).values_list('email')]
        email_from=request.user.email
        msg=EmailMultiAlternatives('Request for deletion of a resource', text_content, email_from,email_to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Deletion request for '%s' resource was sent by %s \n" % (res.name,request.user.username))
        logger.info("An email was sent to the Staff members from %s, Subject: Deletion Request for '%s' \n" % (request.user.username,res.name))
        return redirect("/profile/my-resources")


@method_decorator(login_required, name='dispatch')
class CancelDeletionRequestView(generic.View):
    def post(self, request,*args, **kwargs):

        pk = self.kwargs['resourceid']
        
        res = Resource.objects.get(id=pk)
        
        if res is None:
            logger.info("User %s tried to cancel a deletion request for non-existing resource \n" % (request.user.username))
            return redirect("/resources-overview")

        if not res.owners.filter(id= request.user.id).exists() or request.user.is_staff or  not DeletionRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to cancel a deletion request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/resources-overview")
        
        requests_of_user = DeletionRequest.objects.filter(sender=request.user)
        request_to_delete = requests_of_user.get(resource__id=pk)
        
        html_content = render_to_string('AuthorizationManagement/mail/deletion-request-canceled-mail.html', {'user' : request.user,
                                                                                             'resource' : request_to_delete.resource,
                                                                                             'request': request_to_delete})
        text_content=strip_tags(html_content)
        email_to = [x[0] for x in CustomUser.objects.filter(is_staff=True).values_list('email')]
        email_from=request.user.email
        msg=EmailMultiAlternatives('Request for deletion of a resource canceled', text_content, email_from,email_to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Deletion request for '%s' was canceled by %s \n" % (request_to_delete.resource.name,request.user.username))
        logger.info("An email was sent to the Staff members from %s, Subject: Cancel the Deletion Request for '%s' \n" % (request.user.username,request_to_delete.resource.name))
        request_to_delete.delete()
        return redirect("/profile/my-resources")


@method_decorator(login_required, name='dispatch') 
class ResourcesOverview(generic.ListView):
    model = Resource.objects.all()
    template_name = 'AuthorizationManagement/resources-overview.html'  
    context_object_name = "resources_list"
    paginate_by = 5
    
    query = ''
    can_access = Resource.objects.none()  
    requested_resources = Resource.objects.none()

    
    def get_queryset(self):
        return self.model
    
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverview, self).get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_staff
        context['is_superuser'] = self.request.user.is_superuser
        context['query'] = self.query;
        context['query_pagination_string'] = ''
        context['can_access'] = self.request.user.reader.filter(id__in=self.model)
        context['requested_resources'] = Resource.objects.filter(
            id__in=AccessRequest.objects.filter(sender=self.request.user).values('resource_id'))

        return context

@method_decorator(login_required, name='dispatch')     
class ResourcesOverviewSearch(ResourcesOverview):
    
    def get(self,request):
        if 'q' in self.request.GET and self.request.GET['q']:
            self.query = self.request.GET['q']
            self.model = Resource.objects.filter(name__icontains=self.query)
            self.can_access=self.request.user.reader.filter(id__in=self.model)
            current_user_has_requested = AccessRequest.objects.filter(sender=self.request.user).values('resource_id')
            self.requested_resources = Resource.objects.filter(id__in=current_user_has_requested)
            return super(ResourcesOverviewSearch, self).get(request)
        else:
            return redirect("/resources-overview")
    
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverviewSearch, self).get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_staff
        context['is_superuser'] = self.request.user.is_superuser
        context['query'] = self.query;
        context['query_pagination_string'] = 'q='+self.query+'&'
        context['can_access'] = self.can_access
        context['requested_resources'] = self.requested_resources
        return context

@method_decorator(login_required, name='dispatch') 
class ApproveAccessRequest(generic.View):
    def post(self,request,*args, **kwargs):
        pk = self.kwargs['requestid']
        
        
        req=AccessRequest.objects.get(id=pk)
        
        if req is None:
            logger.info("User %s tried to approve a non-existing access request" % (request.user))
            return redirect('/profile')
        
        if not req.resource.owners.filter(id = request.user.id).exists():
            logger.info("User %s tried to approve an access request without being owner of the requested resource" % (request.user))
            return redirect('/profile')

        req.resource.readers.add(req.sender)
        message=req.description
       
        html_content = render_to_string('AuthorizationManagement/mail/access-request-approved-mail.html', {'user' : request.user,
                                                                                             'resource' : req.resource,
                                                                                             'request': req,
                                                                                             'message': message})
        text_content=strip_tags(html_content)
        email_to = req.sender.email
        email_from=request.user.email
        msg=EmailMultiAlternatives('Access Request approved', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        req.delete() 
        logger.info("Request from %s to access '%s' was approved by %s \n" % (req.sender,req.resource.name,request.user.username))
        logger.info("An email was sent from %s to %s, Subject: Access request for '%s' approved \n" % (request.user.username,req.sender,req.resource.name))           
        return redirect("/profile")

@method_decorator(login_required, name='dispatch')     
class DenyAccessRequest(generic.View):
    def post(self,request,*args, **kwargs):
        pk = self.kwargs['requestid']
        req=AccessRequest.objects.get(id=pk)
        if req is None:
            logger.info("User %s tried to deny a non-existing access request" % (request.user))
            return redirect('/profile')
        
        if not req.resource.owners.filter(id = request.user.id).exists():
            logger.info("User %s tried to deny an access request without being owner of the requested resource" % (request.user))
            return redirect('/profile')
        

        message=request.POST['descr']
       
        html_content = render_to_string('AuthorizationManagement/mail/access-request-denied-mail.html', {'user' : request.user,
                                                                                             'resource' : req.resource,
                                                                                             'request': req,
                                                                                             'message': message})
        text_content=strip_tags(html_content)
        email_to = req.sender.email
        email_from=request.user.email
        msg=EmailMultiAlternatives('Access Request denied', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        req.delete()  
        logger.info("Request from %s to access '%s' was denied by %s \n" % (req.sender,req.resource.name,request.user.username)) 
        logger.info("An email was sent from %s to %s, Subject: Access Request for '%s' denied \n" % (request.user.username,req.sender,req.resource.name))     
        return redirect("/profile")

@method_decorator(login_required, name='dispatch')     
class SendAccessRequestView(generic.View):
    def post(self,request,*args, **kwargs):
        pk = self.kwargs['resourceid']

        res=Resource.objects.get(id=pk)
        if res is None:
            logger.info("User %s tried to send an access request for non-existing resource \n" % (request.user.username))
            return redirect("/resources-overview")

        if res.readers.filter(id= request.user.id).exists() or request.user.is_staff or AccessRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to inconsistently send an access request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/resources-overview")
        
        req=AccessRequest.objects.create(sender= request.user, resource=res, description=request.POST['descr'])
        message=req.description
       
        html_content = render_to_string('AuthorizationManagement/mail/access-resource-mail.html', {'user' : request.user,
                                                                                             'resource' : res,
                                                                                             'request': req,
                                                                                             'message': message})
        text_content=strip_tags(html_content)
        email_to = [x[0] for x in res.owners.values_list('email')]
        email_from=request.user.email
        msg=EmailMultiAlternatives('AccessPermission', text_content, email_from,email_to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Access request for resource '%s' with id '%s' was sent by %s \n" % (res.name,pk,request.user.username))
        logger.info("An email was sent from %s to '%s' owners, Subject: Access Request for '%s' \n" % (request.user.username,res.name,res.name))
        return redirect("/resources-overview")
   

@method_decorator(login_required, name='dispatch')     
class CancelAccessRequest(generic.View):
    def post(self,request,*args, **kwargs):
        pk = self.kwargs['resourceid']

        
        res=Resource.objects.get(id=pk)
        
        if res is None:
            logger.info("User %s tried to cancel an access request for non-existing resource \n" % (request.user.username))
            return redirect("/resources-overview")

        if res.readers.filter(id= request.user.id).exists() or request.user.is_staff or  not AccessRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to inconsistently cancel an access request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/resources-overview")
        
        requests_of_user = AccessRequest.objects.filter(sender=request.user)
        request_to_delete = requests_of_user.get(resource__id=pk)
        request_to_delete.delete()
        
        html_content=render_to_string('AuthorizationManagement/mail/access-request-canceled-mail.html', {'user' : request.user,
                                                                                                    'resource' : request_to_delete.resource,
                                                                                                    'request': request_to_delete})                                                               
        text_content=strip_tags(html_content)
        email_to = [x[0] for x in request_to_delete.resource.owners.values_list('email')]
        email_from=request.user.email
        msg=EmailMultiAlternatives('Access Request canceled', text_content, email_from,email_to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Access request for '%s' was canceled by %s \n" % (request_to_delete.resource.name,request.user.username))
        logger.info("An email was sent from %s to '%s' owners, Subject: Cancel the Access Request for '%s' \n" % (request.user.username,request_to_delete.resource.name,request_to_delete.resource.name))
        return redirect("/resources-overview")
    

@method_decorator(login_required, name='dispatch')     
class OpenResourceView(generic.View):
    def get(self,request,*args, **kwargs):
        pk = self.kwargs['resourceid']

        if not Resource.objects.filter(id=pk).exists():
            logger.info("User %s tried to access a non-existing resource \n" % (request.user.username))
            raise Http404("The requested file doesn't exist!")


        resource=Resource.objects.get(id=pk)

        if (not resource.readers.filter(id= request.user.id).exists())and (not request.user.is_staff) :
            raise PermissionDenied

        logger.info("User %s accessed '%s' with id = %s \n" % (request.user.username,resource.name,resource.id))
        ## Download function that tests the functionality.
        ## It could be replaced with another view according to the specific resource
        return download(request,resource)
    
@login_required()
def download(request,resource):
    relative_path = request.path
    if relative_path.find(os.sep) == -1:
        relative_path = relative_path.replace(utilities.getOppositeOSDirectorySep(),os.sep)  
        
    relative_path_elements = relative_path.split(os.sep,1)
    relative_path = relative_path_elements[len(relative_path_elements)-1]

    file_name = resource.link.name
    relative_path = relative_path.replace(str(resource.id),file_name)

    absolute_path = os.path.join(settings.BASE_DIR, relative_path)
    data = mimetypes.guess_type(absolute_path)
    

    f = open(absolute_path,'rb')

    myfile = File(f)
    response = HttpResponse(myfile.read(), content_type=data[0])
    
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    return response


class PermissionEditingView(generic.ListView):
    model = User.objects.all()
    template_name='AuthorizationManagement/edit-permissions.html'
    resource = Resource.objects.all()
    query = ''
    context_object_name = "user_list"
    #paginate_by = 2
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        resource=Resource.objects.get(id=self.kwargs['resourceid'])
        if resource is None:
            logger.info("User %s tried to edit the permissions of a non-existing resource \n" % (request.user.username))
            return redirect('/')
        
        if request.user.is_staff :
            return redirect('/resource-manager/AuthorizationManagement/resource/'+self.kwargs['resourceid']+'/change/')
        if resource.owners.filter(id=request.user.id).exists():
            return super().dispatch(request,*args, **kwargs)
        
        logger.info("User %s tried to edit the permissions of resource %s \n" % (request.user.username,resource.name))
        return redirect('/')


    
    def post (self, request,*args, **kwargs ):

        
            resource=Resource.objects.get(id=self.kwargs['resourceid'])
            readerlist = request.POST.getlist('reader[]')
            ownerlist = request.POST.getlist('owner[]')
            
            for user in resource.readers.filter(id__in=self.model):
                if user.id in readerlist:
                    continue
                resource.readers.remove(user)
                
                html_content=render_to_string('AuthorizationManagement/mail/access-removed-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                text_content=strip_tags(html_content)
                email_to = [user.email]
                email_from=request.user.email
                msg=EmailMultiAlternatives('Access Permission removed', text_content, email_from,email_to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info("Access permission for '%s' was removed by %s from %s \n" % (resource.name,request.user.username,user.username))
                logger.info("An email was sent from %s to '%s' , Subject: Access permission removed \n" % (request.user.username,user.username))
            for userid in readerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.readers.filter(id__in=self.model):
                    continue
                resource.readers.add(user)
                
                html_content=render_to_string('AuthorizationManagement/mail/access-granted-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                text_content=strip_tags(html_content)
                email_to = [user.email]
                email_from=request.user.email
                msg=EmailMultiAlternatives('Access Permission granted', text_content, email_from,email_to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info("Access permission for '%s' was granted by %s \n" % (resource.name,request.user.username))
                logger.info("An email was sent from %s to '%s' , Subject: Access permission granted \n" % (request.user.username,user.username))
            if len(resource.owners.all() )   > 1:
                for user in resource.owners.filter(id__in=self.model):
                
                    if user.id in ownerlist:
                        continue
                    resource.owners.remove(user)
                    html_content=render_to_string('AuthorizationManagement/mail/ownership-revoked-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                    text_content=strip_tags(html_content)
                    email_to = [user.email]
                    email_from=request.user.email
                    msg=EmailMultiAlternatives('Ownership revoked', text_content, email_from,email_to)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    logger.info("ownership for '%s' was revoked by %s from %s \n" % (resource.name,request.user.username, user.username))
                    logger.info("An email was sent from %s to '%s' , Subject: ownership revoked \n" % (request.user.username,user.username))
            for userid in ownerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.owners.filter(id__in=self.model):
                    continue 
                user.reader.add(resource)
                user.__class__=Owner
                user.save()
                owner = user
                resource.owners.add(owner)
                
                html_content=render_to_string('AuthorizationManagement/mail/ownership-granted-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                text_content=strip_tags(html_content)
                email_to = [user.email]
                email_from=request.user.email
                msg=EmailMultiAlternatives('Ownership granted', text_content, email_from,email_to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info("ownership for '%s' was granted by %s \n" % (resource.name,request.user.username))
                logger.info("An email was sent from %s to '%s' , Subject: ownership granted \n" % (request.user.username,user.username))
            return redirect('/profile/my-resources/')
        
        
    
    def get_queryset(self):
        return self.model
    

        
    def get_context_data(self, **kwargs):
        context = super(PermissionEditingView, self).get_context_data(**kwargs)
        context['resource'] = Resource.objects.get(id=self.kwargs['resourceid'])
        context['owners'] = Resource.objects.get(id=self.kwargs['resourceid']).owners.all()
        context['readers'] = Resource.objects.get(id=self.kwargs['resourceid']).readers.all()
        context['query'] = self.query
        context['query_pagination_string'] = ''
        return context
    
    
    
@method_decorator(login_required, name='dispatch')     
class PermissionEditingViewSearch(PermissionEditingView):
    
    def post(self, request,*args, **kwargs):
            self.query = self.request.GET['q']
            self.model = User.objects.filter(username__icontains=self.query)
            resource=Resource.objects.get(id=self.kwargs['resourceid'])
            readerlist = request.POST.getlist('reader[]')
            ownerlist = request.POST.getlist('owner[]')
        
            for user in resource.readers.filter(id__in=self.model):
                if user.id in readerlist:
                    continue
                resource.readers.remove(user)
                
                html_content=render_to_string('AuthorizationManagement/mail/access-removed-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                text_content=strip_tags(html_content)
                email_to = [user.email]
                email_from=request.user.email
                msg=EmailMultiAlternatives('Access Permission removed', text_content, email_from,email_to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info("Access permission for '%s' was removed by %s from %s \n" % (resource.name,request.user.username,user.email))
                logger.info("An email was sent from %s to '%s' , Subject: Access permission for removed\n" % (request.user.username,user.username))
            for userid in readerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.readers.filter(id__in=self.model):
                    continue
                resource.readers.add(user)
                
                html_content=render_to_string('AuthorizationManagement/mail/access-granted-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                text_content=strip_tags(html_content)
                email_to = [user.email]
                email_from=request.user.email
                msg=EmailMultiAlternatives('Access Permission granted', text_content, email_from,email_to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info("Access permission for '%s' was granted by %s \n" % (resource.name,request.user.username))
                logger.info("An email was sent from %s to '%s' , Subject: Access permission granted \n" % (request.user.username,user.username))
            if len(resource.owners.all())  > 1:
                for user in resource.owners.filter(id__in=self.model):
                
                    if user.id in ownerlist:
                        continue
                    resource.owners.remove(user)
                    html_content=render_to_string('AuthorizationManagement/mail/ownership-revoked-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                    text_content=strip_tags(html_content)
                    email_to = [user.email]
                    email_from=request.user.email
                    msg=EmailMultiAlternatives('Ownership revoked', text_content, email_from,email_to)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    logger.info("ownership for '%s' was revoked by %s from %s \n" % (resource.name,request.user.username, user.username))
                    logger.info("An email was sent from %s to '%s' , Subject: ownership revoked \n" % (request.user.username,user.username))
            for userid in ownerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.owners.filter(id__in=self.model):
                    continue 
                user.reader.add(resource)
                user.__class__=Owner
                user.save()
                owner = user
                resource.owners.add(owner)
                
                html_content=render_to_string('AuthorizationManagement/mail/ownership-granted-mail.html', {'user' : request.user,
                                                                                                    'resource' : resource})                                                               
                text_content=strip_tags(html_content)
                email_to = [user.email]
                email_from=request.user.email
                msg=EmailMultiAlternatives('Ownership granted', text_content, email_from,email_to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info("ownership for '%s' was granted by %s \n" % (resource.name,request.user.username))
                logger.info("An email was sent from %s to '%s' , Subject: ownership granted \n" % (request.user.username,user.username))
            return redirect('/profile/my-resources/')
    def get(self,request,*args, **kwargs):
        if 'q' in self.request.GET and self.request.GET['q']:
            self.query = self.request.GET['q']
            self.model = User.objects.filter(username__icontains=self.query)
        return super().get(request,*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(PermissionEditingViewSearch, self).get_context_data(**kwargs)
        context['resource'] = Resource.objects.get(id=self.kwargs['resourceid'])
        context['owners'] = Resource.objects.get(id=self.kwargs['resourceid']).owners.all()
        context['readers'] = Resource.objects.get(id=self.kwargs['resourceid']).readers.all()
        context['query'] = self.query
        context['query_pagination_string'] = 'q='+self.query+'&'
        return context


@method_decorator(login_required, name='dispatch')
class DeleteResourceView(generic.View):
    def post(self, request,*args, **kwargs):
        
        pk = self.kwargs['resourceid']
        
        
        res=Resource.objects.get(id=pk)
        
        
        if res is None:
            logger.info("User %s tried to delete a non-existing resource" % (request.user))
            return redirect('/profile')
        
        if not request.user.is_staff :
            logger.info("User %s tried to delete the resource '%s' without being an administrator" % (request.user,res.name))
            return redirect('/profile')

        html_content = render_to_string('AuthorizationManagement/mail/delete-resource-mail.html',
                                        {'user': request.user,
                                         'resource': res,
                                         'message': request.POST['descr']})
        text_content = strip_tags(html_content)


        # delete all permissions for this resource
        res.owners.clear()
        res.readers.clear()

        # delete all requests for this resource
        AccessRequest.objects.filter(resource=res).delete()
        DeletionRequest.objects.filter(resource=res).delete()

             
        email_to = [x[0] for x in res.owners.values_list('email')]
        email_from = request.user.email
        msg = EmailMultiAlternatives('File deleted by admin', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("User %s deleted resource %s " % (request.user.username,res.name))
        logger.info("An email was sent to all '%s' owners, Subject: '%s' is deleted " % (res.name,res.name))
        
        res.delete()
        return redirect("/profile/my-resources")

@method_decorator(login_required, name='dispatch')
class ApproveDeletionRequest(generic.View):
    def post(self, request,*args, **kwargs):
        
        pk = self.kwargs['requestid']
        
        
        req=DeletionRequest.objects.get(id=pk)
        
        if req is None:
            logger.info("User %s tried to approve a non-existing deletion request" % (request.user))
            return redirect('/profile')
        
        if not request.user.is_staff :
            logger.info("User %s tried to approve a deletion request without being an administrator" % (request.user))
            return redirect('/profile')
        
        owners = req.resource.owners.all()
        message = req.description

        html_content = render_to_string('AuthorizationManagement/mail/delete-request-accepted-mail.html',
                                        {'user': request.user,
                                         'resource': req.resource,
                                         'request': req,
                                         'message': message})
        text_content = strip_tags(html_content)

        res = req.resource

        # delete all permissions for this resource
        res.owners.clear()
        res.readers.clear()

        # delete all requests for this resource
        AccessRequest.objects.filter(resource=res).delete()
        DeletionRequest.objects.filter(resource=res).delete()


        # send email to request sender
        email_to = req.sender.email
        email_from = request.user.email
        msg = EmailMultiAlternatives('Deletion Request approved', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("An email was sent from %s to %s, Subject: Deletion Request for '%s' accepted \n" % (request.user.username,req.sender,req.resource.name))

        # notify all owners
        email_to = [x[0] for x in res.owners.values_list('email')]
        email_from = request.user.email
        msg = EmailMultiAlternatives('Deletion Request approved', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("An email was sent to all '%s' owners, Object: '%s' is deleted " % (req.resource.name,req.resource.name))
              
        res.delete()
        req.delete()

        logger.info("Request from %s to delete '%s' accepted by %s \n" % (req.sender,req.resource.name,request.user.username))
        
        return redirect("/profile")

@method_decorator(login_required, name='dispatch')
class DenyDeletionRequest(generic.View):
    def post(self, request,*args, **kwargs):
        
        pk = self.kwargs['requestid']
        req=DeletionRequest.objects.get(id=pk)
        
        if req is None:
            logger.info("User %s tried to deny a non-existing deletion request" % (request.user))
            return redirect('/profile')
        
        if not request.user.is_staff:
            logger.info("User %s tried to deny a deletion request without being an administrator" % (request.user))
            return redirect('/profile')
        
        message = request.POST['descr']

        html_content = render_to_string('AuthorizationManagement/mail/delete-request-denied-mail.html',
                                        {'user': request.user,
                                         'resource': req.resource,
                                         'request': req,
                                         'message': message})
        text_content = strip_tags(html_content)
        email_to = req.sender.email
        email_from = request.user.email
        msg = EmailMultiAlternatives('Deletion Request denied', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Request from %s to delete '%s' was denied by %s \n" % (req.sender,req.resource.name,request.user.username))
        logger.info("An email was sent from %s to %s, Subject: Deletion Request for '%s' denied\n" % (request.user.username,req.sender,req.resource.name))
        req.delete()
        return redirect("/profile")


@method_decorator(login_required, name='dispatch')
class AddNewResourceView(generic.View):
    def post(self,request):
        form = AddNewResourceForm(request.POST , request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            instance.owners.add(request.user.id)
            instance.readers.add(request.user.id)

            logger.info("User %s created the '%s' Resource \n" % (request.user.username,instance.name))
            return redirect("/resources-overview")# what happens in the browser after submitting

    def get(self,request):
        form = AddNewResourceForm()

        args = {}
        args.update(csrf(request))
        
        args['form'] = form
        return render_to_response('AuthorizationManagement/add-new-resource.html', args)

class EditNameView(generic.View):
    def post(self, request):
            request.user.first_name=request.POST['firstName']
            request.user.last_name=request.POST['lastName']
            request.user.save()
            return redirect('/profile')