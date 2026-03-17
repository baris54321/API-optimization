from django.shortcuts import render
from rest_framework.views import APIView
from .models import AppUser, AppPost, AppComment
from rest_framework.response import Response
from .serializers import AppUserSerializer, AppPostSerializer, AppCommentSerializer
from rest_framework import status


# Create your views here.


class UserList(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None):
        users = AppUser.objects.all()
        serializer = AppUserSerializer(users, many=True)
        return Response(serializer.data)

# get user 
class UserDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
  
  """

    def get(self, request, pk, format=None):
        user = AppUser.objects.filter(pk=pk).only('id', 'username', 'email').first()
    
        if not user:
            return Response(
                {
                    "status": "error",
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND  

            ) 
        
        # Get user posts
        posts = AppPost.objects.filter(author=user).only('id', 'title', 'body', 'created_at', 'updated_at')

        # Get user comments
        # we need to get the comments for the posts of the user
        comments = AppComment.objects.filter(post__in=posts).only('id', 'text', 'created_at')

        # Serialize user data
        user_data = {
            "user": AppUserSerializer(user).data,
            "posts": AppPostSerializer(posts, many=True).data,
            "comments": AppCommentSerializer(comments, many=True).data
        }
        return Response(user_data)

        


        