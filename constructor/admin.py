from django.contrib import admin
from django.contrib.auth.base_user import BaseUserManager

from .models import User, Category, Service, PartyConstructor, Order

class UserManager(BaseUserManager):
    def create_user(self, username, phone_number, first_name, last_name, password=None, role='user'):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(
            username=username,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, first_name, last_name, password=None):
        user = self.create_user(
            username=username,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role='superuser',  # <-- Important
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(PartyConstructor)
admin.site.register(Order)

