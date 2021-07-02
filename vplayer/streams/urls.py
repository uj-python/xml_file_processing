from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views
from django.conf import settings

app_name = 'player'


urlpatterns = [
    path("",views.window,name='window'),
    path("create_me",views.create_me,name='create_me'),
]