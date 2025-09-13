// src/pages/DesignEditor/MyDesignsPage.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

interface SavedDesign {
  id: string;
  productSlug: string;
  name: string;
  designData: any;
  createdAt: string;
  previewImage?: string;
}

const MyDesignsPage: React.FC = () => {
  const [designs, setDesigns] = useState<SavedDesign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    loadDesigns();
  }, []);

  const loadDesigns = async () => {
    setIsLoading(true);
    try {
      // For now, load from localStorage (will be replaced with API call)
      const savedDesigns = JSON.parse(localStorage.getItem('userDesigns') || '[]');
      setDesigns(savedDesigns);
    } catch (error) {
      console.error('Failed to load designs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteDesign = async (designId: string) => {
    if (!window.confirm('Are you sure you want to delete this design?')) {
      return;
    }

    try {
      // Remove from localStorage (will be replaced with API call)
      const existingDesigns = JSON.parse(localStorage.getItem('userDesigns') || '[]');
      const updatedDesigns = existingDesigns.filter((d: SavedDesign) => d.id !== designId);
      localStorage.setItem('userDesigns', JSON.stringify(updatedDesigns));
      
      // Update state
      setDesigns(updatedDesigns);
      
      alert('Design deleted successfully!');
    } catch (error) {
      console.error('Failed to delete design:', error);
      alert('Failed to delete design. Please try again.');
    }
  };

  const duplicateDesign = async (design: SavedDesign) => {
    try {
      const newDesign = {
        ...design,
        id: Date.now().toString(),
        name: `${design.name} (Copy)`,
        createdAt: new Date().toISOString(),
      };

      // Save to localStorage (will be replaced with API call)
      const existingDesigns = JSON.parse(localStorage.getItem('userDesigns') || '[]');
      existingDesigns.push(newDesign);
      localStorage.setItem('userDesigns', JSON.stringify(existingDesigns));
      
      // Update state
      setDesigns(existingDesigns);
      
      alert('Design duplicated successfully!');
    } catch (error) {
      console.error('Failed to duplicate design:', error);
      alert('Failed to duplicate design. Please try again.');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Authentication Required
          </h2>
          <p className="text-gray-600 mb-4">
            Please log in to view your designs.
          </p>
          <Link to="/login" className="btn-primary">
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Designs</h1>
              <p className="text-gray-600 mt-2">
                Manage and edit your saved designs
              </p>
            </div>
            
            <Link
              to="/design/templates"
              className="btn-primary"
            >
              Create New Design
            </Link>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading your designs...</p>
          </div>
        ) : designs.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No designs yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first design.
            </p>
            <div className="mt-6">
              <Link
                to="/design/templates"
                className="btn-primary"
              >
                Create Your First Design
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {designs.map(design => (
              <div key={design.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200">
                {/* Design Preview */}
                <div className="relative h-48 bg-gray-100 flex items-center justify-center">
                  {design.previewImage ? (
                    <img
                      src={design.previewImage}
                      alt={design.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <p className="mt-2 text-sm text-gray-500 capitalize">
                        {design.productSlug?.replace('-', ' ')} Design
                      </p>
                    </div>
                  )}
                  
                  {/* Overlay with actions */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-40 transition-all duration-200 flex items-center justify-center opacity-0 hover:opacity-100">
                    <div className="flex space-x-2">
                      <Link
                        to={`/design/editor/${design.productSlug}?design=${design.id}`}
                        className="bg-white text-primary-600 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors duration-200"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => duplicateDesign(design)}
                        className="bg-white text-green-600 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors duration-200"
                      >
                        Duplicate
                      </button>
                    </div>
                  </div>
                </div>

                {/* Design Info */}
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-1 truncate">
                        {design.name}
                      </h3>
                      <p className="text-sm text-gray-500 capitalize mb-2">
                        {design.productSlug?.replace('-', ' ')}
                      </p>
                      <p className="text-xs text-gray-400">
                        Created {new Date(design.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    
                    {/* More Actions Menu */}
                    <div className="relative">
                      <button
                        onClick={() => deleteDesign(design.id)}
                        className="text-gray-400 hover:text-red-600 transition-colors duration-200"
                        title="Delete design"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyDesignsPage;