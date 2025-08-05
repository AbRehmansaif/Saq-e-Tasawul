from django.urls import path
from .views import HybridRecommendationAPIView, HomeRecommendationAPIView

urlpatterns = [
    path('hybrid/<int:product_id>/', HybridRecommendationAPIView.as_view(), name='hybrid-recommendation'),
    path('hybrid/', HomeRecommendationAPIView.as_view(), name='home-recommendation'),
]
