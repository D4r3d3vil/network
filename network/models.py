from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

        
class Comment(models.Model):
    user = models.CharField(User, max_length=100) 
    comment = models.TextField(max_length=1000) 
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User,  blank=True)    
    def to_dict(self):
        r = {
            "user": self.user,
            "comment": self.comment,
            "timestamp": self.timestamp.isoformat(),
            "likes": [user.username for user in self.likes.all()],
        }
    def __str__(self):
        return self.user.username + ": " + self.comment


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=500, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User,  blank=True, related_name="liked_user")
    comments = models.ManyToManyField(Comment, blank=True, related_name="commented_post") 

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    read = models.BooleanField(default=False)
    link = models.TextField()

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ManyToManyField(
        User,  blank=True, related_name="follower_user")
    following = models.ManyToManyField(
        User,  blank=True, related_name="following_user")
    description = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    notifications = models.ManyToManyField(Notification, blank=True, related_name="notifications")

    def __str__(self):
        return self.user.username
