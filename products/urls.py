from django.urls import path
from products import views

urlpatterns = [
    path('dashboard/', views.pricing_dashboard, name='pricing_dashboard'),
    path('api/update/<int:product_id>/', views.pricing_api_update, name='pricing_api_update'),
    path('api/bulk-update/', views.pricing_api_bulk_update, name='pricing_api_bulk_update'),
    path('api/train-model/', views.train_ml_model, name='train_ml_model'),
]