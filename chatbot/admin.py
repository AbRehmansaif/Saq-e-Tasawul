from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatIntent, ProductQuery

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['session_id', 'created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content"

@admin.register(ChatIntent)
class ChatIntentAdmin(admin.ModelAdmin):
    list_display = ['name', 'confidence_threshold', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(ProductQuery)
class ProductQueryAdmin(admin.ModelAdmin):
    list_display = ['session', 'query_text_preview', 'results_count', 'timestamp']
    list_filter = ['timestamp', 'results_count']
    search_fields = ['query_text', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def query_text_preview(self, obj):
        return obj.query_text[:50] + "..." if len(obj.query_text) > 50 else obj.query_text
    query_text_preview.short_description = "Query"
