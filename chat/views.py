from .models import ChatGroup, Message
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid

# Create your views here.
@login_required(login_url='login')
def home(request):
    """
    Render the home page of the chat application.
    """
    user_id = request.user.id
    groups = ChatGroup.get_user_groups(user_id)
    data = []

    for group in groups:
        data.append({
            "id": group["_id"],
            "name": group["name"],
            "is_group": group["is_group"],
            "members": group["members"],
            "admin_id": group["admin_id"],
            "created_at": group["created_at"],
        })
    
    context = {
        "groups": data,
        "user_id": user_id,
    }
    return render(request, 'chat/home.html', context=context)

@login_required(login_url='login')
def chat_room(request, chat_id):
    user_id = request.user.id

    # Fetch all messages for this chat
    messages = Message().find_many({"chat_id": chat_id})
    messages = sorted(messages, key=lambda x: x.get("timestamp"))  # sort by timestamp

    # You can also convert timestamps to localtime if needed
    return render(request, 'chat/chat_room.html', {
        'messages': messages,
        'user_id': user_id
    })

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm']
        
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'auth/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your chat list view name
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def chat_room_view(request, chat_id):
    # Fetch chat group info
    group = ChatGroup().get_data_by_id(chat_id)
    chat_id = group.get("_id") if group else None

    if not group:
        return render(request, 'chat/not_found.html', {'chat_id': chat_id})

    # Fetch messages
    messages_cursor = Message().find_many({"chat_id": chat_id})
    messages = list(messages_cursor)
    return render(request, 'chat/chat_room.html', {
        'group': group,
        'chat_id': chat_id,
        'messages': messages,
        'current_user_id': request.user.id  # for aligning left/right
    })

def fetch_users_modal(request):
    users = User.objects.all().exclude(id=request.user.id)  # Exclude current user
    html = render(request, 'chat/user_list_modal.html', {'users': users}).content.decode('utf-8')
    return JsonResponse({'html': html})

@csrf_exempt
@login_required
def create_group(request):
    if request.method == "POST":
        import json
        from ipdb import set_trace; set_trace()  # For debugging purposes
        user_ids = json.loads(request.POST.get('user_ids'))
        group_name = request.POST.get('group_name', None).strip()
        current_user = request.user

        members = User.objects.filter(id__in=user_ids)
        if not members.exists():
            return JsonResponse({'error': 'No users selected'}, status=400)

        is_group = len(members) > 1

        if is_group and not group_name:
            return JsonResponse({'error': 'Group name is required for group chats'}, status=400)

        # Auto-name if single user
        if not is_group:
            group_name = f"{current_user.username}_{members.first().username}"

        group = ChatGroup(
            _id = str(uuid.uuid4()),  # Generate a unique ID
            members=[current_user.id] + [user.id for user in members],
            name=group_name,
            is_group=is_group,
            admin_id=current_user.id if is_group else None
        )
        group.save()
        return JsonResponse({'message': 'Group created!'})
