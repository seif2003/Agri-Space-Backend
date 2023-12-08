from rest_framework import serializers
from .models import Post, Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']

class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['title', 'description', 'images', 'phone', 'category', 'price', 'user']
