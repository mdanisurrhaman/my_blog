#!/usr/bin/env python
"""
CHECK CATEGORIES DEBUG SCRIPT
=============================
This script checks all category-related issues in your Django blog project.
Run with: python check_categories.py
"""

import os
import sys
import django
from datetime import datetime

# Add project root to Python path
sys.path.append('.')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
try:
    django.setup()
except Exception as e:
    print(f"❌ Failed to setup Django: {e}")
    print("Make sure you're in the project root directory with manage.py")
    sys.exit(1)

from blog_app.models import Category, Post, Comment
from django.contrib.auth.models import User
from django.db import connection
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def check_database_connection():
    """Check database connection"""
    print_header("DATABASE CONNECTION")
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_categories_table():
    """Check if categories table exists"""
    print_header("CATEGORIES TABLE")
    try:
        cursor = connection.cursor()
        # Check if table exists (MySQL)
        cursor.execute("SHOW TABLES LIKE 'blog_app_category'")
        result = cursor.fetchone()
        if result:
            print("✅ Categories table exists")
            
            # Count rows
            cursor.execute("SELECT COUNT(*) FROM blog_app_category")
            count = cursor.fetchone()[0]
            print(f"   Total categories in database: {count}")
            return True
        else:
            print("❌ Categories table does not exist!")
            return False
    except Exception as e:
        print(f"⚠️  Could not check categories table: {e}")
        # Try SQLite method
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blog_app_category'")
            result = cursor.fetchone()
            if result:
                print("✅ Categories table exists (SQLite)")
                cursor.execute("SELECT COUNT(*) FROM blog_app_category")
                count = cursor.fetchone()[0]
                print(f"   Total categories: {count}")
                return True
        except:
            pass
        return False

def list_all_categories():
    """List all categories with details"""
    print_header("ALL CATEGORIES")
    
    categories = Category.objects.all()
    total = categories.count()
    
    if total == 0:
        print("❌ No categories found in the database!")
        print("\n   Creating sample categories...")
        sample_cats = [
            "Technology", "Science", "Art & Design", 
            "Travel", "Food & Cooking", "Health & Fitness",
            "Education", "Business", "Entertainment"
        ]
        
        created = 0
        for cat_name in sample_cats:
            cat, created_flag = Category.objects.get_or_create(name=cat_name)
            if created_flag:
                created += 1
                print(f"   ✅ Created: {cat_name}")
        
        if created > 0:
            print(f"\n   Created {created} sample categories")
            categories = Category.objects.all()
            total = categories.count()
        else:
            print("   No new categories created (they may already exist)")
    
    print(f"\nTotal categories: {total}")
    
    if total > 0:
        print("\nCategory Details:")
        print("-" * 50)
        for i, cat in enumerate(categories, 1):
            post_count = cat.post_set.count()
            print(f"{i:2}. {cat.name:20} | Posts: {post_count:3} | ID: {cat.id}")
            
            # Show latest posts in this category
            if post_count > 0:
                latest = cat.post_set.order_by('-publish_date')[:3]
                for post in latest:
                    print(f"     - '{post.title[:40]}...' by {post.author}")
    
    return total

def check_posts_without_categories():
    """Check posts that don't have categories assigned"""
    print_header("POSTS WITHOUT CATEGORIES")
    
    posts_without_cat = Post.objects.filter(category__isnull=True)
    count = posts_without_cat.count()
    
    print(f"Posts without categories: {count}")
    
    if count > 0:
        print("\nPosts missing categories:")
        print("-" * 60)
        for i, post in enumerate(posts_without_cat[:10], 1):  # Show first 10
            print(f"{i:2}. ID: {post.id:4} | Title: '{post.title[:50]}...'")
            print(f"     Author: {post.author} | Status: {post.status} | Created: {post.created_date.date()}")
        
        if count > 10:
            print(f"\n   ... and {count - 10} more posts")
        
        # Offer to fix
        print("\n" + "="*60)
        print("FIX OPTIONS:")
        print("1. Assign all to 'Uncategorized' category")
        print("2. Create new category and assign all")
        print("3. Assign random existing categories")
        print("4. Skip (do nothing)")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            # Create or get 'Uncategorized' category
            uncategorized, created = Category.objects.get_or_create(name="Uncategorized")
            if created:
                print(f"✅ Created 'Uncategorized' category")
            
            updated = 0
            for post in posts_without_cat:
                post.category = uncategorized
                post.save()
                updated += 1
            
            print(f"✅ Assigned {updated} posts to 'Uncategorized' category")
            
        elif choice == '2':
            cat_name = input("Enter new category name: ").strip()
            if cat_name:
                new_cat, created = Category.objects.create(name=cat_name)
                updated = 0
                for post in posts_without_cat:
                    post.category = new_cat
                    post.save()
                    updated += 1
                print(f"✅ Created '{cat_name}' and assigned {updated} posts")
            else:
                print("❌ No category name provided")
                
        elif choice == '3':
            existing_cats = list(Category.objects.all())
            if existing_cats:
                import random
                updated = 0
                for post in posts_without_cat:
                    post.category = random.choice(existing_cats)
                    post.save()
                    updated += 1
                print(f"✅ Assigned random categories to {updated} posts")
            else:
                print("❌ No existing categories to assign")
    
    return count

def check_category_posts_distribution():
    """Check how posts are distributed among categories"""
    print_header("CATEGORY POSTS DISTRIBUTION")
    
    categories = Category.objects.all().order_by('name')
    
    if not categories.exists():
        print("No categories found")
        return
    
    total_posts = Post.objects.count()
    
    print(f"{'Category':<25} {'Posts':<6} {'%':<6} {'Avg Posts/Day':<12}")
    print("-" * 55)
    
    for cat in categories:
        posts = cat.post_set.all()
        count = posts.count()
        
        if count > 0:
            # Calculate average posts per day
            if posts.count() > 1:
                dates = sorted([p.created_date for p in posts])
                days_diff = (dates[-1] - dates[0]).days
                if days_diff > 0:
                    avg_per_day = count / days_diff
                    avg_str = f"{avg_per_day:.2f}"
                else:
                    avg_str = "N/A"
            else:
                avg_str = "N/A"
        else:
            avg_str = "N/A"
        
        percentage = (count / total_posts * 100) if total_posts > 0 else 0
        
        print(f"{cat.name:<25} {count:<6} {percentage:5.1f}% {avg_str:<12}")
    
    print("-" * 55)
    print(f"{'TOTAL':<25} {total_posts:<6} {100:5.1f}%")

def check_template_files():
    """Check if category-related template files exist"""
    print_header("TEMPLATE FILES CHECK")
    
    required_templates = [
        'blog_app/home.html',
        'blog_app/category_posts.html',
        'blog_app/post_detail.html',
        'blog_app/post_form.html',
        'base.html'
    ]
    
    missing = []
    
    for template_name in required_templates:
        try:
            get_template(template_name)
            print(f"✅ {template_name}")
        except TemplateDoesNotExist:
            print(f"❌ {template_name} - MISSING!")
            missing.append(template_name)
        except Exception as e:
            print(f"⚠️  {template_name} - Error: {e}")
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} template(s)")
        print("To create missing templates, run:")
        for template in missing:
            print(f"  touch {template.replace('blog_app/', 'blog_app/templates/blog_app/')}")
    else:
        print("\n✅ All required templates exist")

def check_views_and_urls():
    """Check if category-related views and URLs work"""
    print_header("VIEWS & URLS CHECK")
    
    from django.urls import reverse, resolve
    from blog_app import views
    
    urls_to_check = [
        ('home', 'Home page'),
        ('category_posts', 'Category posts page'),
    ]
    
    for url_name, description in urls_to_check:
        try:
            if url_name == 'category_posts':
                # Need a category ID
                if Category.objects.exists():
                    category = Category.objects.first()
                    url = reverse(url_name, args=[category.id])
                else:
                    print(f"⚠️  {description}: No categories to test")
                    continue
            else:
                url = reverse(url_name)
            
            # Check if URL resolves
            resolved = resolve(url)
            print(f"✅ {description}: {url}")
            print(f"   Resolves to: {resolved.func.__name__}")
            
        except Exception as e:
            print(f"❌ {description}: {e}")

def check_forms():
    """Check if forms handle categories correctly"""
    print_header("FORMS CHECK")
    
    from blog_app.forms import PostForm
    
    try:
        form = PostForm()
        
        # Check if category field exists
        if 'category' in form.fields:
            print("✅ PostForm has 'category' field")
            
            # Check choices
            field = form.fields['category']
            queryset = field.queryset
            if queryset is not None:
                print(f"   Category choices: {queryset.count()} options")
                
                if queryset.count() == 0:
                    print("   ⚠️  No category options available!")
            else:
                print("   ⚠️  Category field has no queryset")
        else:
            print("❌ PostForm missing 'category' field!")
            
    except Exception as e:
        print(f"❌ Error checking forms: {e}")

def generate_recommendations():
    """Generate recommendations based on findings"""
    print_header("RECOMMENDATIONS")
    
    total_categories = Category.objects.count()
    total_posts = Post.objects.count()
    posts_without_cat = Post.objects.filter(category__isnull=True).count()
    
    recommendations = []
    
    if total_categories == 0:
        recommendations.append("⚠️ Create at least 3-5 categories in Django Admin")
    
    if posts_without_cat > 0:
        recommendations.append(f"⚠️ Assign categories to {posts_without_cat} uncategorized posts")
    
    if total_posts > 0 and total_categories > 0:
        # Check if some categories have no posts
        empty_categories = Category.objects.filter(post__isnull=True).count()
        if empty_categories > 0:
            recommendations.append(f"⚠️ {empty_categories} categories have no posts")
    
    # Check if category template is being used
    if not os.path.exists("blog_app/templates/blog_app/category_posts.html"):
        recommendations.append("⚠️ Create category_posts.html template")
    
    if recommendations:
        print("Issues found:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("✅ No major issues found!")
    
    print("\nQuick fixes:")
    print("1. Create categories: python manage.py shell")
    print("   >>> from blog_app.models import Category")
    print("   >>> Category.objects.create(name='Your Category')")
    print("\n2. Fix uncategorized posts:")
    print("   >>> for post in Post.objects.filter(category__isnull=True):")
    print("   ...     post.category = Category.objects.first()")
    print("   ...     post.save()")

def export_categories_report():
    """Export categories report to file"""
    print_header("EXPORTING REPORT")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"categories_report_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        # Redirect print to file
        import io
        from contextlib import redirect_stdout
        
        f_capture = io.StringIO()
        with redirect_stdout(f_capture):
            # Re-run the checks but capture output
            print("CATEGORIES DEBUG REPORT")
            print("="*70)
            print(f"Generated: {datetime.now()}")
            print(f"Project: Django Blog")
            print("="*70)
            
            # Database info
            print("\nDATABASE INFO:")
            print(f"Categories: {Category.objects.count()}")
            print(f"Total Posts: {Post.objects.count()}")
            print(f"Posts without categories: {Post.objects.filter(category__isnull=True).count()}")
            
            # List categories
            print("\nCATEGORIES LIST:")
            for cat in Category.objects.all():
                post_count = cat.post_set.count()
                f.write(f"{cat.name}: {post_count} posts\n")
            
            # List posts without categories
            uncat_posts = Post.objects.filter(category__isnull=True)
            if uncat_posts.exists():
                f.write("\nPOSTS WITHOUT CATEGORIES:\n")
                for post in uncat_posts:
                    f.write(f"- {post.title} (ID: {post.id}, Author: {post.author})\n")
        
        f.write(f_capture.getvalue())
    
    print(f"✅ Report saved to: {filename}")
    print(f"📄 Open with: notepad {filename}")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("DJANGO BLOG - CATEGORIES DEBUG TOOL")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Project: django-blog")
    print("="*70)
    
    # Run all checks
    if not check_database_connection():
        print("\n❌ Cannot proceed without database connection")
        return
    
    check_categories_table()
    total_categories = list_all_categories()
    
    if total_categories > 0:
        check_posts_without_categories()
        check_category_posts_distribution()
        check_forms()
    else:
        print("\n⚠️  Skipping some checks because no categories exist")
    
    check_template_files()
    check_views_and_urls()
    
    generate_recommendations()
    
    # Ask if user wants to export report
    print("\n" + "="*70)
    export = input("Export detailed report to file? (y/n): ").strip().lower()
    if export == 'y':
        export_categories_report()
    
    print("\n" + "="*70)
    print("DEBUG COMPLETE")
    print("="*70)
    
    # Quick fixes prompt
    print("\nQUICK FIXES AVAILABLE:")
    print("1. Create sample data: python create_sample_data.py")
    print("2. Reset categories: python manage.py shell")
    print("3. Check admin: http://127.0.0.1:8000/admin/")
    print("4. Run server: python manage.py runserver")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()