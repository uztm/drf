import uuid
from django.utils import timezone


from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ---------- Custom User ----------
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

class User(AbstractBaseUser, PermissionsMixin):  # PermissionsMixin important!
    ROLE_CHOICES = (
        ('user', 'User'),
        ('partner', 'Partner'),
        ('superuser', 'Superuser'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)      # Can access Django admin
    is_superuser = models.BooleanField(default=False)   # Has all permissions

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    objects = UserManager()

    def __str__(self):
        return self.username


# ---------- Categories ----------
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# ---------- Services ----------
class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.BigIntegerField()
    photos = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    availability_date = models.DateTimeField(default=timezone.now)  # Ensure default is set

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return self.title





# ---------- Party Constructor ----------
class PartyConstructor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="party_constructors")
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    budget_from = models.DecimalField(max_digits=12, decimal_places=2)
    budget_to = models.DecimalField(max_digits=12, decimal_places=2)
    guest_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    services = models.ManyToManyField('Service', related_name="party_constructors")

    def __str__(self):
        return self.title


# ---------- Orders  ----------
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    party = models.OneToOneField(PartyConstructor, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.BigIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order for {self.party.title}"
