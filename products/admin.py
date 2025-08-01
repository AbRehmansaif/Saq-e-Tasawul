from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from core.models import Product, ProductSalesHistory, PriceChangeLog
from products.ml.train_model import train_price_model
import csv


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'base_price', 'max_price', 'selling_price', 
        'weekly_sales', 'last_week_sales', 'demand_indicator',
        'stock_count', 'in_stock', 'price_actions'
    ]
    list_filter = ['in_stock', 'created_at']
    search_fields = ['title', 'pid']
    readonly_fields = ['pid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('pid', 'user', 'title', 'image')
        }),
        ('Pricing', {
            'fields': ('base_price', 'max_price', 'selling_price', 'price_adjustment_step')
        }),
        ('Inventory & Sales', {
            'fields': ('stock_count', 'in_stock', 'weekly_sales', 'last_week_sales')
        }),
        ('Demand Settings', {
            'fields': ('demand_threshold_high', 'demand_threshold_low')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def demand_indicator(self, obj):
        score = obj.calculate_demand_score()
        if score > 1.2:
            color = 'green'
            text = 'High ↑'
        elif score < 0.8:
            color = 'red'
            text = 'Low ↓'
        else:
            color = 'orange'
            text = 'Normal →'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    demand_indicator.short_description = 'Demand'

    def price_actions(self, obj):
        return format_html(
            '<a class="button" href="/admin/pricing/update-price/{}/">Update Price</a>',
            obj.pk
        )
    price_actions.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update-price/<int:product_id>/', self.update_single_price, name='update_single_price'),
            path('update-all-prices/', self.update_all_prices, name='update_all_prices'),
            path('train-model/', self.train_model_view, name='train_model'),
            path('pricing-dashboard/', self.pricing_dashboard, name='pricing_dashboard'),
            path('export-data/', self.export_data, name='export_data'),
        ]
        return custom_urls + urls

    def update_single_price(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            old_price = product.selling_price
            new_price = product.update_price()
            messages.success(
                request, 
                f'Price updated for {product.title}: ${old_price} → ${new_price}'
            )
        except Product.DoesNotExist:
            messages.error(request, 'Product not found')
        except Exception as e:
            messages.error(request, f'Error updating price: {str(e)}')
        
        return redirect('/admin/pricing/product/')

    def update_all_prices(self, request):
        try:
            products = Product.objects.filter(in_stock=True)
            updated_count = 0
            
            for product in products:
                product.update_price()
                updated_count += 1
            
            messages.success(request, f'Updated prices for {updated_count} products')
        except Exception as e:
            messages.error(request, f'Error updating prices: {str(e)}')
        
        return redirect('/admin/pricing/product/')

    def train_model_view(self, request):
        try:
            model = train_price_model()
            messages.success(request, 'ML model trained successfully!')
        except Exception as e:
            messages.error(request, f'Error training model: {str(e)}')
        
        return redirect('/admin/pricing/product/')

    def pricing_dashboard(self, request):
        context = {
            'products': Product.objects.all(),
            'recent_changes': PriceChangeLog.objects.select_related('product')[:20],
            'title': 'Dynamic Pricing Dashboard'
        }
        return render(request, 'admin/pricing_dashboard.html', context)

    def export_data(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pricing_data.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Product', 'Base Price', 'Max Price', 'Current Price', 
            'Weekly Sales', 'Last Week Sales', 'Demand Score', 'Stock'
        ])
        
        for product in Product.objects.all():
            writer.writerow([
                product.title,
                product.base_price,
                product.max_price,
                product.selling_price,
                product.weekly_sales,
                product.last_week_sales,
                product.calculate_demand_score(),
                product.stock_count
            ])
        
        return response

@admin.register(ProductSalesHistory)
class ProductSalesHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'weekly_sales', 'selling_price', 'demand_score']
    list_filter = ['date', 'product']
    readonly_fields = ['date']

@admin.register(PriceChangeLog)
class PriceChangeLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'old_price', 'new_price', 'price_change_amount', 'weekly_sales', 'timestamp']
    list_filter = ['timestamp', 'product']
    readonly_fields = ['timestamp']

    def price_change_amount(self, obj):
        change = obj.new_price - obj.old_price
        color = 'green' if change > 0 else 'red' if change < 0 else 'gray'
        return format_html(
            '<span style="color: {};">${:.2f}</span>',
            color, change
        )
    price_change_amount.short_description = 'Change'