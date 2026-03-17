from django.shortcuts import render
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import AppUser, AppPost, AppComment
from .serializers import AppUserSerializer, AppPostSerializer, AppCommentSerializer


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
class UserDetailV1(APIView):

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

        # Get posts
        posts = AppPost.objects.filter(author=user).only(
            'id', 'title', 'body', 'created_at'
        )

        response_posts = []

        for post in posts:
            # Get comments for each post
            comments = AppComment.objects.filter(post=post).only(
                'id', 'text', 'created_at'
            )

            response_posts.append({
                "id": post.id,
                "title": post.title,
                "body": post.body,
                "created_at": post.created_at,
                "comments": AppCommentSerializer(comments, many=True).data
            })

        response_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "posts": response_posts
        }

        return Response(response_data)
    

class UserDetailV2(APIView):

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

        posts = AppPost.objects.filter(author_id=pk).only(
            'id', 'title', 'body', 'created_at'
        ).prefetch_related(
            Prefetch(
                'appcomment_set',
                queryset=AppComment.objects.only('id', 'text', 'created_at', 'post_id'),
            )
        )

        response_posts = []
        for post in posts:
            response_posts.append({
                "id": post.id,
                "title": post.title,
                "body": post.body,
                "created_at": post.created_at,
                "comments": AppCommentSerializer(post.appcomment_set.all(), many=True).data,
            })

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "posts": response_posts,
        })