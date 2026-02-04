from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from datetime import timedelta
from . models import *
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sessions.models import Session
import re
from uuid import UUID

MAX_ATTEMPTS = 5
LOCKOUT_TIME = 3600  # 1 hour


@never_cache
def superuser_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        # ---------------- VALIDATION ----------------
        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return render(request, "admin_login.html")

        # Prevent links in username/password
        if "http://" in username or "https://" in username or "<" in username or ">" in username:
            messages.error(request, "Invalid characters in username.")
            return render(request, "admin_login.html")

        if "http://" in password or "https://" in password or "<" in password or ">" in password:
            messages.error(request, "Invalid characters in password.")
            return render(request, "admin_login.html")

        # Allow only safe username characters (letters, numbers, @/./+/-/_)
        if not re.match(r'^[\w.@+-]+$', username):
            messages.error(request, "Username contains invalid characters.")
            return render(request, "admin_login.html")

        # ---------------- RATE LIMITING ----------------
        attempts_key = f"login_attempts_{username}"
        block_key = f"login_block_{username}"

        if cache.get(block_key):
            messages.error(
                request,
                "Too many failed login attempts. Try again after 1 hour."
            )
            return render(request, "admin_login.html")

        # ---------------- AUTHENTICATION ----------------
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            # Successful login → reset attempts
            cache.delete(attempts_key)
            cache.delete(block_key)
            login(request, user)
            return redirect("admin-dashboard")
        else:
            # Failed attempt
            attempts = cache.get(attempts_key, 0) + 1
            cache.set(attempts_key, attempts, LOCKOUT_TIME)

            remaining = MAX_ATTEMPTS - attempts

            if attempts >= MAX_ATTEMPTS:
                cache.set(block_key, True, LOCKOUT_TIME)
                messages.error(
                    request,
                    "Account locked due to multiple failed login attempts. Try again after 1 hour."
                )
            else:
                messages.error(
                    request,
                    f"Invalid credentials. {remaining} attempt(s) remaining."
                )

    return render(request, "admin_login.html")

# @never_cache
# @login_required(login_url="/login/")
# @user_passes_test(lambda u: u.is_superuser)
# def admin_dashboard(request):
#
#     if request.method == "POST":
#         action = request.POST.get("action")
#
#         # ================= CATEGORY =================
#         if action == "add_category":
#             name = request.POST.get("category_name")
#             if name:
#                 Category.objects.get_or_create(name=name)
#                 messages.success(request, "Category added successfully")
#
#         elif action == "edit_category":
#             category_id = request.POST.get("category_id")
#             name = request.POST.get("category_name")
#             category = get_object_or_404(Category, id=category_id)
#             category.name = name
#             category.save()
#             messages.success(request, "Category updated successfully")
#
#         elif action == "delete_category":
#             category_id = request.POST.get("category_id")
#             Category.objects.filter(id=category_id).delete()
#             messages.success(request, "Category deleted successfully")
#
#         # ================= STORY =================
#         elif action == "add_story":
#             link = request.POST.get("link")
#             description = request.POST.get("description")
#             media = request.FILES.get("media")
#
#             if not media:
#                 messages.error(request, "Image or video is required")
#                 return redirect("admin-dashboard")
#
#             story = Story(link=link, description=description)
#
#             if media.content_type.startswith("image"):
#                 story.image = media
#             elif media.content_type.startswith("video"):
#                 story.video = media
#             else:
#                 messages.error(request, "Unsupported file type")
#                 return redirect("admin-dashboard")
#
#             story.save()
#             messages.success(request, "Story added successfully")
#
#         return redirect("admin-dashboard")
#
#     # ================= GET =================
#     categories = Category.objects.order_by("-id")
#     stories = Story.objects.order_by("-created_at")
#
#     # Show all posts in the news grid, no filtering by category
#     news_posts = Post.objects.order_by("-created_at")
#     all_posts = news_posts  # same as news_posts, can be used elsewhere if needed
#
#     return render(
#         request,
#         "admin_dashboard.html",
#         {
#             "categories": categories,
#             "stories": stories,
#             "news_posts": news_posts,
#             "all_posts": all_posts,
#         }
#     )

@never_cache
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):

    if request.method == "POST":
        action = request.POST.get("action")

        # ================= CATEGORY =================
        if action == "add_category":
            name = request.POST.get("category_name")
            if name:
                Category.objects.get_or_create(name=name)
                messages.success(request, "Category added successfully")

        elif action == "edit_category":
            category_id = request.POST.get("category_id")
            name = request.POST.get("category_name")
            category = get_object_or_404(Category, id=category_id)
            category.name = name
            category.save()
            messages.success(request, "Category updated successfully")

        elif action == "delete_category":
            category_id = request.POST.get("category_id")
            Category.objects.filter(id=category_id).delete()
            messages.success(request, "Category deleted successfully")

        # ================= STORY =================
        elif action == "add_story":
            link = request.POST.get("link")
            description = request.POST.get("description")
            media = request.FILES.get("media")

            if not media:
                messages.error(request, "Image or video is required")
                return redirect("admin-dashboard")

            story = Story(link=link, description=description)

            if media.content_type.startswith("image"):
                story.image = media
            elif media.content_type.startswith("video"):
                story.video = media
            else:
                messages.error(request, "Unsupported file type")
                return redirect("admin-dashboard")

            story.save()
            messages.success(request, "Story added successfully")

        return redirect("admin-dashboard")

    # ================= GET =================
    categories = Category.objects.order_by("-id")
    stories = Story.objects.order_by("-created_at")

    news_posts = Post.objects.order_by("-created_at")
    all_posts = news_posts

    # ================= USERS LIST =================

    # all normal users (Signup model)
    signups = Signup.objects.order_by("-created_at")

    # active sessions
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    active_user_ids = set()

    for session in active_sessions:
        data = session.get_decoded()
        uid = data.get("_auth_user_id")
        if uid:
            active_user_ids.add(int(uid))

    # map Django users (google + local)
    django_users = {
        u.username: u
        for u in User.objects.filter(
            username__in=signups.values_list("username", flat=True),
            is_superuser=False
        ).select_related("profile")
    }

    # final users list with status
    users = []
    for signup in signups:
        dj_user = django_users.get(signup.username)

        is_active = False
        last_login = None

        if dj_user:
            is_active = dj_user.id in active_user_ids
            last_login = dj_user.last_login

        users.append({
            "signup": signup,
            "is_active": is_active,
            "last_login": last_login,
            "provider": getattr(dj_user.profile, "provider", "local") if dj_user else "local",
        })

    # active users first
    users.sort(key=lambda x: x["is_active"], reverse=True)

    return render(
        request,
        "admin_dashboard.html",
        {
            "categories": categories,
            "stories": stories,
            "news_posts": news_posts,
            "all_posts": all_posts,

            # 👇 users list (final)
            "users": users,
        }
    )



@login_required
@require_POST
def edit_news(request, pk):
    try:
        post = get_object_or_404(Post, pk=pk)

        title = request.POST.get("title")
        description = request.POST.get("description")
        category_id = request.POST.get("category")

        if not title or not description or not category_id:
            return JsonResponse({"error": "Missing required fields."}, status=400)

        post.title = title
        post.description = description
        post.category_id = category_id

        # Handle media uploads
        if request.FILES.get("media"):
            file = request.FILES["media"]
            if file.content_type.startswith("image"):
                post.image = file
                post.video = None  # Clear old video
            elif file.content_type.startswith("video"):
                post.video = file
                post.image = None  # Clear old image

        post.save()

        media_type = None
        media_url = None
        if post.image:
            media_type = "image"
            media_url = post.image.url
        elif post.video:
            media_type = "video"
            media_url = post.video.url

        return JsonResponse({
            "title": post.title,
            "description": post.description,
            "media_type": media_type,
            "media_url": media_url,
        })

    except Exception as e:
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def delete_news(request):
    ids = request.POST.get("ids", "")

    if ids:
        Post.objects.filter(id__in=ids.split(",")).delete()

    return redirect("admin-dashboard")

# views.py
@require_POST
@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_story(request):
    ids = request.POST.get("ids", "")
    if ids:
        Story.objects.filter(id__in=ids.split(",")).delete()
    return redirect("admin-dashboard")



@never_cache
def admin_logout(request):
    logout(request)
    return redirect("login")

def user_logout(request):
    logout(request)
    return redirect(request.GET.get('next', '/'))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_post(request):
    if request.method == "POST":
        title = request.POST.get("title")
        category_id = request.POST.get("category")
        description = request.POST.get("description")
        media = request.FILES.get("media")

        if not title or not category_id:
            messages.error(request, "Title and category are required")
            return redirect("admin-dashboard")

        category = Category.objects.filter(id=category_id).first()
        if not category:
            messages.error(request, "Invalid category selected")
            return redirect("admin-dashboard")

        post = Post(
            title=title,
            category=category,
            description=description
        )

        if media:
            if media.content_type.startswith("image"):
                post.image = media
            elif media.content_type.startswith("video"):
                post.video = media

        post.save()
        messages.success(request, "Post published successfully")
        return redirect("admin-dashboard")

def base(request):
    """
    Base view to render common context:
    - All categories (for filters/navigation)
    - Media types (Image / Video)
    - Logged-in user profile (if any)
    """
    categories = Category.objects.all().order_by("name")
    media_types = ["Image", "Video"]

    profile = None
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)

    context = {
        "categories": categories,
        "media_types": media_types,
        "profile": profile,   # 👈 added
    }

    return render(request, "base.html", context)

import random

def index(request):
    posts = (
        Post.objects
        .select_related("category")
        .order_by("-created_at")
    )

    stories = Story.objects.order_by("-created_at")
    categories = Category.objects.all()

    # --------------------
    # Filters
    # --------------------
    category_id = request.GET.get("category")
    media_type = request.GET.get("media")
    date = request.GET.get("date")

    # ✅ UUID-safe category filter
    if category_id:
        try:
            UUID(category_id)
            posts = posts.filter(category_id=category_id)
        except ValueError:
            pass  # ignore invalid UUIDs

    if media_type == "Image":
        posts = posts.filter(image__isnull=False).exclude(image="")
    elif media_type == "Video":
        posts = posts.filter(video__isnull=False).exclude(video="")

    if date:
        posts = posts.filter(created_at__date=date)

    # --------------------
    # BIG POST POSITIONS
    # --------------------
    total = posts.count()

    possible_indexes = list(range(0, total, 6))
    big_indexes = random.sample(
        possible_indexes,
        min(3, len(possible_indexes))
    )

    profile = (
        getattr(request.user, "profile", None)
        if request.user.is_authenticated
        else None
    )

    return render(request, "index.html", {
        "posts": posts,
        "stories": stories,
        "categories": categories,
        "profile": profile,
        "big_indexes": big_indexes,
    })


def newsview(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    categories = Category.objects.all().order_by("name")

    comments = (
        Comment.objects
        .filter(post=post)
        .select_related("user", "user__profile")
        .order_by("-created_at")
    )

    # ✅ RELATED NEWS (same category, exclude current post)
    related_posts = (
        Post.objects
        .filter(category=post.category)
        .exclude(id=post.id)
        .order_by("-created_at")[:10]
    )

    profile = (
        getattr(request.user, "profile", None)
        if request.user.is_authenticated
        else None
    )

    return render(request, "newsview.html", {
        "post": post,
        "categories": categories,
        "media_types": ["Image", "Video"],
        "profile": profile,
        "comments": comments,
        "related_posts": related_posts,
    })


# Patterns
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]{3,30}$')  # letters, numbers, _.- allowed
EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
SQL_PATTERN = re.compile(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC|UNION)\b', re.IGNORECASE)
MAX_USERNAME = 30
MAX_PASSWORD = 128


# ---------------- SIGNUP ----------------
@require_POST
@csrf_exempt
def signup_ajax(request):
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")
    confirm = request.POST.get("confirm", "")

    # 1️⃣ Check required fields
    if not all([username, email, password, confirm]):
        return JsonResponse({"success": False, "error": "All fields are required"})

    # 2️⃣ Validate username
    if not USERNAME_PATTERN.match(username):
        return JsonResponse({"success": False, "error": "Invalid username. Use 3-30 letters, numbers, _.- only."})
    if SQL_PATTERN.search(username):
        return JsonResponse({"success": False, "error": "Invalid username content."})

    # 3️⃣ Validate email
    if not EMAIL_PATTERN.match(email):
        return JsonResponse({"success": False, "error": "Invalid email address"})
    if SQL_PATTERN.search(email):
        return JsonResponse({"success": False, "error": "Invalid email content."})

    # 4️⃣ Validate password
    if password != confirm:
        return JsonResponse({"success": False, "error": "Passwords do not match"})
    if len(password) < 6 or len(password) > MAX_PASSWORD:
        return JsonResponse({"success": False, "error": "Password must be 6-128 characters"})

    # 5️⃣ Check duplicates
    if Signup.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "error": "Username already exists"})
    if Signup.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "error": "Email already registered"})

    # 6️⃣ Create Signup entry
    signup = Signup.objects.create(
        username=username,
        email=email,
        password=make_password(password)
    )

    # 7️⃣ Create Django User
    user, created = User.objects.get_or_create(
        username=signup.username,
        defaults={"email": signup.email}
    )
    if created:
        user.set_password(password)
        user.save()

    # 8️⃣ Create Profile
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"email": signup.email, "provider": "local"}
    )

    # 9️⃣ Auto-login
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse({"success": True})


# ---------------- LOGIN ----------------
@require_POST
@csrf_exempt
def login_ajax(request):
    username_or_email = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    if not username_or_email or not password:
        return JsonResponse({"success": False, "error": "All fields are required"})

    # Validate input lengths
    if len(username_or_email) > 100 or len(password) > MAX_PASSWORD:
        return JsonResponse({"success": False, "error": "Invalid input length"})
    if SQL_PATTERN.search(username_or_email):
        return JsonResponse({"success": False, "error": "Invalid characters in username/email"})

    # Find user
    try:
        signup = Signup.objects.get(username=username_or_email)
    except Signup.DoesNotExist:
        try:
            signup = Signup.objects.get(email=username_or_email)
        except Signup.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid credentials"})

    # Check password
    if not check_password(password, signup.password):
        return JsonResponse({"success": False, "error": "Invalid credentials"})

    # Get or create Django User and Profile
    user, created = User.objects.get_or_create(username=signup.username, defaults={"email": signup.email})
    if created:
        user.set_password(password)
        user.save()
    profile, _ = Profile.objects.get_or_create(user=user, defaults={"email": signup.email, "provider": "local"})

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse({"success": True})


# ---------------- FORGOT PASSWORD ----------------
@require_POST
@csrf_exempt
def forgot_password_ajax(request):
    username_or_email = request.POST.get("username", "").strip()
    if not username_or_email:
        return JsonResponse({"success": False, "error": "Please enter username or email"})

    if len(username_or_email) > 100 or SQL_PATTERN.search(username_or_email):
        return JsonResponse({"success": False, "error": "Invalid input"})

    # Find user
    try:
        user = Signup.objects.get(username=username_or_email)
    except Signup.DoesNotExist:
        try:
            user = Signup.objects.get(email=username_or_email)
        except Signup.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"})

    # Generate reset token and send email
    token = user.generate_reset_token()
    reset_link = f"http://127.0.0.1:8000/reset-password/{token}/"

    try:
        send_mail(
            subject="Reset Your Password",
            message=f"Hello {user.username},\n\nClick this link to reset your password:\n{reset_link}\n\nThis link expires in 1 hour.",
            from_email="News App <no-reply@smtp-brevo.com>",
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Failed to send email: {str(e)}"})

    return JsonResponse({"success": True, "message": "Password reset link sent to your email."})

def reset_password_view(request, token):
    user = Signup.objects.filter(
        reset_token=token,
        reset_token_expiry__gt=timezone.now()
    ).first()

    if not user:
        return render(request, "reset_password.html", {
            "error": "Invalid or expired reset link"
        })

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if not password or password != confirm:
            return render(request, "reset_password.html", {
                "error": "Passwords do not match"
            })

        user.password = make_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.save()

        return redirect("login_page")

    return render(request, "reset_password.html")


# Patterns for validation
URL_PATTERN = re.compile(r'https?://\S+', re.IGNORECASE)
SQL_PATTERN = re.compile(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC|UNION)\b', re.IGNORECASE)
MAX_COMMENT_LENGTH = 500


@login_required
@require_POST
def add_comment(request):
    post_id = request.POST.get("post_id")
    text = request.POST.get("text", "").strip()
    audio = request.FILES.get("audio")
    parent_id = request.POST.get("parent_id")

    if not post_id:
        return JsonResponse({"error": "Post ID missing"}, status=400)

    if not text and not audio:
        return JsonResponse({"error": "Empty comment"}, status=400)

    post = get_object_or_404(Post, id=post_id)

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.get_full_name(),
            "email": request.user.email,
        }
    )

    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id)

    comment = Comment.objects.create(
        user=request.user,
        post=post,
        parent=parent,
        text=text,
        audio=audio
    )

    return JsonResponse({
        "id": comment.id,
        "text": comment.text,
        "audio": comment.audio.url if comment.audio else "",
        "username": request.user.username,
        "avatar": profile.avatar or "/static/avatar.png",
        "parent_id": parent.id if parent else None,
        "likes_count": 0
    })


@login_required
@require_POST
def like_comment(request):
    comment_id = request.POST.get("comment_id")
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)  # unlike
    else:
        comment.likes.add(request.user)     # like

    return JsonResponse({
        "likes_count": comment.likes.count()
    })


@login_required
@require_POST
def delete_comment(request):
    comment_id = request.POST.get("comment_id")
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    comment.delete()
    return JsonResponse({"success": True})

@login_required
@require_POST
def toggle_comment_like(request):
    comment = get_object_or_404(Comment, id=request.POST.get("comment_id"))

    like, created = CommentLike.objects.get_or_create(
        user=request.user, comment=comment
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "count": comment.likes.count()
    })

@login_required
@require_POST
def toggle_post_like(request):
    post = get_object_or_404(Post, id=request.POST.get("post_id"))

    like, created = PostLike.objects.get_or_create(
        user=request.user, post=post
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "count": post.likes.count()
    })

@login_required
def post_like(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        # Check if user already liked
        liked = PostLike.objects.filter(post=post, user=request.user).first()
        if liked:
            liked.delete()
            user_liked = False
        else:
            PostLike.objects.create(post=post, user=request.user)
            user_liked = True

        # Return updated like count
        likes_count = post.likes.count()  # this uses related_name="likes"
        return JsonResponse({"likes_count": likes_count, "user_liked": user_liked})

    return JsonResponse({"error": "Invalid request"}, status=400)

@never_cache
@login_required
def profile_view(request):
    categories = Category.objects.all()
    posts = Post.objects.filter(user=request.user).order_by("-id")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category_id = request.POST.get("category")
        description = request.POST.get("description", "").strip()
        media = request.FILES.get("media")

        if not title or not category_id:
            messages.error(request, "Title and category are required.")
            return redirect("profile")

        image = video = None

        if media:
            if media.content_type.startswith("image/"):
                image = media
            elif media.content_type.startswith("video/"):
                video = media
            else:
                messages.error(request, "Upload a valid image or video.")
                return redirect("profile")

        category = get_object_or_404(Category, id=category_id)

        Post.objects.create(
            title=title,
            category=category,
            description=description,
            image=image,
            video=video,
            user=request.user
        )

        messages.success(request, "Post uploaded successfully!")
        return redirect("profile")

    return render(request, "profile.html", {
        "categories": categories,
        "posts": posts,
    })

@login_required
@require_POST
def edit_post_ajax(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    post.title = request.POST.get("title")
    post.description = request.POST.get("description")

    media = request.FILES.get("media")
    if media:
        if media.content_type.startswith("image/"):
            post.image = media
            post.video = None
        elif media.content_type.startswith("video/"):
            post.video = media
            post.image = None

    post.save()
    return JsonResponse({"success": True})

@login_required
@require_POST
def delete_post_ajax(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return JsonResponse({"success": True})
