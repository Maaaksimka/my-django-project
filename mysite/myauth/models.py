from django.contrib.auth.models import User
from django.db import models


def user_avatar_directory_path(instance: "User", filename: str) -> str:
    return "avatar/user_{pk}/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )

class Profile(models.Model):
    avatar = models.FileField(null=True, blank=True, upload_to=user_avatar_directory_path,)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
