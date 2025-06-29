import openai
import requests
from typing import Dict, Any, Optional
from django.conf import settings

class LLMService:
    """Handle Large Language Model integrations"""
    
    def __init__(self):
        self.openai_client = None
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
    
    def generate_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate response using available LLM"""
        
        # Try OpenAI first
        if self.openai_client:
            return self._openai_response(user_message, context)
        
        # Try LM Studio
        if hasattr(settings, 'LM_STUDIO_BASE_URL'):
            response = self._lm_studio_response(user_message, context)
            if response:
                return response
        
        # Fallback to rule-based response
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
                f"{settings.LM_STUDIO_BASE_URL}/chat/completions",
                json={
                    "model": "local-model",
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
        base_prompt = """You are a helpful AI shopping assistant for an e-commerce platform. 
        You help customers find products, check order status, and provide shopping assistance.
        
        Keep responses concise, friendly, and helpful. Focus on the customer's needs.
        
        Available context:"""
        
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