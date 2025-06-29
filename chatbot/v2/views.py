from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from chatbot.services.chat_service import ChatService
from chatbot.serializers import ChatRequestSerializer, ChatResponseSerializer, ChatMessageSerializer
from chatbot.models import ChatSession, ChatMessage

class ChatAPIView(APIView):
    """Main chat API endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle chat message"""
        serializer = ChatRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_service = ChatService()
            response_data = chat_service.process_message(
                message=serializer.validated_data['message'],
                session_id=serializer.validated_data.get('session_id'),
                user_id=serializer.validated_data.get('user_id')
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Internal server error',
                'message': 'Sorry, I encountered an error processing your request. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatHistoryAPIView(APIView):
    """Get chat history for a session"""
    permission_classes = [AllowAny]
    
    def get(self, request, session_id):
        """Get chat history"""
        try:
            session = ChatSession.objects.get(session_id=session_id, is_active=True)
            messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
            serializer = ChatMessageSerializer(messages, many=True)
            
            return Response({
                'session_id': session_id,
                'messages': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ChatSession.DoesNotExist:
            return Response({
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)

class SessionCreateAPIView(APIView):
    """Create new chat session"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create new session"""
        user_id = request.data.get('user_id')
        
        session = ChatSession.objects.create(
            user_id=user_id if user_id else None
        )
        
        return Response({
            'session_id': session.session_id,
            'created_at': session.created_at
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def quick_search(request):
    """Quick product search endpoint"""
    query = request.data.get('query', '')
    
    if not query:
        return Response({
            'error': 'Query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from core.models import Product
        from .serializers import ProductSerializer
        
        products = Product.objects.filter(
            title__icontains=query,
            product_status='published',
            status=True
        )[:5]
        
        serializer = ProductSerializer(products, many=True)
        
        return Response({
            'query': query,
            'results': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Search failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)