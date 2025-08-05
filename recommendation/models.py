from django.db import models
from django.conf import settings
from core.models import Product

class RecommendationCache(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    recommended_products = models.JSONField()  # Stores product IDs
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name_plural = "Recommendation Cache"

    def __str__(self):
        return f"Recommendations for {self.user} - {self.product.title}"
