from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/update/', views.update_post, name='update_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('my-posts/', views.user_posts, name='user_posts'),
    path('post/<int:pk>/download/', views.download_post_image, name='download_post_image'),

]