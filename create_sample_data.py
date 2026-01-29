#!/usr/bin/env python
"""
SAMPLE DATA GENERATOR FOR DJANGO BLOG
=====================================
This script populates your database with realistic sample data for testing.
Run with: python create_sample_data.py

Features:
- Creates sample categories
- Creates sample users
- Creates sample blog posts with rich content
- Creates sample comments
- Sets up admin user
- Creates images placeholder

Requirements: Pillow (for image handling)
"""

import os
import sys
import django
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.files import File

# Add project root to Python path
sys.path.append('.')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Failed to setup Django: {e}")
    print("Make sure you're in the project root directory with manage.py")
    sys.exit(1)

from blog_app.models import Category, Post, Comment
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont
import io

# ============================================
# CONFIGURATION
# ============================================
class Config:
    NUM_CATEGORIES = 10
    NUM_USERS = 5
    NUM_POSTS = 50
    MAX_COMMENTS_PER_POST = 15
    SAMPLE_IMAGES = True
    CLEAR_EXISTING_DATA = False  # Set to True to wipe existing data first
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    ADMIN_EMAIL = 'admin@blog.com'

# ============================================
# SAMPLE DATA
# ============================================
SAMPLE_CATEGORIES = [
    "Technology & AI",
    "Science & Nature", 
    "Art & Design",
    "Travel & Adventure",
    "Food & Cooking",
    "Health & Fitness",
    "Education & Learning",
    "Business & Finance",
    "Entertainment & Movies",
    "Sports & Games",
    "Lifestyle & Fashion",
    "Music & Podcasts",
    "Programming & Coding",
    "Photography",
    "Gardening & DIY"
]

SAMPLE_USERNAMES = [
    "alex_johnson", "sarah_miller", "mike_chen", "lisa_wong", 
    "david_smith", "emma_wilson", "james_brown", "sophia_garcia",
    "robert_taylor", "olivia_davis"
]

SAMPLE_FIRST_NAMES = ["Alex", "Sarah", "Mike", "Lisa", "David", "Emma", "James", "Sophia", "Robert", "Olivia"]
SAMPLE_LAST_NAMES = ["Johnson", "Miller", "Chen", "Wong", "Smith", "Wilson", "Brown", "Garcia", "Taylor", "Davis"]

SAMPLE_POST_TITLES = [
    # Technology
    "The Future of Artificial Intelligence in 2024",
    "Understanding Blockchain: Beyond Cryptocurrency",
    "How to Get Started with Machine Learning",
    "The Rise of Quantum Computing",
    "10 Programming Languages to Learn This Year",
    
    # Science
    "Climate Change: What We Can Do Today",
    "The Mysteries of Deep Sea Exploration",
    "Renewable Energy Solutions for Homes",
    "The Science Behind Good Sleep",
    "Understanding Black Holes and Space-Time",
    
    # Travel
    "Top 10 Travel Destinations for 2024",
    "Budget Travel Tips for Backpackers",
    "Sustainable Tourism: How to Travel Responsibly",
    "Hidden Gems in Southeast Asia",
    "A Guide to Solo Travel Safety",
    
    # Food
    "Easy Meal Prep Recipes for Busy Professionals",
    "The Art of Sourdough Bread Making",
    "10 Healthy Smoothie Recipes",
    "Exploring International Cuisines at Home",
    "Vegetarian Cooking for Beginners",
    
    # Health
    "Morning Routines of Successful People",
    "Yoga for Stress Relief: A Beginner's Guide",
    "Nutrition Myths Debunked",
    "Home Workouts Without Equipment",
    "Mental Health Tips for Remote Workers",
    
    # Business
    "Startup Success Stories from 2023",
    "Digital Marketing Strategies for Small Businesses",
    "How to Invest in Stocks for Beginners",
    "Remote Work Best Practices",
    "Building a Personal Brand Online",
    
    # Entertainment
    "Best Movies and TV Shows of 2024",
    "The Evolution of Video Game Graphics",
    "Music Production Tips for Beginners",
    "Behind the Scenes of Hollywood",
    "The Impact of Streaming Services",
    
    # Lifestyle
    "Minimalist Living: How to Declutter Your Life",
    "Sustainable Living Tips for Everyday",
    "Gardening Basics for Apartment Dwellers",
    "DIY Home Improvement Projects",
    "Digital Detox: Why and How"
]

SAMPLE_CONTENT_PARAGRAPHS = [
    "In today's rapidly evolving world, technology continues to reshape how we live and work. From artificial intelligence to renewable energy, innovations are driving progress at an unprecedented pace.",
    
    "The importance of sustainable practices cannot be overstated. As we face global challenges like climate change, individual actions combined with systemic changes can make a significant difference.",
    
    "Learning is a lifelong journey that extends far beyond formal education. Whether you're picking up a new skill or deepening existing knowledge, the process of learning itself brings immense satisfaction.",
    
    "Travel opens our minds to new cultures, perspectives, and ways of life. Even local exploration can provide valuable insights and refresh our outlook on daily routines.",
    
    "Health is not just the absence of disease, but a state of complete physical, mental, and social well-being. Small, consistent habits often lead to the most significant long-term benefits.",
    
    "Creativity manifests in countless forms, from artistic expression to problem-solving in business. Cultivating a creative mindset helps us navigate complex challenges with innovative solutions.",
    
    "Community and connection form the foundation of meaningful lives. Building strong relationships and contributing to our communities creates a sense of purpose and belonging.",
    
    "Financial literacy is an essential skill for navigating modern life. Understanding basic principles of budgeting, saving, and investing can provide security and open up opportunities.",
    
    "Food is more than just sustenance—it's culture, connection, and creativity. Learning to cook and appreciate diverse cuisines enriches our lives in countless ways.",
    
    "Personal growth requires intentional reflection and action. Setting goals, developing habits, and embracing challenges helps us become the best versions of ourselves."
]

SAMPLE_COMMENTS = [
    "Great article! Really enjoyed reading this.",
    "Thanks for sharing these insights.",
    "I have a different perspective on this topic...",
    "Could you elaborate more on the second point?",
    "This has been really helpful for my project.",
    "I've been looking for information like this for weeks!",
    "Interesting take on the subject.",
    "The examples really helped me understand the concept.",
    "What are your sources for this information?",
    "Looking forward to the next article in this series.",
    "This changed my perspective completely.",
    "Practical and actionable advice. Thank you!",
    "I tried this approach and it worked wonderfully.",
    "More people need to read this.",
    "Clear and concise explanation. Well done!"
]

# ============================================
# HELPER FUNCTIONS
# ============================================
def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def generate_random_text(paragraphs=3):
    """Generate random content from sample paragraphs"""
    return "\n\n".join(random.sample(SAMPLE_CONTENT_PARAGRAPHS, min(paragraphs, len(SAMPLE_CONTENT_PARAGRAPHS))))

def generate_lorem_ipsum(words=100):
    """Generate Lorem Ipsum text"""
    lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    words_list = lorem.split()
    result = []
    for _ in range(words):
        result.append(random.choice(words_list))
    return " ".join(result)

def create_sample_image(post_title, width=800, height=400):
    """Create a sample image for posts"""
    try:
        # Create a new image with a random background color
        bg_color = (
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        
        image = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(image)
        
        # Try to add text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
            
            # Add title text
            text = post_title[:30] + "..." if len(post_title) > 30 else post_title
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
        except:
            pass  # Skip text if font fails
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
    except Exception as e:
        print(f"⚠️  Could not create image: {e}")
        return None

def clear_existing_data():
    """Clear existing data if configured"""
    if Config.CLEAR_EXISTING_DATA:
        print_header("CLEARING EXISTING DATA")
        try:
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Category.objects.all().delete()
            
            # Delete regular users but keep superusers
            User.objects.filter(is_superuser=False).delete()
            
            print("✅ Cleared existing data")
        except Exception as e:
            print(f"⚠️  Error clearing data: {e}")

# ============================================
# MAIN DATA CREATION FUNCTIONS
# ============================================
def create_admin_user():
    """Create or get admin user"""
    print_header("ADMIN USER")
    
    try:
        admin_user, created = User.objects.get_or_create(
            username=Config.ADMIN_USERNAME,
            defaults={
                'email': Config.ADMIN_EMAIL,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password(Config.ADMIN_PASSWORD)
            admin_user.save()
            print(f"✅ Created admin user: {Config.ADMIN_USERNAME}/{Config.ADMIN_PASSWORD}")
        else:
            # Ensure admin has correct permissions
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password(Config.ADMIN_PASSWORD)
            admin_user.save()
            print(f"✅ Updated existing admin user")
        
        return admin_user
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return None

def create_sample_users():
    """Create sample regular users"""
    print_header("SAMPLE USERS")
    
    users = []
    
    # Get or create admin first
    admin_user = create_admin_user()
    if admin_user:
        users.append(admin_user)
    
    # Create regular users
    for i in range(min(Config.NUM_USERS, len(SAMPLE_USERNAMES))):
        username = SAMPLE_USERNAMES[i]
        first_name = SAMPLE_FIRST_NAMES[i % len(SAMPLE_FIRST_NAMES)]
        last_name = SAMPLE_LAST_NAMES[i % len(SAMPLE_LAST_NAMES)]
        email = f"{username}@example.com"
        password = f"{username}123"
        
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                print(f"✅ Created user: {username}/{password} ({first_name} {last_name})")
            else:
                print(f"⏩ User already exists: {username}")
            
            users.append(user)
        except Exception as e:
            print(f"❌ Failed to create user {username}: {e}")
    
    print(f"\nTotal users: {len(users)}")
    return users

def create_sample_categories():
    """Create sample categories"""
    print_header("SAMPLE CATEGORIES")
    
    categories = []
    
    for i in range(min(Config.NUM_CATEGORIES, len(SAMPLE_CATEGORIES))):
        cat_name = SAMPLE_CATEGORIES[i]
        
        try:
            category, created = Category.objects.get_or_create(name=cat_name)
            
            if created:
                print(f"✅ Created category: {cat_name}")
            else:
                print(f"⏩ Category already exists: {cat_name}")
            
            categories.append(category)
        except Exception as e:
            print(f"❌ Failed to create category {cat_name}: {e}")
    
    # If no categories were created, create at least one
    if not categories:
        category = Category.objects.create(name="General")
        categories.append(category)
        print(f"✅ Created default category: General")
    
    print(f"\nTotal categories: {len(categories)}")
    return categories

def create_sample_posts(users, categories):
    """Create sample blog posts"""
    print_header("SAMPLE BLOG POSTS")
    
    if not categories:
        print("❌ No categories available. Cannot create posts.")
        return []
    
    posts = []
    
    for i in range(min(Config.NUM_POSTS, len(SAMPLE_POST_TITLES))):
        title = SAMPLE_POST_TITLES[i]
        author = random.choice(users)
        category = random.choice(categories)
        
        # Generate content - mix of sample paragraphs and lorem ipsum
        content = generate_random_text(paragraphs=random.randint(2, 5))
        content += "\n\n" + generate_lorem_ipsum(words=random.randint(50, 200))
        
        # Random status (80% published, 20% draft)
        status = 'published' if random.random() < 0.8 else 'draft'
        
        # Random publish date (from 30 days ago to now)
        publish_date = timezone.now() - timedelta(days=random.randint(0, 30))
        
        try:
            post = Post.objects.create(
                title=title,
                content=content,
                author=author,
                category=category,
                status=status,
                publish_date=publish_date
            )
            
            # Add image if enabled
            if Config.SAMPLE_IMAGES:
                try:
                    img_bytes = create_sample_image(title)
                    if img_bytes:
                        post.image.save(
                            f"sample_image_{post.id}.jpg",
                            File(img_bytes),
                            save=True
                        )
                        print(f"✅ Created post with image: '{title}'")
                    else:
                        print(f"✅ Created post: '{title}'")
                except Exception as img_error:
                    print(f"✅ Created post (no image): '{title}' - Image error: {img_error}")
            else:
                print(f"✅ Created post: '{title}'")
            
            posts.append(post)
            
        except Exception as e:
            print(f"❌ Failed to create post '{title}': {e}")
    
    print(f"\nTotal posts created: {len(posts)}")
    return posts

def create_sample_comments(posts, users):
    """Create sample comments for posts"""
    print_header("SAMPLE COMMENTS")
    
    if not posts:
        print("❌ No posts available. Cannot create comments.")
        return 0
    
    total_comments = 0
    
    for post in posts:
        # Random number of comments per post (0 to MAX_COMMENTS_PER_POST)
        num_comments = random.randint(0, Config.MAX_COMMENTS_PER_POST)
        
        for _ in range(num_comments):
            author = random.choice(users)
            content = random.choice(SAMPLE_COMMENTS)
            
            # Add some variation to comments
            if random.random() < 0.3:  # 30% chance to have longer comment
                content += " " + generate_lorem_ipsum(words=random.randint(10, 30))
            
            # Random comment date (after post publish date, up to now)
            comment_date = post.publish_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23)
            )
            
            try:
                comment = Comment.objects.create(
                    post=post,
                    author=author,
                    content=content,
                    approved=random.random() < 0.9,  # 90% approved
                    created_date=comment_date
                )
                total_comments += 1
            except Exception as e:
                print(f"❌ Failed to create comment: {e}")
    
    print(f"Total comments created: {total_comments}")
    return total_comments

def print_summary(users, categories, posts, comment_count):
    """Print final summary"""
    print_header("DATA GENERATION SUMMARY")
    
    print("✅ DATA GENERATED SUCCESSFULLY!")
    print("\n📊 STATISTICS:")
    print(f"   Users: {len(users)}")
    print(f"   Categories: {len(categories)}")
    print(f"   Posts: {len(posts)}")
    print(f"   Comments: {comment_count}")
    
    # Calculate published vs draft
    published_posts = Post.objects.filter(status='published').count()
    draft_posts = Post.objects.filter(status='draft').count()
    print(f"   Published posts: {published_posts}")
    print(f"   Draft posts: {draft_posts}")
    
    # Calculate posts per category
    print("\n📈 POSTS PER CATEGORY:")
    for category in categories:
        count = category.post_set.count()
        print(f"   {category.name}: {count} posts")
    
    # Calculate posts per user
    print("\n👥 POSTS PER USER:")
    for user in users:
        count = user.blog_posts.count()
        if count > 0:
            print(f"   {user.username}: {count} posts")
    
    print("\n🔑 ADMIN CREDENTIALS:")
    print(f"   URL: http://127.0.0.1:8000/admin/")
    print(f"   Username: {Config.ADMIN_USERNAME}")
    print(f"   Password: {Config.ADMIN_PASSWORD}")
    
    print("\n👤 SAMPLE USER CREDENTIALS (all passwords are 'username123'):")
    for user in users:
        if user.username != Config.ADMIN_USERNAME:
            print(f"   {user.username} / {user.username}123")
    
    print("\n🚀 QUICK ACTIONS:")
    print("   1. Run server: python manage.py runserver")
    print("   2. Visit blog: http://127.0.0.1:8000/")
    print("   3. Admin panel: http://127.0.0.1:8000/admin/")
    print("   4. Test categories: http://127.0.0.1:8000/category/1/")
    
    print("\n🎉 Your Django blog is now populated with sample data!")

def main():
    """Main function to run the sample data generation"""
    print("\n" + "="*70)
    print(" DJANGO BLOG - SAMPLE DATA GENERATOR")
    print("="*70)
    print(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Project: django-blog")
    print("="*70)
    
    # Confirm with user
    print("\n⚠️  This script will create sample data in your database.")
    print("   Existing data might be modified.")
    
    response = input("\nContinue? (y/n): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    # Clear existing data if configured
    clear_existing_data()
    
    # Create data
    users = create_sample_users()
    categories = create_sample_categories()
    posts = create_sample_posts(users, categories)
    comment_count = create_sample_comments(posts, users)
    
    # Print summary
    print_summary(users, categories, posts, comment_count)

def quick_setup():
    """Quick setup without prompts"""
    print("Running quick setup...")
    Config.CLEAR_EXISTING_DATA = False
    
    users = create_sample_users()
    categories = create_sample_categories()
    posts = create_sample_posts(users, categories)
    comment_count = create_sample_comments(posts, users)
    
    print("\n✅ Quick setup complete!")
    print(f"Created: {len(users)} users, {len(categories)} categories, {len(posts)} posts")
    print(f"Admin: {Config.ADMIN_USERNAME}/{Config.ADMIN_PASSWORD}")

if __name__ == "__main__":
    try:
        # Check for command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--quick":
            quick_setup()
        else:
            main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Make sure you're in the project root directory")
        print("   2. Run migrations: python manage.py migrate")
        print("   3. Install Pillow: pip install Pillow")
        print("   4. Check Django settings")