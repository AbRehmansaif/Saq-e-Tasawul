import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from products.models import Product, PriceChangeLog


@staff_member_required
def pricing_dashboard(request):
    """Render the pricing dashboard with all required data"""
    # Get all products
    products = Product.objects.all()
    
    # Get recent price changes (last 20)
    recent_changes = PriceChangeLog.objects.select_related('product').order_by('-timestamp')[:20]
    
    # Prepare statistics
    stats = {
        'total_products': products.count(),
        'high_demand': products.filter(weekly_sales__gt=100).count(),  # Example threshold
    }
    
    # Prepare data for JavaScript
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'title': product.title,
            'selling_price': float(product.selling_price),
            'base_price': float(product.base_price),
            'max_price': float(product.max_price),
            'weekly_sales': product.weekly_sales,
            'last_week_sales': product.last_week_sales,
            'demand_high': product.demand_high,
            'demand_low': product.demand_low,
            'stock_count': product.stock_count,
            'in_stock': product.in_stock, 
        })
    
    changes_data = []
    for change in recent_changes:
        changes_data.append({
            'product_title': change.product.title,
            'old_price': float(change.old_price),
            'new_price': float(change.new_price),
            'timestamp': change.timestamp.isoformat(),
        })
    
    context = {
        'stats': stats,
        'recent_changes': recent_changes,
        'products_json': json.dumps(products_data),
        'changes_json': json.dumps(changes_data),
    }
    
    return render(request, 'admin/pricing_dashboard.html', context)

@staff_member_required
def pricing_api_update(request, product_id):
    """API endpoint to update product price"""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, pk=product_id)
            old_price = product.selling_price
            new_price = product.update_price()
            
            # Create price change record
            PriceChange.objects.create(
                product=product,
                old_price=old_price,
                new_price=new_price
            )
            
            return JsonResponse({
                'success': True,
                'old_price': float(old_price),
                'new_price': float(new_price),
                'product': product.title
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method'
    }, status=405)

@staff_member_required
def pricing_api_bulk_update(request):
    """API endpoint to update prices for multiple products"""
    if request.method == 'POST':
        try:
            product_ids = json.loads(request.body).get('product_ids', [])
            results = []
            
            for product_id in product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    old_price = product.selling_price
                    new_price = product.update_price()
                    
                    # Create price change record
                    PriceChange.objects.create(
                        product=product,
                        old_price=old_price,
                        new_price=new_price
                    )
                    
                    results.append({
                        'success': True,
                        'product_id': product_id,
                        'old_price': float(old_price),
                        'new_price': float(new_price)
                    })
                except Exception as e:
                    results.append({
                        'success': False,
                        'product_id': product_id,
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'results': results
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method'
    }, status=405)

@staff_member_required
def pricing_analytics(request):
    """View for pricing analytics dashboard"""
    try:
        # Get all products
        products = Product.objects.all()
        
        # Get recent price changes (last 50)
        recent_changes = PriceChangeLog.objects.select_related('product').order_by('-timestamp')[:50]
        
        # Convert products to list of dictionaries for JSON serialization
        products_data = []
        for product in products:
            products_data.append({
                'title': product.title,
                'selling_price': float(product.selling_price),
                'base_price': float(product.base_price),
                'max_price': float(product.max_price),
                'weekly_sales': product.weekly_sales,
                'last_week_sales': product.last_week_sales,
                'demand_high': product.demand_threshold_high,
                'demand_low': product.demand_threshold_low
            })
        
        # Convert recent changes to list of dictionaries
        changes_data = []
        for change in recent_changes:
            changes_data.append({
                'product_title': change.product.title,
                'old_price': float(change.old_price),
                'new_price': float(change.new_price),
                'timestamp': change.timestamp.isoformat(),
                'reason': getattr(change, 'reason', 'Auto-adjustment')
            })
        
        # Calculate statistics
        total_products = len(products_data)
        high_demand_count = sum(1 for p in products_data if p['weekly_sales'] > p['demand_high'])
        low_demand_count = sum(1 for p in products_data if p['weekly_sales'] < p['demand_low'])
        normal_demand_count = total_products - high_demand_count - low_demand_count
        
        # Calculate average margin
        total_revenue = sum(p['selling_price'] * p['weekly_sales'] for p in products_data)
        total_cost = sum(p['base_price'] * p['weekly_sales'] for p in products_data)
        avg_margin = 0
        if total_revenue > 0:
            avg_margin = round(((total_revenue - total_cost) / total_revenue) * 100, 1)
        
        context = {
            'products_json': json.dumps(products_data),
            'changes_json': json.dumps(changes_data),
            'stats': {
                'total_products': total_products,
                'high_demand': high_demand_count,
                'low_demand': low_demand_count,
                'normal_demand': normal_demand_count,
                'avg_margin': avg_margin
            }
        }
        
        return render(request, 'pricing/analytics.html', context)
        
    except Exception as e:
        # Handle any errors gracefully
        context = {
            'products_json': json.dumps([]),
            'changes_json': json.dumps([]),
            'stats': {
                'total_products': 0,
                'high_demand': 0,
                'low_demand': 0,
                'normal_demand': 0,
                'avg_margin': 0
            },
            'error_message': f"Error loading analytics data: {str(e)}"
        }
        
        return render(request, 'pricing/analytics.html', context)

# Optional: Add a bulk price update endpoint
@staff_member_required 
@csrf_exempt
def bulk_price_update(request):
    """API endpoint to update prices for multiple products"""
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            product_ids = data.get('product_ids', [])
            
            results = []
            for product_id in product_ids:
                try:
                    product = get_object_or_404(Product, pk=product_id)
                    old_price = product.selling_price
                    new_price = product.update_price()
                    
                    results.append({
                        'product_id': product_id,
                        'product_title': product.title,
                        'success': True,
                        'old_price': float(old_price),
                        'new_price': float(new_price)
                    })
                except Exception as e:
                    results.append({
                        'product_id': product_id,
                        'success': False,
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'results': results
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)