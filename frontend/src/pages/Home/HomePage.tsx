// src/pages/Home/HomePage.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from 'antd/lib/card';
import Spin from 'antd/lib/spin';
import Row from 'antd/lib/row';
import Col from 'antd/lib/col';
import { productsService, Product, ProductCategory } from '../../services/products';
import '../../styles/hero.css';

const { Meta } = Card;

const HomePage: React.FC = () => {
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [designProducts, setDesignProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHomeData();
  }, []);

  const loadHomeData = async () => {
    try {
      const [featured, design, cats] = await Promise.all([
        productsService.getBestsellers(),
        productsService.getDesignProducts(),
        productsService.getCategories(),
      ]);
      
      setFeaturedProducts(featured.slice(0, 4));
      setDesignProducts(design.slice(0, 6));
      setCategories(cats.slice(0, 6));
    } catch (error) {
      console.error('Failed to load home data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Hero Section */}
      <section className="hero-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1>
              Professional Quality
              <span> Custom Printing</span>
            </h1>
            <p className="max-w-3xl mx-auto">
              From business cards to banners, we deliver high-quality printing solutions 
              with fast turnaround times and competitive prices.
            </p>
            <div>
              <Link 
                to="/products" 
                className="hero-button hero-button-primary"
              >
                Browse Products
              </Link>
              <Link 
                to="/design/templates" 
                className="hero-button hero-button-secondary"
              >
                Design Tool
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Browse by Category
            </h2>
            <p className="text-gray-600 text-lg">
              Find the perfect printing solution for your needs
            </p>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <Spin size="large" />
            </div>
          ) : (
            <Row gutter={24}>
              {categories.map(category => (
                <Col xs={12} sm={8} lg={4} key={category.id}>
                  <Link to={`/products?category=${category.slug}`}>
                    <Card
                      hoverable
                      className="text-center h-full"
                      bodyStyle={{ padding: '24px 16px' }}
                    >
                      <div className="text-4xl mb-3">
                        {category.icon || '📋'}
                      </div>
                      <h3 className="font-medium text-gray-900 mb-2">
                        {category.name}
                      </h3>
                      <p className="text-sm text-gray-500 line-clamp-2">
                        {category.description}
                      </p>
                    </Card>
                  </Link>
                </Col>
              ))}
            </Row>
          )}
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Bestselling Products
            </h2>
            <p className="text-gray-600 text-lg">
              Our most popular printing services
            </p>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <Spin size="large" />
            </div>
          ) : (
            <Row gutter={24}>
              {featuredProducts.map(product => (
                <Col xs={24} sm={12} lg={6} key={product.id}>
                  <Card
                    hoverable
                    cover={
                      <div className="h-48 bg-gray-100 relative overflow-hidden">
                        {product.primary_image ? (
                          <img
                            src={product.primary_image}
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <div className="text-gray-400">
                              <div className="text-3xl mb-2">📄</div>
                              <div className="text-sm">{product.name}</div>
                            </div>
                          </div>
                        )}
                        {product.bestseller && (
                          <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs">
                            Bestseller
                          </div>
                        )}
                      </div>
                    }
                    actions={[
                      <Link to={`/products/${product.category.slug}/${product.slug}`}>
                        <span className="inline-block px-3 py-1 text-white bg-primary-600 rounded text-sm">
                          Order Now
                        </span>
                      </Link>,
                      ...(product.design_tool_enabled ? [
                        <Link to={`/design/editor/${product.slug}`}>
                          <span className="inline-block px-3 py-1 bg-gray-800 text-white rounded text-sm">
                            Design
                          </span>
                        </Link>
                      ] : [])
                    ]}
                  >
                    <Meta
                      title={product.name}
                      description={
                        <div>
                          <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                            {product.short_description}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-lg font-semibold text-primary-600">
                              ₹{product.base_price}
                            </span>
                            <span className="text-xs text-gray-500">
                              {product.category.name}
                            </span>
                          </div>
                        </div>
                      }
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          )}

          <div className="text-center mt-8">
            <Link to="/products">
              <span className="inline-block px-5 py-2 bg-primary-600 text-white rounded text-base">
                View All Products
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* Design Tool Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Row gutter={48} align="middle">
            <Col xs={24} lg={12}>
              <div>
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                  No Design? <span className="text-primary-600">No Problem!</span>
                </h2>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Our powerful design tool lets you create professional designs in minutes. 
                  With templates, drag-and-drop editing, and thousands of design elements, 
                  you can create stunning prints without any design experience.
                </p>
                
                <div className="space-y-4 mb-8">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <span className="text-gray-700">Professional templates for every need</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <span className="text-gray-700">Drag-and-drop editor (like PowerPoint)</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <span className="text-gray-700">High-resolution export for printing</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <span className="text-gray-700">Save and edit your designs anytime</span>
                  </div>
                </div>

                <div className="space-x-4">
                  <Link to="/design/templates">
                    <span className="inline-block px-5 py-2 bg-primary-600 text-white rounded text-base">
                      Try Design Tool
                    </span>
                  </Link>
                  <Link to="/products?design_tool_enabled=true">
                    <span className="inline-block px-5 py-2 border border-gray-300 rounded text-base">
                      Design-Enabled Products
                    </span>
                  </Link>
                </div>
              </div>
            </Col>
            
            <Col xs={24} lg={12}>
              {loading ? (
                <div className="text-center py-8">
                  <Spin size="large" />
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {designProducts.slice(0, 4).map(product => (
                    <Card
                      key={product.id}
                      hoverable
                      size="small"
                      cover={
                        <div className="h-32 bg-gray-100 relative">
                          {product.primary_image ? (
                            <img
                              src={product.primary_image}
                              alt={product.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                              <span style={{ fontSize: 24 }}>🎨</span>
                            </div>
                          )}
                        </div>
                      }
                    >
                      <Meta
                        title={<span className="text-sm font-medium">{product.name}</span>}
                        description={
                          <Link to={`/design/editor/${product.slug}`}>
                            <span className="inline-block w-full text-center px-3 py-1 bg-primary-600 text-white rounded text-sm">
                              Design Now
                            </span>
                          </Link>
                        }
                      />
                    </Card>
                  ))}
                </div>
              )}
            </Col>
          </Row>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose Drishthi Printing?
            </h2>
            <p className="text-gray-600 text-lg">
              We make professional printing simple and affordable
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Fast Turnaround</h3>
              <p className="text-gray-600">
                Quick delivery without compromising on quality. Most orders ready in 24-48 hours.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Premium Quality</h3>
              <p className="text-gray-600">
                High-quality materials and state-of-the-art printing technology for perfect results.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Design Support</h3>
              <p className="text-gray-600">
                Free design assistance and our powerful online design tool to create stunning prints.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-primary-100 text-lg mb-8">
            Join thousands of satisfied customers who trust us with their printing needs.
          </p>
          <div className="space-x-4">
            <Link to="/products">
              <span className="inline-block px-5 py-2 bg-white text-primary-600 rounded text-base">
                Browse Products
              </span>
            </Link>
            <Link to="/design/templates">
              <span className="inline-block px-5 py-2 bg-white text-primary-600 rounded text-base">
                Start Designing
              </span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;