from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start_interview, name="start_interview"),
    path("list/", views.list_interviews, name="list_interviews"),
    path("<uuid:interview_id>/", views.get_interview, name="get_interview"),
    path("<uuid:interview_id>/send/", views.send_message, name="send_message"),
    path("<uuid:interview_id>/end/", views.end_interview, name="end_interview"),
    path(
        "<uuid:interview_id>/articles/<uuid:article_id>/chat/",
        views.start_article_chat,
        name="start_article_chat",
    ),
    path(
        "article-chat/<uuid:chat_id>/", views.get_article_chat, name="get_article_chat"
    ),
    path(
        "article-chat/<uuid:chat_id>/send/",
        views.send_article_message,
        name="send_article_message",
    ),
]
