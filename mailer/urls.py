from django.urls import include
from django.urls import path

from . import views

urlpatterns = [
    path('tinymce/', include('tinymce.urls')),
    path('view_email_template', views.index),
]
