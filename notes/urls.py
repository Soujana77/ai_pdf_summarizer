from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_pdf, name='upload'),

    # Extra AI tools
    path('keywords/', views.ai_keywords, name='keywords'),
    path('bullets/', views.ai_bullets, name='bullets'),
    path('explain5/', views.ai_explain5, name='explain5'),
    path('simplify/', views.ai_simplify, name='simplify'),
    path('translate/', views.ai_translate, name='translate'),
]
