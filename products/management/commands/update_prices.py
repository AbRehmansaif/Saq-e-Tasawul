from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = 'Update prices for all products based on demand'

    def handle(self, *args, **options):
        products = Product.objects.filter(in_stock=True)
        updated_count = 0
        
        for product in products:
            old_price = product.selling_price
            new_price = product.update_price()
            
            if old_price != new_price:
                updated_count += 1
                self.stdout.write(
                    f'{product.title}: ${old_price} → ${new_price}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} product prices')
        )
