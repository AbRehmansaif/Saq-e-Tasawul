# from typing import Dict, Any, List, Optional
# from django.db.models import Q
# from core.models import Product, CartOrder, Category
# from chatbot.models import ChatSession, ChatMessage
# from chatbot.v2.serializers import ProductSerializer, OrderSerializer
# from chatbot.services.nlp_service import NLPService
# from chatbot.services.llm_service import LLMService

# class ChatService:
#     """Main chat service that orchestrates NLP and response generation"""
    
#     def __init__(self):
#         self.nlp_service = NLPService()
#         self.llm_service = LLMService()
    
#     def process_message(self, message: str, session_id: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
#         """Process incoming chat message and generate response"""
        
#         # Get or create chat session
#         session = self._get_or_create_session(session_id, user_id)
        
#         # Save user message
#         user_message = ChatMessage.objects.create(
#             session=session,
#             message_type='user',
#             content=message
#         )
        
#         # Extract entities and classify intent
#         entities = self.nlp_service.extract_entities(message)
#         intent = self.nlp_service.classify_intent(message, entities)
        
#         # Update user message metadata
#         user_message.metadata = {
#             'entities': entities,
#             'intent': intent
#         }
#         user_message.save()
        
#         # Generate response based on intent
#         response_data = self._generate_response(message, intent, entities, session)
        
#         # Save bot response
#         bot_message = ChatMessage.objects.create(
#             session=session,
#             message_type='bot',
#             content=response_data['message'],
#             metadata={
#                 'intent': intent,
#                 'entities': entities,
#                 'data': response_data.get('data', {})
#             }
#         )
        
#         # Return complete response
#         return {
#             'message': response_data['message'],
#             'session_id': session.session_id,
#             'intent': intent,
#             'data': response_data.get('data'),
#             'suggestions': response_data.get('suggestions', []),
#             'metadata': {
#                 'entities': entities,
#                 'message_id': bot_message.id
#             }
#         }
    
#     def _get_or_create_session(self, session_id: Optional[str], user_id: Optional[int]) -> ChatSession:
#         """Get existing or create new chat session"""
#         if session_id:
#             try:
#                 return ChatSession.objects.get(session_id=session_id, is_active=True)
#             except ChatSession.DoesNotExist:
#                 pass
        
#         # Create new session
#         session = ChatSession.objects.create(
#             user_id=user_id if user_id else None
#         )
#         return session
    
#     def _generate_response(self, message: str, intent: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
#         """Generate response based on intent and entities"""
        
#         if intent == 'product_search':
#             return self._handle_product_search(message, entities, session)
#         elif intent == 'order_inquiry':
#             return self._handle_order_inquiry(message, entities, session)
#         elif intent == 'stock_inquiry':
#             return self._handle_stock_inquiry(message, entities, session)
#         elif intent == 'category_browse':
#             return self._handle_category_browse(message, entities, session)
#         elif intent == 'help_request':
#             return self._handle_help_request(message, entities, session)
#         else:
#             return self._handle_general_inquiry(message, entities, session)
    
#     def _handle_product_search(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
#         """Handle product search queries"""
#         # Build query
#         query = Q(product_status='published', status=True)
        
#         # Search by extracted entities
#         search_terms = []
        
#         if entities['colors']:
#             for color in entities['colors']:
#                 search_terms.append(color)
        
#         if entities['categories']:
#             for category in entities['categories']:
#                 search_terms.append(category)
        
#         if entities['brands']:
#             for brand in entities['brands']:
#                 search_terms.append(brand)
        
#         # If no specific entities, use the full message for search
#         if not search_terms:
#             search_terms = message.split()
        
#         # Build search query
#         for term in search_terms:
#             query &= (
#                 Q(title__icontains=term) |
#                 Q(description__icontains=term) |
#                 Q(tags__name__icontains=term) |
#                 Q(category__title__icontains=term)
#             )
        
#         # Execute search
#         products = Product.objects.filter(query).distinct()[:10]
        
#         # Log the search
#         from chatbot.models import ProductQuery
#         ProductQuery.objects.create(
#             session=session,
#             query_text=message,
#             extracted_entities=entities,
#             results_count=products.count()
#         )
        
#         if products.exists():
#             serialized_products = ProductSerializer(products, many=True).data
            
#             # Generate contextual response using LLM
#             context = {
#                 'intent': 'product_search',
#                 'entities': entities,
#                 'products': serialized_products
#             }
            
#             llm_response = self.llm_service.generate_response(message, context)
            
#             return {
#                 'message': llm_response if llm_response else f"I found {products.count()} products that match your search:",
#                 'data': {
#                     'products': serialized_products
#                 },
#                 'suggestions': [
#                     "Show more products",
#                     "Filter by price",
#                     "Check availability",
#                     "Show similar items"
#                 ]
#             }
#         else:
#             categories = Category.objects.all()
#             suggestions = [cat.title for cat in categories[:5]] if categories.exists() else []

#             return {
#                 'message': "I couldn't find any products matching your search. But here are the categories available in our shop:",
#                 'data': {
#                     'categories': [{'id': cat.id, 'title': cat.title} for cat in categories]
#                 },
#                 'suggestions': suggestions if suggestions else ["Search again"]
#             }
    
#     def _handle_order_inquiry(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
#         """Handle order status inquiries"""
#         order_ids = entities.get('order_ids', [])
        
#         if not order_ids:
#             return {
#                 'message': "I'd be happy to help you track your order. Please provide your order ID (it usually starts with ORD, BUY, or is a 5-10 digit number).",
#                 'suggestions': [
#                     "Enter order ID",
#                     "Check recent orders",
#                     "Contact support"
#                 ]
#             }
        
#         # Try to find the order
#         order = None
#         for order_id in order_ids:
#             # Clean the order ID
#             clean_id = order_id.replace('#', '').replace('ORDER', '').replace('ORD', '').replace('BUY', '')
            
#             # Search for order
#             order = CartOrder.objects.filter(
#                 Q(oid__icontains=clean_id) | 
#                 Q(tracking_id__icontains=clean_id) |
#                 Q(sku__icontains=clean_id)
#             ).first()
            
#             if order:
#                 break
        
#         if order:
#             serialized_order = OrderSerializer(order).data
            
#             # Generate contextual response
#             context = {
#                 'intent': 'order_inquiry',
#                 'entities': entities,
#                 'order': serialized_order
#             }
            
#             llm_response = self.llm_service.generate_response(message, context)
            
#             return {
#                 'message': llm_response if llm_response else f"Here's the information for your order:",
#                 'data': {
#                     'order': serialized_order
#                 },
#                 'suggestions': [
#                     "Track package",
#                     "Contact support",
#                     "Order again"
#                 ]
#             }
#         else:
#             return {
#                 'message': f"I couldn't find an order with ID {order_ids[0]}. Please double-check the order number or contact our support team.",
#                 'suggestions': [
#                     "Try different order ID",
#                     "Contact support",
#                     "Check email confirmation"
#                 ]
#             }
    
#     def _handle_stock_inquiry(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
#         """Handle stock availability inquiries"""
#         # Similar to product search but focus on stock status
#         products = self._search_products_by_entities(entities, message)
        
#         if products.exists():
#             in_stock_products = products.filter(in_stock=True)
#             out_of_stock_products = products.filter(in_stock=False)
            
#             stock_info = []
#             for product in products:
#                 try:
#                     stock_qty = int(product.stock_count) if product.stock_count else 0
#                 except (ValueError, TypeError):
#                     stock_qty = 0
                
#                 stock_info.append({
#                     'product': ProductSerializer(product).data,
#                     'stock_quantity': stock_qty,
#                     'in_stock': product.in_stock
#                 })
            
#             message_parts = []
#             if in_stock_products.exists():
#                 message_parts.append(f"{in_stock_products.count()} items are in stock")
#             if out_of_stock_products.exists():
#                 message_parts.append(f"{out_of_stock_products.count()} items are out of stock")
            
#             return {
#                 'message': f"Stock status: {', '.join(message_parts)}",
#                 'data': {
#                     'stock_info': stock_info
#                 },
#                 'suggestions': [
#                     "Show in-stock items only",
#                     "Notify when available",
#                     "Find alternatives"
#                 ]
#             }
#         else:
#             return {
#                 'message': "Please specify which product you'd like to check stock for.",
#                 'suggestions': [
#                     "Search for product",
#                     "Browse categories",
#                     "Show popular items"
#                 ]
#             }
    
#     def _handle_category_browse(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
#         """Handle category browsing requests"""
#         from core.models import Category
        
#         categories = Category.objects.all()
#         category_data = []
        
#         for category in categories:
#             category_data.append({
#                 'id': category.id,
#                 'title': category.title,
#                 'product_count': category.product_count(),
#             })
        
#         return {
#             'message': "Here are our available product categories:",
#             'data': {
#                 'categories': category_data
#             },
#             'suggestions': [cat['title'] for cat in category_data[:5]]
#         }
    
#     def _handle_help_request(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
#         """Handle help and support requests"""
#         return {
#             'message': "I'm here to help! I can assist you with:\n\n• Finding products and checking availability\n• Tracking your orders and delivery status\n• Browsing product categories\n• Checking prices and deals\n• General shopping questions\n\nWhat would you like help with?",
#             'suggestions': [
#                 "Find products",
#                 "Track my order", 
#                 "Browse categories",
#                 "Check deals",
#                 "Contact support"
#             ]
#         }
    
#     def _handle_general_inquiry(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
#         """Handle general inquiries"""
#         context = {
#             'intent': 'general_inquiry',
#             'entities': entities
#         }
        
#         llm_response = self.llm_service.generate_response(message, context)
        
#         return {
#             'message': llm_response if llm_response else "I understand you're looking for information. Could you please be more specific about what you need? I can help you find products, track orders, or answer questions about our store.",
#             'suggestions': [
#                 "Search products",
#                 "Track order",
#                 "Browse categories",
#                 "Get help"
#             ]
#         }
    
#     def _search_products_by_entities(self, entities: Dict[str, Any], fallback_text: str = "") -> Any:
#         """Search products based on extracted entities"""
#         query = Q(product_status='published', status=True)
        
#         search_terms = []
        
#         # Collect search terms from entities
#         if entities.get('colors'):
#             search_terms.extend(entities['colors'])
#         if entities.get('categories'):
#             search_terms.extend(entities['categories'])
#         if entities.get('brands'):
#             search_terms.extend(entities['brands'])
        
#         # If no entities, use fallback text
#         if not search_terms and fallback_text:
#             search_terms = fallback_text.split()
        
#         # Build search query
#         for term in search_terms:
#             query &= (
#                 Q(title__icontains=term) |
#                 Q(description__icontains=term) |
#                 Q(tags__name__icontains=term) |
#                 Q(category__title__icontains=term)
#             )
        
#         return Product.objects.filter(query).distinct()


from typing import Dict, Any, List, Optional
from django.db.models import Q
from requests import session
from core.models import Product, CartOrder, CartOrderProducts, Category
from chatbot.models import ChatSession, ChatMessage
from chatbot.v2.serializers import ProductSerializer, OrderSerializer
from chatbot.services.nlp_service import NLPService
from chatbot.services.llm_service import LLMService

class ChatService:
    """Main chat service that orchestrates NLP and response generation"""

    def __init__(self):
        self.nlp_service = NLPService()
        self.llm_service = LLMService()

    def process_message(self, message: str, session_id: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Process incoming chat message and generate response"""

        session = self._get_or_create_session(session_id, user_id)

        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )

        entities = self.nlp_service.extract_entities(message)
        intent = self.nlp_service.classify_intent(message, entities)

        user_message.metadata = {
            'entities': entities,
            'intent': intent
        }
        user_message.save()

        response_data = self._generate_response(message, intent, entities, session)

        last_bot_msg = session.messages.filter(message_type='bot').last()
        if last_bot_msg and last_bot_msg.content == response_data['message']:
            response_data['message'] = "Let me know how else I can assist you."

        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=response_data['message'],
            metadata={
                'intent': intent,
                'entities': entities,
                'data': response_data.get('data', {})
            }
        )

        return {
            'message': response_data['message'],
            'session_id': session.session_id,
            'intent': intent,
            'data': response_data.get('data'),
            'suggestions': response_data.get('suggestions', []),
            'metadata': {
                'entities': entities,
                'message_id': bot_message.id
            }
        }

    def _get_or_create_session(self, session_id: Optional[str], user_id: Optional[int]) -> ChatSession:
        if session_id:
            try:
                return ChatSession.objects.get(session_id=session_id, is_active=True)
            except ChatSession.DoesNotExist:
                pass
        return ChatSession.objects.create(user_id=user_id if user_id else None)

    def _generate_response(self, message: str, intent: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        try:
            if message.strip().lower() == "show more products":
                return self._search_products_by_entities(message, {}, session)

            if intent == 'product_search':
                return self._handle_product_search(message, entities, session)
            elif intent == 'order_inquiry':
                return self._handle_order_inquiry(message, entities, session)
            elif intent == 'stock_inquiry':
                return self._handle_stock_inquiry(message, entities, session)
            elif intent == 'category_browse':
                return self._handle_category_browse(message, entities, session)
            elif intent == 'help_request':
                return self._handle_help_request(message, entities, session)
            elif intent == 'return_policy':
                return self._handle_return_policy(message, entities, session)
            elif intent == 'popular_items':
                return self._handle_popular_items(message, entities, session)
            elif intent == 'price_inquiry':
                return self._handle_price_inquiry(message, entities, session)
            else:
                return self._handle_general_inquiry(message, entities, session)

        except Exception as e:
            print("[Chatbot ERROR]", e)
            return {
                "message": "Sorry, I encountered an error processing your request. Please try again.",
                "suggestions": ["Browse categories", "Search again"]
            }

    # def _handle_product_search(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
    #     query = Q(product_status='published', status=True)
    #     search_terms = []

    #     if entities.get('colors'):
    #         search_terms.extend(entities['colors'])
    #     if entities.get('categories'):
    #         search_terms.extend(entities['categories'])
    #     if entities.get('brands'):
    #         search_terms.extend(entities['brands'])

    #     if not search_terms:
    #         search_terms = message.split()

    #     for term in search_terms:
    #         matched_category = Category.objects.filter(title__icontains=term).first()
    #         if matched_category:
    #             return {
    #                 'message': f"I found the category '{matched_category.title}'. Click below to browse all products.",
    #                 'data': {
    #                     'category': {
    #                         'id': matched_category.cid,
    #                         'title': matched_category.title,
    #                         'product_count': matched_category.product_count(),
    #                         'url': f"/category/{matched_category.cid}/shop-product-right.html"
    #                     }
    #                 },
    #                 'suggestions': [
    #                     f"Browse {matched_category.title}",
    #                     "Search again",
    #                     "Get deals on this category"
    #                 ]
    #             }

    #     for term in search_terms:
    #         query &= (
    #             Q(title__icontains=term) |
    #             Q(description__icontains=term) |
    #             Q(tags__name__icontains=term) |
    #             Q(category__title__icontains=term)
    #         )

    #     products = Product.objects.filter(query).distinct()[:10]

    #     from core.models import ProductQuery
    #     ProductQuery.objects.create(
    #         session=session,
    #         query_text=message,
    #         extracted_entities=entities,
    #         results_count=products.count()
    #     )

    #     if products.exists():
    #         serialized_products = ProductSerializer(products, many=True).data
    #         context = {
    #             'intent': 'product_search',
    #             'entities': entities,
    #             'products': serialized_products
    #         }
    #         llm_response = self.llm_service.generate_response(message, context)
    #         return {
    #             'message': llm_response if llm_response else f"I found {products.count()} products that match your search. Let me show you the results.",
    #             'data': {
    #                 'products': serialized_products
    #             },
    #             'suggestions': [
    #                 "Show more products",
    #                 "Filter by price",
    #                 "Check availability",
    #                 "Show similar items"
    #             ]
    #         }
    #     else:
    #         return {
    #             'message': "I couldn't find any products matching your search. Try different keywords or browse our categories.",
    #             'suggestions': [
    #                 "Browse categories",
    #                 "Show popular items",
    #                 "Search again"
    #             ]
    #         }
    
    def _handle_product_search(self, message, entities, session):
        from core.models import Product
        from django.db.models import Q

        limit = 4
        is_show_more = message.strip().lower() == "show more products"

        if not isinstance(session.metadata, dict):
            session.metadata = {}

        if not is_show_more:
            products = entities.get("products") or []
            colors = entities.get("colors") or []
            categories = entities.get("categories") or []
            brands = entities.get("brands") or []

            session.metadata["product_search_terms"] = (
                products + colors + categories + brands
            ) or message.split()
            session.metadata["shown_product_count"] = 0

        search_terms = session.metadata.get("product_search_terms", [])
        shown = session.metadata.get("shown_product_count", 0)

        query = Q(product_status="published", status=True)

        if entities.get('products'):  # Try exact product title first
            for product_title in entities['products']:
                query &= Q(title__iexact=product_title)
        else:
            for term in search_terms:
                query &= (
                    Q(title__icontains=term) |
                    Q(description__icontains=term) |
                    Q(tags__name__icontains=term) |
                    Q(category__title__icontains=term)
                )

        all_products = Product.objects.filter(query).distinct()

        total_products = all_products.count()
        products = all_products[shown:shown + limit]

        if products.exists():
            serialized = ProductSerializer(products, many=True).data

            session.metadata["shown_product_count"] = shown + len(products)
            session.save()

            response_text = (
                f"🛍️ I found {total_products} product(s). Here are some:"
                if shown == 0 else
                "🧾 Here are more products you might like:"
            )

            suggestions = (
                ["Show more products"] if session.metadata["shown_product_count"] < total_products
                else ["🗂️ Browse categories", "More Products", "📞 Get help"]
            )

            return {
                "message": response_text,
                "data": {"products": serialized},
                "suggestions": suggestions
            }

        return {
            "message": "❗ No matching products found. Please try another keyword or browse categories.",
            "suggestions": ["🗂️ Browse categories", "📞 Get help"]
        }
        
        



    def _handle_order_inquiry(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        order_ids = entities.get('order_ids', [])

        if not order_ids:
            return {
                'message': "I'd be happy to help you track your order. Please provide your order ID (it usually starts with ORD, BUY, or is a 5-10 digit number).",
                'suggestions': [
                    "Enter order ID",
                    "Check recent orders",
                    "📞 Get help"
                ]
            }

        order = None
        for order_id in order_ids:
            clean_id = order_id.replace('#', '').replace('ORDER', '').replace('ORD', '').replace('BUY', '')
            order = CartOrder.objects.filter(
                Q(oid__icontains=clean_id) |
                Q(tracking_id__icontains=clean_id) |
                Q(sku__icontains=clean_id)
            ).first()
            if order:
                break

        if order:
            serialized_order = OrderSerializer(order).data
            context = {
                'intent': 'order_inquiry',
                'entities': entities,
                'order': serialized_order
            }
            llm_response = self.llm_service.generate_response(message, context)
            return {
                'message': llm_response if llm_response else f"Here's the information for your order:",
                'data': {
                    'order': serialized_order
                },
                'suggestions': [
                    "Track package",
                    "Contact support",
                    "Order again",
                    "📞 Get help"
                ]
            }
        else:
            return {
                'message': f"I couldn't find an order with ID {order_ids[0]}. Please double-check the order number or contact our support team.",
                'suggestions': [
                    "Try different order ID",
                    "Contact support",
                    "Check email confirmation",
                    "📞 Get help"
                ]
            }

    def _handle_stock_inquiry(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        products = self._search_products_by_entities(entities, message)

        if products.exists():
            in_stock_products = products.filter(in_stock=True)
            out_of_stock_products = products.filter(in_stock=False)

            stock_info = []
            for product in products:
                try:
                    stock_qty = int(product.stock_count) if product.stock_count else 0
                except (ValueError, TypeError):
                    stock_qty = 0
                stock_info.append({
                    'product': ProductSerializer(product).data,
                    'stock_quantity': stock_qty,
                    'in_stock': product.in_stock
                })

            message_parts = []
            if in_stock_products.exists():
                message_parts.append(f"{in_stock_products.count()} items are in stock")
            if out_of_stock_products.exists():
                message_parts.append(f"{out_of_stock_products.count()} items are out of stock")

            return {
                'message': f"Stock status: {', '.join(message_parts)}",
                'data': {
                    'stock_info': stock_info
                },
                'suggestions': [
                    "Show in-stock items only",
                    "Notify when available",
                    "Find alternatives",
                    "📞 Get help"
                ]
            }
        else:
            return {
                'message': "Please specify which product you'd like to check stock for.",
                'suggestions': [
                    "Search for product",
                    "Browse categories",
                    "Show popular items",
                    "📞 Get help"
                ]
            }

    def _handle_category_browse(self, message, entities, session):
        try:
            from core.models import Category
            categories = Category.objects.all()

            if not categories.exists():
                return {
                    "message": "❗ No categories available at the moment.",
                    "suggestions": ["Search products", "Help"]
                }

            # Use set to prevent duplicates
            suggestions = list(set([f"Show {cat.title.strip()}" for cat in categories]))[:6]

            return {
                "message": "🗂️ Here are our available product categories:",
                "suggestions": suggestions
            }

        except Exception as e:
            print("[Chatbot] Category browse error:", e)
            return {
                "message": "⚠️ Could not load categories. Please try again later.",
                "suggestions": ["Search products", "Help"]
            }


    def _handle_help_request(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """Handle help and support requests"""

        # Try to get user's name from session.user if it exists
        user_name = session.user.first_name if session.user and hasattr(session.user, 'first_name') and session.user.first_name else "there"

        return {
            'message': (
                f"👋 Hi {user_name}! I'm your shopping assistant. <br>"
                "🤖 Here’s how I can help you today: <br><br>"
                
                "📞 <b>You can reach our support team anytime:</b> <br>"
                '📧 Email: <a href="mailto:support@example.com" style="color:#3366cc; text-decoration:underline;">support@example.com</a><br>'
                '💬 WhatsApp: <a href="https://wa.me/923001234567" target="_blank" style="color:#3366cc;">+92 300 1234567</a><br>'
                '🌐 Help Center: <a href="/contact/" target="_blank" style="color:#3366cc;">Visit here</a><br>'

                "🕒 Hours: Mon–Fri, 9am–6pm (PKT) <br><br>"
                
                "❓ You can also ask general shopping questions or try options below: <br>"
            ),
            'suggestions': [
                "🔍 Find products",
                "📦 Track my order",
                "🗂️ Browse categories",
                "💸 Check deals",
            ]
        }


    def _handle_general_inquiry(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        context = {
            'intent': 'general_inquiry',
            'entities': entities
        }

        llm_response = self.llm_service.generate_response(message, context)

        return {
            'message': llm_response if llm_response else (
                "🤖 I understand you're looking for information.\n\n"
                "Could you please be more specific about what you need?\n\n"
                "I can help you with:\n"
                "🔍 Searching for products\n"
                "📦 Tracking orders\n"
                "🗂️ Browsing categories\n"
                "💬 Getting general help\n\n"
                "What would you like to do next?"
            ),
            'suggestions': [
                "🔍 Search products",
                "📦 Track order",
                "🗂️ Browse categories",
                "📞 Get help"
            ]

        }
        
    def _handle_price_inquiry(self, message, entities, session):
        products = self._search_products_by_entities(entities, message)
        if products.exists():
            serialized = ProductSerializer(products, many=True).data
            return {
                'message': "Here are the prices for your requested products:",
                'data': {'products': serialized},
                'suggestions': ["Sort by price", "Search again"]
            }
        return {
            'message': "No price-related products found.",
            'suggestions': ["🔍 Search products"]
        }

    def _search_products_by_entities(self, entities: Dict[str, Any], fallback_text: str = "") -> Any:
        query = Q(product_status='published', status=True)
        search_terms = []

        if entities.get('colors'):
            search_terms.extend(entities['colors'])
        if entities.get('categories'):
            search_terms.extend(entities['categories'])
        if entities.get('brands'):
            search_terms.extend(entities['brands'])

        if not search_terms and fallback_text:
            search_terms = fallback_text.split()

        for term in search_terms:
            query &= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(tags__name__icontains=term) |
                Q(category__title__icontains=term)
            )

        return Product.objects.filter(query).distinct()

    def _handle_popular_items(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """Handle requests for popular or best-selling items"""
        # You can define popularity by most sold or most recent or manually marked "featured"
        popular_products = Product.objects.filter(
            product_status='published',
            status=True
        ).order_by('-total_sold')[:10]  # or use '-created_at' for newest

        if popular_products.exists():
            serialized = ProductSerializer(popular_products, many=True).data
            context = {
                'intent': 'popular_items',
                'entities': entities,
                'products': serialized
            }
            llm_response = self.llm_service.generate_response(message, context)

            return {
                'message': llm_response or "Here are some of our most popular items right now:",
                'data': {
                    'products': serialized
                },
                'suggestions': [
                    "🗂️ Browse categories",
                    "📞 Get help"
                ]
            }
        else:
            return {
                'message': "I couldn't find popular products at the moment. Try searching for something specific.",
                'suggestions': [
                    "🔍 Search products",
                    "🗂️ Browse categories",
                    "🛍️ Check deals",
                    "📞 Get help"
                ]
            }
    
    def _handle_return_policy(self, message: str, entities: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """Provide return policy information"""
        return {
            'message': (
                "🔁 Our Return Policy: <br>"
                "• You can return items within **7 days** of delivery. <br>"
                "• Items must be unused, in original packaging. <br>"
                "• To initiate a return, go to your order history and click 'Request Return'. <br>"
                "• For more details, please visit our [Return Policy page](https://yourwebsite.com/returns). <br>"
                "Would you like help returning a product or tracking an order?"
            ),
            'suggestions': [
                "Return a product",
                "Track my order",
                "Contact support",
                "Go to homepage",
                "📞 Get help"
            ],
            'data': {}
        }

