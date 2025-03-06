from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .models import User
from .serializers import CreateUserSerializer, UserUpdateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import permissions

class Signup(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class MyPage(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request, pk):
        user = self.get_user(pk)
        serializer = UserUpdateSerializer(user)
        response_data = serializer.data
        response_data['preferred_genre'] = [
            genre.genre_name for genre in user.preferred_genre.all()
        ]
        response_data['preferred_game'] = [
            game.title for game in user.preferred_game.all()
        ]
        
        return Response(serializer.data)
    
    def put(self, request,pk):
        user = self.get_user(request.user.pk)
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    def delete(self, request, pk):
        user = self.get_user(request.user.pk)
        user.delete()
        return Response({"message":"withdrawal"},status=status.HTTP_204_NO_CONTENT)