from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    phoneNumber = models.CharField(max_length=15, unique=True, null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')
    
    def __str__(self):
        return self.username