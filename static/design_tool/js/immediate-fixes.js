/**
 * Immediate Fixes for Canvas and Template Issues
 * Ensures only one canvas system runs and templates load properly
 */

(function() {
    'use strict';

    console.log('Applying immediate fixes...');

    // Fix 1: Prevent duplicate canvas initialization
    function preventDuplicateCanvas() {
        // Disable the original DOMContentLoaded handler if it exists
        if (typeof window.initializeCanvas === 'function') {
            console.log('Disabling original canvas initialization');
            const originalInit = window.initializeCanvas;
            window.initializeCanvas = function() {
                console.log('Original canvas initialization blocked');
                return;
            };
        }

        // Clear any existing guide overlays immediately
        const existingGuides = document.querySelectorAll('.guide-overlay, #guide-overlay');
        existingGuides.forEach(guide => {
            if (guide.parentNode) {
                guide.parentNode.removeChild(guide);
                console.log('Removed existing guide overlay');
            }
        });

        // Clear any existing visual guides layers
        if (window.canvas && window.canvas.find) {
            try {
                const guideLayers = window.canvas.find('.visual-guides-layer');
                guideLayers.forEach(layer => {
                    if (layer.destroy) layer.destroy();
                });
            } catch (error) {
                console.warn('Error clearing visual guide layers:', error);
            }
        }
    }

    // Fix 2: Proper template loading function
    function fixTemplateLoading() {
        // Override any existing template loading functions
        window.loadTemplates = async function(filters = {}) {
            try {
                console.log('Loading templates with filters:', filters);

                const url = new URL('/api/design/templates/', window.location.origin);
                Object.entries(filters).forEach(([key, value]) => {
                    if (value !== null && value !== undefined && value !== '') {
                        url.searchParams.append(key, value);
                    }
                });

                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                console.log('Templates loaded successfully:', data.results?.length || 0);

                return data;
            } catch (error) {
                console.error('Template loading failed:', error);
                throw error;
            }
        };

        // Create a working template application function
        window.applyTemplate = async function(templateId) {
            try {
                console.log('Applying template:', templateId);

                // Get canvas
                const canvas = window.canvas || (window.canvasManager && window.canvasManager.getCanvas());
                if (!canvas) {
                    throw new Error('Canvas not available');
                }

                // Load template data
                const response = await fetch(`/api/design/templates/${templateId}/`);
                if (!response.ok) {
                    throw new Error(`Failed to load template: ${response.statusText}`);
                }

                const template = await response.json();
                console.log('Template data loaded:', template.name);

                // Clear canvas (except guides)
                const objects = canvas.getObjects().slice();
                objects.forEach(obj => {
                    if (!obj.customType || !obj.customType.includes('guide')) {
                        canvas.remove(obj);
                    }
                });

                // Apply template data
                if (template.template_data && template.template_data.objects) {
                    for (const objData of template.template_data.objects) {
                        try {
                            const fabricObj = await createFabricObjectFromData(objData);
                            if (fabricObj) {
                                canvas.add(fabricObj);
                            }
                        } catch (error) {
                            console.warn('Failed to create object:', objData, error);
                        }
                    }
                }

                // Set background
                if (template.template_data && template.template_data.background) {
                    canvas.setBackgroundColor(template.template_data.background);
                }

                canvas.renderAll();
                console.log('Template applied successfully');

                // Show success message
                showNotification('Template loaded successfully!', 'success');

                return true;

            } catch (error) {
                console.error('Template application failed:', error);
                showNotification('Failed to load template: ' + error.message, 'error');
                throw error;
            }
        };
    }

    // Fix 3: Create Fabric objects from template data
    async function createFabricObjectFromData(objData) {
        if (!objData || !objData.type) return null;

        switch (objData.type) {
            case 'text':
                return new fabric.Text(objData.text || 'Sample Text', {
                    left: objData.left || 0,
                    top: objData.top || 0,
                    fontFamily: objData.fontFamily || 'Arial',
                    fontSize: objData.fontSize || 16,
                    fill: objData.fill || '#000000',
                    selectable: true
                });

            case 'rect':
                return new fabric.Rect({
                    left: objData.left || 0,
                    top: objData.top || 0,
                    width: objData.width || 100,
                    height: objData.height || 100,
                    fill: objData.fill || '#000000',
                    selectable: true
                });

            case 'circle':
                return new fabric.Circle({
                    left: objData.left || 0,
                    top: objData.top || 0,
                    radius: objData.radius || 50,
                    fill: objData.fill || '#000000',
                    selectable: true
                });

            case 'image':
                if (objData.src) {
                    return new Promise((resolve) => {
                        fabric.Image.fromURL(objData.src, (img) => {
                            if (img) {
                                img.set({
                                    left: objData.left || 0,
                                    top: objData.top || 0,
                                    selectable: true
                                });
                            }
                            resolve(img);
                        });
                    });
                }
                break;

            default:
                console.warn('Unknown object type:', objData.type);
                return null;
        }
    }

    // Fix 4: Simple notification function
    function showNotification(message, type = 'info') {
        // Try existing notification system first
        if (window.utils && window.utils.notify) {
            window.utils.notify[type](message);
            return;
        }

        // Fallback notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-family: Arial, sans-serif;
            font-size: 14px;
            z-index: 10000;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;

        // Set color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    // Fix 5: Ensure safe function calls
    function fixSafeCalls() {
        if (!window.safeCall) {
            window.safeCall = function(fn, context, ...args) {
                try {
                    if (typeof fn === 'function') {
                        return fn.apply(context, args);
                    } else if (typeof fn === 'string' && window[fn]) {
                        return window[fn].apply(context, args);
                    } else {
                        console.warn('safeCall: function not found:', fn);
                        return null;
                    }
                } catch (error) {
                    console.error('safeCall error:', error);
                    return null;
                }
            };
        }
    }

    // Apply all fixes immediately
    preventDuplicateCanvas();
    fixTemplateLoading();
    fixSafeCalls();
    window.showNotification = showNotification;
    window.createFabricObjectFromData = createFabricObjectFromData;

    console.log('Immediate fixes applied successfully');

    // Ensure canvas is properly initialized
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded, checking canvas...');

        // Wait a bit then ensure proper canvas initialization
        setTimeout(() => {
            if (!window.canvas || !window.canvasManager) {
                console.log('Initializing canvas...');
                if (window.initializeCanvasSafely) {
                    window.initializeCanvasSafely();
                } else if (window.createEnhancedCanvas) {
                    window.createEnhancedCanvas();
                }
            }

            // Force template gallery initialization
            if (window.initializeTemplateGallery) {
                window.initializeTemplateGallery();
            }
        }, 1000);
    });

})();