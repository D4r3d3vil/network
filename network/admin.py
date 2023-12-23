from django.contrib import admin
from network.models import Post, User, Profile, ChatRoom, ChatMessage
# Register your models here.


admin.site.register(Post)
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(ChatMessage)
admin.site.register(ChatRoom)