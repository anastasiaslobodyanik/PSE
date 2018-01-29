from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.files import File
from django.conf import settings
import os
from django.utils.decorators import method_decorator


@login_required()
def homeView(request):
    is_admin=request.user.is_staff
    return render(request, 'AuthorizationManagement/home.html', {'is_admin': is_admin})


@method_decorator(login_required, name='dispatch')
class ProfileView(generic.ListView):
    model = User
    template_name = 'AuthorizationManagement/profile.html'

    def get_queryset(self):
        resources = MyResourcesView.get_queryset(self)
        return AccessRequest.objects.filter(resource__in=resources)

    
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
        context['query_pagination_string'] = ''
        context['deletion_requested'] = Resource.objects.filter(
            id__in=DeletionRequest.objects.filter(sender=self.request.user).values('resource_id'))
        return context


@method_decorator(login_required, name='dispatch')
class SendDeletionRequestView(generic.View):
    def  post(self, request):
        elements = request.path.rsplit('/')

        DeletionRequest.objects.create(sender=request.user,
                                       resource=Resource.objects.get(id=elements[2]),
                                       description=request.GET)
        return redirect("/my-resources")


@method_decorator(login_required, name='dispatch')
class CancelDeletionRequestView(generic.View):
    def post(self, request):
        elements = request.path.rsplit('/')
        requests_of_user = DeletionRequest.objects.filter(sender=request.user)
        request_to_delete = requests_of_user.get(resource__id=elements[2])
        request_to_delete.delete()
        return redirect("/my-resources")


@method_decorator(login_required, name='dispatch') 
class ResourcesOverview(generic.ListView):
    model = Resource.objects.all()
    template_name = 'AuthorizationManagement/resources-overview.html'  
    context_object_name = "resources_list"
    paginate_by = 5
    canAccess = Resource.objects.none()  
    requested_resources = Resource.objects.none()

    
    def get_queryset(self):
        return self.model
    
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverview, self).get_context_data(**kwargs)
        context['query_pagination_string'] = ''
        context['can_access'] = self.request.user.reader.filter(id__in=self.model)
        context['requested_resources'] = Resource.objects.filter(
            id__in=AccessRequest.objects.filter(sender=self.request.user).values('resource_id'))

        return context

@method_decorator(login_required, name='dispatch')     
class ResourcesOverviewSearch(generic.ListView):
    model = Resource.objects.all()
    template_name = 'AuthorizationManagement/resources-overview.html'  
    context_object_name = "resources_list"

    paginate_by = 5
    query = ''
    can_access = Resource.objects.none()
    requested_resources = Resource.objects.none()
    
    def get_queryset(self):
        return self.model

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
        context['query'] = self.query;
        context['query_pagination_string'] = 'q='+self.query+'&'
        context['can_access'] = self.can_access
        context['requested_resources'] = self.requested_resources
        return context
    
@login_required()
def approve_access_request(request):
    elements=request.path.rsplit('/')
    req=AccessRequest.objects.get(id=elements[2])
    req.resource.readers.add(req.sender)
    req.delete()    
    return redirect("/profile")

@login_required()
def deny_access_request(request):
    elements=request.path.rsplit('/')
    req=AccessRequest.objects.get(id=elements[2])
    req.delete()    
    return redirect("/profile")

@method_decorator(login_required, name='dispatch')     
class SendAccessRequestView(generic.View):
    def post(self,request):
        elements=request.path.rsplit('/')

  
        #method sendAccessRequest returns error, for testing purposes the request is created manually until the error is cleared
        #-Sonya
        AccessRequest.objects.create(sender=request.user,
                                      resource = Resource.objects.get(id=elements[2]), description = request.GET)
        return redirect("/resources-overview")
   

@method_decorator(login_required, name='dispatch')     
class CancelAccessRequest(generic.View):
    def post(self,request):
        elements=request.path.rsplit('/')
        requests_of_user = AccessRequest.objects.filter(sender=request.user)
        request_to_delete = requests_of_user.get(resource__id=elements[2])
        request_to_delete.delete()
        return redirect("/resources-overview")
    

@method_decorator(login_required, name='dispatch')     
class OpenResourceView(generic.View):
    def get(self,request):
        return download(request)
    
@login_required()
def download(request):
    relativePath = request.path
    if relativePath.find(os.sep) == -1:
        relativePath = relativePath.replace(getOppositeOSDirectorySep(),os.sep)  
        
    els = relativePath.split(os.sep,1)
    relativePath = els[len(els)-1]
          
    f = open(os.path.join(settings.BASE_DIR, relativePath), 'r')
    myfile = File(f)
    response = HttpResponse(myfile, content_type='text/plain')
    
    elements = myfile.name.rsplit(os.sep);
    fileName = elements[len(elements)-1]
    response['Content-Disposition'] = 'attachment; filename=' + fileName
    return response


class PermissionEditingView(generic.ListView):
    model = User
    template_name='AuthorizationManagement/edit-permissions.html'
    resource = Resource.objects.all()
    paginate_by = 5
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        resource=Resource.objects.get(id=self.kwargs['resourceid'])
        if request.user.is_staff :
            return redirect('/resource-manager/AuthorizationManagement/resource/'+self.kwargs['resourceid']+'/change/')
        if resource.owners.filter(id=request.user.id).exists():
            return super().dispatch(request,*args, **kwargs)
        return redirect('/')
    
    
    
    def post (self, request,*args, **kwargs ):
        resource=Resource.objects.get(id=self.kwargs['resourceid'])
        readerlist = request.POST.getlist('reader[]')
        ownerlist = request.POST.getlist('owner[]')
        resource.readers.clear()
        for user in resource.owners.all():
            resource.readers.add(user)
        for userid in readerlist:
            user=CustomUser.objects.get(id=userid)
            resource.readers.add(user)
            #email
        for userid in ownerlist:
            user=CustomUser.objects.get(id=userid)
            user.reader.add(resource)
            #email
            user.__class__=Owner
            user.save()
            owner = user
            resource.owners.add(owner)
        return redirect('/my-resources/')
         
        
    def get_context_data(self, **kwargs):
        context = super(PermissionEditingView, self).get_context_data(**kwargs)
        context['resource'] = Resource.objects.get(id=self.kwargs['resourceid'])
        context['owners'] = Resource.objects.get(id=self.kwargs['resourceid']).owners.all()
        context['readers'] = Resource.objects.get(id=self.kwargs['resourceid']).readers.all()
        return context
        

def getOppositeOSDirectorySep():
    if os.sep=='/':
        return '\\'
    else:
        return '/'

@method_decorator(login_required, name='dispatch') 
class ChosenRequestsView(generic.DetailView):
    model = AccessRequest
    template_name = "AuthorizationManagement/handle-request.html"


def permissionForChosenResourceView():
    return

def requestView():
    return

