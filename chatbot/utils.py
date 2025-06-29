import re
from typing import List, Dict, Any
from django.utils import timezone
from datetime import timedelta

def clean_text(text: str) -> str:
    """Clean and normalize text input"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-.,!?]', '', text)
    
    return text.strip()

def extract_price_range(text: str) -> Dict[str, float]:
    """Extract price range from text"""
    price_patterns = [
        r'\$(\d+(?:\.\d{2})?)\s*-\s*\$(\d+(?:\.\d{2})?)',  # $10 - $20
        r'(\d+(?:\.\d{2})?)\s*-\s*(\d+(?:\.\d{2})?)',      # 10 - 20
        r'under\s+\$?(\d+(?:\.\d{2})?)',                   # under $20
        r'below\s+\$?(\d+(?:\.\d{2})?)',                   # below $20
        r'above\s+\$?(\d+(?:\.\d{2})?)',                   # above $20
        r'over\s+\$?(\d+(?:\.\d{2})?)',                    # over $20
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'under' in pattern or 'below' in pattern:
                return {'max_price': float(match.group(1))}
            elif 'above' in pattern or 'over' in pattern:
                return {'min_price': float(match.group(1))}
            else:
                return {
                    'min_price': float(match.group(1)),
                    'max_price': float(match.group(2))
                }
    
    return {}

def get_chat_suggestions(intent: str, context: Dict[str, Any]) -> List[str]:
    """Generate contextual chat suggestions"""
    base_suggestions = {
        'product_search': [
            "Show more details",
            "Check availability", 
            "Compare prices",
            "Add to cart",
            "Find similar items"
        ],
        'order_inquiry': [
            "Track package",
            "Update delivery address",
            "Contact support",
            "Cancel order",
            "Order again"
        ],
        'stock_inquiry': [
            "Notify when available",
            "Find alternatives",
            "Check other stores",
            "Pre-order",
            "Add to wishlist"
        ],
        'help_request': [
            "Find products",
            "Track order",
            "Return policy",
            "Contact support",
            "FAQ"
        ]
    }
    
    return base_suggestions.get(intent, [
        "Search products",
        "Track order", 
        "Browse categories",
        "Get help"
    ])

def log_chat_analytics(session_id: str, intent: str, entities: Dict[str, Any]):
    """Log chat analytics (placeholder for future analytics system)"""
    analytics_data = {
        'session_id': session_id,
        'intent': intent,
        'entities': entities,
        'timestamp': timezone.now().isoformat()
    }
    
    # Here you could send to analytics service, log to file, etc.
    print(f"Analytics: {analytics_data}")

def is_session_expired(session_created_at, hours=24):
    """Check if chat session is expired"""
    expiry_time = session_created_at + timedelta(hours=hours)
    return timezone.now() > expiry_time