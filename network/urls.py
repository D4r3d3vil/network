from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("", views.allPost, name="allposts"),
    path("p/<post>", views.post, name="post"),
    path("u/<username>", views.profile, name="profile"),
    path("following/", views.following, name="following"),
    path("like/", views.like),
    path("follow/", views.follow),
    path("edit_post/", views.edit_post),
    path("addpost/", views.addpost),
    path("comment/", views.comment),
    path("comment/like/", views.like_comment),
    path("notifications/", views.get_notifications),
    path("chat/", views.chats, name="chat"),
    path("chat/<roomId>", views.chat_room, name="chatRoom"),
    path("messages/<roomId>/", views.get_chats, name="getChats"),
    path("404", views.fourofour, name="404")
]
