from django.db import models
from decimal import Decimal
import json


class EnhancedPricingCalculator(models.Model):
    """
    Enhanced pricing calculator based on Creative Print Arts analysis
    Includes CPA-compatible parameter validation and pricing structure
    """

    # Enhanced book sizes with CPA-compatible display formats
    BOOK_SIZES = {
        'A4': {
            'width': 210,
            'height': 297,
            'display': 'A4 (8.27 x 11.69 in)',
            'cpa_format': 'A 4 (8.27 x 11.69 in / 210 x 297 mm)'
        },
        'Letter': {
            'width': 216,
            'height': 279,
            'display': 'Letter (8.5 x 11 in)',
            'cpa_format': 'US Letter (8.5 x 11 in / 216 x 279 mm)'
        },
        'Executive': {
            'width': 178,
            'height': 254,
            'display': 'Executive (7 x 10 in)',
            'cpa_format': 'Executive (7 x 10 in / 178 x 254 mm)'
        },
        'A5': {
            'width': 148,
            'height': 210,
            'display': 'A5 (5.83 x 8.27 in)',
            'cpa_format': 'A 5 (5.83 x 8.27 in / 148 x 210 mm)'
        },
    }

    # Enhanced rates from CPA analysis with improved pricing
    BOOK_RATES = {
        'A4': {
            'bw_standard': {'75gsm': 1.15, '100gsm': 1.40, '100gsm_art': 1.85, '130gsm_art': 2.15},
            'bw_premium': {'75gsm': 1.35, '100gsm': 1.60, '100gsm_art': 2.05, '130gsm_art': 2.35},
            'color_standard': {'75gsm': 2.55, '100gsm': 2.75, '100gsm_art': 2.95, '130gsm_art': 3.20},
            'color_premium': {'75gsm': 2.75, '100gsm': 2.95, '100gsm_art': 3.15, '130gsm_art': 3.35},
            'shipping': {'bw': 0.12, 'color': 0.15}
        },
        'Letter': {
            'bw_standard': {'75gsm': 1.15, '100gsm': 1.40, '100gsm_art': 1.85, '130gsm_art': 2.15},
            'bw_premium': {'75gsm': 1.35, '100gsm': 1.60, '100gsm_art': 2.05, '130gsm_art': 2.35},
            'color_standard': {'75gsm': 2.55, '100gsm': 2.75, '100gsm_art': 2.95, '130gsm_art': 3.20},
            'color_premium': {'75gsm': 2.75, '100gsm': 2.95, '100gsm_art': 3.15, '130gsm_art': 3.35},
            'shipping': {'bw': 0.12, 'color': 0.15}
        },
        'Executive': {
            'bw_standard': {'75gsm': 1.05, '100gsm': 1.30, '100gsm_art': 1.75, '130gsm_art': 2.05},
            'bw_premium': {'75gsm': 1.25, '100gsm': 1.50, '100gsm_art': 1.95, '130gsm_art': 2.25},
            'color_standard': {'75gsm': 2.45, '100gsm': 2.65, '100gsm_art': 2.85, '130gsm_art': 3.10},
            'color_premium': {'75gsm': 2.65, '100gsm': 2.85, '100gsm_art': 3.05, '130gsm_art': 3.25},
            'shipping': {'bw': 0.10, 'color': 0.13}
        },
        'A5': {
            'bw_standard': {'75gsm': 0.65, '100gsm': 0.80, '100gsm_art': 0.95, '130gsm_art': 1.15},
            'bw_premium': {'75gsm': 0.80, '100gsm': 0.95, '100gsm_art': 1.15, '130gsm_art': 1.30},
            'color_standard': {'75gsm': 1.30, '100gsm': 1.40, '100gsm_art': 1.50, '130gsm_art': 1.63},
            'color_premium': {'75gsm': 1.40, '100gsm': 1.50, '100gsm_art': 1.65, '130gsm_art': 1.80},
            'shipping': {'bw': 0.06, 'color': 0.08}
        }
    }

    # Enhanced binding options with CPA-compatible formats
    BINDING_OPTIONS = {
        'paperback_perfect': {
            'name': 'Paperback (Perfect)',
            'rate': 45,
            'min_pages': 32,
            'max_pages': 800,
            'cpa_format': 'Perfect Binding'
        },
        'spiral_binding': {
            'name': 'Spiral Binding',
            'rate': 45,
            'min_pages': 20,
            'max_pages': 470,
            'cpa_format': 'Spiral Binding'
        },
        'hardcover': {
            'name': 'Hardcover',
            'rate': 160,
            'min_pages': 32,
            'max_pages': 800,
            'cpa_format': 'Hard Cover'
        },
        'saddle_stitch': {
            'name': 'Saddle Stitch',
            'rate': 30,
            'min_pages': 8,
            'max_pages': 48,
            'cpa_format': 'Saddle Stitch'
        },
        'wire_o_bound': {
            'name': 'Wire-O Bound',
            'rate': 65,
            'min_pages': 32,
            'max_pages': None,
            'cpa_format': 'Wire-O Binding'
        }
    }

    # Paper types with CPA-compatible formats
    PAPER_TYPES = {
        '75gsm': {'display': '75 GSM Offset Paper', 'cpa_format': '75 gsm Offset Paper'},
        '100gsm': {'display': '100 GSM Offset Paper', 'cpa_format': '100 gsm Offset Paper'},
        '100gsm_art': {'display': '100 GSM Art Paper', 'cpa_format': '100 gsm Art Paper'},
        '130gsm_art': {'display': '130 GSM Art Paper', 'cpa_format': '130 gsm Art Paper'},
    }

    # Print types with CPA-compatible formats
    PRINT_TYPES = {
        'bw_standard': {'display': 'Black & White Standard', 'cpa_format': 'Black & White'},
        'bw_premium': {'display': 'Black & White Premium', 'cpa_format': 'Black & White'},
        'color_standard': {'display': 'Color Standard', 'cpa_format': 'Colour'},
        'color_premium': {'display': 'Color Premium', 'cpa_format': 'Colour'},
    }

    # Enhanced quantity discounts
    QUANTITY_DISCOUNTS = [
        {'min': 25, 'discount': 0.02, 'label': '2%'},
        {'min': 50, 'discount': 0.04, 'label': '4%'},
        {'min': 75, 'discount': 0.06, 'label': '6%'},
        {'min': 100, 'discount': 0.08, 'label': '8%'},
        {'min': 150, 'discount': 0.10, 'label': '10%'},
        {'min': 200, 'discount': 0.12, 'label': '12%'},
        {'min': 250, 'discount': 0.14, 'label': '14%'},
        {'min': 300, 'discount': 0.16, 'label': '16%'},
        {'min': 500, 'discount': 0.18, 'label': '18%'},
        {'min': 1000, 'discount': 0.20, 'label': '20%'}
    ]

    # Enhanced design services rates
    DESIGN_RATES = {
        'cover_design': 1500,
        'isbn_allocation': 1500,
        'design_support': {'A4': 55, 'Letter': 55, 'Executive': 50, 'A5': 45},
        'formatting_per_page': 50
    }

    # GST and other charges
    GST_RATE = 0.18  # 18% GST

    @classmethod
    def validate_cpa_compatibility(cls, size, paper_type, print_type, binding_type):
        """
        Validate if parameters are compatible with CPA format
        Returns: (is_valid, cpa_form_data)
        """
        errors = []
        cpa_data = {}

        # Validate size
        if size not in cls.BOOK_SIZES:
            errors.append(f"Invalid size: {size}")
        else:
            cpa_data['booksizeoption'] = cls.BOOK_SIZES[size]['cpa_format']

        # Validate paper type
        if paper_type not in cls.PAPER_TYPES:
            errors.append(f"Invalid paper type: {paper_type}")
        else:
            cpa_data['papertype'] = cls.PAPER_TYPES[paper_type]['cpa_format']

        # Validate binding type
        if binding_type not in cls.BINDING_OPTIONS:
            errors.append(f"Invalid binding type: {binding_type}")
        else:
            cpa_data['bindingtype'] = cls.BINDING_OPTIONS[binding_type]['cpa_format']

        # Validate print type
        if print_type not in cls.PRINT_TYPES:
            errors.append(f"Invalid print type: {print_type}")
        else:
            cpa_data['interioronp'] = cls.PRINT_TYPES[print_type]['cpa_format']

        return len(errors) == 0, cpa_data, errors

    @classmethod
    def calculate_enhanced_book_price(cls, size='A4', paper_type='75gsm', print_type='bw_standard',
                                    pages=100, quantity=50, binding_type='paperback_perfect',
                                    include_cover_design=False, include_isbn=False,
                                    include_design_support=False, include_gst=True):
        """
        Enhanced book pricing calculation with CPA compatibility validation
        """

        result = {
            'breakdown': [],
            'subtotal': Decimal('0.00'),
            'discount': Decimal('0.00'),
            'gst': Decimal('0.00'),
            'total': Decimal('0.00'),
            'per_book': Decimal('0.00'),
            'errors': [],
            'cpa_compatible': False,
            'cpa_form_data': {}
        }

        # Validate CPA compatibility
        is_valid, cpa_data, validation_errors = cls.validate_cpa_compatibility(
            size, paper_type, print_type, binding_type
        )

        if validation_errors:
            result['errors'].extend(validation_errors)
            return result

        result['cpa_compatible'] = True
        result['cpa_form_data'] = {
            **cpa_data,
            'product_id': '201',  # CPA book printing product ID
            'book_page_count': str(pages),
            'qty': str(quantity)
        }

        # Validate inputs against our rate structure
        if size not in cls.BOOK_RATES:
            result['errors'].append(f"No rates available for size: {size}")
            return result

        if print_type not in cls.BOOK_RATES[size]:
            result['errors'].append(f"No rates available for print type: {print_type}")
            return result

        if paper_type not in cls.BOOK_RATES[size][print_type]:
            result['errors'].append(f"No rates available for paper type: {paper_type}")
            return result

        if binding_type not in cls.BINDING_OPTIONS:
            result['errors'].append(f"Invalid binding type: {binding_type}")
            return result

        # Check page limits
        binding = cls.BINDING_OPTIONS[binding_type]
        if pages < binding['min_pages']:
            result['errors'].append(f"Minimum {binding['min_pages']} pages required for {binding['name']}")
            return result
        if binding['max_pages'] and pages > binding['max_pages']:
            result['errors'].append(f"Maximum {binding['max_pages']} pages allowed for {binding['name']}")
            return result

        # Calculate printing cost
        page_rate = Decimal(str(cls.BOOK_RATES[size][print_type][paper_type]))
        printing_cost = pages * page_rate * quantity
        result['breakdown'].append({
            'item': f'Printing ({pages} pages × {quantity} books × Rs.{page_rate})',
            'cost': printing_cost
        })

        # Calculate binding cost
        binding_cost = Decimal(str(binding['rate'])) * quantity
        result['breakdown'].append({
            'item': f'{binding["name"]} ({quantity} books × Rs.{binding["rate"]})',
            'cost': binding_cost
        })

        # Calculate shipping
        shipping_type = 'color' if 'color' in print_type else 'bw'
        shipping_rate = Decimal(str(cls.BOOK_RATES[size]['shipping'][shipping_type]))
        shipping_cost = pages * shipping_rate * quantity
        result['breakdown'].append({
            'item': f'Shipping ({pages} pages × {quantity} books × Rs.{shipping_rate})',
            'cost': shipping_cost
        })

        result['subtotal'] = printing_cost + binding_cost + shipping_cost

        # Add one-time design costs
        if include_cover_design:
            cover_cost = Decimal(str(cls.DESIGN_RATES['cover_design']))
            result['breakdown'].append({
                'item': 'Cover Design (One-time)',
                'cost': cover_cost
            })
            result['subtotal'] += cover_cost

        if include_isbn:
            isbn_cost = Decimal(str(cls.DESIGN_RATES['isbn_allocation']))
            result['breakdown'].append({
                'item': 'ISBN Allocation (One-time)',
                'cost': isbn_cost
            })
            result['subtotal'] += isbn_cost

        if include_design_support:
            design_cost = Decimal(str(cls.DESIGN_RATES['design_support'][size]))
            result['breakdown'].append({
                'item': f'Design Support ({size})',
                'cost': design_cost
            })
            result['subtotal'] += design_cost

        # Calculate quantity discount
        discount_info = cls.get_quantity_discount(quantity)
        if discount_info['percentage'] > 0:
            result['discount'] = result['subtotal'] * Decimal(str(discount_info['percentage']))
            result['breakdown'].append({
                'item': f'Quantity Discount ({quantity} books - {discount_info["label"]})',
                'cost': -result['discount']
            })

        # Calculate subtotal after discount
        subtotal_after_discount = result['subtotal'] - result['discount']

        # Calculate GST
        if include_gst:
            result['gst'] = subtotal_after_discount * Decimal(str(cls.GST_RATE))
            result['breakdown'].append({
                'item': f'GST ({int(cls.GST_RATE * 100)}%)',
                'cost': result['gst']
            })

        result['total'] = subtotal_after_discount + result['gst']
        result['per_book'] = result['total'] / quantity if quantity > 0 else Decimal('0.00')

        return result

    @classmethod
    def get_quantity_discount(cls, quantity):
        """Get applicable quantity discount"""
        for tier in reversed(cls.QUANTITY_DISCOUNTS):
            if quantity >= tier['min']:
                return {
                    'percentage': tier['discount'],
                    'label': tier['label'],
                    'min_quantity': tier['min']
                }
        return {'percentage': 0, 'label': 'No Discount', 'min_quantity': 0}

    @classmethod
    def get_available_options(cls):
        """
        Get all available options for form building
        """
        return {
            'sizes': [
                {'value': k, 'label': v['display'], 'dimensions': f"{v['width']}x{v['height']}mm"}
                for k, v in cls.BOOK_SIZES.items()
            ],
            'paper_types': [
                {'value': k, 'label': v['display']}
                for k, v in cls.PAPER_TYPES.items()
            ],
            'print_types': [
                {'value': k, 'label': v['display']}
                for k, v in cls.PRINT_TYPES.items()
            ],
            'binding_types': [
                {
                    'value': k,
                    'label': v['name'],
                    'min_pages': v['min_pages'],
                    'max_pages': v['max_pages']
                }
                for k, v in cls.BINDING_OPTIONS.items()
            ],
            'quantity_discounts': cls.QUANTITY_DISCOUNTS
        }


class PricingRule(models.Model):
    """
    Dynamic pricing rules for different product combinations
    """
    name = models.CharField(max_length=255)
    product_category = models.CharField(max_length=100)
    size = models.CharField(max_length=50, blank=True)
    paper_type = models.CharField(max_length=50, blank=True)
    print_type = models.CharField(max_length=50, blank=True)

    # Pricing parameters
    base_rate = models.DecimalField(max_digits=10, decimal_places=4)
    minimum_pages = models.IntegerField(default=1)
    maximum_pages = models.IntegerField(null=True, blank=True)
    minimum_quantity = models.IntegerField(default=1)

    # Additional costs
    setup_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product_category', 'size', 'paper_type']
        unique_together = ['product_category', 'size', 'paper_type', 'print_type']

    def __str__(self):
        return f"{self.name} - {self.product_category}"


class ComponentOption(models.Model):
    """
    Individual component options (sizes, papers, finishes, etc.)
    """
    COMPONENT_TYPES = [
        ('size', 'Size'),
        ('paper', 'Paper Type'),
        ('binding', 'Binding'),
        ('finish', 'Finish'),
        ('print', 'Print Type'),
        ('design', 'Design Service'),
    ]

    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)  # Internal code for calculations
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    # Pricing impact
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    modifier_type = models.CharField(
        max_length=20,
        choices=[
            ('fixed', 'Fixed Amount'),
            ('percentage', 'Percentage'),
            ('multiplier', 'Rate Multiplier'),
        ],
        default='fixed'
    )

    # Compatibility and constraints
    compatible_categories = models.JSONField(default=list)
    min_pages = models.IntegerField(null=True, blank=True)
    max_pages = models.IntegerField(null=True, blank=True)
    min_quantity = models.IntegerField(default=1)

    # Display options
    sort_order = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['component_type', 'sort_order', 'name']
        unique_together = ['component_type', 'code']

    def __str__(self):
        return f"{self.get_component_type_display()}: {self.display_name}"
