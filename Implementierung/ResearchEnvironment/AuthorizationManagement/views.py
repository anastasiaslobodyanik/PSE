from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Resource
from .models import User
from .models import Owner


# def index(request):
#    return HttpResponse("Test home page rendering using def. Later on it must be rewritten with view class.")
def foo(request, requestID=None, resourceID=None, userID=None):
    if requestID is not None:
        html = "<html><body>Test!requestID = %s .</body></html>" % requestID
    elif userID is not None:
        html = "<html><body>Test!userID = %s .</body></html>" % userID
    else:
        html = "<html><body>Test!resourceID = %s .</body></html>" % resourceID 
    return HttpResponse(html)

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
    model = Owner
    template_name = 'AuthorizationManagement/my-resources.html'
    
class MyRequestsView(generic.ListView):
    model = Owner
    template_name = 'AuthorizationManagement/my-requests.html'

class ResourcesOverview(generic.ListView):
    model = Resource
    template_name = 'AuthorizationManagement/my-resources-overview.html'  
    context_object_name = "resources_list"
    paginate_by = 2
    
    def get_context_data(self, **kwargs):
        context = super(ResourcesOverview, self).get_context_data(**kwargs)
        context['query_pagination_string'] = ''
        return context
    
    
class ResourcesOverviewSearch(generic.ListView):
     model = Resource.objects.all()
     template_name = 'AuthorizationManagement/my-resources-overview.html'  
     context_object_name = "resources_list"
     paginate_by = 2
     query = ''
     
     
     def get_queryset(self):
         return self.model
     
     def get(self,request):
        if 'q' in self.request.GET and self.request.GET['q']:
          self.query = self.request.GET['q']
          self.model = Resource.objects.filter(name__icontains=self.query)
          return super(ResourcesOverviewSearch, self).get(request)
        else:
          return redirect("/resources-overview")
    
     def get_context_data(self, **kwargs):
        context = super(ResourcesOverviewSearch, self).get_context_data(**kwargs)
        context['query'] = self.query;
        context['query_pagination_string'] = 'q='+self.query+'&'
        return context
            
        
#shows a search field
@login_required()
def search_form(request):
    return render(request, 'AuthorizationManagement/search-resources.html')
  
     



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


def profileView(request):
    return

def chosenRequestsView(request):
    return

def myResourcesView(request):
    return
def deleteResourceView():
    return

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