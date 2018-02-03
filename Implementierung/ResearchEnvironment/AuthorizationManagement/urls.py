from django.urls import path
# from AuthorizationManagement import views
from django.urls.conf import re_path
from .admin import resource_manager
from .admin import user_manager
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    re_path(r'^resource-manager/', resource_manager.urls),
    re_path(r'^user-manager/', user_manager.urls),
       
    re_path(r'^profile/$', ProfileView.as_view(), name = 'profile'),
    re_path(r'^profile/my-resources/$', MyResourcesView.as_view(), name = 'my resources' ),
    re_path(r'^profile/my-resources/(?P<resourceid>\d+)-edit-users-permissions/$', PermissionEditingView.as_view(), name='edit permissions'),
    re_path(r'^profile/my-resources/(?P<resourceid>\d+)-edit-users-permissions/search$', PermissionEditingViewSearch.as_view(), name='edit permissions searching for user'),
    re_path(r'^profile/my-resources/add-new-resource/$', AddNewResourceView.as_view(), name='add-new-resource'),
    re_path(r'^profile/edit-name/$', EditNameView.as_view(), name='edit-name'),

    re_path(r'^approve-access-request/(?P<requestid>\d+)$', ApproveAccessRequest.as_view(), name='approve access request'),
    re_path(r'^deny-access-request/(?P<requestid>\d+)$', DenyAccessRequest.as_view(), name='deny access request'),

    re_path(r'^approve-deletion-request/(?P<requestid>\d+)*$', ApproveDeletionRequest.as_view(), name='approve deletion request'),
    re_path(r'^deny-deletion-request/(?P<requestid>\d+)$', DenyDeletionRequest.as_view(), name='deny deletion request'),

    re_path(r'^send-deletion-request/(?P<resourceid>\d+)$', SendDeletionRequestView.as_view(), name='send delete request'),
    re_path(r'^cancel-deletion-request/(?P<resourceid>\d+)$', CancelDeletionRequestView.as_view(), name='send delete request'),
        
    re_path(r'^resources-overview/$', ResourcesOverview.as_view(), name='resource-overview'),
    re_path(r'^resources-overview/search$', ResourcesOverviewSearch.as_view(), name='search-resources'),

    re_path(r'^resources/(?P<resourceid>\d+)$', OpenResourceView.as_view(), name='open resources'),
    re_path(r'^send-access-request/(?P<resourceid>\d+)$', SendAccessRequestView.as_view(), name='send-access-request'),
    re_path(r'^cancel-access-request/(?P<resourceid>\d+)$', CancelAccessRequest.as_view(), name='cancel-access-request'),
    
    re_path(r'^delete-resource/(?P<resourceid>\d+)*$', DeleteResourceView.as_view(), name='delete resource'),
     
]
