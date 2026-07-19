from django.urls import path

from . import views

urlpatterns = [
    path("", views.create_snippet, name="create_snippet"),
    path("list/", views.list_snippets, name="list_snippets"),
    path("<slug>/", views.view_snippet, name="view_snippet"),
]
