// src/pages/Cart/CartPage.tsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Button, 
  InputNumber, 
  Row, 
  Col, 
  Divider, 
  Empty,
  Tag,
  Popconfirm,
  Spin,
  Statistic,
  Space,
  Image
} from 'antd';
import {
  DeleteOutlined,
  ShoppingOutlined,
  CreditCardOutlined,
  EditOutlined
} from '@ant-design/icons';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import { CartItem } from '../../services/cart';

const CartPage: React.FC = () => {
  const { cart, loading, updateQuantity, removeItem, clearCart, getCartTotals } = useCart();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const totals = getCartTotals();

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full text-center">
          <div className="py-8">
            <ShoppingOutlined style={{ fontSize: 64 }} className="text-gray-300 mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Please Log In
            </h2>
            <p className="text-gray-600 mb-6">
              You need to be logged in to view your shopping cart.
            </p>
            <Button type="primary" size="large" onClick={() => navigate('/login')}>
              Log In
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          <p className="text-gray-600 mt-2">
            {cart?.items?.length || 0} item(s) in your cart
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <Spin size="large" />
            <p className="mt-4 text-gray-600">Loading your cart...</p>
          </div>
        ) : !cart || cart.items.length === 0 ? (
          <div className="text-center py-12">
            <Card>
              <Empty
                image={<ShoppingOutlined style={{ fontSize: 64 }} className="text-gray-300" />}
                description={
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Your cart is empty
                    </h3>
                    <p className="text-gray-500 mb-4">
                      Add some products to get started
                    </p>
                  </div>
                }
              >
                <Link to="/products">
                  <Button type="primary" size="large" icon={<ShoppingOutlined />}>
                    Continue Shopping
                  </Button>
                </Link>
              </Empty>
            </Card>
          </div>
        ) : (
          <Row gutter={24}>
            {/* Cart Items */}
            <Col xs={24} lg={16}>
              <Card 
                title="Cart Items" 
                extra={
                  <Popconfirm
                    title="Are you sure you want to clear your cart?"
                    onConfirm={clearCart}
                    okText="Yes"
                    cancelText="No"
                  >
                    <Button type="ghost" danger size="small">
                      Clear Cart
                    </Button>
                  </Popconfirm>
                }
              >
                <div className="space-y-4">
                  {cart.items.map((item: CartItem, index: number) => (
                    <div key={item.id}>
                      <Row gutter={16} align="middle">
                        {/* Product Image */}
                        <Col xs={6} sm={4}>
                          <div className="aspect-square">
                            {item.product.primary_image ? (
                              <Image
                                src={item.product.primary_image}
                                alt={item.product.name}
                                width="100%"
                                height="100%"
                                style={{ objectFit: 'cover' }}
                                className="rounded-lg"
                              />
                            ) : (
                              <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
                                <span className="text-gray-400 text-2xl">📄</span>
                              </div>
                            )}
                          </div>
                        </Col>

                        {/* Product Details */}
                        <Col xs={18} sm={20}>
                          <Row gutter={16} align="middle">
                            <Col xs={24} sm={12} md={10}>
                              <div>
                                <h4 className="font-medium text-gray-900 mb-1">
                                  {item.product.name}
                                </h4>
                                <p className="text-sm text-gray-500 mb-2">
                                  {item.product.category}
                                </p>
                                
                                {/* Product Options */}
                                {item.product_options && Object.keys(item.product_options).length > 0 && (
                                  <div className="flex flex-wrap gap-1 mb-2">
                                    {Object.entries(item.product_options).map(([key, value]) => (
                                      <Tag key={key}>
                                        {key}: {value as string}
                                      </Tag>
                                    ))}
                                  </div>
                                )}

                                <p className="text-sm text-gray-600">
                                  ₹{item.unit_price} per unit
                                </p>
                              </div>
                            </Col>

                            {/* Quantity */}
                            <Col xs={12} sm={6} md={6}>
                              <div className="text-center">
                                <label className="block text-xs text-gray-500 mb-1">
                                  Quantity
                                </label>
                                <InputNumber
                                  min={1}
                                  max={999}
                                  value={item.quantity}
                                  onChange={(value) => updateQuantity(item.id, value || 1)}
                                  size="small"
                                  style={{ width: '100%' }}
                                />
                              </div>
                            </Col>

                            {/* Price */}
                            <Col xs={8} sm={4} md={5}>
                              <div className="text-center">
                                <label className="block text-xs text-gray-500 mb-1">
                                  Total
                                </label>
                                <p className="font-semibold text-lg text-primary-600">
                                  ₹{parseFloat(item.total_price).toFixed(2)}
                                </p>
                              </div>
                            </Col>

                            {/* Actions */}
                            <Col xs={4} sm={2} md={3}>
                              <Space direction="vertical" size="small">
                                <Link to={`/products/${item.product.slug}`}>
                                  <Button 
                                    type="ghost" 
                                    icon={<EditOutlined />} 
                                    size="small"
                                    title="Edit Product"
                                  />
                                </Link>
                                <Popconfirm
                                  title="Remove this item?"
                                  onConfirm={() => removeItem(item.id)}
                                  okText="Yes"
                                  cancelText="No"
                                >
                                  <Button 
                                    type="ghost" 
                                    danger 
                                    icon={<DeleteOutlined />} 
                                    size="small"
                                    title="Remove Item"
                                  />
                                </Popconfirm>
                              </Space>
                            </Col>
                          </Row>
                        </Col>
                      </Row>
                      
                      {index < cart.items.length - 1 && <Divider />}
                    </div>
                  ))}
                </div>
              </Card>
            </Col>

            {/* Order Summary */}
            <Col xs={24} lg={8}>
              <Card title="Order Summary" className="sticky top-4">
                <div className="space-y-4">
                  {/* Summary Items */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Items ({totals.itemCount})</span>
                      <span>₹{totals.subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>GST (18%)</span>
                      <span>₹{totals.gstAmount.toFixed(2)}</span>
                    </div>
                    <Divider className="my-2" />
                    <div className="flex justify-between text-lg font-semibold">
                      <span>Total</span>
                      <span className="text-primary-600">₹{totals.total.toFixed(2)}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2 pt-4">
                    <Button
                      type="primary"
                      size="large"
                      block
                      icon={<CreditCardOutlined />}
                      onClick={() => navigate('/checkout')}
                    >
                      Proceed to Checkout
                    </Button>
                    
                    <Link to="/products">
                      <Button size="large" block>
                        Continue Shopping
                      </Button>
                    </Link>
                  </div>

                  {/* Shipping Info */}
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">
                      📦 Shipping Information
                    </h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• Free shipping on orders above ₹1000</li>
                      <li>• Standard delivery: 3-5 business days</li>
                      <li>• Express delivery available</li>
                    </ul>
                  </div>

                  {/* Help */}
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">
                      Need Help?
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      Have questions about your order?
                    </p>
                    <Link to="/contact">
                      <Button type="ghost" size="small" className="p-0">
                        Contact Support
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            </Col>
          </Row>
        )}
      </div>
    </div>
  );
};

export default CartPage;