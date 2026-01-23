# news/signals.py
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from allauth.socialaccount.signals import social_account_added, social_account_updated
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            email=instance.email,
            full_name=instance.get_full_name()
        )


@receiver(social_account_added)
@receiver(social_account_updated)
def update_profile_from_google(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    data = sociallogin.account.extra_data

    profile, _ = Profile.objects.get_or_create(user=user)

    profile.full_name = data.get("name", "")
    profile.email = data.get("email", "")
    profile.avatar = data.get("picture", "")
    profile.provider = "google"
    profile.save()
