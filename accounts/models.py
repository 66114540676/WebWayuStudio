from django.db import models
from django.contrib.auth.models import AbstractUser

def user_directory_path(instance, filename):
    return f"profile_user_pics/user_{instance.username}/{filename}"

class CustomUser(AbstractUser):
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.username