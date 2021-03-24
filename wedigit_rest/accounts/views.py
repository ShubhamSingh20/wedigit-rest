from typing import Any, Dict

from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,TokenRefreshSerializer)
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

from accounts.models import User
from accounts.serializer import UserSerializer

# Create your views here.

class LoginObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs) -> Dict:
        data : Dict = super().validate(attrs)
        data['user'] = UserSerializer(instance=self.user).data
        return data

class JWTAuthLogin(TokenObtainPairView):
    serializer_class = LoginObtainPairSerializer

    def post(self, request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)

        if accessToken := response.data['access']:
            response.set_cookie('jwt', accessToken, httponly=True)

        if refreshToken := response.data['refresh']:
            response.set_cookie('refresh', refreshToken, httponly=True)

        return response

class JWTAuthRefresh(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)

        if accessToken := response.data['access']:
            response.set_cookie('jwt', accessToken, httponly=True)

        if refreshToken := response.data['refresh']:
            response.set_cookie('refresh', refreshToken, httponly=True)

        return response

class JWTAuthMe(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        return Response({
            'user': UserSerializer(instance=request.user).data
        }, status=status.HTTP_200_OK)

class JWTSignUpView(APIView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        unhased_password : str = request.data.get('password', None)
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user : User = serializer.save()
        
        jwt_serializer = LoginObtainPairSerializer(data={
            'email': user.email, 
            'password': unhased_password
        })

        try:
            jwt_serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = Response(data=jwt_serializer.validated_data, status=status.HTTP_200_OK)
        
        if accessToken := jwt_serializer.validated_data.get('access', False):
            response.set_cookie('jwt', accessToken, httponly=True)

        if refreshToken := jwt_serializer.validated_data.get('refresh', False):
            response.set_cookie('refresh', refreshToken, httponly=True)

        return response

class JWTLogout(APIView):
    """
        Need to implment a token blacklisting startegy later on
        to invalidate tokens
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        response = Response({
            'detail': 'logged out successfully',
        }, status=status.HTTP_200_OK)

        response.delete_cookie('jwt')
        response.delete_cookie('refresh')

        return response

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'slug'
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminUser]

    def paginate_queryset(self, queryset) -> Any:
        if 'all' not in self.request.GET:
            return super().paginate_queryset(queryset)
