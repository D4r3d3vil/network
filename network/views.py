from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Profile, Comment, Notification, ChatRoom, ChatMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from pyfcm import FCMNotification

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
@csrf_exempt
def setToken(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        user = User.objects.get(id=request.user.id)
        user.registration_id = token
        user.save()
        notify(request.user, 'token added', f'javascript:alert("you now recieve notifications")')

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def fourofour(request):
    return render(request, 'network/404.html', {})

def chats(request):
    user = User.objects.get(id=request.user.id)
    rooms = ChatRoom.objects.filter(members=user)
    return render(request, 'network/rooms.html', {'rooms':rooms})

@staff_member_required(login_url='/404')
@login_required
def chat_room(request, roomId):
    user = User.objects.get(id=request.user.id)
    try:
        roomModel = ChatRoom.objects.get(roomId=roomId)
        roomModel.messages.filter(timestamp__gt=user.lastMsgRead)
    except:
        return render(request, 'network/404.html', {'message':'Room not found it may have been deleted.'})
    user.save()
    return render(request, 'network/chat_room.html', {'room':roomModel.name, 'roomId':roomModel.roomId, 'messages':roomModel.messages})

@staff_member_required
@login_required
def get_chats(request, roomId):
    if request.method == "GET":
        user = User.objects.get(id=request.user.id)
        try:
            roomModel = ChatRoom.objects.get(roomId=roomId)
            roomMessages = roomModel.messages.filter(timestamp__gt=user.lastMsgRead)
        except:
            return render(request, 'network/404.html', {'message':'Room not found it may have been deleted.'})
        user.save()
        return JsonResponse({'messages': serializers.serialize("json", roomMessages.all())})
    elif request.method == "POST":
        message = ChatMessage(message=request.POST.get('message'), user=request.user.username)
        message.save()
        roomModel = ChatRoom.objects.get(roomId=roomId)
        roomModel.messages.add(message)
        roomModel.save()
        if '.' in request.POST.get('message'):
            for member in roomModel.members.exclude(user=request.user):
                notify(member, f'New message in the {roomModel.name} group', 'https://maincs50.pythonanywhere.com/')
        return JsonResponse({'status': 200})

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
                    notify(request.user, text, f"/u/{request.user}")
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
                notify(request.user, f"{request.user} now follows you!", f"/u/{request.user}")
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
                notify(request.user, f"{request.user} no longer follows you.", f"/u/{request.user}")
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
                notification = Notification.objects.filter(
                    text=f"{request.user} uploaded something new!",
                    link=f"/u/{request.user}",
                ).first()
                if notification:
                    notification.read = False
                    notification.save()
                else:
                    notify(follower, f"{request.user} uploaded something new!", f"/u/{request.user}")
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
                    notify(request.user, f"{request.user} commented on your post", f"/u/{request.user}")
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
push_service = FCMNotification(api_key='AAAAwk-2Q9I:APA91bFaxi6IKG6R7vYo027BQ5cxOUEaWODSbmiiIF47RBWe2Xl2PJaQFx5yM6KGLJ9h_vibaqRNVOHKKYfb8KV8Ij6kb-G2bcQMvtUFpKTvP4WHNpfqzaxjlBkENPnQdryF0C2V5ckX')
def notify(user, text, link):
    notification = Notification(text=text, link=link)
    notification.save()
    user_profile = Profile.objects.get(user=user)
    user_profile.notifications.add(notification)
    user_profile.save()
    user = User.objects.get(id=user.id)
    push_service.notify_single_device(
        registration_id=user.registration_id,
        message_title='New notification',
        message_body=text
    )
    return 200 
def showFirebaseJS(request):
    data='importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
         'var firebaseConfig = {' \
         '        apiKey: "AIzaSyC_CZ-eSpJmK2f2O-Cou-yEs00HTVRHvVc",' \
         '        authDomain: "network-3ae0a.firebaseapp.com",' \
         '        projectId: "network-3ae0a",' \
         '        storageBucket: "network-3ae0a.appspot.com",' \
         '        messagingSenderId: "834561000402",' \
         '        appId: "1:834561000402:web:940807b16af3321e127e0b",' \
         ' };' \
         'firebase.initializeApp(firebaseConfig);' \
         'const messaging=firebase.messaging();' \
         'messaging.setBackgroundMessageHandler(function (payload) {' \
         '    console.log(payload);' \
         '    const notification=JSON.parse(payload);' \
         '    const notificationOption={' \
         '        body:notification.body,' \
         '        icon:notification.icon' \
         '    };' \
         '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
         '});'

    return HttpResponse(data,content_type="text/javascript")