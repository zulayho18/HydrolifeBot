from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Bosh sahifaga xush kelibsiz!")