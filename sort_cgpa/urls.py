from django.urls import path
from . import views

app_name = 'sort_cgpa'

urlpatterns = [
    path('', views.upload_file, name="sort_cgpa"),
]