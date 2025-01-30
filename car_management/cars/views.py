from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status,generics,permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view,permission_classes
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render

from django.db.models import Q
from .models import Car
from .serializers import CarSerializer

def frontview(request):
    # This function will render the 'home.html' template
    domain = request.get_host()
    full_domain = f"{request.scheme}://{domain}"  # Construct full domain
    api_url = f"{full_domain}"
    print(api_url)
    return render(request, 'base2.html',context={"api_url": api_url})
    return render(request, 'base.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """ Register a new user """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """ Login user and return token """
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])  # Only allow authenticated users to log out
def logout_user(request):
    """ Logout user and delete their token """
    try:
        request.auth.delete()  # Delete the token
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid token or user already logged out'}, status=status.HTTP_400_BAD_REQUEST)

class CarListCreateView(generics.ListCreateAPIView):
    """ Create a car and list all cars of the logged-in user """
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allows file uploads

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ Retrieve, update, or delete a car """
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        """ Allow all users to view any car """
        return Car.objects.filter(owner=self.request.user) 

    def perform_update(self, serializer):
        """ Allow update only if the user owns the car """
        car = self.get_object()
        if car.owner != self.request.user:
            return Response({'error': 'You can only update your own cars.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """ Allow delete only if the user owns the car """
        if instance.owner != self.request.user:
            return Response({'error': 'You can only delete your own cars.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
    
class CarSearchView(generics.ListAPIView):
    """ Search for cars globally across title, description, and tags """
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'tags']

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Car.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )
        return Car.objects.none()