from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.core.files.images import ImageFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Post, Image
from user.models import CustomUser
from django.core.files.base import ContentFile
import base64
import json
from django.contrib.auth import get_user_model
from functools import wraps
from django.http import HttpResponseForbidden
from rest_framework.authtoken.models import Token


from termcolor import colored
from pyfiglet import figlet_format

User = get_user_model()

def token_auth_required(view_method):
    def _wrapped_view(self, request, *args, **kwargs):
        authorization_header = request.headers.get('Authorization')

        if not authorization_header or not authorization_header.startswith('Token '):
            return JsonResponse({'error': 'Invalid or missing authorization token'}, status=401)

        token_key = authorization_header.split(' ')[1]

        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        request.authenticated_user = token.user

        return view_method(self, request, *args, **kwargs)

    return _wrapped_view


class PostView(View):
    
    @token_auth_required
    def post(self, request, *args, **kwargs):
        user = request.authenticated_user

        try:
            user = CustomUser.objects.get(id=user.id)
            images = request.FILES.getlist('images')
            image_objects = [Image.objects.create(image=image) for image in images]
            post = Post.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                phone=request.POST['phone'],
                category=request.POST['category'],
                price=request.POST['price'],
                user=user,
            )
            post.images.set(image_objects)
            post.save()

            text = f"Post created successfully"
            print(colored(figlet_format(text), color="green"))

            return JsonResponse({'message': 'Post created successfully'}, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Something went wrong... unable to create post'}, status=500)
    
    @token_auth_required
    def delete(self, request, post_id, *args, **kwargs):
        user = request.authenticated_user

        try:
            post = Post.objects.get(id=post_id)

            if user != post.user:
                return JsonResponse({'error': 'Permission denied'}, status=403)

            post.delete()

            text = f"Post deleted successfully"
            print(colored(figlet_format(text), color="green"))

            return JsonResponse({'message': 'Post deleted successfully'}, status=200)

        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Something went wrong... unable to delete post'}, status=500)


class GetUserPostsView(View):
    @token_auth_required
    def get(self, request,*args, **kwargs):
        user = request.authenticated_user
        try:
            user = CustomUser.objects.get(id=user.id)
            posts = Post.objects.filter(user=user)

            post_data = []
            for post in posts:
                post_images = [{'image_url': image.image.url} for image in post.images.all()]

                post_info = {
                    'post_id': post.pk,
                    'title': post.title,
                    'description': post.description,
                    'category': post.category,
                    'price': post.price,
                    'images': post_images,
                }

                post_data.append(post_info)
                
            text1 = f"{user.first_name} {user.last_name}"
            text2 = "viewed their posts"

            print(colored(figlet_format(text2), color="green") + colored(figlet_format(text1), color="blue"))

            return JsonResponse({'posts': post_data}, status=200)

        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)

        except Exception as e:
            return JsonResponse({'error': 'Something went wrong. Unable to retrieve posts.'}, status=500)

class GetCategoryPostsView(View):
    def get(self, request, category, *args, **kwargs):
        try:
            posts = Post.objects.filter(category=category)

            post_data = []
            for post in posts:
                post_images = [{'image_url': image.image.url} for image in post.images.all()]

                post_info = {
                    'post_id': post.pk,
                    'title': post.title,
                    'description': post.description,
                    'category': post.category,
                    'price': post.price,
                    'images': post_images,
                    'user_first_name': post.user.first_name,
                    'user_last_name': post.user.last_name,
                }

                post_data.append(post_info)

            return JsonResponse({'posts': post_data}, status=200)

        except Exception as e:
            return JsonResponse({'error': 'Something went wrong. Unable to retrieve posts.'}, status=500)
