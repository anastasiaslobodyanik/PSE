from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Resource
from .models import User


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

class ProfilView(generic.DetailView, generic.ListView):
    model = User
    template_name = 'AuthorizationManagement/profile.html'

#shows a search field
@login_required()
def search_form(request):
    return render(request, 'AuthorizationManagement/search-resources.html')
  
#shows results of the search  
@login_required()
def search(request):
    if 'q' in request.GET and request.GET['q']:
        query = request.GET['q']
        resource = Resource.objects.filter(name__icontains=query)
        return render(request, 'AuthorizationManagement/resources-overview.html',
                      {'resource': resource, 'query': query})
    else:
        return render(request, 'AuthorizationManagement/try-searching-again.html')  
    





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

def bar3(request):
    html= "<html><body><form action=/authentification/logout/><input type=submit value=logout/></form></body></html>"
    return HttpResponse(html)

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