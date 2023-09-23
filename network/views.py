from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Profile, Comment, Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            nexturl = request.GET.get('next', '/')
            login(request, user)
            return redirect(nexturl)
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not password or password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        profile = Profile()
        profile.user = user
        profile.save()
        return HttpResponseRedirect(reverse("allposts"))
    else:
        return render(request, "network/register.html")


@login_required
def allPost(request):
    get_filter = request.GET.get("filter")
    search_query = request.GET.get("q")
    posts = Post.objects.all().order_by("-timestamp")
    if get_filter == "likes":
        posts = posts.annotate(like_count=Count("likes")).order_by("-like_count")
    else:
        posts = posts.annotate(comment_count=Count("comments")).order_by(
            "-comment_count"
        )
    if search_query:
        posts = list(filter(lambda post: search_query in post.post, posts))
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, "network/allpost.html", {"posts": posts})


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        users_profile = Profile.objects.get(user=request.user)
    except:
        return render(request, "network/profile.html", {"error": True})
    get_filter = request.GET.get("filter")
    search_query = request.GET.get("q")
    posts = Post.objects.filter(user=user)
    if get_filter == "likes":
        posts = posts.annotate(like_count=Count("likes")).order_by("-like_count")
    elif get_filter == "comment":
        posts = posts.annotate(comment_count=Count("comments")).order_by(
            "-comment_count"
        )
    else:
        posts = posts.all().order_by("-timestamp")
    if search_query:
        posts = list(filter(lambda post: search_query in post.post, posts))
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    context = {
        "posts": posts,
        "user": user,
        "profile": profile,
        "users_profile": users_profile,
    }
    return render(request, "network/profile.html", context)


@login_required
def following(request):
    get_filter = request.GET.get("filter")
    search_query = request.GET.get("q")
    following = Profile.objects.get(user=request.user).following.all()
    posts = Post.objects.filter(user__in=following).order_by("-timestamp")
    if get_filter == "likes":
        posts = posts.annotate(like_count=Count("likes")).order_by("-like_count")
    else:
        posts = posts.annotate(comment_count=Count("comments")).order_by(
            "-comment_count"
        )
    if search_query:
        posts = list(filter(lambda post: search_query in post.post, posts))
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, "network/following.html", {"posts": posts})


@login_required
@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get("id")
        is_liked = request.POST.get("is_liked")
        try:
            post = Post.objects.get(id=post_id)
            if request.user != post.user:
                if is_liked == "no":
                    text = f"{request.user} liked your post!"
                    user = Profile.objects.get(user=post.user)
                    if user.notifications.filter(text=text).exists():
                        notification = Notification.objects.get(text=text)
                        notification.delete()
                        user.notifications.remove(notification)
                    post.likes.add(request.user)
                    is_liked = "yes"
                    notification = Notification(text=text, link=f"/u/{request.user}")
                    notification.save()
                    user.notifications.add(notification)
                    user.save()
                elif is_liked == "yes":
                    post.likes.remove(request.user)
                    is_liked = "no"
                    post.save()
            return JsonResponse(
                {"like_count": post.likes.count(), "is_liked": is_liked, "status": 201}
            )
        except Exception as e:
            return JsonResponse({"error": "Post not found"}, status=404)
    if request.method == "GET":
        post_id = request.GET.get("id")
        try:
            is_liked = "no"
            post = Post.objects.get(id=post_id)
            if request.user == post.user or request.user in post.likes.all():
                is_liked = "yes"
            return JsonResponse(
                {"like_count": post.likes.count(), "is_liked": is_liked, "status": 200}
            )
        except Post.DoesNotExist:
            return JsonResponse({"msg": "post doesnt exist"}, status=400)


@login_required
@csrf_exempt
def follow(request):
    if request.method == "POST":
        user = request.POST.get("user")
        action = request.POST.get("action")

        if action == "Follow":
            try:
                user = User.objects.get(username=user)
                profile = Profile.objects.get(user=request.user)
                profile.following.add(user)
                profile.save()
                profile = Profile.objects.get(user=user)
                profile.follower.add(request.user)
                text = f"{request.user} no longer follows you."
                if profile.notifications.filter(text=text).exists():
                    notification = Notification.objects.get(text=text)
                    profile.notifications.remove(notification)
                    notification.delete()
                notification = Notification(
                    text=f"{request.user} now follows you!",
                    link=f"/u/{request.user}",
                )
                notification.save()
                profile.notifications.add(notification)
                profile.save()
                return JsonResponse(
                    {
                        "status": 201,
                        "action": "Unfollow",
                        "follower_count": profile.follower.count(),
                    },
                    status=201,
                )
            except Exception as e:
                return JsonResponse({}, status=404)
        else:
            try:
                user = User.objects.get(username=user)
                profile = Profile.objects.get(user=request.user)
                profile.following.remove(user)
                profile.save()
                profile = Profile.objects.get(user=user)
                profile.follower.remove(request.user)
                text = f"{request.user} now follows you!"
                if profile.notifications.filter(text=text).exists():
                    notification = Notification.objects.get(text=text)
                    profile.notifications.remove(notification)
                    notification.delete()
                notification = Notification(
                    text=f"{request.user} no longer follows you.",
                    link=f"/u/{request.user}",
                )
                notification.save()
                profile.notifications.add(notification)
                profile.save()
                return JsonResponse(
                    {
                        "status": 201,
                        "action": "Follow",
                        "follower_count": profile.follower.count(),
                    },
                    status=201,
                )
            except Exception as e:
                return JsonResponse({}, status=404)
    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def edit_post(request):
    if request.method == "POST":
        post_id = request.POST.get("id")
        new_post = request.POST.get("post")
        try:
            post = Post.objects.get(id=post_id)
            if post.user == request.user:
                post.post = new_post.strip()
                post.save()
                return JsonResponse({}, status=201)
        except:
            return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def addpost(request):
    if request.method == "POST":
        post = request.POST.get("post")
        if len(post) != 0:
            obj = Post()
            obj.post = post
            obj.user = request.user
            obj.save()
            context = {
                "status": 201,
                "post_id": obj.id,
                "username": request.user.username,
                "timestamp": obj.timestamp.strftime("%B %d, %Y, %I:%M %p"),
            }
            sender_profile = Profile.objects.get(user=request.user)
            for follower in sender_profile.follower.all():
                user_profile = Profile.objects.get(user=follower)
                notification = Notification.objects.filter(
                    text=f"{request.user} uploaded something new!",
                    link=f"/u/{request.user}",
                ).first()
                if notification:
                    notification.read = False
                    notification.save()
                else:
                    notification = Notification(
                        text=f"{request.user} uploaded something new!",
                        link=f"/u/{request.user}",
                    )
                    notification.save()
                user_profile.notifications.add(notification)
                user_profile.save()
            return JsonResponse(context, status=201)
    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def comment(request):
    if request.method == "POST":
        post_id = request.POST.get("id")
        comment = request.POST.get("comment")
        try:
            post = Post.objects.get(id=post_id)
            comment, created = Comment.objects.get_or_create(
                user=request.user.username, comment=comment
            )
            post.comments.add(comment)
            if not request.user == post.user:
                notification = Notification.objects.filter(
                    text=f"{request.user} commented on your post",
                    link=f"/u/{request.user}",
                ).first()
                if notification:
                    notification.read = False
                    notification.save()
                else:
                    notification = Notification(
                        text=f"{request.user} commented on your post",
                        link=f"/u/{request.user}",
                    )
                    notification.save()
                user = Profile.objects.get(user=post.user)
                user.notifications.add(notification)
                user.save()
            post.save()
            return JsonResponse(
                {
                    "status": 200,
                }
            )
        except Post.DoesNotExist:
            return JsonResponse({"msg": "post doesnt exist"}, status=400)

@login_required
@csrf_exempt
def get_notifications(request):
    if request.method == "GET":
        user_profile = Profile.objects.get(user=request.user)
        return JsonResponse(
            {
                "notifications": list(
                    user_profile.notifications.values(
                        "text", "timestamp", "read", "link"
                    )
                ),
                "status": 200,
            }
        )
    if request.method == "POST":
        user_profile = Profile.objects.get(user=request.user)
        for notification in user_profile.notifications.all():
            notification.read = True
            notification.save()
        user_profile.save()
        return JsonResponse({"status": 200})

@csrf_exempt
@login_required
def like_comment(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        is_liked = request.POST.get("is_liked")
        comment_obj = Comment.objects.get(id=comment_id)
        if request.user.username != comment_obj.user:
            if is_liked == "no":
                comment_obj.likes.add(request.user)
                is_liked = "yes"
                comment_obj.save()
            elif is_liked == "yes":
                comment_obj.likes.remove(request.user)
                is_liked = "no"
                comment_obj.save()
            return JsonResponse(
                {"like_count": comment_obj.likes.count(), "is_liked": is_liked, "status": 201}
            )
        return JsonResponse({'status':200})
        


@csrf_exempt
@login_required
def post(request, post):
    post_obj = Post.objects.get(id=post)
    get_filter = request.GET.get("filter")
    comments = post_obj.comments
    if get_filter == "likes":
        comments = comments.annotate(like_count=Count("likes")).order_by("-like_count")
    else:
        comments = comments.all().order_by("-timestamp")
    return render(request, "network/post.html", {
        "post": post_obj, 
        "comments": comments,
        "status": 200,
    })
