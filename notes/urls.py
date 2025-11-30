from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_pdf, name='upload'),
]
