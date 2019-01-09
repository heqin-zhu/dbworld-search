from django.urls import path,re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/',views.index),
    #re_path(r'sort\=\w+',views.sortData),
    path('sort=<str:key>',views.sortData),
    path('update',views.update),
    path('search',views.search),
]
