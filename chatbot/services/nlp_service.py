import spacy
import re
from typing import Dict, List, Tuple, Any
from django.conf import settings
from core.models import Product, CartOrder

class NLPService:
    """Handle NLP processing using spaCy"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, use basic tokenizer
            print("Warning: spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from user input"""
        entities = {
            'products': [],
            'order_ids': [],
            'colors': [],
            'brands': [],
            'price_ranges': [],
            'categories': [],
            'quantities': []
        }
        
        if not self.nlp:
            return self._fallback_extraction(text)
        
        doc = self.nlp(text.lower())
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG"]:
                entities['brands'].append(ent.text)
            elif ent.label_ == "MONEY":
                entities['price_ranges'].append(ent.text)
            elif ent.label_ == "CARDINAL":
                entities['quantities'].append(ent.text)
        
        # Extract order IDs using regex
        order_patterns = [
            r'\b(ORD|ORDER|BUY)\d+\b',
            r'\b\d{5,10}\b',  # 5-10 digit numbers
            r'#\w+\d+',
        ]
        
        for pattern in order_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['order_ids'].extend(matches)
        
        # Extract colors
        colors = [
            'red', 'blue', 'green', 'yellow', 'black', 'white', 'pink', 
            'purple', 'orange', 'brown', 'gray', 'grey', 'silver', 'gold'
        ]
        for color in colors:
            if color in text.lower():
                entities['colors'].append(color)
        
        # Extract product categories
        categories = [
            'shoes', 'shirt', 'pants', 'dress', 'phone', 'laptop', 'watch',
            'headphones', 'electronics', 'clothing', 'accessories'
        ]
        for category in categories:
            if category in text.lower():
                entities['categories'].append(category)
        
        return entities
    
    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback extraction without spaCy"""
        entities = {
            'products': [],
            'order_ids': [],
            'colors': [],
            'brands': [],
            'price_ranges': [],
            'categories': [],
            'quantities': []
        }
        
        # Simple regex-based extraction
        order_patterns = [
            r'\b(ORD|ORDER|BUY)\d+\b',
            r'\b\d{5,10}\b',
            r'#\w+\d+',
        ]
        
        for pattern in order_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['order_ids'].extend(matches)
        
        # Extract colors and categories (same as above)
        colors = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'pink', 'purple', 'orange', 'brown', 'gray', 'grey', 'silver', 'gold']
        for color in colors:
            if color in text.lower():
                entities['colors'].append(color)
        
        categories = ['shoes', 'shirt', 'pants', 'dress', 'phone', 'laptop', 'watch', 'headphones', 'electronics', 'clothing', 'accessories']
        for category in categories:
            if category in text.lower():
                entities['categories'].append(category)
        
        return entities
    
    def classify_intent(self, text: str, entities: Dict[str, Any]) -> str:
        """Classify user intent based on text and entities"""
        text_lower = text.lower()
        
        # Order-related intents
        if any(keyword in text_lower for keyword in ['order', 'track', 'delivery', 'shipped', 'status']) or entities['order_ids']:
            return 'order_inquiry'
        
        # Product search intents
        if any(keyword in text_lower for keyword in ['search', 'find', 'show', 'looking for', 'want', 'need', 'buy']):
            return 'product_search'
        
        # Stock inquiry
        if any(keyword in text_lower for keyword in ['stock', 'available', 'in stock', 'inventory']):
            return 'stock_inquiry'
        
        # Price inquiry
        if any(keyword in text_lower for keyword in ['price', 'cost', 'how much', 'expensive', 'cheap']):
            return 'price_inquiry'
        
        # Category browsing
        if any(keyword in text_lower for keyword in ['category', 'browse', 'section', 'department']):
            return 'category_browse'
        
        # Help/Support
        if any(keyword in text_lower for keyword in ['help', 'support', 'assist', 'question']):
            return 'help_request'
        
        # Default
        return 'general_inquiry'