from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, LoginSerializer, UserSerializer
from .models import User

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Registers a new user and returns JWT tokens (refresh and access).",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "refresh": "string",
                        "access": "string"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input",
                examples={
                    "application/json": {
                        "user": ["This field is required."],
                        "password": ["This field is required."]
                    }
                }
            ),
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Login a user",
        operation_description="Authenticates a user and returns JWT tokens (refresh and access).",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "refresh": "string",
                        "access": "string"
                    }
                }
            ),
            401: openapi.Response(
                description="Invalid credentials",
                examples={
                    "application/json": {
                        "error": "Invalid credentials"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input",
                examples={
                    "application/json": {
                        "username": ["This field is required."],
                        "password": ["This field is required."]
                    }
                }
            ),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCredentialView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)