from django.contrib import admin
from .models import Category, Post, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'publish_date']
    list_filter = ['status', 'category', 'publish_date']
    search_fields = ['title', 'content']
    date_hierarchy = 'publish_date'
    ordering = ['-publish_date']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'created_date', 'approved']
    list_filter = ['approved', 'created_date']
    search_fields = ['content', 'author__username']
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = "Approve selected comments"