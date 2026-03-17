from collections import defaultdict

from django.db import connection
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
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
    

class UserDetailV3(APIView):

    def get(self, request, pk, format=None):
        user = AppUser.objects.filter(pk=pk).values('id', 'username', 'email').first()
        if not user:
            return Response(
                {
                    "status": "error",
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        posts = list(
            AppPost.objects.filter(author_id=pk)
            .values('id', 'title', 'body', 'created_at')
        )

        post_ids = [p['id'] for p in posts]

        comments = (
            AppComment.objects.filter(post_id__in=post_ids)
            .values('id', 'text', 'created_at', 'post_id')
        )

        comments_by_post = defaultdict(list)
        for c in comments:
            comments_by_post[c.pop('post_id')].append(c)

        for post in posts:
            post['comments'] = comments_by_post.get(post['id'], [])

        return Response({
            "user": user,
            "posts": posts,
        })


class UserDetailV4(APIView):

    QUERY = """
        WITH post_comments AS (
            SELECT
                p.id, p.title, p.body, p.created_at,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'id',         c.id,
                            'text',       c.text,
                            'created_at', c.created_at
                        ) ORDER BY c.id
                    ) FILTER (WHERE c.id IS NOT NULL),
                    '[]'::json
                ) AS comments
            FROM app_post p
            LEFT JOIN app_comment c ON c.post_id = p.id
            WHERE p.author_id = %s
            GROUP BY p.id
        )
        SELECT json_build_object(
            'user', json_build_object(
                'id',       u.id,
                'username', u.username,
                'email',    u.email
            ),
            'posts', COALESCE(
                (SELECT json_agg(
                    json_build_object(
                        'id',         pc.id,
                        'title',      pc.title,
                        'body',       pc.body,
                        'created_at', pc.created_at,
                        'comments',   pc.comments
                    ) ORDER BY pc.id
                ) FROM post_comments pc),
                '[]'::json
            )
        )::text
        FROM app_user u
        WHERE u.id = %s
    """

    def get(self, request, pk, format=None):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM app_user WHERE id = %s", [pk]
            )
            if cursor.fetchone() is None:
                return JsonResponse(
                    {"status": "error", "message": "User not found"},
                    status=404,
                )

            cursor.execute(self.QUERY, [pk, pk])
            json_str = cursor.fetchone()[0]

        return HttpResponse(json_str, content_type="application/json")