from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from apps.products.models import Product


def compute_price(product: Product, quantity: int, options: dict) -> dict:
    base = Decimal(product.base_price)
    # Assume base price is for 50 units if min_quantity == 1 else for min_quantity
    reference_qty = product.min_quantity or 1
    if reference_qty < 1:
        reference_qty = 1

    total = base * Decimal(quantity) / Decimal(max(1, reference_qty))

    # Apply option modifiers if present
    modifiers_total = Decimal('0')
    for opt_key, opt_val in (options or {}).items():
        # Try to find a matching option list on product (e.g., paper_options)
        list_name = f"{opt_key}_options"
        option_list = getattr(product, list_name, []) or []
        for opt in option_list:
            if str(opt.get('value')) == str(opt_val):
                try:
                    modifiers_total += Decimal(str(opt.get('price_modifier', 0)))
                except Exception:
                    pass
                break

    total = total + modifiers_total

    # Simple bulk discounts example from description
    if quantity >= 300:
        total *= Decimal('0.86')
    elif quantity >= 200:
        total *= Decimal('0.90')
    elif quantity >= 100:
        total *= Decimal('0.94')
    elif quantity >= 50:
        total *= Decimal('0.98')

    per_piece = (total / Decimal(max(1, quantity))) if quantity else total

    return {
        'total': round(total, 2),
        'per_piece': round(per_piece, 2),
        'modifiers_total': round(modifiers_total, 2)
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def price_quote(request):
    try:
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity') or 0)
        options = request.data.get('options') or {}
        product = Product.objects.get(id=product_id, status='active')
    except Exception:
        return Response({'detail': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)

    data = compute_price(product, quantity, options)
    return Response(data)


