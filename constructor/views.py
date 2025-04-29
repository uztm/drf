from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .permissions import IsOwnerMatchingUsername, IsStaffOrSuperUser
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerCrud
    permission_classes = (IsAuthenticated, IsStaffOrSuperUser)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

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

        return queryset

class PartyConstructorViewSet(viewsets.ModelViewSet):
    queryset = PartyConstructor.objects.all()
    serializer_class = PartyConstructorSerializer

    def create(self, request, *args, **kwargs):
        # Ensure that the request data is valid before processing
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Handle the create logic, which includes saving the services
            party_constructor = serializer.save()
            return Response(self.get_serializer(party_constructor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # Update the PartyConstructor and handle services
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            party_constructor = serializer.save()
            return Response(self.get_serializer(party_constructor).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PartyConstructorDetailView(viewsets.ModelViewSet):
    queryset = PartyConstructor.objects.all()
    serializer_class = PartyConstructorDetailSerializer
    permission_classes = (IsAuthenticated,IsOwnerMatchingUsername)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user(self, request):
        username = request.query_params.get('username')
        user_id = request.query_params.get('id')

        if not username or not user_id:
            return Response({'error': 'username and id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            return Response({'error': 'Invalid UUID format'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = PartyConstructor.objects.select_related('user').prefetch_related('services').filter(
            user__id=user_id,
            user__username=username
        )

        if not queryset.exists():
            return Response({'error': 'PartyConstructor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)  # <-- many=True because now it's a list
        return Response(serializer.data)

    @action(detail=False, methods=['get'])

    def by(self, request):

        username = request.query_params.get('username')

        party_id = request.query_params.get('party_id')

        if not username or not party_id:
            return Response({'error': 'username, id, and party_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            party_id = uuid.UUID(party_id)
        except ValueError:
            return Response({'error': 'Invalid UUID format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = PartyConstructor.objects.select_related('user').prefetch_related('services').get(
                id=party_id,
                user__username=username
            )
        except PartyConstructor.DoesNotExist:
            return Response({'error': 'PartyConstructor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
