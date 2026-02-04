from django.urls import path
from . import views
from . views import *

urlpatterns = [
    # -----------------------
    # User panel URLs
    # -----------------------
    path("", index, name="index"),
    path("news/<uuid:post_id>/", newsview, name="newsview"),

    # -----------------------
    # Admin URLs
    # -----------------------
    path('adminlogin/', views.superuser_login, name='login'),
    path('dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('adminlogout/', views.user_logout, name='logout'),

    path('stories/delete/', views.delete_story, name='delete-story'),
    path('add-post/', views.add_post, name='add-post'),
    path('news/edit/<int:pk>/', views.edit_news, name='edit-news'),
    path('news/delete/', views.delete_news, name='delete-news'),
    path('comment/add/', views.add_comment, name='add_comment'),
    path('comment/like/', views.like_comment, name='like_comment'),
    path('comment/delete/', views.delete_comment, name='delete_comment'),
    path('post/like/', views.post_like, name='post_like'),
    path('profile',views.profile_view, name='profile'),

    path("post/edit/<int:post_id>/", views.edit_post_ajax, name="edit_post_ajax"),
    path("post/delete/<int:post_id>/", views.delete_post_ajax, name="delete_post_ajax"),


    # -----------------------
    # AJAX URLs
    # -----------------------
    # User login page (your custom login modal)
    path('login/', views.base, name='user-login'),

    path('signup-ajax/', views.signup_ajax, name='signup_ajax'),
    path('login-ajax/', views.login_ajax, name='login_ajax'),
    path('forgot-password-ajax/', views.forgot_password_ajax),
    path('reset-password/', views.reset_password_view, name='reset_password'),
]
