from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
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
from AuthorizationManagement import utilities
from django.http import Http404
from django.template import RequestContext


logger = logging.getLogger(__name__)


class HomeView(generic.View):
    model = User

    def get(self, request):
        is_admin = request.user.is_staff
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
    
    query = ''
    can_access = Resource.objects.none()  
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
        context['query'] = self.query;
        context['query_pagination_string'] = 'q='+self.query+'&'
        context['can_access'] = self.can_access
        context['requested_resources'] = self.requested_resources
        return context

@method_decorator(login_required, name='dispatch') 
class ApproveAccessRequest(generic.View):
    def post(self,request):
        elements=request.path.rsplit('/')
        req=AccessRequest.objects.get(id=elements[2])
        req.resource.readers.add(req.sender)
        req.delete()    
        return redirect("/profile")

@method_decorator(login_required, name='dispatch')     
class DenyAccessRequest(generic.View):
    def post(self,request):
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
                                      resource = Resource.objects.get(id=elements[2]), description = request.POST['descr'])
        
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
    def get(self,request,*args, **kwargs):
        return download(request,self.kwargs['resourceid'])
    
@login_required()
def download(request,pk):
    relative_path = request.path
    if relative_path.find(os.sep) == -1:
        relative_path = relative_path.replace(utilities.getOppositeOSDirectorySep(),os.sep)  
        
    relative_path_elements = relative_path.split(os.sep,1)
    relative_path = relative_path_elements[len(relative_path_elements)-1]
    
    if not Resource.objects.filter(id=pk).exists():
        raise Http404("The requested file doesn't exist!")
    
            
    resource=Resource.objects.get(id=pk)
    file_name = resource.link.name
    relative_path = relative_path.replace(pk+'',file_name)
    
    
    f = open(os.path.join(settings.BASE_DIR, relative_path), 'r')
    myfile = File(f)
    response = HttpResponse(myfile, content_type='text/plain')
    
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    return response


class PermissionEditingView(generic.ListView):
    model = User.objects.all()
    template_name='AuthorizationManagement/edit-permissions.html'
    resource = Resource.objects.all()
    query = ''
    context_object_name = "user_list"
    
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
            
            for user in resource.readers.filter(id__in=self.model):
                if user.id in readerlist:
                    continue
                resource.readers.remove(user)
                #hier email fuer entzogene zugriffsrechte
            for userid in readerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.readers.filter(id__in=self.model):
                    continue
                resource.readers.add(user)
                #hier email fuer vergebene zugriffsrechte
            if len(resource.owners.all()) - len(User.objects.filter(is_staff=True))   > 1:
                for user in resource.owners.filter(id__in=self.model):
                
                    if user.id in ownerlist:
                        continue
                    resource.owners.remove(user)
                #hier email fuer entzogene besitzerrechte
            for userid in ownerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.owners.filter(id__in=self.model):
                    continue 
                user.reader.add(resource)
                user.__class__=Owner
                user.save()
                owner = user
                resource.owners.add(owner)
                #email fuer vergebene besitzerrechte
            
            return redirect('/profile/my-resources/')
        
        
    
    def get_queryset(self):
        return self.model
    
        
    def get_context_data(self, **kwargs):
        context = super(PermissionEditingView, self).get_context_data(**kwargs)
        context['resource'] = Resource.objects.get(id=self.kwargs['resourceid'])
        context['owners'] = Resource.objects.get(id=self.kwargs['resourceid']).owners.all()
        context['readers'] = Resource.objects.get(id=self.kwargs['resourceid']).readers.all()
        context['query'] = self.query
        return context
    
    
    
@method_decorator(login_required, name='dispatch')     
class PermissionEditingViewSearch(PermissionEditingView):
    
    def post(self, request,*args, **kwargs):
            self.query = self.request.GET['q']
            self.model = User.objects.filter(username__icontains=self.query)
            resource=Resource.objects.get(id=self.kwargs['resourceid'])
            readerlist = request.POST.getlist('reader[]')
            ownerlist = request.POST.getlist('owner[]')
            #resource.readers.clear()
            for user in resource.readers.filter(id__in=self.model):
                if user.id in readerlist:
                    continue
                resource.readers.remove(user)
                #hier email fuer entzogene zugriffsrechte
            for userid in readerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.readers.filter(id__in=self.model):
                    continue
                resource.readers.add(user)
                #hier email fuer vergebene zugriffsrechte
            if len(resource.owners.all()) - len(User.objects.filter(is_staff=True))   > 1:
                for user in resource.owners.filter(id__in=self.model):
                
                    if user.id in ownerlist:
                        continue
                    resource.owners.remove(user)
                
                #hier email fuer entzogene besitzerrechte
            for userid in ownerlist:
                user=CustomUser.objects.get(id=userid)
                if user in resource.owners.filter(id__in=self.model):
                    continue 
                user.reader.add(resource)
                user.__class__=Owner
                user.save()
                owner = user
                resource.owners.add(owner)
                #email fuer vergebene besitzerrechte
            
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
        return context
        
@login_required()    
def AddNewResource(request):
    if request.POST:
        print(request.FILES)
        form = AddNewResourceForm(request.POST , request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            instance.owners.add(request.user.id)
            instance.readers.add(request.user.id)

            
            return redirect("/resources-overview")# what happens in the browser after submitting
    else:
        form = AddNewResourceForm()
           
    args = {} 
    args.update(csrf(request))  
        
    args['form'] = form
    return render_to_response('AuthorizationManagement/add-new-resource.html', args)


class PageNotFoundView(generic.View):
    def get(self,request):
        response = render_to_response('AuthorizationManagement/404.html', {},
                                  context_instance=RequestContext(request))
        response.status_code = 404
        return response    

def permissionForChosenResourceView():
    return

def requestView():
    return

