from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required


def index(request):
    return HttpResponse("Test home page rendering using def. Later on it must be rewritten with view class.")
def foo(request, requestID=None, resourceID=None, userID=None):
    if requestID is not None:
        html = "<html><body>Test!requestID = %s .</body></html>" % requestID
    elif userID is not None:
        html = "<html><body>Test!userID = %s .</body></html>" % userID
    else:
        html = "<html><body>Test!resourceID = %s .</body></html>" % resourceID 
    return HttpResponse(html)
@login_required(login_url='dummy/login')
def homeView(request):
    return render(request, 'homeView.html')
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