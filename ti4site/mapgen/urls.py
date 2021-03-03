from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('generate_map', views.generate_map, name="index")
]
