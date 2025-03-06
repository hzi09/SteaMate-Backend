from django.db import models
from pandas import Timestamp

# Create your models here.
class ChatSession(models.Model):
    user_id = models.ForeignKey("account.User", on_delete=models.CASCADE, related_name="chat_sessions")
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session_id = models.ForeignKey("chatmate.ChatSession", on_delete=models.CASCADE, related_name="chat_messages")
    user_message = models.TextField()
    chatbot_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)