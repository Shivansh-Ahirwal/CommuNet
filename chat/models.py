from django.db import models
import datetime
from .utils.base_models import BaseMongoModel
from django.contrib.auth.models import User

class ChatGroup(BaseMongoModel):

    collection = "chat_groups"

    _id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    is_group = models.BooleanField(default=False)
    admin_id = models.IntegerField()
    members = models.JSONField()
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False

    def save(self):
        document = {
            "_id": self._id,
            "name": self.name,
            "is_group": self.is_group,
            "admin_id": self.admin_id,
            "members": self.members,
            "created_at": self.created_at or datetime.datetime.utcnow(),
        }
        return self.insert_one(document)

    @staticmethod
    def get_user_groups(user_id):
        """Get all groups that include user_id in members"""
        instance = ChatGroup()
        return instance.find_many({"members": {"$in": [user_id]}})


class Message(BaseMongoModel):

    collection = "messages"

    _id = models.CharField(max_length=50, primary_key=True)
    chat_id = models.CharField(max_length=50)
    sender_id = models.IntegerField()
    text = models.TextField(blank=True, null=True)
    media = models.JSONField(blank=True, null=True, default=dict)
    timestamp = models.DateTimeField(null=True, blank=True)
    status = models.JSONField(blank=True, null=True)
    reply_to = models.CharField(max_length=50, null=True, blank=True)
    is_forwarded = models.BooleanField(default=False)

    class Meta:
        managed = False

    def save(self):
        document = {
            "_id": self._id,
            "chat_id": self.chat_id,
            "sender_id": self.sender_id,
            "text": self.text,
            "media": self.media,
            "status": self.status,
            "reply_to": self.reply_to,
            "is_forwarded": self.is_forwarded,
            "timestamp": self.timestamp or datetime.datetime.utcnow(),
            "created_at": datetime.datetime.utcnow(),
        }
        return self.insert_one(document)

class VideoCallSession(models.Model):
    caller = models.ForeignKey(User, related_name='caller_sessions', on_delete=models.CASCADE)
    callee = models.ForeignKey(User, related_name='callee_sessions', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='initiated')  # initiated, ongoing, ended
    
    class Meta:
        ordering = ['-created_at']