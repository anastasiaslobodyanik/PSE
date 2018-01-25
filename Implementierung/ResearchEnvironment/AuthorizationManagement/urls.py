from django.urls import path

from AuthorizationManagement import views
from django.urls.conf import re_path
from .admin import resource_manager
from .admin import user_manager

urlpatterns = [
    path('', views.homeView, name='home'),
    re_path(r'^resource-manager/', resource_manager.urls),
    re_path(r'^user-manager/', user_manager.urls),
        
    
    
    #this section should be commented for now, so that we can work with the /admin interface from django; 
    #that means views.foo should not be used for now
    
    
    
    re_path(r'^profile/', views.ProfileView.as_view(), name = 'profile'),
    re_path(r'^my-resources/$', views.MyResourcesView.as_view(), name = 'my resources' ),
    # re_path(r'^profile/handle/$', views.ChosenRequestView.as_view(), name = 'handle request'),
    re_path(r'^handle/(?P<pk>\d+)$', views.ChosenRequestsView.as_view(), name='handle request'),

    #     re_path(r'^profile/resources/add_new_resource/$', views.index),
#     re_path(r'^profile/resources/(?P<resourceID>\w+)_send_deletion_request/$', views.foo),
#     re_path(r'^profile/resources/(?P<resorceID>\w+)_edit_users_permissions/$', views.foo),
#     re_path(r'^profile/resources/(?P<resourceID>\w+)_edit_users_permissions/reason_for_change/$', views.foo),
#
#     re_path(r'^login/$', views.index),
#
#     re_path(r'^manage_users/$', views.index),
#     re_path(r'^manage_users/block_user/$', views.index),
#     re_path(r'^manage_users/delete_user/$', views.index),
#     re_path(r'^manage_users/(?P<userID>\w+)_permissions_for_resources/$', views.foo),
#     re_path(r'^manage_users/(?P<userID>\w+)_permissions_for_resources/reason_for_change/$', views.foo),
#
#     re_path(r'^manage_resources/$', views.index),
#     re_path(r'^manage_resources/delete_resource/$', views.index),
#     re_path(r'^manage_resources/(?P<resourceID>\w+)_permissions_for_users/$', views.foo),
#     re_path(r'^manage_resources/(?P<resourceID>\w+)_permissions_for_users/reason_for_change/$', views.foo),

    
    re_path(r'^search-resources/$', views.search_form, name='search-resources'),
    re_path(r'^search/$', views.search, name='search'),
    re_path(r'^search/(?P<pk>\d+)$', views.ResourceDetailView.as_view(), name='resource-info'),
    re_path(r'^resources/\w+\d*\.txt$', views.download, name='download resources')

      
#     re_path(r'^resources_overview/(?P<resourceID>\w+)_send_request/$', views.foo),
#        
#     re_path(r'^(?P<resourceID>\w+)/$', views.foo),
      
     
    
]
