# import openai
# import requests
# from typing import Dict, Any, Optional
# from django.conf import settings

# class LLMService:
#     """Handle Large Language Model integrations"""
    
#     def __init__(self):
#         self.openai_client = None
#         if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
#             openai.api_key = settings.OPENAI_API_KEY
#             self.openai_client = openai
    
#     def generate_response(self, user_message: str, context: Dict[str, Any]) -> str:
#         """Generate response using available LLM"""
        
#         # Try OpenAI first
#         if self.openai_client:
#             return self._openai_response(user_message, context)
        
#         # Try LM Studio
#         if hasattr(settings, 'LM_STUDIO_BASE_URL'):
#             response = self._lm_studio_response(user_message, context)
#             if response:
#                 return response
        
#         # Fallback to rule-based response
#         return self._fallback_response(user_message, context)
    
#     def _openai_response(self, user_message: str, context: Dict[str, Any]) -> str:
#         """Generate response using OpenAI GPT"""
#         try:
#             system_prompt = self._build_system_prompt(context)
            
#             response = self.openai_client.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_message}
#                 ],
#                 max_tokens=200,
#                 temperature=0.7
#             )
            
#             return response.choices[0].message.content.strip()
#         except Exception as e:
#             print(f"OpenAI API error: {e}")
#             return None
    
#     def _lm_studio_response(self, user_message: str, context: Dict[str, Any]) -> Optional[str]:
#         """Generate response using LM Studio local API"""
#         try:
#             system_prompt = self._build_system_prompt(context)
            
#             response = requests.post(
#                 f"{settings.LM_STUDIO_BASE_URL}/chat/completions",
#                 json={
#                     "model": "local-model",
#                     "messages": [
#                         {"role": "system", "content": system_prompt},
#                         {"role": "user", "content": user_message}
#                     ],
#                     "max_tokens": 200,
#                     "temperature": 0.7
#                 },
#                 timeout=10
#             )
            
#             if response.status_code == 200:
#                 return response.json()['choices'][0]['message']['content'].strip()
#         except Exception as e:
#             print(f"LM Studio API error: {e}")
        
#         return None
    
#     def _build_system_prompt(self, context: Dict[str, Any]) -> str:
#         """Build system prompt based on context"""
#         base_prompt = """You are a helpful AI shopping assistant for an e-commerce platform. 
#         You help customers find products, check order status, and provide shopping assistance.
        
#         Keep responses concise, friendly, and helpful. Focus on the customer's needs.
        
#         Available context:"""
        
#         if context.get('intent'):
#             base_prompt += f"\nUser Intent: {context['intent']}"
        
#         if context.get('entities'):
#             base_prompt += f"\nExtracted Entities: {context['entities']}"
        
#         if context.get('products'):
#             base_prompt += f"\nFound Products: {len(context['products'])} products match the query"
        
#         if context.get('order'):
#             base_prompt += f"\nOrder Information: Order found with status {context['order'].get('status', 'unknown')}"
        
#         return base_prompt
    
#     def _fallback_response(self, user_message: str, context: Dict[str, Any]) -> str:
#         """Fallback rule-based response"""
#         intent = context.get('intent', 'general_inquiry')
        
#         responses = {
#             'product_search': "I found some products that match your search. Let me show you the results.",
#             'order_inquiry': "I can help you track your order. Please provide your order ID.",
#             'stock_inquiry': "I'll check the stock availability for you.",
#             'price_inquiry': "Here are the current prices for the products you're interested in.",
#             'category_browse': "Here are our available product categories.",
#             'help_request': "I'm here to help! You can ask me about products, orders, shipping, and more.",
#             'general_inquiry': "I understand you're looking for information. Could you please be more specific about what you need?"
#         }
        
#         return responses.get(intent, responses['general_inquiry'])


import openai
import requests
from typing import Dict, Any, Optional
from django.conf import settings


class LLMService:
    """Handle Large Language Model integrations"""

    def __init__(self):
        self.openai_client = None

        # Set OpenAI key if available (optional)
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai

    def generate_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate response using available LLM"""

        # Priority 1: Use OpenAI if key is available
        if self.openai_client:
            return self._openai_response(user_message, context)

        # Priority 2: Use LM Studio (local server)
        if hasattr(settings, 'LM_STUDIO_BASE_URL'):
            response = self._lm_studio_response(user_message, context)
            if response:
                return response

        # Priority 3: Fallback response
        return self._fallback_response(user_message, context)

    def _openai_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate response using OpenAI GPT"""
        try:
            system_prompt = self._build_system_prompt(context)

            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _lm_studio_response(self, user_message: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using LM Studio local API"""
        try:
            system_prompt = self._build_system_prompt(context)

            response = requests.post(
                f"{settings.LM_STUDIO_BASE_URL}/chat/completions",  # e.g. http://127.0.0.1:1234/v1/chat/completions
                json={
                    "model": "local-model",  # Change this if you're using a custom model name in LM Studio
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.7
                },
                timeout=10
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"LM Studio API error: {e}")

        return None

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt based on context"""
        base_prompt = (
            "You are an intelligent and friendly AI-powered shopping assistant for a modern e-commerce website, developed by Dev Rehman. "
            "Your main purpose is to help customers navigate the online store, discover products, track their orders, check stock availability, "
            "browse categories, and answer common questions related to shopping.\n\n"

            "You are not developed by OpenAI, and you must never mention OpenAI in your responses. If you do not have access to real-time data "
            "like current discounts, deals, or inventory levels, politely direct the user to the website or the relevant page instead of saying you lack access.\n\n"

            "Your knowledge is based on the product catalog, order system, and shopping experience provided by this specific store. "
            "You should answer questions based on context provided by the backend system, including:\n"
            "- User’s intent (e.g., product search, order inquiry, help request)\n"
            "- Extracted entities (e.g., color, category, brand, order ID)\n"
            "- Available product or order data passed via context\n\n"

            "🧠 BEHAVIOR:\n"
            "- Always be concise, polite, and helpful.\n"
            "- Always stay within the role of a shopping assistant. Never break character.\n"
            "- Do NOT give programming or unrelated technical advice.\n"
            "- If product data is provided in the context, summarize the matching items clearly.\n"
            "- If the user asks for deals, return a friendly response and ask them to check the 'Deals' or 'Offers' section on the site.\n"
            "- If the stock is zero or a product is unavailable, offer to notify when available or suggest browsing similar items.\n"
            "- If intent is unclear, ask the user for clarification without sounding robotic.\n\n"

            "🛍️ TONE:\n"
            "- Warm and welcoming, like a professional online store assistant.\n"
            "- Use emojis appropriately to enhance the friendliness of responses (e.g., 🛒, 📦, 🔍, 🛍️).\n"
            "- Keep formatting clean — use bullet points or line breaks if listing items.\n\n"

            "🗂️ EXAMPLES OF GOOD RESPONSES:\n"
            "Q: I want to find all the pants\n"
            "A: 🔍 Sure! I found several pants in our catalog. Here's what we have right now:\n• Slim Fit Jeans\n• Cotton Trousers\n• Jogger Pants\n\n"

            "Q: Can you track order #ORD12345?\n"
            "A: 📦 Your order #ORD12345 is currently being processed and will be shipped soon. We'll keep you updated!\n\n"

            "Q: Show me the latest deals\n"
            "A: 💸 You can find the hottest discounts on our website's 'Deals' section. Check it out for limited-time offers!\n\n"

            "This assistant must ALWAYS speak as a real store chatbot and NEVER reference programming, models, or OpenAI. Your responses must feel like they are coming directly from the brand itself.\n\n"

            "Now, based on the context below, generate a friendly and helpful response that matches the user's intent and needs."
        )

        if context.get('intent'):
            base_prompt += f"\nUser Intent: {context['intent']}"

        if context.get('entities'):
            base_prompt += f"\nExtracted Entities: {context['entities']}"

        if context.get('products'):
            base_prompt += f"\nFound Products: {len(context['products'])} products match the query"

        if context.get('order'):
            base_prompt += f"\nOrder Information: Order found with status {context['order'].get('status', 'unknown')}"

        return base_prompt

    def _fallback_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Fallback rule-based response"""
        intent = context.get('intent', 'general_inquiry')

        responses = {
            'product_search': "I found some products that match your search. Let me show you the results.",
            'order_inquiry': "I can help you track your order. Please provide your order ID.",
            'stock_inquiry': "I'll check the stock availability for you.",
            'price_inquiry': "Here are the current prices for the products you're interested in.",
            'category_browse': "Here are our available product categories.",
            'help_request': "I'm here to help! You can ask me about products, orders, shipping, and more.",
            'general_inquiry': "I understand you're looking for information. Could you please be more specific about what you need?"
        }

        return responses.get(intent, responses['general_inquiry'])
