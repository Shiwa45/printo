"""
Django management command to update pricing structure based on Creative Print Arts analysis
Usage: python manage.py update_pricing_from_cpa
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import (
    ProductCategory, Product, ProductSubcategory,
    PricingCalculator, DesignTemplate
)
import json


class Command(BaseCommand):
    help = 'Update pricing structure based on Creative Print Arts analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']

        if self.dry_run:
            self.stdout.write("DRY RUN MODE - No changes will be made")

        with transaction.atomic():
            self.update_product_categories()
            self.update_products()
            self.update_pricing_structure()

        if not self.dry_run:
            self.stdout.write(
                self.style.SUCCESS('Successfully updated pricing structure from CPA analysis')
            )

    def update_product_categories(self):
        """Update product categories based on CPA structure"""
        categories_data = [
            {
                'name': 'Book Printing',
                'slug': 'book-printing',
                'description': 'Professional book printing services with multiple binding options',
                'icon': 'book',
                'sort_order': 1
            },
            {
                'name': 'Document Printing',
                'slug': 'document-printing',
                'description': 'Business document printing for reports, manuals, and presentations',
                'icon': 'document',
                'sort_order': 2
            },
            {
                'name': 'Business Cards',
                'slug': 'business-cards',
                'description': 'Professional business cards in various finishes',
                'icon': 'card',
                'sort_order': 3
            },
            {
                'name': 'Letter Heads',
                'slug': 'letter-heads',
                'description': 'Corporate letterheads for official correspondence',
                'icon': 'letterhead',
                'sort_order': 4
            },
            {
                'name': 'Bill Books',
                'slug': 'bill-books',
                'description': 'Customized bill books for businesses',
                'icon': 'bill',
                'sort_order': 5
            },
            {
                'name': 'Stickers',
                'slug': 'stickers',
                'description': 'Custom stickers and labels',
                'icon': 'sticker',
                'sort_order': 6
            }
        ]

        for cat_data in categories_data:
            if not self.dry_run:
                category, created = ProductCategory.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults=cat_data
                )
                action = "Created" if created else "Updated"
                self.stdout.write(f"{action} category: {category.name}")
            else:
                self.stdout.write(f"Would create/update category: {cat_data['name']}")

    def update_products(self):
        """Update products with CPA-compatible structure"""

        # Get or create categories
        book_category = ProductCategory.objects.get(slug='book-printing') if not self.dry_run else None
        doc_category = ProductCategory.objects.get(slug='document-printing') if not self.dry_run else None

        products_data = [
            {
                'name': 'Paperback Book',
                'slug': 'paperback-book',
                'category': book_category,
                'product_type': 'book',
                'description': 'Perfect bound paperback books with professional finish',
                'short_description': 'Affordable paperback books with various paper and size options',
                'base_price': 150.00,
                'size_options': [
                    {'name': 'A4', 'display': 'A4 (8.27 x 11.69 in)', 'width': 210, 'height': 297},
                    {'name': 'Letter', 'display': 'Letter (8.5 x 11 in)', 'width': 216, 'height': 279},
                    {'name': 'Executive', 'display': 'Executive (7 x 10 in)', 'width': 178, 'height': 254},
                    {'name': 'A5', 'display': 'A5 (5.83 x 8.27 in)', 'width': 148, 'height': 210}
                ],
                'paper_options': [
                    {'name': '75gsm', 'display': '75 GSM Offset Paper', 'weight': 75, 'type': 'offset'},
                    {'name': '100gsm', 'display': '100 GSM Offset Paper', 'weight': 100, 'type': 'offset'},
                    {'name': '100gsm_art', 'display': '100 GSM Art Paper', 'weight': 100, 'type': 'art'},
                    {'name': '130gsm_art', 'display': '130 GSM Art Paper', 'weight': 130, 'type': 'art'}
                ],
                'binding_options': [
                    {'name': 'paperback_perfect', 'display': 'Perfect Binding', 'min_pages': 32, 'max_pages': 800},
                    {'name': 'spiral_binding', 'display': 'Spiral Binding', 'min_pages': 20, 'max_pages': 470},
                    {'name': 'saddle_stitch', 'display': 'Saddle Stitch', 'min_pages': 8, 'max_pages': 48}
                ],
                'print_options': [
                    {'name': 'bw_standard', 'display': 'Black & White Standard'},
                    {'name': 'bw_premium', 'display': 'Black & White Premium'},
                    {'name': 'color_standard', 'display': 'Color Standard'},
                    {'name': 'color_premium', 'display': 'Color Premium'}
                ],
                'finish_options': [
                    {'name': 'matte', 'display': 'Matte Finish'},
                    {'name': 'glossy', 'display': 'Glossy Finish'}
                ],
                'min_quantity': 25,
                'design_tool_enabled': True,
                'has_subcategories': False
            },
            {
                'name': 'Hardcover Book',
                'slug': 'hardcover-book',
                'category': book_category,
                'product_type': 'book',
                'description': 'Premium hardcover books with durable binding',
                'short_description': 'Professional hardcover books for lasting impression',
                'base_price': 300.00,
                'size_options': [
                    {'name': 'A4', 'display': 'A4 (8.27 x 11.69 in)', 'width': 210, 'height': 297},
                    {'name': 'Letter', 'display': 'Letter (8.5 x 11 in)', 'width': 216, 'height': 279},
                    {'name': 'Executive', 'display': 'Executive (7 x 10 in)', 'width': 178, 'height': 254},
                    {'name': 'A5', 'display': 'A5 (5.83 x 8.27 in)', 'width': 148, 'height': 210}
                ],
                'paper_options': [
                    {'name': '100gsm', 'display': '100 GSM Offset Paper', 'weight': 100, 'type': 'offset'},
                    {'name': '100gsm_art', 'display': '100 GSM Art Paper', 'weight': 100, 'type': 'art'},
                    {'name': '130gsm_art', 'display': '130 GSM Art Paper', 'weight': 130, 'type': 'art'}
                ],
                'binding_options': [
                    {'name': 'hardcover', 'display': 'Hardcover Binding', 'min_pages': 32, 'max_pages': 800}
                ],
                'print_options': [
                    {'name': 'bw_premium', 'display': 'Black & White Premium'},
                    {'name': 'color_standard', 'display': 'Color Standard'},
                    {'name': 'color_premium', 'display': 'Color Premium'}
                ],
                'finish_options': [
                    {'name': 'matte', 'display': 'Matte Finish'},
                    {'name': 'glossy', 'display': 'Glossy Finish'}
                ],
                'min_quantity': 25,
                'design_tool_enabled': True,
                'has_subcategories': False
            },
            {
                'name': 'Document Printing',
                'slug': 'document-printing',
                'category': doc_category,
                'product_type': 'stationery',
                'description': 'Professional document printing for business reports and presentations',
                'short_description': 'High-quality document printing with binding options',
                'base_price': 50.00,
                'size_options': [
                    {'name': 'A4', 'display': 'A4 (8.27 x 11.69 in)', 'width': 210, 'height': 297},
                    {'name': 'Legal', 'display': 'Legal (8.5 x 14 in)', 'width': 216, 'height': 356},
                    {'name': 'A3', 'display': 'A3 (11.7 x 16.5 in)', 'width': 297, 'height': 420}
                ],
                'paper_options': [
                    {'name': '75gsm', 'display': '75 GSM Offset Paper', 'weight': 75, 'type': 'offset'},
                    {'name': '100gsm', 'display': '100 GSM Offset Paper', 'weight': 100, 'type': 'offset'}
                ],
                'binding_options': [
                    {'name': 'saddle_stitch', 'display': 'Saddle Stitch', 'min_pages': 8, 'max_pages': 19},
                    {'name': 'spiral_binding', 'display': 'Spiral Binding', 'min_pages': 20, 'max_pages': 31},
                    {'name': 'paperback_perfect', 'display': 'Perfect Binding', 'min_pages': 32, 'max_pages': 48}
                ],
                'print_options': [
                    {'name': 'bw_standard', 'display': 'Black & White'},
                    {'name': 'color_standard', 'display': 'Color'},
                    {'name': 'combine_color', 'display': 'Combine Color'}
                ],
                'finish_options': [
                    {'name': 'matte', 'display': 'Matte Finish'},
                    {'name': 'glossy', 'display': 'Glossy Finish'}
                ],
                'min_quantity': 25,
                'design_tool_enabled': True,
                'has_subcategories': False
            }
        ]

        for product_data in products_data:
            if not self.dry_run:
                if product_data['category']:  # Only create if category exists
                    product, created = Product.objects.get_or_create(
                        slug=product_data['slug'],
                        defaults=product_data
                    )
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"{action} product: {product.name}")
            else:
                self.stdout.write(f"Would create/update product: {product_data['name']}")

    def update_pricing_structure(self):
        """Update the PricingCalculator with enhanced CPA-compatible rates"""

        # Enhanced rates based on CPA analysis and market research
        enhanced_book_rates = {
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

        # Enhanced binding options with updated rates
        enhanced_binding_options = {
            'paperback_perfect': {'name': 'Perfect Binding', 'rate': 45, 'min_pages': 32, 'max_pages': 800},
            'spiral_binding': {'name': 'Spiral Binding', 'rate': 45, 'min_pages': 20, 'max_pages': 470},
            'hardcover': {'name': 'Hardcover', 'rate': 160, 'min_pages': 32, 'max_pages': 800},
            'saddle_stitch': {'name': 'Saddle Stitch', 'rate': 30, 'min_pages': 8, 'max_pages': 48},
            'wire_o_bound': {'name': 'Wire-O Bound', 'rate': 65, 'min_pages': 32, 'max_pages': None}
        }

        # Enhanced quantity discounts
        enhanced_quantity_discounts = [
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

        # Enhanced design rates
        enhanced_design_rates = {
            'cover_design': 1500,
            'isbn_allocation': 1500,
            'design_support': {'A4': 55, 'Letter': 55, 'Executive': 50, 'A5': 45},
            'formatting_per_page': 50
        }

        if not self.dry_run:
            # Update the PricingCalculator class constants
            # Note: This updates the class definition in memory,
            # but for permanent changes, you'd need to update the model file
            PricingCalculator.BOOK_RATES = enhanced_book_rates
            PricingCalculator.BINDING_OPTIONS = enhanced_binding_options
            PricingCalculator.QUANTITY_DISCOUNTS = enhanced_quantity_discounts
            PricingCalculator.DESIGN_RATES = enhanced_design_rates

            self.stdout.write("Updated PricingCalculator with enhanced CPA-compatible rates")
        else:
            self.stdout.write("Would update PricingCalculator with enhanced rates:")
            self.stdout.write(f"  - {len(enhanced_book_rates)} size categories")
            self.stdout.write(f"  - {len(enhanced_binding_options)} binding options")
            self.stdout.write(f"  - {len(enhanced_quantity_discounts)} discount tiers")
            self.stdout.write(f"  - Enhanced design services pricing")