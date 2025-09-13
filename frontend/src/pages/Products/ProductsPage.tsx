// src/pages/Products/ProductsPage.tsx
import React, { useState, useEffect } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import Input from 'antd/lib/input';
import Select from 'antd/lib/select';
import Pagination from 'antd/lib/pagination';
import Spin from 'antd/lib/spin';
import Card from 'antd/lib/card';
import Tag from 'antd/lib/tag';
import { productsService, Product, ProductCategory } from '../../services/products';

const { Option } = Select;
const { Meta } = Card;

const ProductsPage: React.FC = () => {
  const { categorySlug } = useParams<{ categorySlug: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentCategory, setCurrentCategory] = useState<ProductCategory | null>(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 12,
    total: 0,
  });

  // Filters
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [selectedCategory, setSelectedCategory] = useState(categorySlug || 'all');
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
  const [showDesignEnabled, setShowDesignEnabled] = useState(false);
  const [sortBy, setSortBy] = useState('featured');

  // Load data on component mount and when filters change
  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadProducts();
  }, [categorySlug, searchParams, pagination.current, selectedCategory, showFeaturedOnly, showDesignEnabled, sortBy]);

  useEffect(() => {
    if (categorySlug && categories.length > 0) {
      const category = categories.find(c => c.slug === categorySlug);
      setCurrentCategory(category || null);
      setSelectedCategory(categorySlug);
    }
  }, [categorySlug, categories]);

  const loadCategories = async () => {
    try {
      const data = await productsService.getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadProducts = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.current,
        ...(selectedCategory !== 'all' && { category: selectedCategory }),
        ...(searchQuery && { search: searchQuery }),
        ...(showFeaturedOnly && { featured: true }),
        ...(showDesignEnabled && { design_tool_enabled: true }),
      };

      const data = await productsService.getProducts(params);
      setProducts(data.results);
      setPagination(prev => ({
        ...prev,
        total: data.count,
      }));
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle search
  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setSearchParams(prev => {
      if (value) {
        prev.set('search', value);
      } else {
        prev.delete('search');
      }
      return prev;
    });
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  // Handle filter changes
  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handlePageChange = (page: number) => {
    setPagination(prev => ({ ...prev, current: page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              {currentCategory ? currentCategory.name : 'All Products'}
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              {currentCategory 
                ? currentCategory.description 
                : 'Professional quality printing services for all your business needs'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="flex-1 max-w-lg">
              <Input.Search
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onSearch={handleSearch}
                prefix={<span role="img" aria-label="search">🔍</span>}
                size="large"
              />
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center space-x-2">
                <span className="text-gray-500">⚙️</span>
                <Select
                  value={selectedCategory}
                  onChange={handleCategoryChange}
                  style={{ minWidth: 150 }}
                  size="large"
                >
                  <Option value="all">All Categories</Option>
                  {categories.map(category => (
                    <Option key={category.slug} value={category.slug}>
                      {category.name}
                    </Option>
                  ))}
                </Select>
              </div>

              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showFeaturedOnly}
                    onChange={(e) => setShowFeaturedOnly(e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Featured only</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showDesignEnabled}
                    onChange={(e) => setShowDesignEnabled(e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Design tool</span>
                </label>
              </div>

              <Select
                value={sortBy}
                onChange={setSortBy}
                style={{ minWidth: 120 }}
                size="large"
              >
                <Option value="featured">Featured</Option>
                <Option value="name">Name</Option>
                <Option value="price">Price</Option>
                <Option value="newest">Newest</Option>
              </Select>
            </div>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <Spin size="large" />
            <p className="mt-4 text-gray-600">Loading products...</p>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4 text-5xl">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
            <p className="text-gray-500 mb-4">
              Try adjusting your search criteria or browse different categories.
            </p>
            <button className="px-4 py-2 bg-primary-600 text-white rounded" onClick={() => {
              setSearchQuery('');
              setSelectedCategory('all');
              setShowFeaturedOnly(false);
              setShowDesignEnabled(false);
              handleSearch('');
            }}>
              Clear Filters
            </button>
          </div>
        ) : (
          <>
            {/* Results Info */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                Showing {products.length} of {pagination.total} products
              </p>
              <div className="text-sm text-gray-500">
                Page {pagination.current} of {Math.ceil(pagination.total / pagination.pageSize)}
              </div>
            </div>

            {/* Products Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map(product => (
                <Card
                  key={product.id}
                  hoverable
                  cover={
                    <div className="relative h-48 bg-gray-100">
                      {product.primary_image ? (
                        <img
                          src={product.primary_image}
                          alt={product.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <div className="text-center text-gray-400">
                            <div className="text-3xl mb-2">📄</div>
                            <div className="text-sm">{product.name}</div>
                          </div>
                        </div>
                      )}
                      
                      {/* Badges */}
                      <div className="absolute top-2 left-2 flex flex-col space-y-1">
                        {product.featured && (
                          <Tag color="gold" className="text-xs">Featured</Tag>
                        )}
                        {product.bestseller && (
                          <Tag color="red" className="text-xs">Bestseller</Tag>
                        )}
                        {product.design_tool_enabled && (
                          <Tag color="blue" className="text-xs">Design Tool</Tag>
                        )}
                      </div>
                    </div>
                  }
                  actions={[
                    <Link to={`/products/${product.category.slug}/${product.slug}`}>
                      <span className="inline-block w-full text-center px-3 py-1 bg-primary-600 text-white rounded text-sm">View Details</span>
                    </Link>,
                    ...(product.design_tool_enabled ? [
                      <Link to={`/design/editor/${product.slug}`}>
                        <span className="inline-block w-full text-center px-3 py-1 border rounded text-sm">Design Now</span>
                      </Link>
                    ] : [])
                  ]}
                >
                  <Meta
                    title={
                      <div className="space-y-1">
                        <h3 className="font-medium text-gray-900 line-clamp-2">
                          {product.name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {product.category.name}
                        </p>
                      </div>
                    }
                    description={
                      <div className="space-y-2">
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {product.short_description}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-lg font-semibold text-primary-600">
                            ₹{product.base_price}
                          </span>
                          <span className="text-xs text-gray-500">
                            Min: {product.min_quantity}
                          </span>
                        </div>
                      </div>
                    }
                  />
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {pagination.total > pagination.pageSize && (
              <div className="flex justify-center mt-8">
                <Pagination
                  current={pagination.current}
                  total={pagination.total}
                  pageSize={pagination.pageSize}
                  onChange={handlePageChange}
                  showSizeChanger={false}
                  showQuickJumper
                  showTotal={(total, range) =>
                    `${range[0]}-${range[1]} of ${total} products`
                  }
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ProductsPage;