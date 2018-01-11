from django.http import HttpResponse


def index(request):
    return HttpResponse("Test home page rendering using def. Later on it must be rewritten with view class.")