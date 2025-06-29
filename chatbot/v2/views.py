from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer

from chatbot.services.chat_service import ChatService
from chatbot.v2.serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ChatMessageSerializer,
)
from chatbot.models import ChatSession, ChatMessage


# ✅ Main Chat API View (GET for UI page, POST for messages)
# class ChatAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         return render(request, 'chat_bot/chatbot_ui.html')

#     def post(self, request):
#         serializer = ChatRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(
#                 {
#                     'error': 'Invalid request data',
#                     'details': serializer.errors,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             chat_service = ChatService()
#             response_data = chat_service.process_message(
#                 message=serializer.validated_data['message'],
#                 session_id=serializer.validated_data.get('session_id'),
#                 user_id=serializer.validated_data.get('user_id'),
#             )

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {
#                     'error': 'Internal server error',
#                     'message': 'Sorry, I encountered an error processing your request. Please try again.',
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

class ChatAPIView(APIView):
    """Main chat API: Renders UI (GET) and handles chat (POST)."""
    permission_classes = [AllowAny]

    def get(self, request):
        # Render chatbot UI
        return render(request, 'chat_bot/chatbot_ui.html')

    def post(self, request):
        # Handle user chat input
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid request data',
                    'details': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            chat_service = ChatService()
            response_data = chat_service.process_message(
                message=serializer.validated_data['message'],
                session_id=serializer.validated_data.get('session_id'),
                user_id=serializer.validated_data.get('user_id'),
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Optional: log the error for debugging
            import traceback
            print("Error in ChatAPIView:", traceback.format_exc())

            return Response(
                {
                    'error': 'Internal server error',
                    'message': 'Sorry, I encountered an error processing your request. Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ✅ Chat History API View
class ChatHistoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(session_id=session_id, is_active=True)
            messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
            serializer = ChatMessageSerializer(messages, many=True)

            return Response(
                {
                    'session_id': session_id,
                    'messages': serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND,
            )


# ✅ Session Create API View
class SessionCreateAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user_id = request.data.get('user_id')
        session = ChatSession.objects.create(
            user_id=user_id if user_id else None
        )

        return Response(
            {
                'session_id': session.session_id,
                'created_at': session.created_at,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        return Response(
            {
                "error": "GET method not allowed for this endpoint."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


# ✅ Quick Search API Function View
@api_view(['POST'])
@permission_classes([AllowAny])
def quick_search(request):
    query = request.data.get('query', '')

    if not query:
        return Response(
            {'error': 'Query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from core.models import Product
        from .serializers import ProductSerializer

        products = Product.objects.filter(
            title__icontains=query,
            product_status='published',
            status=True,
        )[:5]

        serializer = ProductSerializer(products, many=True)

        return Response(
            {
                'query': query,
                'results': serializer.data,
                'count': len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                'error': 'Search failed',
                'message': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
