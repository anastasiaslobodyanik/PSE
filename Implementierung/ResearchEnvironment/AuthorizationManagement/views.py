from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Resource
from .models import User
from .models import Owner
from .models import AccessRequest
from django.core.files import File
from django.conf import settings
import os
from django.utils.decorators import method_decorator
from django.http.response import HttpResponseRedirect
from AuthorizationManagement.models import CustomUser


@login_required()
def homeView(request):
    return render(request, 'AuthorizationManagement/home.html')

class ProfileView(generic.ListView):
    model = User
    template_name = 'AuthorizationManagement/profile.html'

    def get_queryset(self):
        resources = MyResourcesView.get_queryset(self)
        return AccessRequest.objects.filter(resource__in=resources)
    
class MyResourcesView(generic.ListView):
    model = Resource
    template_name = 'AuthorizationManagement/my-resources.html'

    def get_queryset(self):
        current_user = Owner.objects.get(id=self.request.user.id)
        return current_user.owner.all()

class ResourcesOverview(generic.ListView):
    model = Resource.objects.all()
    template_name = 'AuthorizationManagement/my-resources-overview.html'  
    context_object_name = "resources_list"
    paginate_by = 5
    canAccess = Resource.objects.none()  
    requested_resources=Resource.objects.none()

    
    def get_queryset(self):
        return self.model
    
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverview, self).get_context_data(**kwargs)
        context['query_pagination_string'] = ''
        context['can_access'] = self.request.user.reader.filter(id__in=self.model)
        context['requested_resources'] = Resource.objects.filter(
            id__in=AccessRequest.objects.filter(sender=self.request.user).values('resource_id'))

        return context
    
class ResourcesOverviewSearch(generic.ListView):
    model = Resource.objects.all()
    template_name = 'AuthorizationManagement/my-resources-overview.html'  
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
                
def send_access_request(request):
    elements=request.path.rsplit('/')

  
    #method sendAccessRequest returns error, for testing purposes the request is created manually until the error is cleared
    #-Sonya
    AccessRequest.objects.create(sender=request.user,
                                      resource = Resource.objects.get(id=elements[2]), description = request.GET)
    return redirect("/resources-overview")
    
def cancel_access_request(request):
    elements=request.path.rsplit('/')
    requests_of_user = AccessRequest.objects.filter(sender=request.user)
    request_to_delete = requests_of_user.get(resource__id=elements[2])
    request_to_delete.delete()
    return redirect("/resources-overview")
    
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


def getOppositeOSDirectorySep():
    if os.sep=='/':
        return '\\'
    else:
        return '/'
    
class PermissionEditingView(generic.ListView):
    model = User
    template_name='AuthorizationManagement/edit-permissions.html'
    resource = Resource.objects.all()
    #paginate
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        resource=Resource.objects.get(id=self.kwargs['resourceid'])
        if resource.owners.filter(id=request.user.id).exists():
            return super().dispatch(request,*args, **kwargs)
        return redirect('/')
    
    def post (self, request,*args, **kwargs ):
        resource=Resource.objects.get(id=self.kwargs['resourceid'])
        readerlist = request.POST.getlist('reader[]')
        ownerlist = request.POST.getlist('owner[]')
        
        
        resource.readers.clear()
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
        


#Those views have to be classes and to inherit from different generic classes, 
#they must NOT be implemented as functions(with def). For example:
#  
#    class ResourceInfoView(generic.DetailView):
#        model = models.Resource
#        template_name = '...'
#        .
#        .
#    .
#
# - Alex


class ChosenRequestsView(generic.DetailView):
    model = AccessRequest
    template_name = "AuthorizationManagement/handle-request.html"


def permissionForChosenResourceView():
    return

def manageUsersView():
    return

def permissionsForResourceView():
    return

def manageResourcesView():
    return

def permissionsForUsersView():
    return

def resourcesOverview():
    return

def openResourceView():
    return

def requestView():
    return

def resourceInfoView():
    return