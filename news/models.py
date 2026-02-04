from django.db import models
from django.core.exceptions import ValidationError
import uuid
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Story(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    link = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="stories/images/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="stories/videos/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Require at least one media
        if not self.image and not self.video:
            raise ValidationError("A story must have an image or a video.")

    def __str__(self):
        return self.link or f"Story #{self.id}"



class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    image = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    video = CloudinaryField(
        "video",
        resource_type="video",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )

    def is_admin_post(self):
        return self.user and self.user.is_superuser

class Signup(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # store hashed password
    created_at = models.DateTimeField(auto_now_add=True)

    # For password reset
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username

    def generate_reset_token(self):
        self.reset_token = uuid.uuid4().hex
        self.reset_token_expiry = timezone.now() + timedelta(hours=1)
        self.save()
        return self.reset_token

    def is_reset_token_valid(self, token):
        return self.reset_token == token and self.reset_token_expiry > timezone.now()

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    avatar = models.URLField(blank=True)
    provider = models.CharField(max_length=50, default='google')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')
    text = models.TextField(blank=True)
    audio = models.FileField(upload_to="comments/audio/", blank=True, null=True)
    likes = models.ManyToManyField(User, blank=True, related_name='liked_comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.post.id}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")  # one like per user


