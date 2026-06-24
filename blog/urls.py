from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("blog/<int:blog_id>/", views.blog_detail, name="blog_detail"),
]

