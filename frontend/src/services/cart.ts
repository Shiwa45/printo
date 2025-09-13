// src/services/cart.ts
import { api, handleResponse } from './api';

// Cart Types
export interface CartItem {
  id: number;
  product: {
    id: number;
    name: string;
    slug: string;
    category: string;
    base_price: string;
    primary_image?: string;
  };
  quantity: number;
  product_options: any;
  unit_price: string;
  total_price: string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total_amount: number;
  total_items: number;
  created_at: string;
  updated_at: string;
}

export interface AddToCartRequest {
  product_id: number;
  quantity: number;
  options?: any;
}

export const cartService = {
  // Get current cart
  getCart: async (): Promise<Cart> => {
    const response = await api.get<Cart>('/cart/');
    return handleResponse(response);
  },

  // Add item to cart
  addToCart: async (data: AddToCartRequest): Promise<CartItem> => {
    const response = await api.post<CartItem>('/cart/add_item/', data);
    return handleResponse(response);
  },

  // Update cart item quantity
  updateCartItem: async (itemId: number, quantity: number): Promise<CartItem | null> => {
    const response = await api.patch(`/cart/update_item/`, {
      item_id: itemId,
      quantity: quantity
    });
    return handleResponse(response);
  },

  // Remove item from cart
  removeCartItem: async (itemId: number): Promise<void> => {
    await api.patch(`/cart/update_item/`, {
      item_id: itemId,
      quantity: 0
    });
  },

  // Clear entire cart
  clearCart: async (): Promise<void> => {
    const cart = await cartService.getCart();
    for (const item of cart.items) {
      await cartService.removeCartItem(item.id);
    }
  },

  // Calculate cart totals (local calculation for immediate feedback)
  calculateCartTotals: (items: CartItem[]) => {
    const subtotal = items.reduce((sum, item) => sum + parseFloat(item.total_price), 0);
    const gstAmount = subtotal * 0.18; // 18% GST
    const total = subtotal + gstAmount;
    
    return {
      subtotal,
      gstAmount,
      total,
      itemCount: items.reduce((sum, item) => sum + item.quantity, 0)
    };
  },
};

export default cartService;