import math
from decimal import Decimal
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone

STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)


STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)


RATING = (
    (1,  "★☆☆☆☆"),
    (2,  "★★☆☆☆"),
    (3,  "★★★☆☆"),
    (4,  "★★★★☆"),
    (5,  "★★★★★"),
)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20,
                         prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Food")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def product_count(self):
        return Product.objects.filter(category=self).count()

    def __str__(self):
        return self.title


class Tags(models.Model):
    pass


class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20,
                         prefix="ven", alphabet="abcdefgh12345")

    title = models.CharField(max_length=100, default="Nestify")
    image = models.ImageField(
        upload_to=user_directory_path, default="vendor.jpg")
    cover_image = models.ImageField(
        upload_to=user_directory_path, default="vendor.jpg")
    # description = models.TextField(null=True, blank=True, default="I am am Amazing Vendor")
    description = CKEditor5Field(config_name='extends', null=True, blank=True)

    address = models.CharField(max_length=100, default="123 Main Street.")
    contact = models.CharField(max_length=100, default="+123 (456) 789")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title


class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10,
                         max_length=20, alphabet="abcdefgh12345")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL, null=True, related_name="product")

    title = models.CharField(max_length=100, default="Fresh Pear")
    image = models.ImageField(
        upload_to=user_directory_path, default="product.jpg")
    # description = models.TextField(null=True, blank=True, default="This is the product")
    description = CKEditor5Field(config_name='extends', null=True, blank=True)

    price = models.DecimalField(
        max_digits=12, decimal_places=2, default="0.00")
    old_price = models.DecimalField(
        max_digits=12, decimal_places=2, default="2.99")
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2
    )
    max_price = models.DecimalField(
        max_digits=12, decimal_places=2
    )
    selling_price = models.DecimalField(
        max_digits=12, decimal_places=2, 
    )
    specifications = CKEditor5Field(config_name='extends', null=True, blank=True)
    # specifications = models.TextField(null=True, blank=True)
    type = models.CharField(
        max_length=100, default="Organic", null=True, blank=True)
    stock_count = models.CharField(
        max_length=100, default="10", null=True, blank=True)
    life = models.CharField(
        max_length=100, default="100 Days", null=True, blank=True)
    mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    weekly_sales = models.IntegerField(
        default=0
    )
    last_week_sales = models.IntegerField(
        default=0
    )
    tags = TaggableManager(blank=True)
    price_adjustment_step = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=0.50
    )  # Step size for price changes
    demand_threshold_high = models.IntegerField(
        default=20
    )  # Sales above this = high demand
    demand_threshold_low = models.IntegerField(
        default=5
    )
    # tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)

    product_status = models.CharField(
        choices=STATUS, max_length=10, default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10,
                         prefix="sku", alphabet="1234567890")
    demand_high = models.IntegerField(
        default=100, verbose_name="High Demand Threshold"
    )
    demand_low = models.IntegerField(
        default=20, verbose_name="Low Demand Threshold"
    )
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_precentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price

    def save(self, *args, **kwargs):
        # Set initial selling price as average if not set
        if not self.selling_price:
            self.selling_price = (self.base_price + self.max_price) / 2
        super().save(*args, **kwargs)

    def calculate_demand_score(self):
        """Calculate demand score based on current vs previous week sales"""
        if self.last_week_sales == 0:
            return 1.0  # Neutral if no previous data
        
        # Calculate percentage change
        change_ratio = self.weekly_sales / self.last_week_sales
        
        # Convert to demand score (1.0 = neutral, >1.0 = increasing demand, <1.0 = decreasing)
        return change_ratio

    def get_predicted_price(self):
        """Get AI-predicted price with step-wise adjustments"""
        try:
            import joblib
            import pandas as pd
            from datetime import date
            import os
            
            # Load the trained model
            model_path = os.path.join('pricing_model.pkl')
            if not os.path.exists(model_path):
                return self.apply_demand_based_pricing()
            
            model = joblib.load(model_path)
            
            # Prepare input data
            input_df = pd.DataFrame([{
                'product_id': hash(self.id) % 10000,
                'weekly_sales': self.weekly_sales,
                'prev_week_sales': self.last_week_sales,
                'stock_count': int(self.stock_count) if self.stock_count else 0,
                'date': date.today().toordinal(),
                'current_price': float(self.selling_price or self.base_price),
                'demand_score': self.calculate_demand_score(),
            }])
            
            # Get prediction
            predicted_price = model.predict(input_df)[0]
            
            # Apply constraints and return
            return round(min(max(predicted_price, float(self.base_price)), float(self.max_price)), 2)
            
        except Exception as e:
            print(f"ML prediction failed: {e}")
            return self.apply_demand_based_pricing()

    def apply_demand_based_pricing(self):
        """Apply rule-based step-wise pricing based on demand"""
        current_price = Decimal(str(self.selling_price or self.base_price))
        demand_score = self.calculate_demand_score()
        
        # Determine price adjustment direction and magnitude
        if self.weekly_sales > self.demand_threshold_high:
            # High demand - increase price in steps
            steps = math.ceil((self.weekly_sales - self.demand_threshold_high) / 5)  # 1 step per 5 extra sales
            adjustment = min(steps * self.price_adjustment_step, self.max_price - current_price)
            new_price = current_price + Decimal(str(adjustment))
            
        elif self.weekly_sales < self.demand_threshold_low:
            # Low demand - decrease price in steps
            deficit = self.demand_threshold_low - self.weekly_sales
            steps = math.ceil(deficit / 3)  # 1 step per 3 sales deficit
            adjustment = min(steps * self.price_adjustment_step, current_price - self.base_price)
            new_price = current_price - Decimal(str(adjustment))
            
        else:
            # Moderate demand - small adjustments based on trend
            if demand_score > 1.2:  # 20% increase
                new_price = current_price + (self.price_adjustment_step / 2)
            elif demand_score < 0.8:  # 20% decrease
                new_price = current_price - (self.price_adjustment_step / 2)
            else:
                new_price = current_price  # No change
        
        # Ensure price stays within bounds
        new_price = max(self.base_price, min(new_price, self.max_price))
        return float(new_price)

    def update_price(self):
        """Update the selling price based on AI/ML prediction"""
        new_price = self.get_predicted_price()
        old_price = self.selling_price
        self.selling_price = Decimal(str(new_price))
        self.price = self.selling_price  # Sync price field for frontend
        self.save()
        
        # Log the price change
        PriceChangeLog.objects.create(
            product=self,
            old_price=old_price,
            new_price=self.selling_price,
            weekly_sales=self.weekly_sales,
            demand_score=self.calculate_demand_score()
        )
        
        return new_price

    def __str__(self):
        return self.title

class ProductSalesHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_history')
    date = models.DateField(auto_now_add=True)
    weekly_sales = models.IntegerField()
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_count = models.IntegerField(default=0)
    demand_score = models.FloatField(default=1.0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.product.title} - {self.date}"

class PriceChangeLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_changes')
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    weekly_sales = models.IntegerField()
    demand_score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']


class ProductImages(models.Model):
    images = models.ImageField(
        upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(
        Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"


############################################## Cart, Order, OrderITems and Address ##################################
############################################## Cart, Order, OrderITems and Address ##################################
############################################## Cart, Order, OrderITems and Address ##################################
############################################## Cart, Order, OrderITems and Address ##################################


class CartOrder(models.Model):
    PAYMENT_METHODS = (
        ("PAID", "Paid"),
        ("COD", "Cash on Delivery"),
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default="PAID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    coupons = models.ManyToManyField("core.Coupon", blank=True)
    
    shipping_method = models.CharField(max_length=100, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_website_address = models.CharField(max_length=100, null=True, blank=True)


    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    sku = ShortUUIDField(null=True, blank=True, length=5,prefix="SKU", max_length=20, alphabet="1234567890")
    oid = ShortUUIDField(null=True, blank=True, length=8, max_length=20, alphabet="1234567890")
    stripe_payment_intent = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Cart Order"


class CartOrderProducts(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    total = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))


############################################## Product Revew, wishlists, Address ##################################
############################################## Product Revew, wishlists, Address ##################################
############################################## Product Revew, wishlists, Address ##################################
############################################## Product Revew, wishlists, Address ##################################


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        if self.product:
            return self.product.title
        else:
            return f"review - {self.pk}"

    def get_rating(self):
        return self.rating


class wishlist_model(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "wishlists"

    def __str__(self):
        return self.product.title


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mobile = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"


class Coupon(models.Model):
    code = models.CharField(max_length=1000)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code}"
    