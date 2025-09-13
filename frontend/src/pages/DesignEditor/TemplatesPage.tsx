// src/pages/DesignEditor/TemplatesPage.tsx
import React, { useState } from 'react';
import { Link, useParams } from 'react-router-dom';

interface Template {
  id: string;
  name: string;
  category: string;
  productType: string;
  previewImage: string;
  isPremium: boolean;
  isFeatured: boolean;
}

// Mock template data (will be replaced with API data later)
const mockTemplates: Template[] = [
  {
    id: '1',
    name: 'Modern Business Card',
    category: 'Business Cards',
    productType: 'business-cards',
    previewImage: 'https://via.placeholder.com/300x180/3981e6/ffffff?text=Modern+Business+Card',
    isPremium: false,
    isFeatured: true,
  },
  {
    id: '2',
    name: 'Creative Brochure',
    category: 'Brochures',
    productType: 'brochures',
    previewImage: 'https://via.placeholder.com/300x180/06b6d4/ffffff?text=Creative+Brochure',
    isPremium: true,
    isFeatured: true,
  },
  {
    id: '3',
    name: 'Event Flyer',
    category: 'Flyers',
    productType: 'flyers',
    previewImage: 'https://via.placeholder.com/300x180/10b981/ffffff?text=Event+Flyer',
    isPremium: false,
    isFeatured: false,
  },
  {
    id: '4',
    name: 'Professional Poster',
    category: 'Posters',
    productType: 'posters',
    previewImage: 'https://via.placeholder.com/300x180/f59e0b/ffffff?text=Professional+Poster',
    isPremium: true,
    isFeatured: false,
  },
  {
    id: '5',
    name: 'Marketing Banner',
    category: 'Banners',
    productType: 'banners',
    previewImage: 'https://via.placeholder.com/300x180/ef4444/ffffff?text=Marketing+Banner',
    isPremium: false,
    isFeatured: true,
  },
  {
    id: '6',
    name: 'Elegant Business Card',
    category: 'Business Cards',
    productType: 'business-cards',
    previewImage: 'https://via.placeholder.com/300x180/8b5cf6/ffffff?text=Elegant+Business+Card',
    isPremium: true,
    isFeatured: false,
  },
  {
    id: '7',
    name: 'Product Catalog',
    category: 'Marketing Materials',
    productType: 'marketing-materials',
    previewImage: 'https://via.placeholder.com/300x180/f59e0b/ffffff?text=Product+Catalog',
    isPremium: false,
    isFeatured: true,
  },
  {
    id: '8',
    name: 'Sales Brochure',
    category: 'Marketing Materials',
    productType: 'marketing-materials',
    previewImage: 'https://via.placeholder.com/300x180/06b6d4/ffffff?text=Sales+Brochure',
    isPremium: true,
    isFeatured: true,
  },
  {
    id: '9',
    name: 'Company Newsletter',
    category: 'Marketing Materials',
    productType: 'marketing-materials',
    previewImage: 'https://via.placeholder.com/300x180/10b981/ffffff?text=Newsletter',
    isPremium: false,
    isFeatured: false,
  },
];

const TemplatesPage: React.FC = () => {
  const { category } = useParams<{ category?: string }>();
  const [selectedCategory, setSelectedCategory] = useState<string>(
    category ? category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'All'
  );
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showPremiumOnly, setShowPremiumOnly] = useState<boolean>(false);

  // Get unique categories
  const categories = ['All', ...Array.from(new Set(mockTemplates.map(t => t.category)))];

  // Filter templates
  const filteredTemplates = mockTemplates.filter(template => {
    const matchesCategory = selectedCategory === 'All' || template.category === selectedCategory;
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPremium = !showPremiumOnly || template.isPremium;
    
    return matchesCategory && matchesSearch && matchesPremium;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Design Templates
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Choose from hundreds of professionally designed templates or start from scratch
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="flex-1 max-w-lg">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">Category:</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>

              {/* Premium Filter */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="premium-filter"
                  checked={showPremiumOnly}
                  onChange={(e) => setShowPremiumOnly(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="premium-filter" className="ml-2 text-sm text-gray-700">
                  Premium only
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Start Options */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          {['business-cards', 'brochures', 'flyers', 'posters', 'banners'].map(productType => (
            <Link
              key={productType}
              to={`/design/editor/${productType}`}
              className="bg-white border border-gray-200 rounded-lg p-4 text-center hover:border-primary-500 hover:shadow-md transition-all duration-200"
            >
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 capitalize">
                {productType.replace('-', ' ')}
              </h3>
              <p className="text-sm text-gray-500">Start from scratch</p>
            </Link>
          ))}
        </div>

        {/* Templates Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredTemplates.map(template => (
            <div key={template.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200">
              {/* Template Preview */}
              <div className="relative">
                <img
                  src={template.previewImage}
                  alt={template.name}
                  className="w-full h-48 object-cover"
                />
                
                {/* Badges */}
                <div className="absolute top-2 left-2 flex space-x-1">
                  {template.isFeatured && (
                    <span className="bg-yellow-500 text-white text-xs px-2 py-1 rounded">
                      Featured
                    </span>
                  )}
                  {template.isPremium && (
                    <span className="bg-purple-500 text-white text-xs px-2 py-1 rounded">
                      Premium
                    </span>
                  )}
                </div>

                {/* Overlay with actions */}
                <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-40 transition-all duration-200 flex items-center justify-center opacity-0 hover:opacity-100">
                  <Link
                    to={`/design/editor/${template.productType}?template=${template.id}`}
                    className="bg-white text-primary-600 px-4 py-2 rounded-md font-medium hover:bg-gray-100 transition-colors duration-200"
                  >
                    Use Template
                  </Link>
                </div>
              </div>

              {/* Template Info */}
              <div className="p-4">
                <h3 className="font-medium text-gray-900 mb-1">{template.name}</h3>
                <p className="text-sm text-gray-500">{template.category}</p>
              </div>
            </div>
          ))}
        </div>

        {/* No results */}
        {filteredTemplates.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No templates found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or browse different categories.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplatesPage;