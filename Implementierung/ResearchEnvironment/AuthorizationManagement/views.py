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
from django.db.models import Q


from itertools import chain


logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class HomeView(generic.View):
    model = User

    def get(self, request):
        is_admin = request.user.is_staff
        return render(request, 'AuthorizationManagement/home.html', {'is_admin': is_admin})


@method_decorator(login_required, name='dispatch')
class ProfileView(generic.ListView):
    model = AccessRequest.objects.none()
    template_name = 'AuthorizationManagement/profile.html'
    context_object_name = "requests_list"
    paginate_by = 4
    
    def get(self,request):
        current_user = self.request.user
        resources = MyResourcesView.get_queryset(self)
        
        # load access requests if user owns any resources
        if resources.exists():
            self.model = AccessRequest.objects.filter(resource__in=resources).order_by('-creationDate')

          
        # load all deletion request if user is staff
        if self.model.exists():            
            if current_user.is_staff and DeletionRequest.objects.all().exists():
                self.model=get_sorted_requests(self.model, DeletionRequest.objects.all().order_by('-creationDate'))               
                #self.model = list(chain(self.model,DeletionRequest.objects.all()))
        else: 
            if current_user.is_staff and DeletionRequest.objects.all().exists():
                self.model = DeletionRequest.objects.all().order_by('-creationDate')
                
        return super(ProfileView, self).get(request)
    
    def get_queryset(self):
        return self.model
     
    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_staff
        return context
   

# the view for showing all the user's resources
@method_decorator(login_required, name='dispatch')
class MyResourcesView(generic.ListView):
    model = Resource
    template_name = 'AuthorizationManagement/my-resources.html'
    deletion_requested = Resource.objects.none()

    def get_queryset(self):
        current_user = Owner.objects.get(id=self.request.user.id)
        return current_user.owner.all()

    #returns a dictionary representing the template context.
    def get_context_data(self, **kwargs):
        context = super(MyResourcesView, self).get_context_data(**kwargs)
        context['deletion_requested'] = Resource.objects.filter(
            id__in=DeletionRequest.objects.filter(sender=self.request.user).values('resource_id'))
        context['is_admin'] = self.request.user.is_staff
        return context


# the view for sending a deletion request
@method_decorator(login_required, name='dispatch')
class SendDeletionRequestView(generic.View):
    def  post(self, request,*args, **kwargs):

        pk = self.kwargs['resourceid'] # get the id of the resource which is included in the url

        res=Resource.objects.get(id=pk)
        
        # redirects the current user to resources-overview if a resource with such an id does not exist
        if res is None:
            logger.info("User %s tried to send a deletion request for non-existing resource \n" % (request.user.username))
            return redirect("/profile/my-resources")
        
        # raises the PermissionDenied exception if the current user has no ownership for this resource
        if  not res.owners.filter(id= request.user.id).exists():
            logger.info("User %s tried to send a deletion request for resource '%s' without being an owner! \n" % (request.user.username,res.name))
            raise PermissionDenied
        # redirects the current user to profile/my-resources if the user is a staff user or the user has already requested to delete the resource
        if  request.user.is_staff or DeletionRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to inconsistently send a deletion request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/profile/my-resources")
        
        # creates a deletion request with the given description
        req = DeletionRequest.objects.create(sender=request.user,
                                       resource=Resource.objects.get(id=pk),
                                       description=request.POST['descr'])
        message=req.description
        
        # notifies all the staff users
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


# the view for canceling a deletion request
@method_decorator(login_required, name='dispatch')
class CancelDeletionRequestView(generic.View):
    def post(self, request,*args, **kwargs):

        pk = self.kwargs['resourceid'] # get the id of the resource which is included in the url
        
        res = Resource.objects.get(id=pk)
        
        # redirects the current user to resources-overview if a resource with such an id does not exist
        if res is None:
            logger.info("User %s tried to cancel a deletion request for non-existing resource \n" % (request.user.username))
            return redirect("/resources-overview")

        # raises the PermissionDenied exception if the current user has no ownership for this resource
        if  not res.owners.filter(id= request.user.id).exists():
            logger.info("User %s tried to cancel a deletion request for resource '%s' without being an owner! \n" % (request.user.username,res.name))
            raise PermissionDenied
            
        # redirects the current user to resources-overview if the user is a staff user or there is no deletion request 
        if request.user.is_staff or  not DeletionRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to cancel a deletion request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/resources-overview")
        
        requests_of_user = DeletionRequest.objects.filter(sender=request.user) 
        request_to_delete = requests_of_user.get(resource__id=pk)
        
        # notifies all the staff users 
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
    
    # returns a dictionary representing the template context.
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverview, self).get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_staff
        context['query'] = self.query;
        context['query_pagination_string'] = ''
        context['can_access'] = self.request.user.reader.filter(id__in=self.model) # list of resources for which the user has an access permission
        context['requested_resources'] = Resource.objects.filter(
            id__in=AccessRequest.objects.filter(sender=self.request.user).values('resource_id'))

        return context

     
# the view for ResourcesOverview after search
@method_decorator(login_required, name='dispatch')     
class ResourcesOverviewSearch(ResourcesOverview):
    
    # shows  all the resources that was sought or redirects the user if there is no or empty query
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
    
    # returns a dictionary representing the template context.
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverviewSearch, self).get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_staff
        context['query'] = self.query;
        context['query_pagination_string'] = 'q='+self.query+'&'
        context['can_access'] = self.can_access
        context['requested_resources'] = self.requested_resources
        return context

# the view for approving an access request
@method_decorator(login_required, name='dispatch') 
class ApproveAccessRequest(generic.View):
    def post(self,request,*args, **kwargs):
        
        pk = self.kwargs['requestid'] # gets the id of the request which is included in the url
        
        
        req=AccessRequest.objects.get(id=pk)
        
        # redirects the current user to profile if a request with a such id does not exist
        if req is None:
            logger.info("User %s tried to approve a non-existing access request" % (request.user))
            return redirect('/profile')
        
        # raises the PermissionDenied exception if the current user has no ownership for this resource
        if not req.resource.owners.filter(id = request.user.id).exists():
            logger.info("User %s tried to approve an access request without being owner of the requested resource" % (request.user))
            raise PermissionDenied
        
        # adds the sender to the readers list of this resource
        req.resource.readers.add(req.sender)
        message=req.description
       
        # sends an email to sender of the request
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

# the view for denying an access request
@method_decorator(login_required, name='dispatch')     
class DenyAccessRequest(generic.View):
    def post(self,request,*args, **kwargs):
        
        pk = self.kwargs['requestid'] # gets the id of the request which is included in the url
        req=AccessRequest.objects.get(id=pk)
        
        # redirects the current user to profile if a request with a such id does not exist
        if req is None:
            logger.info("User %s tried to deny a non-existing access request" % (request.user))
            return redirect('/profile')
        
        # raises the PermissionDenied exception if the current user has no ownership for this resource
        if not req.resource.owners.filter(id = request.user.id).exists():
            logger.info("User %s tried to deny an access request without being owner of the requested resource" % (request.user))
            raise PermissionDenied
        

        message=request.POST['descr'] # gets the description of the request
       
       
        # sends an email to sender of this request
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

#the view for sending an access request
@method_decorator(login_required, name='dispatch')     
class SendAccessRequestView(generic.View):
    def post(self,request,*args, **kwargs):
        pk = self.kwargs['resourceid'] # gets the id of the resource which is included in the url

        res=Resource.objects.get(id=pk)
        
        # redirects the current user to resources-overview if a resource with a such id does not exist
        if res is None:
            logger.info("User %s tried to send an access request for non-existing resource \n" % (request.user.username))
            return redirect("/resources-overview")

        # redirects the current user to resources-overview if the user is a staff user or already has an access permission to this resource
        # or if the user has already requested to access this resource
        if res.readers.filter(id= request.user.id).exists() or request.user.is_staff or AccessRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to inconsistently send an access request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/resources-overview")
        
        # creates an access request with the given description
        req=AccessRequest.objects.create(sender= request.user, resource=res, description=request.POST['descr'])
        message=req.description
       
       
        # notifies all the owners via email
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
   

# the view for canceling an access request
@method_decorator(login_required, name='dispatch')     
class CancelAccessRequest(generic.View):
    def post(self,request,*args, **kwargs):
        pk = self.kwargs['resourceid'] # gets the id of the resource which is included in the url

        
        res=Resource.objects.get(id=pk)
        
        # redirects the current user to resources-overview if a resource with a such id does not exist
        if res is None:
            logger.info("User %s tried to cancel an access request for non-existing resource \n" % (request.user.username))
            return redirect("/resources-overview")

        # redirects the current user to resources-overview if the user is a staff user or already has an access permission to this resource or if there is no access request
        if res.readers.filter(id= request.user.id).exists() or request.user.is_staff or  not AccessRequest.objects.filter(resource=res,sender = request.user).exists():
            logger.info("User %s tried to inconsistently cancel an access request for resource '%s' \n" % (request.user.username,res.name))
            return redirect("/resources-overview")
        
        # deletes the request
        requests_of_user = AccessRequest.objects.filter(sender=request.user)
        request_to_delete = requests_of_user.get(resource__id=pk)
        request_to_delete.delete()
        
        # notifies all owners  via email
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
        pk = self.kwargs['resourceid'] # gets the id of the resource which is included in the url
        
        # redirects the current user to the 404 if a resource with a such id does not exist 
        if not Resource.objects.filter(id=pk).exists():
            logger.info("User %s tried to access a non-existing resource \n" % (request.user.username))
            raise Http404("The requested file doesn't exist!")


        resource=Resource.objects.get(id=pk)       
        # raises the PermissionDenied exception if the current user is a staff user or has no access permission to this resource
        if (not resource.readers.filter(id=request.user.id).exists())and (not request.user.is_staff) :
            raise PermissionDenied

        logger.info("User %s accessed '%s' with id = %s \n" % (request.user.username,resource.name,resource.id))
        ## Download function that tests the functionality.
        ## It could be replaced with another view according to the specific resource
        return download(request,resource)

def download(request,resource):
    relative_path = request.path
    if relative_path.find(os.sep) == -1:
        relative_path = relative_path.replace(utilities.get_opposite_os_directory_sep(),os.sep)  
        
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
    model = User = User.objects.none()
    template_name='AuthorizationManagement/edit-permissions.html'
    resource = Resource.objects.all()
    query = ''
    context_object_name = "user_list"
    paginate_by = 2
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        resource=Resource.objects.get(id=self.kwargs['resourceid'])
        if resource is None:
            logger.info("User %s tried to edit the permissions of a non-existing resource \n" % (request.user.username))
            return redirect('/')
        #redirects the staff users to resource-manager
        if request.user.is_staff :
            return redirect('/resource-manager/AuthorizationManagement/resource/'+self.kwargs['resourceid']+'/change/')
        #checks if the current user has permission to access this resource
        if resource.owners.filter(id=request.user.id).exists():
            return super().dispatch(request,*args, **kwargs)
        
        logger.info("User %s tried to edit the permissions of resource %s \n" % (request.user.username,resource.name))
        raise PermissionDenied


    
    def post (self, request,*args, **kwargs ):              
            resource=Resource.objects.get(id=self.kwargs['resourceid']) 
            new_readers_list = request.POST.getlist('reader[]')
            new_owners_list = request.POST.getlist('owner[]')
            users_on_page = request.POST.getlist('usersIdsOnPage[]')
            
            real_readers_list = list(resource.readers.values_list('id',flat=True))
            real_owners_list = list(resource.owners.values_list('id',flat=True)) 
            
            user_removed_own_right = False
            no_rights_users =0
            
            for userId in users_on_page:
                user = CustomUser.objects.get(id=userId)
                    #checks if a user granted the access permission for this resource
                if userId in new_readers_list and int(userId) not in real_readers_list:
                    
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
                    
                    #checks if the access permission  was removed from a user 
                elif userId not in new_readers_list and int(userId) in real_readers_list and userId not in new_owners_list:
                    
                    no_rights_users+=1
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
                
                
                owner = Owner.objects.get(id=userId)
                
                #checks if a user granted the ownership of this resource
                if userId in new_owners_list and int(userId) not in real_owners_list:
                    
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
                    
                #checks if the ownership of this resource was revoked from a user
                elif userId not in new_owners_list and int(userId) in real_owners_list and len(resource.owners.all() ) > 1:
                    
                    resource.owners.remove(owner)
                    
                    if int(userId) == self.request.user.id:
                        user_removed_own_right = True
                    
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
              
            if user_removed_own_right:
                path_to_redirect = '/profile/my-resources/'   
            # All users on the page are removed and there is no search        
            elif not('q' in self.request.GET and self.request.GET['q']) and no_rights_users == len(users_on_page):
                path_to_redirect = '/profile/my-resources/'    
            else:  
                path_to_redirect = utilities.get_relative_path_with_parameters(self.request)
            return redirect(path_to_redirect)
        
    
    def get_queryset(self):
        return self.model
    
    def get(self,request,*args, **kwargs):       
        is_owner_of_resource = Resource.objects.get(id=self.kwargs['resourceid']).owners.all().values_list('id',flat=True)
        is_reader_of_resource = Resource.objects.get(id=self.kwargs['resourceid']).readers.all().values_list('id',flat=True)
        self.model = User.objects.filter(Q(id__in=is_owner_of_resource)|Q(id__in=is_reader_of_resource))
        return super().get(request,*args, **kwargs)
        
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
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        
        #If there is no or empty query, the user is redirected to the main edit permission page
        if 'q' in self.request.GET and self.request.GET['q']:
            return super().dispatch(request,*args, **kwargs)
        else:
            path_to_redirect = utilities.get_one_level_lower_path(self.request.path)
            return redirect(path_to_redirect)
        
    def get(self,request,*args, **kwargs):
        self.query = self.request.GET['q']
        self.model = User.objects.filter(username__icontains=self.query)
        return super(generic.ListView,self).get(request,*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(PermissionEditingViewSearch, self).get_context_data(**kwargs)
        context['resource'] = Resource.objects.get(id=self.kwargs['resourceid'])
        context['owners'] = Resource.objects.get(id=self.kwargs['resourceid']).owners.all()
        context['readers'] = Resource.objects.get(id=self.kwargs['resourceid']).readers.all()
        context['query'] = self.query
        context['query_pagination_string'] = 'q='+self.query+'&'
        return context


# the view for deleting a resource
@method_decorator(login_required, name='dispatch')
class DeleteResourceView(generic.View):
    def post(self, request,*args, **kwargs):
        
        pk = self.kwargs['resourceid'] # gets the id of the resource which is included in the url
        
        
        res=Resource.objects.get(id=pk)
        
        # redirects the current user if a resource with a such id does not exist
        if res is None:
            logger.info("User %s tried to delete a non-existing resource" % (request.user))
            return redirect('/profile')
        
        # raises the PermissionDenied exception if the current user is not a staff user
        if not request.user.is_staff :
            logger.info("User %s tried to delete the resource '%s' without being an administrator" % (request.user,res.name))
            raise PermissionDenied

        html_content = render_to_string('AuthorizationManagement/mail/resource-deleted-mail.html',
                                        {'user': request.user,
                                         'resource': res,
                                         'message': request.POST['descr']})
        text_content = strip_tags(html_content)


        # deletes all the access permissions to this resource
        res.owners.clear()
        res.readers.clear()

        # deletes all the requests for this resource
        AccessRequest.objects.filter(resource=res).delete()
        DeletionRequest.objects.filter(resource=res).delete()

        # notifies all the owners     
        email_to = [x[0] for x in res.owners.values_list('email')]
        email_from = request.user.email
        msg = EmailMultiAlternatives('File deleted by admin', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("User %s deleted resource %s " % (request.user.username,res.name))
        logger.info("An email was sent to all '%s' owners, Subject: '%s' is deleted " % (res.name,res.name))
        
        # deletes the resource
        res.delete()
        return redirect("/profile/my-resources")

# the view for approving a deletion request
@method_decorator(login_required, name='dispatch')
class ApproveDeletionRequest(generic.View):
    def post(self, request,*args, **kwargs):
        
        pk = self.kwargs['requestid']
        
        
        req=DeletionRequest.objects.get(id=pk)
        
        # redirects the current user if a request with a such id does not exist
        if req is None:
            logger.info("User %s tried to approve a non-existing deletion request" % (request.user))
            return redirect('/profile')
        
        # raises the PermissionDenied exception if the current user is a staff user
        if not request.user.is_staff :
            logger.info("User %s tried to approve a deletion request without being an administrator" % (request.user))
            raise PermissionDenied
        
        owners = req.resource.owners.all()
        message = req.description # gets the description of the request

        html_content = render_to_string('AuthorizationManagement/mail/delete-request-accepted-mail.html',
                                        {'user': request.user,
                                         'resource': req.resource,
                                         'request': req,
                                         'message': message})
        text_content = strip_tags(html_content)

        res = req.resource

        # deletes all the permissions to this resource
        res.owners.clear()
        res.readers.clear()

        # deletes all the requests for this resource
        AccessRequest.objects.filter(resource=res).delete()
        DeletionRequest.objects.filter(resource=res).delete()


        # sends an email to the sender of the request
        email_to = req.sender.email
        email_from = request.user.email
        msg = EmailMultiAlternatives('Deletion Request approved', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("An email was sent from %s to %s, Subject: Deletion Request for '%s' accepted \n" % (request.user.username,req.sender,req.resource.name))

        # notifies all the owners
        email_to = [x[0] for x in res.owners.values_list('email')]
        email_from = request.user.email
        msg = EmailMultiAlternatives('Deletion Request approved', text_content, email_from, [email_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("An email was sent to all '%s' owners, Object: '%s' is deleted " % (req.resource.name,req.resource.name))
        
        # deletes the resource and the deletion request      
        res.delete()
        req.delete()

        logger.info("Request from %s to delete '%s' accepted by %s \n" % (req.sender,req.resource.name,request.user.username))
        
        return redirect("/profile")

# the view for denying a deletion request
@method_decorator(login_required, name='dispatch')
class DenyDeletionRequest(generic.View):
    
    
    def post(self, request,*args, **kwargs):
        
        pk = self.kwargs['requestid']
        req=DeletionRequest.objects.get(id=pk) 
        
        # redirects the current user if a request with a such id does not exist
        if req is None:
            logger.info("User %s tried to deny a non-existing deletion request" % (request.user))
            return redirect('/profile')
        
        # raises the PermissionDenied exception if the current user is a staff user
        if not request.user.is_staff:
            logger.info("User %s tried to deny a deletion request without being an administrator" % (request.user))
            raise PermissionDenied
        
        message = request.POST['descr'] # gets the description of this request
        
        # notifies the sender of this request via email
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
        
        # deletes the request
        req.delete()
        return redirect("/profile")


# the view for adding a new resource
@method_decorator(login_required, name='dispatch')
class AddNewResourceView(generic.View):
    
    # adds a new resource with the given informations
    def post(self,request):
        form = AddNewResourceForm(request.POST , request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            instance.owners.add(request.user.id)
            instance.readers.add(request.user.id)

            logger.info("User %s created the '%s' Resource \n" % (request.user.username,instance.name))
            return redirect("/profile/my-resources")# what happens in the browser after submitting

    def get(self,request):
        form = AddNewResourceForm()

        args = {}
        args.update(csrf(request))
        
        args['form'] = form
        args['is_admin'] = self.request.user.is_staff
        args['user'] = self.request.user
        return render_to_response('AuthorizationManagement/add-new-resource.html', args)
    

    
# the view for editing the name of the user
@method_decorator(login_required, name='dispatch')
class EditNameView(generic.View):
    
    # updates the firstname and the lastname with the given firstname and lastname
    def post(self, request):
        
        if(request.POST['firstName'] and (not request.POST['firstName'].isspace())): 
            request.user.first_name=request.POST['firstName']
            request.user.save()
        if(request.POST['lastName'] and (not request.POST['lastName'].isspace())):
            request.user.last_name=request.POST['lastName']
            request.user.save()  
        return redirect('/profile')


# returns a sorted list of combination of the access requests and the deletion requests        
def get_sorted_requests(access_request_queryset,deletion_request_queryset):
    access_requests_list = list(access_request_queryset)
    deletion_requests_list = list(deletion_request_queryset)
    
    result = []
    longer_list_len = max(len(access_requests_list),len(deletion_requests_list))
    shorter_list_len = min(len(access_requests_list),len(deletion_requests_list))
    
    if longer_list_len==len(access_requests_list):
        longer_list = access_requests_list
        shorter_list = deletion_requests_list
    else:
        longer_list = deletion_requests_list
        shorter_list = access_requests_list
       
    for i in range(0,longer_list_len):
        result.append(longer_list[i])
        if i<shorter_list_len:
            result.append(shorter_list[i])
            
    return result