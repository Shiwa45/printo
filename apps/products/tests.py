# apps/products/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
import json
from .models import (
    ProductCategory, Product, ProductOption, OptionValue, 
    ProductVariant, PricingRule, PricingTier, EnhancedPricingCalculator
)

class EnhancedProductCatalogTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create category
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category',
            default_bleed=Decimal('3.0'),
            default_safe_zone=Decimal('2.0')
        )
        
        # Create product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            product_type='business_card',
            description='Test product description',
            short_description='Test short description',
            base_width=Decimal('90'),
            base_height=Decimal('54'),
            base_price=Decimal('500.00'),
            minimum_quantity=100,
            status='active'
        )
        
        # Create variant
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name='Standard Size',
            sku='TEST-STD-001',
            width=Decimal('90'),
            height=Decimal('54'),
            price_modifier=Decimal('0'),
            price_modifier_type='fixed'
        )
        
        # Create option
        self.paper_option = ProductOption.objects.create(
            product=self.product,
            name='Paper Type',
            option_type='paper',
            is_required=True,
            display_as_grid=True
        )
        
        # Create option values
        self.standard_paper = OptionValue.objects.create(
            option=self.paper_option,
            name='Standard Paper',
            price_modifier=Decimal('0'),
            is_default=True
        )
        
        self.premium_paper = OptionValue.objects.create(
            option=self.paper_option,
            name='Premium Paper',
            price_modifier=Decimal('100'),
            price_modifier_type='fixed'
        )
        
        # Create pricing rule
        self.pricing_rule = PricingRule.objects.create(
            product=self.product,
            name='Quantity Discounts',
            rule_type='quantity',
            is_active=True,
            priority=1
        )
        
        # Create pricing tiers
        PricingTier.objects.create(
            pricing_rule=self.pricing_rule,
            min_quantity=100,
            max_quantity=249,
            price_modifier=Decimal('0'),
            price_modifier_type='discount_percent'
        )
        
        PricingTier.objects.create(
            pricing_rule=self.pricing_rule,
            min_quantity=250,
            max_quantity=499,
            price_modifier=Decimal('10'),
            price_modifier_type='discount_percent'
        )
        
        self.client = Client()
    
    def test_product_creation(self):
        """Test that products are created correctly"""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.base_price, Decimal('500.00'))
        self.assertTrue(self.product.get_active_variants().exists())
        self.assertTrue(self.product.get_active_options().exists())
    
    def test_variant_dimensions(self):
        """Test variant dimension display"""
        dimensions = self.variant.get_dimensions_display()
        self.assertEqual(dimensions, '90.00 × 54.00 mm')
    
    def test_option_value_price_display(self):
        """Test option value price display"""
        self.assertEqual(self.standard_paper.get_price_display(), 'No additional cost')
        self.assertEqual(self.premium_paper.get_price_display(), '+₹100.0')
    
    def test_pricing_calculator_basic(self):
        """Test basic pricing calculation"""
        calculator = EnhancedPricingCalculator(self.product)
        result = calculator.calculate_price(
            variant=self.variant,
            options={},  # No options for basic test
            quantity=100
        )
        
        self.assertEqual(result['base_price'], Decimal('500.00'))
        self.assertEqual(result['variant_modifier'], Decimal('0.00'))
        self.assertGreater(result['total'], Decimal('0'))
        self.assertEqual(len(result['errors']), 0)
        
        # Check that we have basic components
        self.assertGreater(result['subtotal'], Decimal('0'))
        self.assertGreaterEqual(result['tax'], Decimal('0'))
        self.assertGreaterEqual(result['shipping'], Decimal('0'))
    
    def test_pricing_calculator_with_options(self):
        """Test pricing calculation with options"""
        calculator = EnhancedPricingCalculator(self.product)
        result = calculator.calculate_price(
            variant=self.variant,
            options={'paper': self.premium_paper.id},
            quantity=100
        )
        
        self.assertEqual(result['option_modifiers'], Decimal('100.00'))
        self.assertGreater(result['total'], result['base_price'] * 100)
    
    def test_pricing_calculator_quantity_discount(self):
        """Test quantity discount calculation"""
        calculator = EnhancedPricingCalculator(self.product)
        
        # Test without discount (100 quantity)
        result_100 = calculator.calculate_price(
            variant=self.variant,
            options={},
            quantity=100
        )
        
        # Test with discount (250 quantity)
        result_250 = calculator.calculate_price(
            variant=self.variant,
            options={},
            quantity=250
        )
        
        # 250 quantity should have discount applied
        self.assertGreater(result_250['quantity_discount'], Decimal('0'))
        self.assertLess(result_250['unit_price'], result_100['unit_price'])
    
    def test_product_api_details(self):
        """Test product details API endpoint"""
        url = reverse('products:product_details', kwargs={'product_id': self.product.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['product']['name'], 'Test Product')
        self.assertEqual(len(data['variants']), 1)
        self.assertEqual(len(data['options']), 1)
        self.assertEqual(len(data['options'][0]['values']), 2)
    
    def test_pricing_api_calculation(self):
        """Test pricing calculation API endpoint"""
        url = reverse('products:calculate_price')
        payload = {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'options': {'paper': self.premium_paper.id},
            'quantity': 250
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['quantity'], 250)
        self.assertGreater(data['pricing']['total'], 0)
        self.assertGreater(data['pricing']['quantity_discount'], 0)  # Should have discount
        self.assertGreater(len(data['pricing']['breakdown']), 0)
    
    def test_design_tool_config(self):
        """Test design tool configuration"""
        config = self.product.get_design_tool_config()
        
        self.assertTrue(config['enabled'])
        self.assertEqual(config['width'], 90.0)
        self.assertEqual(config['height'], 54.0)
        self.assertEqual(config['unit'], 'mm')
        self.assertEqual(config['bleed'], 3.0)
        self.assertEqual(config['safe_zone'], 2.0)
        self.assertEqual(config['dpi'], 300)

class ProductCategoryTestCase(TestCase):
    def setUp(self):
        """Set up test data for categories"""
        self.parent_category = ProductCategory.objects.create(
            name='Parent Category',
            slug='parent-category'
        )
        
        self.child_category = ProductCategory.objects.create(
            name='Child Category',
            slug='child-category',
            parent=self.parent_category
        )
    
    def test_category_hierarchy(self):
        """Test category hierarchy functionality"""
        self.assertEqual(self.child_category.parent, self.parent_category)
        self.assertIn(self.child_category, self.parent_category.get_active_children())
    
    def test_category_full_path(self):
        """Test category full path generation"""
        path = self.child_category.get_full_path()
        self.assertEqual(path, 'Parent Category > Child Category')
class PricingServiceTestCase(TestCase):
    def setUp(self):
        """Set up test data for pricing service"""
        # Create category
        self.category = ProductCategory.objects.create(
            name='Business Cards',
            slug='business-cards',
            default_bleed=Decimal('3.0'),
            default_safe_zone=Decimal('2.0')
        )
        
        # Create product
        self.product = Product.objects.create(
            name='Premium Business Cards',
            slug='premium-business-cards',
            category=self.category,
            product_type='business_card',
            description='Premium business cards',
            short_description='High-quality business cards',
            base_width=Decimal('90'),
            base_height=Decimal('54'),
            base_price=Decimal('500.00'),
            minimum_quantity=100,
            status='active',
            rush_fee_percent=Decimal('50.00')
        )
        
        # Create variant
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name='Large Size',
            sku='BC-LRG-001',
            width=Decimal('100'),
            height=Decimal('60'),
            price_modifier=Decimal('100'),
            price_modifier_type='fixed'
        )
        
        # Create paper option
        self.paper_option = ProductOption.objects.create(
            product=self.product,
            name='Paper Type',
            option_type='paper',
            is_required=True
        )
        
        self.premium_paper = OptionValue.objects.create(
            option=self.paper_option,
            name='Premium Paper',
            price_modifier=Decimal('150'),
            price_modifier_type='fixed'
        )
        
        # Create pricing rule
        self.pricing_rule = PricingRule.objects.create(
            product=self.product,
            name='Volume Discounts',
            rule_type='quantity',
            is_active=True,
            priority=1
        )
        
        # Create pricing tiers
        PricingTier.objects.create(
            pricing_rule=self.pricing_rule,
            min_quantity=250,
            max_quantity=499,
            price_modifier=Decimal('10'),
            price_modifier_type='discount_percent'
        )
        
        PricingTier.objects.create(
            pricing_rule=self.pricing_rule,
            min_quantity=500,
            price_modifier=Decimal('15'),
            price_modifier_type='discount_percent'
        )
    
    def test_basic_pricing_calculation(self):
        """Test basic pricing calculation with PricingService"""
        from .services import PricingService
        
        service = PricingService()
        configuration = {
            'quantity': 100,
            'country_code': 'IN'
        }
        
        result = service.calculate_comprehensive_price(self.product, configuration)
        
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['pricing']['base_price'], Decimal('500.00'))
        self.assertGreater(result['pricing']['total'], Decimal('0'))
        self.assertGreater(result['pricing']['tax'], Decimal('0'))
        self.assertGreater(result['pricing']['shipping'], Decimal('0'))
    
    def test_pricing_with_variant_and_options(self):
        """Test pricing with variant and options"""
        from .services import PricingService
        
        service = PricingService()
        configuration = {
            'variant_id': self.variant.id,
            'options': {'Paper Type': self.premium_paper.id},
            'quantity': 100,
            'country_code': 'IN'
        }
        
        result = service.calculate_comprehensive_price(self.product, configuration)
        
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['pricing']['variant_cost'], Decimal('100.00'))
        self.assertEqual(result['pricing']['options_cost'], Decimal('150.00'))
        
        # Check breakdown includes variant and options
        breakdown_types = [item['type'] for item in result['breakdown']]
        self.assertIn('variant', breakdown_types)
        self.assertIn('option', breakdown_types)
    
    def test_quantity_discounts(self):
        """Test quantity discount application"""
        from .services import PricingService
        
        service = PricingService()
        
        # Test with 250 quantity (10% discount)
        config_250 = {'quantity': 250, 'country_code': 'IN'}
        result_250 = service.calculate_comprehensive_price(self.product, config_250)
        
        # Test with 500 quantity (15% discount)
        config_500 = {'quantity': 500, 'country_code': 'IN'}
        result_500 = service.calculate_comprehensive_price(self.product, config_500)
        
        self.assertGreater(result_250['pricing']['quantity_discount'], Decimal('0'))
        self.assertGreater(result_500['pricing']['quantity_discount'], result_250['pricing']['quantity_discount'])
        
        # Check that savings information is included
        self.assertIn('savings', result_250)
        self.assertIn('savings', result_500)
    
    def test_rush_delivery_fee(self):
        """Test rush delivery fee calculation"""
        from .services import PricingService
        
        service = PricingService()
        
        # Without rush delivery
        config_normal = {'quantity': 100, 'country_code': 'IN'}
        result_normal = service.calculate_comprehensive_price(self.product, config_normal)
        
        # With rush delivery
        config_rush = {'quantity': 100, 'country_code': 'IN', 'rush_delivery': True}
        result_rush = service.calculate_comprehensive_price(self.product, config_rush)
        
        self.assertEqual(result_normal['pricing']['rush_fee'], Decimal('0'))
        self.assertGreater(result_rush['pricing']['rush_fee'], Decimal('0'))
        self.assertGreater(result_rush['pricing']['total'], result_normal['pricing']['total'])
    
    def test_design_service_fee(self):
        """Test design service fee"""
        from .services import PricingService
        
        service = PricingService()
        config = {
            'quantity': 100,
            'country_code': 'IN',
            'design_service': True
        }
        
        result = service.calculate_comprehensive_price(self.product, config)
        
        self.assertEqual(result['pricing']['design_fee'], Decimal('1500.00'))
        
        # Check breakdown includes design service
        breakdown_types = [item['type'] for item in result['breakdown']]
        self.assertIn('service', breakdown_types)
    
    def test_price_breaks_calculation(self):
        """Test price breaks calculation"""
        from .services import PricingService
        
        service = PricingService()
        price_breaks = service.get_quantity_price_breaks(self.product)
        
        self.assertGreater(len(price_breaks), 0)
        
        # Check that higher quantities have lower unit prices (due to discounts)
        if len(price_breaks) >= 2:
            # Find a quantity with discount
            discounted_break = None
            for pb in price_breaks:
                if pb['quantity'] >= 250:  # Our discount threshold
                    discounted_break = pb
                    break
            
            if discounted_break:
                self.assertIn('savings', discounted_break)
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        from .services import PricingService
        
        service = PricingService()
        
        # Valid configuration
        valid_config = {
            'variant_id': self.variant.id,
            'options': {'Paper Type': self.premium_paper.id},
            'quantity': 100
        }
        
        validation = service.validate_configuration(self.product, valid_config)
        self.assertEqual(len(validation['errors']), 0)
        
        # Invalid configuration - below minimum quantity
        invalid_config = {
            'quantity': 50  # Below minimum of 100
        }
        
        validation = service.validate_configuration(self.product, invalid_config)
        self.assertGreater(len(validation['errors']), 0)
        self.assertIn('Minimum quantity', validation['errors'][0])
    
    def test_tax_calculation_by_country(self):
        """Test tax calculation for different countries"""
        from .services import PricingService
        
        service = PricingService()
        
        # India (18% GST)
        config_in = {'quantity': 100, 'country_code': 'IN'}
        result_in = service.calculate_comprehensive_price(self.product, config_in)
        
        # US (8% average sales tax)
        config_us = {'quantity': 100, 'country_code': 'US'}
        result_us = service.calculate_comprehensive_price(self.product, config_us)
        
        # India should have higher tax rate
        self.assertGreater(result_in['pricing']['tax'], result_us['pricing']['tax'])

class PricingAPITestCase(TestCase):
    def setUp(self):
        """Set up test data for API tests"""
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            product_type='business_card',
            description='Test product',
            short_description='Test',
            base_width=Decimal('90'),
            base_height=Decimal('54'),
            base_price=Decimal('500.00'),
            minimum_quantity=100,
            status='active'
        )
        
        self.client = Client()
    
    def test_advanced_pricing_api(self):
        """Test the advanced pricing API endpoint"""
        url = reverse('products:calculate_advanced_pricing')
        payload = {
            'product_id': self.product.id,
            'quantity': 100,
            'country_code': 'IN'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['product_id'], self.product.id)
        self.assertIn('pricing', data)
        self.assertIn('breakdown', data)
        self.assertEqual(len(data['errors']), 0)
    
    def test_price_breaks_api(self):
        """Test the price breaks API endpoint"""
        url = reverse('products:get_price_breaks', kwargs={'product_id': self.product.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertIn('price_breaks', data)
        self.assertGreater(len(data['price_breaks']), 0)
    
    def test_product_catalog_api(self):
        """Test the product catalog API endpoint"""
        url = reverse('products:product_catalog')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertIn('products', data)
        self.assertIn('pagination', data)
        self.assertEqual(len(data['products']), 1)  # Our test product
    
    def test_categories_api(self):
        """Test the categories API endpoint"""
        url = reverse('products:categories')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertIn('categories', data)
        self.assertEqual(len(data['categories']), 1)  # Our test category