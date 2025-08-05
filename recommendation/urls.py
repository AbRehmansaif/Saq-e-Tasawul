from django.urls import path
from .views import HybridRecommendationAPIView

urlpatterns = [
    path('hybrid/<int:product_id>/', HybridRecommendationAPIView.as_view(), name='hybrid-recommendation'),
]
