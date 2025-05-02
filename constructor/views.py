import uuid

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.permissions import SAFE_METHODS
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from .permissions import IsOwnerOrAdmin, IsOwnerMatchingUsername
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Service, ServiceImage, PartyConstructor, Order
from .serializers import (
    CategorySerializer,
    ServiceSerializer,
    ServiceImageSerializer,
    PartyConstructorSerializer,
    OrderSerializer, PartyConstructorDetailSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]  # Allow GET, HEAD, OPTIONS for everyone
        return [IsAdminUser()]  # Restrict POST, PUT, DELETE to admin


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        return [IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = Service.objects.all()
        params = self.request.query_params

        # Handle 'date' filter (availability_date should be today or in the future)
        date_filter = params.get('date', None)
        if date_filter:
            # try:
            #     filter_date = make_aware(datetime.strptime(date_filter, '%Y-%m-%d'))
            #     queryset = queryset.filter(availability_date__gte=filter_date)
            # except ValueError:
            pass  # Ignore invalid date formats

        # Handle 'category' filter
        category_filter = params.get('category', None)
        if category_filter and category_filter.lower() != 'all':
            queryset = queryset.filter(category__name=category_filter)

        # Handle 'priceMin' and 'priceMax' filters
        price_min = params.get('priceMin', None)
        price_max = params.get('priceMax', None)
        if price_min and price_max:
            queryset = queryset.filter(price__gte=price_min, price__lte=price_max)
        elif price_min:
            queryset = queryset.filter(price__gte=price_min)
        elif price_max:
            queryset = queryset.filter(price__lte=price_max)

        # Handle 'capacityMin' and 'capacityMax' filters
        capacity_min = params.get('capacityMin', None)
        capacity_max = params.get('capacityMax', None)
        if capacity_min and capacity_max:
            queryset = queryset.filter(capacity__gte=capacity_min, capacity__lte=capacity_max)
        elif capacity_min:
            queryset = queryset.filter(capacity__gte=capacity_min)
        elif capacity_max:
            queryset = queryset.filter(capacity__lte=capacity_max)

        # Randomize the queryset
        queryset = queryset.order_by('?')

        return queryset


class ServiceImageViewSet(viewsets.ModelViewSet):
    queryset = ServiceImage.objects.all()
    serializer_class = ServiceImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Image file to upload",
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                'service',
                openapi.IN_FORM,
                description="Service name associated with the image",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_description="Upload an image for a service",
        responses={201: ServiceImageSerializer}
    )
    def create(self, request, *args, **kwargs):
        service_id = request.data.get('service')
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response(
                {"detail": "Service not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if service.owner != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to add images to this service."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        service_image = self.get_object()
        service = service_image.service

        if service.owner != request.user:
            return Response(
                {"detail": "You do not have permission to update images for this service."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsOwnerOrAdmin()]

class PartyConstructorViewSet(viewsets.ModelViewSet):
    queryset = PartyConstructor.objects.all()
    serializer_class = PartyConstructorSerializer

    def get_permissions(self):
        return [IsOwnerOrAdmin()]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        return [IsOwnerOrAdmin()]

class PartyConstructorDetailView(viewsets.ModelViewSet):
    serializer_class = PartyConstructorDetailSerializer
    permission_classes = (IsAuthenticated,)  # No need for custom permission if you filter by user

    def get_queryset(self):
        return PartyConstructor.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # Already restricted by get_queryset
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by(self, request):
        party_id = request.query_params.get('party_id')

        if not party_id:
            return Response({'error': 'party_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            party_uuid = uuid.UUID(party_id)
        except ValueError:
            return Response({'error': 'Invalid UUID format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = PartyConstructor.objects.select_related('user').prefetch_related('services').get(
                id=party_uuid,
                user=request.user
            )
        except PartyConstructor.DoesNotExist:
            return Response({'error': 'PartyConstructor not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
