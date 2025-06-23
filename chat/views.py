from .models import ChatGroup, Message
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import uuid
from .utils.base_models import BaseMongoModel
from bson import ObjectId
from .tasks import upload_file_to_gridfs


@login_required(login_url='login')
def home(request):
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
    messages = Message().find_many({"chat_id": chat_id})
    messages = sorted(messages, key=lambda x: x.get("timestamp"))
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

        User.objects.create_user(username=username, password=password)
        messages.success(request,
                         "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'auth/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def chat_room_view(request, chat_id):
    group = ChatGroup().get_data_by_id(chat_id)
    chat_id = group.get("_id") if group else None

    if not group:
        return render(request, 'chat/not_found.html', {'chat_id': chat_id})

    messages_cursor = Message().find_many({"chat_id": chat_id})
    messages = list(messages_cursor)
    return render(request, 'chat/chat_room.html', {
        'group': group,
        'chat_id': chat_id,
        'messages': messages,
        'current_user_id': request.user.id
    })


def fetch_users_modal(request):
    users = User.objects.all().exclude(id=request.user.id)
    html = render(request,
                  'chat/user_list_modal.html',
                  {'users': users}).content.decode('utf-8')
    return JsonResponse({'html': html})


@csrf_exempt
@login_required
def create_group(request):
    if request.method == "POST":
        import json
        user_ids = json.loads(request.POST.get('user_ids'))
        group_name = request.POST.get('group_name', None).strip()
        current_user = request.user

        members = User.objects.filter(id__in=user_ids)
        if not members.exists():
            return JsonResponse({'error': 'No users selected'}, status=400)

        is_group = len(members) > 1

        if is_group and not group_name:
            return JsonResponse(
                {'error': 'Group name is required for group chats'},
                status=400)

        if not is_group:
            group_name = f"{current_user.username}_{members.first().username}"

        group = ChatGroup(
            _id=str(uuid.uuid4()),
            members=[current_user.id] + [user.id for user in members],
            name=group_name,
            is_group=is_group,
            admin_id=current_user.id if is_group else None
        )
        group.save()
        return JsonResponse({'message': 'Group created!'})


def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        chat_id = request.POST.get('chat_id')
        sender_id = request.POST.get('sender_id')

        upload_file_to_gridfs.delay(
            file_data=uploaded_file.read(),
            filename=uploaded_file.name,
            content_type=uploaded_file.content_type,
            chat_id=chat_id,
            sender_id=sender_id
        )

        return JsonResponse({'status': 'success',
                             'message': 'File upload initiated'})


def serve_file(request, file_id):
    fs = BaseMongoModel.get_gridfs_instance()
    file = fs.get(ObjectId(file_id))
    response = HttpResponse(file.read(), content_type=file.content_type)
    response['Content-Disposition'] = f'inline; filename="{file.filename}"'
    return response


def broadcast_file_message(chat_id, sender_id, file_id, file_type, text=None):
    file_url = f'/files/{file_id}/'

    channel_layer = get_channel_layer()
    group_name = f'chat_{chat_id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'chat_message',
            'message': text or '',
            'sender_id': sender_id,
            'file_url': file_url,
            'file_id': file_id,
        }
    )
