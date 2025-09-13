// src/context/CartContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { message } from 'antd';
import { cartService, Cart, CartItem, AddToCartRequest } from '../services/cart';
import { useAuth } from './AuthContext';

interface CartContextType {
  cart: Cart | null;
  loading: boolean;
  error: string | null;
  addToCart: (data: AddToCartRequest) => Promise<void>;
  updateQuantity: (itemId: number, quantity: number) => Promise<void>;
  removeItem: (itemId: number) => Promise<void>;
  clearCart: () => Promise<void>;
  refreshCart: () => Promise<void>;
  getCartTotals: () => {
    subtotal: number;
    gstAmount: number;
    total: number;
    itemCount: number;
  };
}

const CartContext = createContext<CartContextType | undefined>(undefined);

interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  // Load cart when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshCart();
    } else {
      setCart(null);
    }
  }, [isAuthenticated]);

  const refreshCart = async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    setError(null);
    try {
      const cartData = await cartService.getCart();
      setCart(cartData);
    } catch (err: any) {
      console.error('Failed to load cart:', err);
      setError('Failed to load cart');
      // For demo purposes, create empty cart structure
      setCart({
        id: 0,
        items: [],
        total_amount: 0,
        total_items: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (data: AddToCartRequest) => {
    if (!isAuthenticated) {
      message.error('Please log in to add items to cart');
      return;
    }

    setLoading(true);
    try {
      await cartService.addToCart(data);
      await refreshCart();
      message.success('Item added to cart!');
    } catch (err: any) {
      console.error('Failed to add to cart:', err);
      message.error('Failed to add item to cart');
      
      // For demo purposes, add to local cart
      if (cart) {
        const mockItem: CartItem = {
          id: Date.now(),
          product: {
            id: data.product_id,
            name: 'Sample Product',
            slug: 'sample-product',
            category: 'Sample Category',
            base_price: '100.00',
          },
          quantity: data.quantity,
          product_options: data.options || {},
          unit_price: '100.00',
          total_price: (100 * data.quantity).toString(),
        };
        
        setCart(prev => prev ? {
          ...prev,
          items: [...prev.items, mockItem],
          total_items: prev.total_items + data.quantity,
          total_amount: prev.total_amount + (100 * data.quantity),
        } : null);
        
        message.success('Item added to cart! (Demo mode)');
      }
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId: number, quantity: number) => {
    if (!cart) return;

    setLoading(true);
    try {
      if (quantity <= 0) {
        await removeItem(itemId);
        return;
      }

      await cartService.updateCartItem(itemId, quantity);
      await refreshCart();
      message.success('Cart updated!');
    } catch (err: any) {
      console.error('Failed to update cart:', err);
      message.error('Failed to update cart');
      
      // For demo purposes, update local cart
      setCart(prev => {
        if (!prev) return null;
        
        const updatedItems = prev.items.map(item => 
          item.id === itemId 
            ? { 
                ...item, 
                quantity, 
                total_price: (parseFloat(item.unit_price) * quantity).toString() 
              }
            : item
        );
        
        const totals = cartService.calculateCartTotals(updatedItems);
        
        return {
          ...prev,
          items: updatedItems,
          total_items: totals.itemCount,
          total_amount: totals.total,
        };
      });
      
      message.success('Cart updated! (Demo mode)');
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (itemId: number) => {
    if (!cart) return;

    setLoading(true);
    try {
      await cartService.removeCartItem(itemId);
      await refreshCart();
      message.success('Item removed from cart!');
    } catch (err: any) {
      console.error('Failed to remove item:', err);
      message.error('Failed to remove item');
      
      // For demo purposes, remove from local cart
      setCart(prev => {
        if (!prev) return null;
        
        const updatedItems = prev.items.filter(item => item.id !== itemId);
        const totals = cartService.calculateCartTotals(updatedItems);
        
        return {
          ...prev,
          items: updatedItems,
          total_items: totals.itemCount,
          total_amount: totals.total,
        };
      });
      
      message.success('Item removed from cart! (Demo mode)');
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    if (!cart || cart.items.length === 0) return;

    setLoading(true);
    try {
      await cartService.clearCart();
      await refreshCart();
      message.success('Cart cleared!');
    } catch (err: any) {
      console.error('Failed to clear cart:', err);
      message.error('Failed to clear cart');
      
      // For demo purposes, clear local cart
      setCart(prev => prev ? {
        ...prev,
        items: [],
        total_items: 0,
        total_amount: 0,
      } : null);
      
      message.success('Cart cleared! (Demo mode)');
    } finally {
      setLoading(false);
    }
  };

  const getCartTotals = () => {
    if (!cart || !cart.items) {
      return {
        subtotal: 0,
        gstAmount: 0,
        total: 0,
        itemCount: 0,
      };
    }

    return cartService.calculateCartTotals(cart.items);
  };

  const value: CartContextType = {
    cart,
    loading,
    error,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    refreshCart,
    getCartTotals,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = (): CartContextType => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export default CartContext;