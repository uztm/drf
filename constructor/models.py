import uuid
from django.utils import timezone
from django.db import models
from django.db import models
from user.models import User

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
    capacity = models.PositiveIntegerField(null=True, blank=True)
    availability_date = models.DateTimeField(default=timezone.now)  

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return self.title

class ServiceImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='service_images/')

    def __str__(self):
        return f"Image for {self.service.title}"




# ---------- Party Constructor ----------
class PartyConstructor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="party_constructors")
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)

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
