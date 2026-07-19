from django.urls import path

from . import views

urlpatterns = [
    path("", views.create_snippet, name="create_snippet"),
    path("list/", views.list_snippets, name="list_snippets"),
    path("<slug:slug>/comments/", views.list_comments, name="list_comments"),
    path("<slug:slug>/comments/post/", views.post_comment, name="post_comment"),
    path("<slug:slug>/delete/", views.delete_snippet, name="delete_snippet"),
    path("<slug:slug>/", views.view_snippet, name="view_snippet"),
]
