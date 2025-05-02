from django.contrib import admin

from .models import Category, Service, PartyConstructor, Order, ServiceImage

admin.site.register(Category)
admin.site.register(Service)
admin.site.register(PartyConstructor)
admin.site.register(Order)
admin.site.register(ServiceImage)
