from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Topic(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name='topics')

    def __str__(self):
        return self.title

class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author.username} on {self.created_at}"

class UserModeration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='moderation')
    banned = models.BooleanField(default=False)
    timeout_until = models.DateTimeField(null=True, blank=True)

    def is_timed_out(self):
        return self.timeout_until and timezone.now() < self.timeout_until

    def __str__(self):
        return f"Moderation info for {self.user.username}"
