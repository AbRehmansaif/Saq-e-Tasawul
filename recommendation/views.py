from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Product
from .utils import get_hybrid_recommendations
from .models import RecommendationCache
from django.shortcuts import get_object_or_404
from rest_framework.renderers import JSONRenderer

# class HybridRecommendationAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, product_id):
#         user = request.user
#         product = get_object_or_404(Product, id=product_id)

#         # Cache lookup
#         cache = RecommendationCache.objects.filter(user=user, product=product).first()
#         if cache:
#             product_ids = cache.recommended_products
#             recommended_products = Product.objects.filter(id__in=product_ids)
#         else:
#             recommended_products = get_hybrid_recommendations(user.id, product.id)
#             RecommendationCache.objects.create(
#                 user=user,
#                 product=product,
#                 recommended_products=[p.id for p in recommended_products]
#             )

#         data = [
#             {
#                 "id": p.id,
#                 "title": p.title,
#                 "price": float(p.price),
#                 "image": p.image.url if p.image else None
#             }
#             for p in recommended_products
#         ]
#         return Response({"status": "success", "recommendations": data})


# class HybridRecommendationAPIView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, product_id):
#         user = request.user
        
#         cache = RecommendationCache.objects.filter(user=user, product_id=product_id).first()
#         if cache:
#             product_ids = cache.recommended_products
#             recommended_products = Product.objects.filter(id__in=product_ids)
#         else:
#             recommended_products = get_hybrid_recommendations(user.id, product_id)
#             RecommendationCache.objects.create(
#                 user=user,
#                 product_id=product_id,
#                 recommended_products=[p.id for p in recommended_products]
#             )
        
#         data = [
#             {
#                 "id": p.id,
#                 "title": p.title,
#                 "price": float(p.price),
#                 "image": p.image.url if p.image else None
#             }
#             for p in recommended_products
#         ]
#         return Response({"status": "success", "recommendations": data})

import logging
logger = logging.getLogger(__name__)

class HybridRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, product_id):
        user = request.user
        logger.info("🔍 Running Hybrid Recommendation API for User %s, Product %s", user.id, product_id)

        recommended_products = get_hybrid_recommendations(user.id, product_id)

        logger.info("✅ View received recommendations: %s", [p.id for p in recommended_products])

        data = [
            {
                "id": p.id,
                "pid": getattr(p, 'pid', None),
                "title": p.title,
                "price": float(p.price),
                "image": p.image.url if p.image else None
            }
            for p in recommended_products
        ]
        return Response({"status": "success", "recommendations": data})

class HomeRecommendationAPIView(APIView):
    renderer_classes = [JSONRenderer]
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        # For demo: recommend top 8 products, or use a utility for general recommendations
        if user:
            # If you want to use hybrid logic for user, you can call get_hybrid_recommendations(user.id, None)
            products = Product.objects.all().order_by('-id')[:8]
        else:
            products = Product.objects.all().order_by('-id')[:8]
        data = [
            {
                "id": p.id,
                "pid": getattr(p, 'pid', None),
                "title": p.title,
                "price": float(p.price),
                "image": p.image.url if p.image else None
            }
            for p in products
        ]
        return Response({"status": "success", "recommendations": data})