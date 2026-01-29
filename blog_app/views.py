from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from .forms import UserRegisterForm, PostForm, CommentForm

def home(request):
    posts = Post.objects.filter(status='published').order_by('-publish_date')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog_app/home.html', context)


def category_posts(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    posts = Post.objects.filter(category=category, status='published').order_by('-publish_date')
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog_app/category_posts.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(approved=True)
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Your comment has been added!')
                return redirect('post_detail', pk=post.pk)
        else:
            messages.warning(request, 'Please login to comment.')
            return redirect('login')
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog_app/post_detail.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'blog_app/post_form.html', {'form': form, 'title': 'Create Post'})

@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user != post.author:
        messages.error(request, 'You are not authorized to edit this post.')
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog_app/post_form.html', {'form': form, 'title': 'Update Post'})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user != post.author:
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    
    return render(request, 'blog_app/confirm_delete.html', {'post': post})

# def category_posts(request, category_id):
#     category = get_object_or_404(Category, pk=category_id)
#     posts = Post.objects.filter(category=category, status='published').order_by('-publish_date')
    
#     context = {
#         'category': category,
#         'posts': posts,
#     }
#     return render(request, 'blog_app/category_posts.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'blog_app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'blog_app/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')

@login_required
def user_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-publish_date')
    return render(request, 'blog_app/user_posts.html', {'posts': posts})

import os
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post


@login_required
def download_post_image(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 🔐 Only author can download
    if post.author != request.user:
        return HttpResponse("You are not allowed to download this file.", status=403)

    if not post.image:
        raise Http404("No image found")

    file_path = post.image.path
    file_name = os.path.basename(file_path)

    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response