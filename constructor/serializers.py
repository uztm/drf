from rest_framework import serializers
from .models import Category, Service, ServiceImage, PartyConstructor, Order
from user.models import User

class CategorySerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = "__all__"

    def get_services(self, obj):
        services = obj.services.all()  # using related_name='services'
        request = self.context.get('request')  # needed for full image URLs if any
        return ServiceSerializer(services, many=True, context={'request': request}).data


class ServiceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    images = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField(source='category.name')  # ✅ Add this line

    class Meta:
        model = Service
        fields = "__all__"  # This will include 'category', but not 'category.name' explicitly
        # OR use: fields = ['id', 'name', ..., 'category', 'category_name', 'images', ...]

    def get_images(self, obj):
        request = self.context.get('request')
        if request and request.method == 'GET':
            images_qs = obj.images.all()
            return ServiceImageSerializer(images_qs, many=True, context=self.context).data
        return None



class ServiceImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

class PartyConstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyConstructor
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ('password','role')
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser': {'write_only': True},
            'is_staff': {'write_only': True},
            'groups': {'write_only': True},
            'user_permissions': {'write_only': True},
        }

class PartyConstructorDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    services = ServiceSerializer(many=True)

    class Meta:
        model = PartyConstructor
        fields = ['id', 'user', 'title', 'event_date','budget', 'guest_count', 'created_at', 'services']

