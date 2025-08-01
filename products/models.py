# from django.db import models
# from shortuuidfield import ShortUUIDField
# from decimal import Decimal
# import math

# class Product(models.Model):
#     pid = ShortUUIDField(
#         unique=True
#     )
#     user = models.ForeignKey(
#         'auth.User', on_delete=models.SET_NULL, 
#         null=True
#     )
#     title = models.CharField(
#         max_length=100
#     )
#     image = models.ImageField(
#         upload_to='products/', blank=True, 
#         null=True
#     )
#     base_price = models.DecimalField(
#         max_digits=12, decimal_places=2
#     )
#     max_price = models.DecimalField(
#         max_digits=12, decimal_places=2
#     )
#     selling_price = models.DecimalField(
#         max_digits=12, decimal_places=2, 
#     )
#     stock_count = models.CharField(
#         max_length=100, default="10", 
#         null=True, blank=True
#     )
#     weekly_sales = models.IntegerField(
#         default=0
#     )
#     last_week_sales = models.IntegerField(
#         default=0
#     )
#     in_stock = models.BooleanField(
#         default=True
#     )
#     price_adjustment_step = models.DecimalField(
#         max_digits=5, decimal_places=2, 
#         default=0.50
#     )  # Step size for price changes
#     demand_threshold_high = models.IntegerField(
#         default=20
#     )  # Sales above this = high demand
#     demand_threshold_low = models.IntegerField(
#         default=5
#     )   # Sales below this = low demand
#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True
#     )
#     demand_high = models.IntegerField(
#         default=100, verbose_name="High Demand Threshold"
#     )
#     demand_low = models.IntegerField(
#         default=20, verbose_name="Low Demand Threshold"
#     )

#     def save(self, *args, **kwargs):
#         # Set initial selling price as average if not set
#         if not self.selling_price:
#             self.selling_price = (self.base_price + self.max_price) / 2
#         super().save(*args, **kwargs)

#     def calculate_demand_score(self):
#         """Calculate demand score based on current vs previous week sales"""
#         if self.last_week_sales == 0:
#             return 1.0  # Neutral if no previous data
        
#         # Calculate percentage change
#         change_ratio = self.weekly_sales / self.last_week_sales
        
#         # Convert to demand score (1.0 = neutral, >1.0 = increasing demand, <1.0 = decreasing)
#         return change_ratio

#     def get_predicted_price(self):
#         """Get AI-predicted price with step-wise adjustments"""
#         try:
#             import joblib
#             import pandas as pd
#             from datetime import date
#             import os
            
#             # Load the trained model
#             model_path = os.path.join('pricing_model.pkl')
#             if not os.path.exists(model_path):
#                 return self.apply_demand_based_pricing()
            
#             model = joblib.load(model_path)
            
#             # Prepare input data
#             input_df = pd.DataFrame([{
#                 'product_id': hash(self.id) % 10000,
#                 'weekly_sales': self.weekly_sales,
#                 'prev_week_sales': self.last_week_sales,
#                 'stock_count': int(self.stock_count) if self.stock_count else 0,
#                 'date': date.today().toordinal(),
#                 'current_price': float(self.selling_price or self.base_price),
#                 'demand_score': self.calculate_demand_score(),
#             }])
            
#             # Get prediction
#             predicted_price = model.predict(input_df)[0]
            
#             # Apply constraints and return
#             return round(min(max(predicted_price, float(self.base_price)), float(self.max_price)), 2)
            
#         except Exception as e:
#             print(f"ML prediction failed: {e}")
#             return self.apply_demand_based_pricing()

#     def apply_demand_based_pricing(self):
#         """Apply rule-based step-wise pricing based on demand"""
#         current_price = Decimal(str(self.selling_price or self.base_price))
#         demand_score = self.calculate_demand_score()
        
#         # Determine price adjustment direction and magnitude
#         if self.weekly_sales > self.demand_threshold_high:
#             # High demand - increase price in steps
#             steps = math.ceil((self.weekly_sales - self.demand_threshold_high) / 5)  # 1 step per 5 extra sales
#             adjustment = min(steps * self.price_adjustment_step, self.max_price - current_price)
#             new_price = current_price + Decimal(str(adjustment))
            
#         elif self.weekly_sales < self.demand_threshold_low:
#             # Low demand - decrease price in steps
#             deficit = self.demand_threshold_low - self.weekly_sales
#             steps = math.ceil(deficit / 3)  # 1 step per 3 sales deficit
#             adjustment = min(steps * self.price_adjustment_step, current_price - self.base_price)
#             new_price = current_price - Decimal(str(adjustment))
            
#         else:
#             # Moderate demand - small adjustments based on trend
#             if demand_score > 1.2:  # 20% increase
#                 new_price = current_price + (self.price_adjustment_step / 2)
#             elif demand_score < 0.8:  # 20% decrease
#                 new_price = current_price - (self.price_adjustment_step / 2)
#             else:
#                 new_price = current_price  # No change
        
#         # Ensure price stays within bounds
#         new_price = max(self.base_price, min(new_price, self.max_price))
#         return float(new_price)

#     def update_price(self):
#         """Update the selling price based on AI/ML prediction"""
#         new_price = self.get_predicted_price()
#         old_price = self.selling_price
#         self.selling_price = Decimal(str(new_price))
#         self.save()
        
#         # Log the price change
#         PriceChangeLog.objects.create(
#             product=self,
#             old_price=old_price,
#             new_price=self.selling_price,
#             weekly_sales=self.weekly_sales,
#             demand_score=self.calculate_demand_score()
#         )
        
#         return new_price

#     def __str__(self):
#         return self.title

# class ProductSalesHistory(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_history')
#     date = models.DateField(auto_now_add=True)
#     weekly_sales = models.IntegerField()
#     selling_price = models.DecimalField(max_digits=12, decimal_places=2)
#     stock_count = models.IntegerField(default=0)
#     demand_score = models.FloatField(default=1.0)

#     class Meta:
#         ordering = ['-date']

#     def __str__(self):
#         return f"{self.product.title} - {self.date}"

# class PriceChangeLog(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_changes')
#     old_price = models.DecimalField(max_digits=12, decimal_places=2)
#     new_price = models.DecimalField(max_digits=12, decimal_places=2)
#     weekly_sales = models.IntegerField()
#     demand_score = models.FloatField()
#     timestamp = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-timestamp']

#     def __str__(self):
#         return f"{self.product.title}: ${self.old_price} → ${self.new_price}"