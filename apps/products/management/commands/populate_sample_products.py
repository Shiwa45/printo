from django.core.management.base import BaseCommand
from apps.products.models import (
    ProductCategory, Product, ProductOption, OptionValue, 
    ProductVariant, PricingRule, PricingTier
)
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate sample products with enhanced features'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample products with enhanced features...')
        
        # Create or get business cards category
        business_cards_cat, created = ProductCategory.objects.get_or_create(
            slug='business-cards',
            defaults={
                'name': 'Business Cards',
                'description': 'Professional business cards for your business',
                'default_bleed': Decimal('3.0'),
                'default_safe_zone': Decimal('2.0'),
                'featured': True
            }
        )
        
        # Create or get business cards product
        business_card, created = Product.objects.get_or_create(
            slug='premium-business-cards',
            defaults={
                'name': 'Premium Business Cards',
                'category': business_cards_cat,
                'product_type': 'business_card',
                'description': 'High-quality premium business cards with various paper options',
                'short_description': 'Professional business cards with premium finishes',
                'base_width': Decimal('90'),
                'base_height': Decimal('54'),
                'base_price': Decimal('500.00'),
                'minimum_quantity': 100,
                'has_design_tool': True,
                'front_back_design_enabled': True,
                'accepted_file_formats': ['PDF', 'PNG', 'JPG', 'AI', 'PSD'],
                'status': 'active',
                'featured': True
            }
        )
        
        if created:
            self.stdout.write(f'Created product: {business_card.name}')
            
            # Create variants
            variants_data = [
                {'name': 'Standard Size', 'sku': 'BC-STD-001', 'width': 90, 'height': 54, 'modifier': 0},
                {'name': 'Large Size', 'sku': 'BC-LRG-001', 'width': 100, 'height': 60, 'modifier': 50},
            ]
            
            for variant_data in variants_data:
                variant, v_created = ProductVariant.objects.get_or_create(
                    product=business_card,
                    name=variant_data['name'],
                    defaults={
                        'sku': variant_data['sku'],
                        'width': Decimal(str(variant_data['width'])),
                        'height': Decimal(str(variant_data['height'])),
                        'price_modifier': Decimal(str(variant_data['modifier'])),
                        'price_modifier_type': 'fixed'
                    }
                )
                if v_created:
                    self.stdout.write(f'  Created variant: {variant.name}')
            
            # Create paper option
            paper_option, created = ProductOption.objects.get_or_create(
                product=business_card,
                name='Paper Type',
                defaults={
                    'option_type': 'paper',
                    'is_required': True,
                    'display_as_grid': True,
                    'show_images': True,
                    'sort_order': 1
                }
            )
            
            if created:
                self.stdout.write(f'  Created option: {paper_option.name}')
                
                # Create paper option values
                paper_values = [
                    {'name': 'Standard Cardstock', 'modifier': 0, 'specs': {'gsm': 300, 'finish': 'matte'}},
                    {'name': 'Premium Cardstock', 'modifier': 100, 'specs': {'gsm': 350, 'finish': 'gloss'}},
                    {'name': 'Luxury Cardstock', 'modifier': 200, 'specs': {'gsm': 400, 'finish': 'spot_uv'}},
                ]
                
                for i, paper_data in enumerate(paper_values):
                    value, v_created = OptionValue.objects.get_or_create(
                        option=paper_option,
                        name=paper_data['name'],
                        defaults={
                            'price_modifier': Decimal(str(paper_data['modifier'])),
                            'specifications': paper_data['specs'],
                            'is_default': i == 0,
                            'sort_order': i
                        }
                    )
                    if v_created:
                        self.stdout.write(f'    Created value: {value.name}')
            
            # Create finish option
            finish_option, created = ProductOption.objects.get_or_create(
                product=business_card,
                name='Finish',
                defaults={
                    'option_type': 'finish',
                    'is_required': True,
                    'display_as_grid': True,
                    'sort_order': 2
                }
            )
            
            if created:
                finish_values = [
                    {'name': 'Matte Finish', 'modifier': 0},
                    {'name': 'Gloss Finish', 'modifier': 25},
                    {'name': 'Spot UV', 'modifier': 75},
                ]
                
                for i, finish_data in enumerate(finish_values):
                    value, v_created = OptionValue.objects.get_or_create(
                        option=finish_option,
                        name=finish_data['name'],
                        defaults={
                            'price_modifier': Decimal(str(finish_data['modifier'])),
                            'is_default': i == 0,
                            'sort_order': i
                        }
                    )
                    if v_created:
                        self.stdout.write(f'    Created value: {value.name}')
            
            # Create quantity pricing rule
            qty_rule, created = PricingRule.objects.get_or_create(
                product=business_card,
                name='Quantity Discounts',
                defaults={
                    'rule_type': 'quantity',
                    'description': 'Volume discounts for bulk orders',
                    'is_active': True,
                    'priority': 1
                }
            )
            
            if created:
                self.stdout.write(f'  Created pricing rule: {qty_rule.name}')
                
                # Create pricing tiers
                tiers_data = [
                    {'min': 100, 'max': 249, 'discount': 0},
                    {'min': 250, 'max': 499, 'discount': 5},
                    {'min': 500, 'max': 999, 'discount': 10},
                    {'min': 1000, 'max': None, 'discount': 15},
                ]
                
                for tier_data in tiers_data:
                    tier, t_created = PricingTier.objects.get_or_create(
                        pricing_rule=qty_rule,
                        min_quantity=tier_data['min'],
                        defaults={
                            'max_quantity': tier_data['max'],
                            'price_modifier': Decimal(str(tier_data['discount'])),
                            'price_modifier_type': 'discount_percent'
                        }
                    )
                    if t_created:
                        self.stdout.write(f'    Created tier: {tier_data["min"]}-{tier_data["max"] or "∞"} ({tier_data["discount"]}% off)')
        
        # Create brochures category and product
        brochures_cat, created = ProductCategory.objects.get_or_create(
            slug='brochures',
            defaults={
                'name': 'Brochures',
                'description': 'Professional brochures and marketing materials',
                'default_bleed': Decimal('3.0'),
                'default_safe_zone': Decimal('2.0'),
                'featured': True
            }
        )
        
        brochure, created = Product.objects.get_or_create(
            slug='tri-fold-brochures',
            defaults={
                'name': 'Tri-Fold Brochures',
                'category': brochures_cat,
                'product_type': 'brochure',
                'description': 'Professional tri-fold brochures for marketing',
                'short_description': 'High-quality tri-fold brochures',
                'base_width': Decimal('297'),
                'base_height': Decimal('210'),
                'base_price': Decimal('800.00'),
                'minimum_quantity': 50,
                'has_design_tool': True,
                'front_back_design_enabled': True,
                'status': 'active'
            }
        )
        
        if created:
            self.stdout.write(f'Created product: {brochure.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated sample products!'))
        self.stdout.write('You can now:')
        self.stdout.write('1. Access the admin panel to manage products')
        self.stdout.write('2. View products in the frontend')
        self.stdout.write('3. Test the enhanced pricing system')
        self.stdout.write('4. Configure additional options and variants')