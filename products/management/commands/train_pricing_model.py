from django.core.management.base import BaseCommand
from products.ml.train_model import train_price_model

class Command(BaseCommand):
    help = 'Train the dynamic pricing ML model'

    def handle(self, *args, **options):
        self.stdout.write('Starting model training...')
        try:
            train_price_model()
            self.stdout.write(
                self.style.SUCCESS('Successfully trained pricing model')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error training model: {str(e)}')
            )
