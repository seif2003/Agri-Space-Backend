"""
from django.urls import path
from . import views 


urlpatterns = [
    path('addPost', views.PostView.as_view(), name='addPost'),
    path('getUserPosts', views.GetUserPostsView.as_view(), name='get_user_posts'),
    path('getPosts/<str:category>/', views.GetCategoryPostsView.as_view(), name='get_posts'),
    path('delete/<int:post_id>/', views.PostView.as_view(), name='post_detail'),
]
"""
from django.urls import path
from .views import PostView, GetUserPostsView, GetCategoryPostsView

urlpatterns = [
    path('addPost', PostView.as_view(), name='addPost'),
    path('getUserPosts/', GetUserPostsView.as_view(), name='get_user_posts'),
    path('getPosts/<str:category>', GetCategoryPostsView.as_view(), name='get_posts'),
    path('delete/<int:post_id>', PostView.as_view(), name='delete_post'),
]
