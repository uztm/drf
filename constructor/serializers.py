from rest_framework import serializers

from .models import *

class UserSerializerCrud(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])

        # Create user
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Assign groups
        if groups:
            user.groups.set(groups)

        # Assign user_permissions
        if user_permissions:
            user.user_permissions.set(user_permissions)

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', None)
        user_permissions = validated_data.pop('user_permissions', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        # Assign groups
        if groups is not None:
            instance.groups.set(groups)

        # Assign user_permissions
        if user_permissions is not None:
            instance.user_permissions.set(user_permissions)

        return instance


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

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

    def get_owner(self, obj):
        # Serialize the owner field with specific fields only
        return {
            'username': obj.owner.username,
            'phone_number': obj.owner.phone_number,
            'first_name': obj.owner.first_name,
            'last_name': obj.owner.last_name,
        }


class PartyConstructorSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField()  # This will take UUID input
    services = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    class Meta:
        model = PartyConstructor
        fields = ['id', 'user', 'title', 'event_date', 'budget_from', 'budget_to', 'guest_count', 'created_at',
                  'services']

    def create(self, validated_data):
        # Fetch the user instance based on the UUID
        user_uuid = validated_data.pop('user')
        user_instance = User.objects.get(id=user_uuid)  # Find the user by UUID

        # Extract services data
        services_data = validated_data.pop('services', [])

        # Create the PartyConstructor instance
        party_constructor = PartyConstructor.objects.create(user=user_instance, **validated_data)

        # Assign services to the PartyConstructor instance
        party_constructor.services.set(services_data)

        return party_constructor

    def update(self, instance, validated_data):
        # Update the PartyConstructor instance and assign services
        user_uuid = validated_data.pop('user', None)
        if user_uuid:
            user_instance = User.objects.get(id=user_uuid)  # Fetch the user by UUID
            instance.user = user_instance

        services_data = validated_data.pop('services', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.services.set(services_data)

        instance.save()
        return instance

class PartyConstructorDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    services = ServiceSerializer(many=True)

    class Meta:
        model = PartyConstructor
        fields = ['id', 'user', 'title', 'event_date', 'budget_from', 'budget_to', 'guest_count', 'created_at', 'services']

