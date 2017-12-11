from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^search/$', views.searchView, name = "search"),
    url(r'^videoProc/$', views.videoProc, name="videoProc"),

]
