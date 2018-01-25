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
    return render(request, 'AuthorizationManagement/home.html')

#details for resource, not yet finished
class ResourceDetailView(generic.DetailView):
    model = Resource
    template_name = 'AuthorizationManagement/resource-details.html'

class ProfileView(generic.ListView):
    model = User
    template_name = 'AuthorizationManagement/profile.html'
    
class MyResourcesView(generic.ListView):
    model = Resource
    template_name = 'AuthorizationManagement/my-resources.html'
    
class MyRequestsView(generic.ListView):
    model = AccessRequest
    template_name = 'AuthorizationManagement/my-requests.html'
    

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

    def handle(self):
        return generic.FormView.as_view()


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