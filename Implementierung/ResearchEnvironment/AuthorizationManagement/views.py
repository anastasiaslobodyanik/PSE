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

@login_required()
def homeView(request):
    is_admin=request.user.is_staff
    return render(request, 'AuthorizationManagement/home.html', {'is_admin': is_admin})

#details for resource, not yet finished
class ResourceDetailView(generic.DetailView):
    model = Resource
    
    template_name = 'AuthorizationManagement/resource-details.html'

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
    paginate_by = 2
    canAccess = Resource.objects.none() 
    
    def get_queryset(self):
        return self.model
    
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverview, self).get_context_data(**kwargs)
        context['query_pagination_string'] = ''
        context['can_access'] = self.request.user.reader.filter(id__in=self.model)
        print(context['can_access'])
        return context
    
class ResourcesOverviewSearch(generic.ListView):
    model = Resource.objects.all()
    template_name = 'AuthorizationManagement/my-resources-overview.html'  
    context_object_name = "resources_list"
    paginate_by = 2
    query = ''
    can_access = Resource.objects.none()     
     
    def get_queryset(self):
        return self.model
     
    def get(self,request):
        if 'q' in self.request.GET and self.request.GET['q']:
            self.query = self.request.GET['q']
            self.model = Resource.objects.filter(name__icontains=self.query)
            self.can_access=self.request.user.reader.filter(id__in=self.model)
            return super(ResourcesOverviewSearch, self).get(request)
        else:
            return redirect("/resources-overview")
    
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverviewSearch, self).get_context_data(**kwargs)
        context['query'] = self.query;
        context['query_pagination_string'] = 'q='+self.query+'&'
        context['can_access'] = self.can_access
        return context
    
@login_required()          
def send_access_request(request):
    elements=request.path.rsplit('/')
    #method sendAccessRequest returns error, for testing purposes the request is created manually until the error is cleared
    #-Sonya
    AccessRequest.objects.create(sender=request.user,
                                      resource = Resource.objects.get(id=elements[2]), description = request.GET['descr'])
    return redirect("/resources-overview")
    
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

class ChosenRequestsView(generic.DetailView):
    model = AccessRequest
    template_name = "AuthorizationManagement/handle-request.html"


def permissionForChosenResourceView():
    return

def requestView():
    return