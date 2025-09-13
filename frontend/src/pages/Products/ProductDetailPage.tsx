// src/pages/Products/ProductDetailPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Button from 'antd/lib/button';
import Card from 'antd/lib/card';
import Carousel from 'antd/lib/carousel';
import Tag from 'antd/lib/tag';
import Tabs from 'antd/lib/tabs';
import InputNumber from 'antd/lib/input-number';
import Select from 'antd/lib/select';
import Row from 'antd/lib/row';
import Col from 'antd/lib/col';
import Spin from 'antd/lib/spin';
import message from 'antd/lib/message';
import Modal from 'antd/lib/modal';
import { productsService, Product } from '../../services/products';
import { useAuth } from '../../context/AuthContext';

const { TabPane } = Tabs;
const { Option } = Select;

const ProductDetailPage: React.FC = () => {
  const { categorySlug, productSlug } = useParams<{ 
    categorySlug: string; 
    productSlug: string; 
  }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  // State
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [selectedOptions, setSelectedOptions] = useState<any>({});
  const [calculatedPrice, setCalculatedPrice] = useState<any>(null);
  const [priceLoading, setPriceLoading] = useState(false);

  useEffect(() => {
    if (productSlug) {
      loadProduct();
    }
  }, [productSlug]);

  useEffect(() => {
    if (product) {
      calculatePrice();
    }
  }, [product, quantity, selectedOptions]);

  const loadProduct = async () => {
    if (!productSlug) return;
    
    setLoading(true);
    try {
      const data = await productsService.getProduct(productSlug);
      setProduct(data);
      
      // Set default options
      const defaultOptions: any = {};
      if (data.size_options && Array.isArray(data.size_options)) {
        defaultOptions.size = data.size_options[0];
      }
      if (data.paper_options && Array.isArray(data.paper_options)) {
        defaultOptions.paper = data.paper_options[0];
      }
      setSelectedOptions(defaultOptions);
      setQuantity(data.min_quantity || 1);
    } catch (error) {
      console.error('Failed to load product:', error);
      message.error('Failed to load product details');
    } finally {
      setLoading(false);
    }
  };

  const calculatePrice = async () => {
    if (!product) return;
    
    setPriceLoading(true);
    try {
      const specifications = {
        quantity,
        ...selectedOptions,
      };
      
      const pricing = await productsService.calculatePricing(product.slug, specifications);
      setCalculatedPrice(pricing);
    } catch (error) {
      console.error('Failed to calculate price:', error);
      // Fallback to base price calculation
      const basePrice = parseFloat(product.base_price);
      setCalculatedPrice({
        subtotal: basePrice * quantity,
        gst_amount: basePrice * quantity * 0.18,
        total: basePrice * quantity * 1.18,
        quantity,
      });
    } finally {
      setPriceLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (!isAuthenticated) {
      Modal.confirm({
        title: 'Login Required',
        content: 'Please log in to add items to your cart.',
        okText: 'Login',
        cancelText: 'Cancel',
        onOk: () => navigate('/login'),
      });
      return;
    }

    // TODO: Implement add to cart API call
    message.success('Product added to cart!');
  };

  const handleDesignNow = () => {
    if (!isAuthenticated) {
      Modal.confirm({
        title: 'Login Required',
        content: 'Please log in to use the design tool.',
        okText: 'Login',
        cancelText: 'Cancel',
        onOk: () => navigate('/login'),
      });
      return;
    }

    navigate(`/design/editor/${product?.slug}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Product Not Found
          </h2>
          <Link to="/products">
            <span className="inline-block px-4 py-2 bg-primary-600 text-white rounded">Browse Products</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <nav className="text-sm">
            <Link to="/" className="text-gray-500 hover:text-gray-700">Home</Link>
            <span className="mx-2 text-gray-400">/</span>
            <Link to="/products" className="text-gray-500 hover:text-gray-700">Products</Link>
            <span className="mx-2 text-gray-400">/</span>
            <Link 
              to={`/products?category=${product.category.slug}`} 
              className="text-gray-500 hover:text-gray-700"
            >
              {product.category.name}
            </Link>
            <span className="mx-2 text-gray-400">/</span>
            <span className="text-gray-900">{product.name}</span>
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Row gutter={32}>
          {/* Product Images */}
          <Col xs={24} lg={12}>
            <Card className="overflow-hidden">
              {product.images && product.images.length > 0 ? (
                <Carousel autoplay>
                  {product.images.map((image, index) => (
                    <div key={index}>
                      <img
                        src={image.image}
                        alt={image.alt_text || product.name}
                        className="w-full h-96 object-cover"
                      />
                    </div>
                  ))}
                </Carousel>
              ) : (
                <div className="w-full h-96 bg-gray-100 flex items-center justify-center">
                  <div className="text-center text-gray-400">
                    <div className="text-6xl mb-4">📄</div>
                    <div className="text-lg">{product.name}</div>
                  </div>
                </div>
              )}
            </Card>
          </Col>

          {/* Product Info */}
          <Col xs={24} lg={12}>
            <div className="space-y-6">
              {/* Header */}
              <div>
                <div className="flex items-start justify-between mb-2">
                  <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>
                  <div className="flex space-x-2">
                    <button className="px-2 py-1 border rounded">❤</button>
                    <button className="px-2 py-1 border rounded">⤴</button>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 mb-4">
                  <Tag color="blue">{product.category.name}</Tag>
                  {product.featured && <Tag color="gold">Featured</Tag>}
                  {product.bestseller && <Tag color="red">Bestseller</Tag>}
                  {product.design_tool_enabled && (
                    <Tag color="purple">Design Tool</Tag>
                  )}
                </div>

                <p className="text-gray-600 text-lg mb-4">
                  {product.short_description}
                </p>

                {/* Price */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-baseline space-x-2">
                    <span className="text-3xl font-bold text-primary-600">
                      ₹{calculatedPrice ? calculatedPrice.total.toFixed(2) : product.base_price}
                    </span>
                    {calculatedPrice && calculatedPrice.quantity > 1 && (
                      <span className="text-gray-500">
                        (₹{(calculatedPrice.total / calculatedPrice.quantity).toFixed(2)} per unit)
                      </span>
                    )}
                  </div>
                  {calculatedPrice && (
                    <div className="text-sm text-gray-600 mt-2">
                      <div>Subtotal: ₹{calculatedPrice.subtotal.toFixed(2)}</div>
                      <div>GST (18%): ₹{calculatedPrice.gst_amount.toFixed(2)}</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Options */}
              <div className="space-y-4">
                {/* Quantity */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity
                  </label>
                  <InputNumber
                    min={product.min_quantity}
                    max={product.max_quantity}
                    value={quantity}
                    onChange={(value) => setQuantity(value || 1)}
                    size="large"
                    style={{ width: 120 }}
                  />
                  <span className="ml-2 text-sm text-gray-500">
                    Min: {product.min_quantity}, Max: {product.max_quantity}
                  </span>
                </div>

                {/* Size Options */}
                {product.size_options && Array.isArray(product.size_options) && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Size
                    </label>
                    <Select
                      value={selectedOptions.size}
                      onChange={(value) => setSelectedOptions((prev: any) => ({ ...prev, size: value }))}
                      style={{ width: 200 }}
                      size="large"
                    >
                      {product.size_options.map((size, index) => (
                        <Option key={index} value={size}>{size}</Option>
                      ))}
                    </Select>
                  </div>
                )}

                {/* Paper Options */}
                {product.paper_options && Array.isArray(product.paper_options) && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Paper Type
                    </label>
                    <Select
                      value={selectedOptions.paper}
                      onChange={(value) => setSelectedOptions((prev: any) => ({ ...prev, paper: value }))}
                      style={{ width: 200 }}
                      size="large"
                    >
                      {product.paper_options.map((paper, index) => (
                        <Option key={index} value={paper}>{paper}</Option>
                      ))}
                    </Select>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="space-y-3">
                {product.design_tool_enabled && (
                  <button
                    className="w-full px-4 py-2 bg-primary-600 text-white rounded"
                    onClick={handleDesignNow}
                  >
                    Design & Order
                  </button>
                )}
                
                <button
                  className={`w-full px-4 py-2 rounded ${product.design_tool_enabled ? 'border' : 'bg-primary-600 text-white'}`}
                  onClick={handleAddToCart}
                >
                  Add to Cart
                </button>
              </div>

              {/* Features */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <span className="text-green-600">✔</span>
                  <span className="text-sm text-gray-600">Quality Guaranteed</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-blue-600">🚚</span>
                  <span className="text-sm text-gray-600">
                    {product.lead_time_days} days delivery
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-purple-600">🔒</span>
                  <span className="text-sm text-gray-600">Secure Payment</span>
                </div>
                {product.rush_available && (
                  <div className="flex items-center space-x-2">
                    <span className="text-orange-500">⭐</span>
                    <span className="text-sm text-gray-600">Rush Available</span>
                  </div>
                )}
              </div>
            </div>
          </Col>
        </Row>

        {/* Product Details Tabs */}
        <div className="mt-12">
          <Tabs defaultActiveKey="description" size="large">
            <TabPane tab="Description" key="description">
              <Card>
                <div 
                  className="prose max-w-none"
                  dangerouslySetInnerHTML={{ __html: product.description }}
                />
              </Card>
            </TabPane>
            
            <TabPane tab="Specifications" key="specifications">
              <Card>
                <Row gutter={16}>
                  <Col span={12}>
                    <h4 className="font-medium mb-2">Product Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Product Type:</span>
                        <span className="font-medium">{product.product_type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Stock Status:</span>
                        <span className="font-medium text-green-600">{product.stock_status}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Lead Time:</span>
                        <span className="font-medium">{product.lead_time_days} days</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Rush Available:</span>
                        <span className="font-medium">{product.rush_available ? 'Yes' : 'No'}</span>
                      </div>
                    </div>
                  </Col>
                  <Col span={12}>
                    <h4 className="font-medium mb-2">Available Options</h4>
                    <div className="space-y-2 text-sm">
                      {product.size_options && (
                        <div>
                          <span className="font-medium">Sizes:</span>
                          <div className="mt-1">
                            {Array.isArray(product.size_options) 
                              ? product.size_options.join(', ')
                              : 'Custom sizes available'
                            }
                          </div>
                        </div>
                      )}
                      {product.paper_options && (
                        <div>
                          <span className="font-medium">Paper Types:</span>
                          <div className="mt-1">
                            {Array.isArray(product.paper_options) 
                              ? product.paper_options.join(', ')
                              : 'Multiple options available'
                            }
                          </div>
                        </div>
                      )}
                    </div>
                  </Col>
                </Row>
              </Card>
            </TabPane>
            
            <TabPane tab="Reviews" key="reviews">
              <Card>
                <div className="text-center py-8 text-gray-500">
                  <span className="text-5xl mb-4 inline-block">⭐</span>
                  <p>Customer reviews coming soon!</p>
                </div>
              </Card>
            </TabPane>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;