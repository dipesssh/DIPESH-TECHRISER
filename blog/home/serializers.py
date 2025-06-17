from rest_framework import serializers

from .models import Blog, Comment
from django.contrib.auth.models import User

# Serializer for the Blog model

class BlogSerializers(serializers.ModelSerializer):
    class Meta:
        model = Blog
        exclude = ['created_at','updated_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uid', 'text', 'created_at']
        read_only_fields = ['uid', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    