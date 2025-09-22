from django.core.management.base import BaseCommand
from apps.products.models import Product
from apps.products.services import PricingService
import json

class Command(BaseCommand):
    help = 'Demonstrate the advanced pricing system'

    def add_arguments(self, parser):
        parser.add_argument('--product-id', type=int, help='Product ID to demo pricing for')
        parser.add_argument('--quantity', type=int, default=100, help='Quantity for pricing demo')

    def handle(self, *args, **options):
        product_id = options.get('product_id')
        quantity = options.get('quantity')
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id, status='active')
            except Product.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Product with ID {product_id} not found'))
                return
        else:
            # Use the first available product
            product = Product.objects.filter(status='active').first()
            if not product:
                self.stdout.write(self.style.ERROR('No active products found. Run populate_sample_products first.'))
                return
        
        self.stdout.write(f'\n=== Advanced Pricing Demo for {product.name} ===\n')
        
        pricing_service = PricingService()
        
        # Demo 1: Basic pricing
        self.stdout.write(self.style.SUCCESS('1. Basic Pricing:'))
        basic_config = {
            'quantity': quantity,
            'country_code': 'IN'
        }
        
        result = pricing_service.calculate_comprehensive_price(product, basic_config)
        self._display_pricing_result(result)
        
        # Demo 2: Pricing with options (if available)
        options = product.get_active_options()
        if options.exists():
            self.stdout.write(self.style.SUCCESS('\n2. Pricing with Options:'))
            option = options.first()
            option_value = option.values.filter(is_active=True).first()
            
            if option_value:
                options_config = {
                    'quantity': quantity,
                    'options': {option.name: option_value.id},
                    'country_code': 'IN'
                }
                
                result = pricing_service.calculate_comprehensive_price(product, options_config)
                self._display_pricing_result(result)
        
        # Demo 3: Bulk pricing (higher quantity)
        if quantity < 500:
            self.stdout.write(self.style.SUCCESS('\n3. Bulk Pricing (500 quantity):'))
            bulk_config = {
                'quantity': 500,
                'country_code': 'IN'
            }
            
            result = pricing_service.calculate_comprehensive_price(product, bulk_config)
            self._display_pricing_result(result)
        
        # Demo 4: Rush delivery
        self.stdout.write(self.style.SUCCESS('\n4. Rush Delivery Pricing:'))
        rush_config = {
            'quantity': quantity,
            'country_code': 'IN',
            'rush_delivery': True
        }
        
        result = pricing_service.calculate_comprehensive_price(product, rush_config)
        self._display_pricing_result(result)
        
        # Demo 5: Design service
        self.stdout.write(self.style.SUCCESS('\n5. With Design Service:'))
        design_config = {
            'quantity': quantity,
            'country_code': 'IN',
            'design_service': True
        }
        
        result = pricing_service.calculate_comprehensive_price(product, design_config)
        self._display_pricing_result(result)
        
        # Demo 6: Price breaks
        self.stdout.write(self.style.SUCCESS('\n6. Quantity Price Breaks:'))
        price_breaks = pricing_service.get_quantity_price_breaks(product)
        
        self.stdout.write('Quantity\tUnit Price\tTotal Price\tSavings')
        self.stdout.write('-' * 50)
        for pb in price_breaks[:6]:  # Show first 6 price breaks
            savings = pb.get('savings', {})
            savings_text = f"Save ₹{savings.get('amount', 0):.0f}" if savings else "No savings"
            self.stdout.write(f"{pb['quantity']}\t\t₹{pb['unit_price']:.2f}\t\t₹{pb['total_price']:.2f}\t\t{savings_text}")
        
        self.stdout.write(f'\n=== Demo Complete ===')
    
    def _display_pricing_result(self, result):
        """Display pricing result in a formatted way"""
        if result['errors']:
            self.stdout.write(self.style.ERROR(f"Errors: {', '.join(result['errors'])}"))
            return
        
        pricing = result['pricing']
        
        self.stdout.write(f"  Base Price: ₹{pricing['base_price']:.2f}")
        if pricing['variant_cost'] > 0:
            self.stdout.write(f"  Variant Cost: ₹{pricing['variant_cost']:.2f}")
        if pricing['options_cost'] > 0:
            self.stdout.write(f"  Options Cost: ₹{pricing['options_cost']:.2f}")
        if pricing['quantity_discount'] > 0:
            self.stdout.write(f"  Quantity Discount: -₹{pricing['quantity_discount']:.2f}")
        if pricing['setup_fees'] > 0:
            self.stdout.write(f"  Setup Fees: ₹{pricing['setup_fees']:.2f}")
        if pricing['rush_fee'] > 0:
            self.stdout.write(f"  Rush Fee: ₹{pricing['rush_fee']:.2f}")
        if pricing['design_fee'] > 0:
            self.stdout.write(f"  Design Fee: ₹{pricing['design_fee']:.2f}")
        
        self.stdout.write(f"  Subtotal: ₹{pricing['subtotal']:.2f}")
        self.stdout.write(f"  Tax (18%): ₹{pricing['tax']:.2f}")
        self.stdout.write(f"  Shipping: ₹{pricing['shipping']:.2f}")
        self.stdout.write(self.style.SUCCESS(f"  TOTAL: ₹{pricing['total']:.2f}"))
        self.stdout.write(f"  Unit Price: ₹{pricing['unit_price']:.2f}")
        
        if 'savings' in result:
            savings = result['savings']
            self.stdout.write(self.style.WARNING(f"  💰 {savings['message']}"))
        
        if result['warnings']:
            for warning in result['warnings']:
                self.stdout.write(self.style.WARNING(f"  ⚠️  {warning}"))