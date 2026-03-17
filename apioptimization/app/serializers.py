from rest_framework import serializers
from .models import AppUser, AppPost, AppComment



class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'email']
    

class AppPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPost
        fields = ['id', 'title', 'body', 'created_at', 'updated_at']
    

class AppCommentSerializer(serializers.ModelSerializer):
    post = AppPostSerializer()
    author = AppUserSerializer()
    class Meta:
        model = AppComment
        fields = ['id', 'text', 'created_at', 'post', 'author']
    