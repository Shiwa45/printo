# apps/products/services.py
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.db.models import Q
from .models import Product, ProductVariant, OptionValue, PricingRule, PricingTier

class PricingService:
    """
    Advanced pricing service for complex pricing calculations
    """
    
    def __init__(self):
        self.tax_rates = {
            'IN': Decimal('0.18'),  # India GST
            'US': Decimal('0.08'),  # Average US sales tax
            'EU': Decimal('0.20'),  # Average EU VAT
            'default': Decimal('0.18')
        }
    
    def calculate_comprehensive_price(self, product: Product, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive pricing for a product configuration
        
        Args:
            product: Product instance
            configuration: Dict containing:
                - variant_id: Optional[int]
                - options: Dict[str, int] (option_name -> option_value_id)
                - quantity: int
                - user_id: Optional[int]
                - country_code: Optional[str]
                - rush_delivery: Optional[bool]
                - design_service: Optional[bool]
        
        Returns:
            Comprehensive pricing breakdown
        """
        
        result = {
            'product_id': product.id,
            'product_name': product.name,
            'configuration': configuration,
            'pricing': {
                'base_price': Decimal('0.00'),
                'variant_cost': Decimal('0.00'),
                'options_cost': Decimal('0.00'),
                'quantity_discount': Decimal('0.00'),
                'setup_fees': Decimal('0.00'),
                'rush_fee': Decimal('0.00'),
                'design_fee': Decimal('0.00'),
                'subtotal': Decimal('0.00'),
                'tax': Decimal('0.00'),
                'shipping': Decimal('0.00'),
                'total': Decimal('0.00'),
                'unit_price': Decimal('0.00'),
            },
            'breakdown': [],
            'discounts_applied': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            quantity = int(configuration.get('quantity', 1))
            if quantity < product.minimum_quantity:
                result['errors'].append(f'Minimum quantity is {product.minimum_quantity}')
                return result
            
            # Base price calculation
            result['pricing']['base_price'] = product.base_price
            result['breakdown'].append({
                'type': 'base',
                'description': f'Base price for {product.name}',
                'unit_price': product.base_price,
                'quantity': quantity,
                'total': product.base_price * quantity
            })
            
            # Variant cost calculation
            variant_cost = self._calculate_variant_cost(
                product, configuration.get('variant_id'), quantity
            )
            result['pricing']['variant_cost'] = variant_cost['total']
            if variant_cost['breakdown']:
                result['breakdown'].extend(variant_cost['breakdown'])
            
            # Options cost calculation
            options_cost = self._calculate_options_cost(
                product, configuration.get('options', {}), quantity
            )
            result['pricing']['options_cost'] = options_cost['total']
            result['breakdown'].extend(options_cost['breakdown'])
            
            # Calculate subtotal before discounts
            subtotal_before_discount = (
                (product.base_price + result['pricing']['variant_cost'] + result['pricing']['options_cost']) * quantity
            )
            
            # Quantity discount calculation
            discount_info = self._calculate_quantity_discounts(
                product, quantity, subtotal_before_discount, configuration
            )
            result['pricing']['quantity_discount'] = discount_info['amount']
            if discount_info['breakdown']:
                result['breakdown'].extend(discount_info['breakdown'])
                result['discounts_applied'].extend(discount_info['discounts'])
            
            # Setup fees calculation
            setup_fees = self._calculate_setup_fees(product, configuration)
            result['pricing']['setup_fees'] = setup_fees['total']
            result['breakdown'].extend(setup_fees['breakdown'])
            
            # Rush delivery fee
            if configuration.get('rush_delivery'):
                rush_fee = subtotal_before_discount * (product.rush_fee_percent / Decimal('100'))
                result['pricing']['rush_fee'] = rush_fee
                result['breakdown'].append({
                    'type': 'fee',
                    'description': f'Rush delivery ({product.rush_fee_percent}%)',
                    'unit_price': rush_fee,
                    'quantity': 1,
                    'total': rush_fee
                })
            
            # Design service fee
            if configuration.get('design_service'):
                design_fee = Decimal('1500.00')  # Base design fee
                result['pricing']['design_fee'] = design_fee
                result['breakdown'].append({
                    'type': 'service',
                    'description': 'Professional design service',
                    'unit_price': design_fee,
                    'quantity': 1,
                    'total': design_fee
                })
            
            # Calculate subtotal
            result['pricing']['subtotal'] = (
                subtotal_before_discount - result['pricing']['quantity_discount'] +
                result['pricing']['setup_fees'] + result['pricing']['rush_fee'] + 
                result['pricing']['design_fee']
            )
            
            # Tax calculation
            tax_info = self._calculate_tax(
                result['pricing']['subtotal'], 
                configuration.get('country_code', 'IN'),
                configuration.get('user_id')
            )
            result['pricing']['tax'] = tax_info['amount']
            if tax_info['breakdown']:
                result['breakdown'].extend(tax_info['breakdown'])
            
            # Shipping calculation
            shipping_info = self._calculate_shipping(
                product, quantity, configuration
            )
            result['pricing']['shipping'] = shipping_info['amount']
            if shipping_info['breakdown']:
                result['breakdown'].extend(shipping_info['breakdown'])
            
            # Final total
            result['pricing']['total'] = (
                result['pricing']['subtotal'] + 
                result['pricing']['tax'] + 
                result['pricing']['shipping']
            )
            
            result['pricing']['unit_price'] = (
                result['pricing']['total'] / quantity if quantity > 0 else Decimal('0.00')
            )
            
            # Add savings information
            if result['pricing']['quantity_discount'] > 0:
                savings_percent = (result['pricing']['quantity_discount'] / subtotal_before_discount) * 100
                result['savings'] = {
                    'amount': result['pricing']['quantity_discount'],
                    'percentage': float(savings_percent),
                    'message': f'You save ₹{result["pricing"]["quantity_discount"]} ({savings_percent:.1f}%) with this quantity!'
                }
            
        except Exception as e:
            result['errors'].append(f'Pricing calculation error: {str(e)}')
        
        return result
    
    def _calculate_variant_cost(self, product: Product, variant_id: Optional[int], quantity: int) -> Dict[str, Any]:
        """Calculate variant-specific costs"""
        result = {'total': Decimal('0.00'), 'breakdown': []}
        
        if not variant_id:
            return result
        
        try:
            variant = ProductVariant.objects.get(id=variant_id, product=product, is_active=True)
            
            if variant.price_modifier != 0:
                if variant.price_modifier_type == 'percent':
                    modifier = product.base_price * (variant.price_modifier / Decimal('100'))
                else:
                    modifier = variant.price_modifier
                
                result['total'] = modifier
                result['breakdown'].append({
                    'type': 'variant',
                    'description': f'Size: {variant.name}',
                    'unit_price': modifier,
                    'quantity': quantity,
                    'total': modifier * quantity
                })
        
        except ProductVariant.DoesNotExist:
            pass
        
        return result
    
    def _calculate_options_cost(self, product: Product, options: Dict[str, int], quantity: int) -> Dict[str, Any]:
        """Calculate options-specific costs"""
        result = {'total': Decimal('0.00'), 'breakdown': []}
        
        for option_name, value_id in options.items():
            try:
                option_value = OptionValue.objects.get(id=value_id, is_active=True)
                
                if option_value.price_modifier != 0:
                    if option_value.price_modifier_type == 'percent':
                        modifier = product.base_price * (option_value.price_modifier / Decimal('100'))
                    else:
                        modifier = option_value.price_modifier
                    
                    result['total'] += modifier
                    result['breakdown'].append({
                        'type': 'option',
                        'description': f'{option_value.option.name}: {option_value.name}',
                        'unit_price': modifier,
                        'quantity': quantity,
                        'total': modifier * quantity
                    })
            
            except OptionValue.DoesNotExist:
                continue
        
        return result
    
    def _calculate_quantity_discounts(self, product: Product, quantity: int, subtotal: Decimal, configuration: Dict) -> Dict[str, Any]:
        """Calculate quantity-based discounts"""
        result = {
            'amount': Decimal('0.00'),
            'breakdown': [],
            'discounts': []
        }
        
        # Check product-specific pricing rules
        now = timezone.now()
        applicable_rules = product.pricing_rules.filter(
            rule_type='quantity',
            is_active=True,
            min_quantity__lte=quantity
        ).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now)
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=now)
        ).filter(
            Q(max_quantity__isnull=True) | Q(max_quantity__gte=quantity)
        ).order_by('-priority')
        
        best_discount = Decimal('0.00')
        best_rule = None
        
        for rule in applicable_rules:
            tier = rule.tiers.filter(
                min_quantity__lte=quantity
            ).filter(
                Q(max_quantity__isnull=True) | Q(max_quantity__gte=quantity)
            ).first()
            
            if tier:
                if tier.price_modifier_type == 'discount_percent':
                    discount = subtotal * (tier.price_modifier / Decimal('100'))
                elif tier.price_modifier_type == 'fixed':
                    discount = tier.price_modifier
                else:
                    continue
                
                if discount > best_discount:
                    best_discount = discount
                    best_rule = {'rule': rule, 'tier': tier}
        
        # Apply default quantity discounts if no specific rules
        if best_discount == 0:
            default_discounts = [
                {'min': 25, 'discount': Decimal('0.02'), 'label': '2% off'},
                {'min': 50, 'discount': Decimal('0.04'), 'label': '4% off'},
                {'min': 100, 'discount': Decimal('0.08'), 'label': '8% off'},
                {'min': 200, 'discount': Decimal('0.12'), 'label': '12% off'},
                {'min': 300, 'discount': Decimal('0.16'), 'label': '16% off'},
            ]
            
            for tier in reversed(default_discounts):
                if quantity >= tier['min']:
                    best_discount = subtotal * tier['discount']
                    best_rule = {'default': True, 'label': tier['label']}
                    break
        
        if best_discount > 0:
            result['amount'] = best_discount
            
            if best_rule.get('default'):
                label = best_rule['label']
                description = f'Quantity discount ({label})'
            else:
                rule = best_rule['rule']
                tier = best_rule['tier']
                label = f'{tier.price_modifier}% off'
                description = f'{rule.name} ({label})'
            
            result['breakdown'].append({
                'type': 'discount',
                'description': description,
                'unit_price': -best_discount,
                'quantity': 1,
                'total': -best_discount
            })
            
            result['discounts'].append({
                'type': 'quantity',
                'name': description,
                'amount': best_discount
            })
        
        return result
    
    def _calculate_setup_fees(self, product: Product, configuration: Dict) -> Dict[str, Any]:
        """Calculate one-time setup fees"""
        result = {'total': Decimal('0.00'), 'breakdown': []}
        
        # Add setup fees based on product type and options
        if product.product_type in ['business_card', 'brochure', 'flyer']:
            # Check if this is a new design (no existing design provided)
            if not configuration.get('existing_design_id'):
                setup_fee = Decimal('100.00')  # Basic setup fee
                result['total'] += setup_fee
                result['breakdown'].append({
                    'type': 'setup',
                    'description': 'Design setup fee',
                    'unit_price': setup_fee,
                    'quantity': 1,
                    'total': setup_fee
                })
        
        return result
    
    def _calculate_tax(self, subtotal: Decimal, country_code: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Calculate applicable taxes"""
        result = {'amount': Decimal('0.00'), 'breakdown': []}
        
        tax_rate = self.tax_rates.get(country_code, self.tax_rates['default'])
        tax_amount = subtotal * tax_rate
        
        if tax_amount > 0:
            result['amount'] = tax_amount
            result['breakdown'].append({
                'type': 'tax',
                'description': f'Tax ({float(tax_rate * 100):.1f}%)',
                'unit_price': tax_amount,
                'quantity': 1,
                'total': tax_amount
            })
        
        return result
    
    def _calculate_shipping(self, product: Product, quantity: int, configuration: Dict) -> Dict[str, Any]:
        """Calculate shipping costs"""
        result = {'amount': Decimal('0.00'), 'breakdown': []}
        
        # Base shipping cost
        base_shipping = Decimal('50.00')
        
        # Weight-based additional shipping for large quantities
        if quantity > 100:
            additional_shipping = Decimal(str(quantity - 100)) * Decimal('0.50')
            total_shipping = base_shipping + additional_shipping
        else:
            total_shipping = base_shipping
        
        # Rush delivery shipping premium
        if configuration.get('rush_delivery'):
            total_shipping *= Decimal('1.5')  # 50% premium for rush
        
        result['amount'] = total_shipping
        result['breakdown'].append({
            'type': 'shipping',
            'description': 'Shipping cost',
            'unit_price': total_shipping,
            'quantity': 1,
            'total': total_shipping
        })
        
        return result
    
    def get_quantity_price_breaks(self, product: Product, variant_id: Optional[int] = None, options: Optional[Dict] = None) -> List[Dict]:
        """
        Get price breaks for different quantities to show bulk pricing
        """
        options = options or {}
        quantities = [25, 50, 100, 250, 500, 1000, 2500, 5000]
        price_breaks = []
        
        for qty in quantities:
            if qty < product.minimum_quantity:
                continue
            
            config = {
                'variant_id': variant_id,
                'options': options,
                'quantity': qty,
                'country_code': 'IN'
            }
            
            pricing = self.calculate_comprehensive_price(product, config)
            
            if not pricing['errors']:
                price_breaks.append({
                    'quantity': qty,
                    'unit_price': float(pricing['pricing']['unit_price']),
                    'total_price': float(pricing['pricing']['total']),
                    'savings': pricing.get('savings', {})
                })
        
        return price_breaks
    
    def validate_configuration(self, product: Product, configuration: Dict) -> Dict[str, List[str]]:
        """
        Validate a product configuration
        """
        errors = []
        warnings = []
        
        # Validate quantity
        quantity = configuration.get('quantity', 1)
        if quantity < product.minimum_quantity:
            errors.append(f'Minimum quantity is {product.minimum_quantity}')
        
        if product.max_quantity and quantity > product.max_quantity:
            errors.append(f'Maximum quantity is {product.max_quantity}')
        
        # Validate variant
        variant_id = configuration.get('variant_id')
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product, is_active=True)
                if variant.stock_quantity is not None and quantity > variant.stock_quantity:
                    warnings.append(f'Requested quantity ({quantity}) exceeds available stock ({variant.stock_quantity})')
            except ProductVariant.DoesNotExist:
                errors.append('Invalid variant selected')
        
        # Validate options
        options = configuration.get('options', {})
        required_options = product.options.filter(is_required=True)
        
        for option in required_options:
            if option.name not in options:
                errors.append(f'Required option "{option.name}" not selected')
            else:
                try:
                    value_id = options[option.name]
                    OptionValue.objects.get(id=value_id, option=option, is_active=True)
                except OptionValue.DoesNotExist:
                    errors.append(f'Invalid value for option "{option.name}"')
        
        return {'errors': errors, 'warnings': warnings}