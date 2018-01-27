from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required

from .models import *
from django.core.files import File
from django.conf import settings
import os
from django.utils.decorators import method_decorator
from django.http.response import HttpResponseRedirect



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
    model = Resource
    template_name = 'AuthorizationManagement/my-resources.html'
    
class MyRequestsView(generic.ListView):
    model = AccessRequest
    template_name = 'AuthorizationManagement/my-requests.html'

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
        return redirect('/profile/')
         
        
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