from rest_framework import serializers
from chatbot.models import ChatSession, ChatMessage, ProductQuery
from core.models import Product, CartOrder

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product data in chat responses"""
    has_discount = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    stock_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'pid', 'title', 'price', 'old_price', 'image', 
            'in_stock', 'stock_count', 'has_discount', 'effective_price',
            'stock_quantity', 'description'
        ]
    
    def get_has_discount(self, obj):
        return obj.old_price > obj.price if obj.old_price else False
    
    def get_effective_price(self, obj):
        return float(obj.price)
    
    def get_stock_quantity(self, obj):
        try:
            return int(obj.stock_count) if obj.stock_count else 0
        except (ValueError, TypeError):
            return 0

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order data in chat responses"""
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = CartOrder
        fields = [
            'oid', 'product_status', 'tracking_id', 'price', 
            'order_date', 'full_name', 'items'
        ]
    
    def get_items(self, obj):
        from core.models import CartOrderProducts
        items = CartOrderProducts.objects.filter(order=obj)
        return [{
            'name': item.item,
            'quantity': item.qty,
            'price': float(item.price)
        } for item in items]

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'metadata', 'timestamp']

class ChatRequestSerializer(serializers.Serializer):
    """Serializer for incoming chat requests"""
    message = serializers.CharField(max_length=1000)
    session_id = serializers.CharField(max_length=25, required=False)
    user_id = serializers.IntegerField(required=False)

class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    message = serializers.CharField()
    session_id = serializers.CharField()
    intent = serializers.CharField(required=False)
    data = serializers.DictField(required=False)
    suggestions = serializers.ListField(child=serializers.CharField(), required=False)
    metadata = serializers.DictField(required=False)