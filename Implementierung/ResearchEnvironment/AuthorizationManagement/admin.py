from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from .models import Resource
from .models import User

admin.site.register(Resource)

# Register your models here.
 
 
#this is the subpage 'Manage Resources' only displayable to the admin
class ResourceManager(AdminSite):     
    pass
    #or methods         
resource_manager = AdminSite(name="ResourceManager")

class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", 
                    "type", 
                    "description"]
    search_fields = ["name", 
                     "type", 
                     "description"]
    
resource_manager.register(Resource, ResourceAdmin)


#this is the subpage 'Manage Users' also only displayable to the admin
class UserManager(AdminSite):
    pass
    #or methods    
user_manager = AdminSite(name="UserManager")

class UserAdmin(admin.ModelAdmin):
    list_display = ["last_name", 
                    "first_name", 
                    "email", 
                    "is_active", 
                    "is_staff", 
                    "last_login", 
                    "date_joined"]
    search_fields = ["username" , 
                     "email", 
                     "first_name", 
                     "last_name"]
    
user_manager.register(User, UserAdmin)
    