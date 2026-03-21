from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def test(request):
    x = 1
    y = 2
    return render(request, 'test.html')