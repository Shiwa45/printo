// src/pages/DesignEditor/EditorPage.tsx
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DesignEditor from '../../components/design-editor/DesignEditor';
import { useAuth } from '../../context/AuthContext';

const EditorPage: React.FC = () => {
  const { productSlug, category } = useParams<{ productSlug: string; category?: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Removed forced redirect to allow anonymous usage

  // Handle save design
  const handleSave = async (designData: any) => {
    try {
      if (!isAuthenticated) {
        const proceed = window.confirm('Please log in to save your design. Go to login now?');
        if (proceed) {
          navigate(`/login`);
        }
        return;
      }

      // TODO: Implement API call to save design
      console.log('Saving design data:', designData);
      
      // For now, just save to localStorage as demo
      const designId = Date.now().toString();
      const designRecord = {
        id: designId,
        productSlug,
        name: `Design for ${productSlug}`,
        designData,
        createdAt: new Date().toISOString(),
      };
      
      // Get existing designs
      const existingDesigns = JSON.parse(localStorage.getItem('userDesigns') || '[]');
      existingDesigns.push(designRecord);
      localStorage.setItem('userDesigns', JSON.stringify(existingDesigns));
      
      // Show success notification (you can integrate with a toast library later)
      alert('Design saved successfully!');
    } catch (error) {
      console.error('Save failed:', error);
      alert('Failed to save design. Please try again.');
    }
  };

  // Handle export design
  const handleExport = async (exportData: any) => {
    try {
      if (!isAuthenticated) {
        const proceed = window.confirm('Please log in to export your design. Go to login now?');
        if (proceed) {
          navigate(`/login`);
        }
        return;
      }

      // TODO: Implement API call to export design
      console.log('Exporting design:', exportData);
      
      // For now, just log the export
      alert('Design exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export design. Please try again.');
    }
  };

  // Get canvas dimensions based on product type
  const getCanvasDimensions = (productSlug: string) => {
    const dimensions: Record<string, { width: number; height: number }> = {
      'business-cards': { width: 1050, height: 600 }, // 3.5" x 2" at 300 DPI
      'brochures': { width: 2550, height: 3300 }, // 8.5" x 11" at 300 DPI
      'flyers': { width: 2550, height: 3300 }, // 8.5" x 11" at 300 DPI
      'posters': { width: 5100, height: 6600 }, // 17" x 22" at 300 DPI
      'banners': { width: 7200, height: 2400 }, // 24" x 8" at 300 DPI
    };
    
    return dimensions[productSlug || 'business-cards'] || dimensions['business-cards'];
  };

  const canvasDimensions = getCanvasDimensions(productSlug || '');

  return (
    <div className="h-screen overflow-hidden">
      <DesignEditor
        productType={productSlug}
        width={canvasDimensions.width}
        height={canvasDimensions.height}
        onSave={handleSave}
        onExport={handleExport}
      />
    </div>
  );
};

export default EditorPage;