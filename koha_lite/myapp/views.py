from django.shortcuts import render,HttpResponse
from .models import TodoItem
def home(request):
    return render(request,"home.html")

def todo(request):
    items = TodoItem.objects.all()
    return render(request,'todo.html',{'todos':items})