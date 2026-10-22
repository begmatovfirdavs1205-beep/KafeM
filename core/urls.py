from django.urls import path

from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("delivery/", views.delivery, name="delivery"),
    path("contacts/", views.contacts, name="contacts"),
]
