from django.db import models
from django.contrib.auth.models import User
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
import json

class ChatSession(models.Model):
    """Track user chat sessions"""
    session_id = ShortUUIDField(unique=True, length=20, max_length=25, prefix="chat_")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Chat Sessions"
    
    def __str__(self):
        return f"Session {self.session_id}"

class ChatMessage(models.Model):
    """Store chat messages"""
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Store extracted entities, intent, etc.
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Chat Messages"
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class ChatIntent(models.Model):
    """Store recognized intents for analytics"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    keywords = models.JSONField(default=list)  # List of keywords that trigger this intent
    confidence_threshold = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Chat Intents"
    
    def __str__(self):
        return self.name

class ProductQuery(models.Model):
    """Track product search queries for analytics"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    query_text = models.TextField()
    extracted_entities = models.JSONField(default=dict)
    results_count = models.IntegerField(default=0)
    clicked_product = models.ForeignKey('core.Product', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product Queries"