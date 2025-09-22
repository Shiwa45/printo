/**
 * Template Canvas Manager
 * Handles loading and applying templates to the canvas
 */

class TemplateCanvasManager {
    constructor(canvasManager, templateLoader) {
        this.canvasManager = canvasManager;
        this.templateLoader = templateLoader;
        this.currentTemplate = null;
        this.loadingTemplate = false;

        this.setupEventListeners();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for template loader events
        document.addEventListener('templateLoader:templateLoaded', (event) => {
            const { template } = event.detail;
            this.dispatchEvent('templateReady', { template });
        });

        document.addEventListener('templateLoader:templateLoadError', (event) => {
            const { error, templateId } = event.detail;
            this.dispatchEvent('templateLoadError', { error, templateId });
        });
    }

    /**
     * Load and apply template to canvas
     */
    async loadTemplateToCanvas(templateId, side = 'single') {
        if (this.loadingTemplate) {
            console.warn('Template loading already in progress');
            return;
        }

        this.loadingTemplate = true;
        this.dispatchEvent('templateLoadStarted', { templateId, side });

        try {
            // Show loading state
            this.showLoadingState();

            // Load template data
            const template = await this.templateLoader.loadTemplate(templateId);

            if (!template.isValid) {
                throw new Error('Template is not valid for loading');
            }

            // Apply template to canvas
            await this.applyTemplateToCanvas(template, side);

            this.currentTemplate = template;
            this.dispatchEvent('templateLoaded', { template, side });

        } catch (error) {
            console.error('Failed to load template to canvas:', error);
            this.showErrorState(error);
            this.dispatchEvent('templateLoadFailed', { error, templateId, side });
        } finally {
            this.loadingTemplate = false;
            this.hideLoadingState();
        }
    }

    /**
     * Apply template data to canvas
     */
    async applyTemplateToCanvas(template, side = 'single') {
        const canvas = this.canvasManager.getCanvas();
        if (!canvas) {
            throw new Error('Canvas not available');
        }

        try {
            // Clear existing objects (except guides)
            this.clearCanvasObjects(canvas);

            // Set canvas dimensions if needed
            this.updateCanvasDimensions(canvas, template);

            // Load template objects
            await this.loadTemplateObjects(canvas, template.template_data);

            // Apply background if specified
            if (template.template_data.background) {
                canvas.setBackgroundColor(template.template_data.background);
            }

            // Re-render canvas
            canvas.renderAll();

            console.log('Template applied successfully:', template.name);

        } catch (error) {
            console.error('Failed to apply template to canvas:', error);
            throw error;
        }
    }

    /**
     * Clear canvas objects (except visual guides)
     */
    clearCanvasObjects(canvas) {
        const objects = canvas.getObjects().slice(); // Create copy to avoid modification during iteration

        objects.forEach(obj => {
            // Keep visual guides and grid
            if (!this.isSystemObject(obj)) {
                canvas.remove(obj);
            }
        });
    }

    /**
     * Check if object is a system object (guides, grid, etc.)
     */
    isSystemObject(obj) {
        return obj.customType === 'grid' ||
               obj.customType === 'bleed' ||
               obj.customType === 'safezone' ||
               obj.customType === 'guide' ||
               (obj.name && obj.name.includes('visual-guide'));
    }

    /**
     * Update canvas dimensions based on template
     */
    updateCanvasDimensions(canvas, template) {
        const templateData = template.template_data;

        if (templateData.width && templateData.height) {
            const currentWidth = canvas.getWidth();
            const currentHeight = canvas.getHeight();

            // Only update if dimensions are significantly different
            if (Math.abs(currentWidth - templateData.width) > 10 ||
                Math.abs(currentHeight - templateData.height) > 10) {

                console.log(`Updating canvas dimensions: ${templateData.width}x${templateData.height}`);
                canvas.setDimensions({
                    width: templateData.width,
                    height: templateData.height
                });
            }
        }
    }

    /**
     * Load template objects into canvas
     */
    async loadTemplateObjects(canvas, templateData) {
        if (!templateData.objects || !Array.isArray(templateData.objects)) {
            console.log('No objects in template data');
            return;
        }

        console.log(`Loading ${templateData.objects.length} template objects`);

        for (const objData of templateData.objects) {
            try {
                const fabricObj = await this.createFabricObject(objData);
                if (fabricObj) {
                    canvas.add(fabricObj);
                }
            } catch (error) {
                console.warn('Failed to create object from template data:', objData, error);
            }
        }
    }

    /**
     * Create Fabric.js object from template data
     */
    async createFabricObject(objData) {
        if (!objData || !objData.type) {
            return null;
        }

        switch (objData.type) {
            case 'text':
                return this.createTextObject(objData);

            case 'rect':
                return this.createRectObject(objData);

            case 'circle':
                return this.createCircleObject(objData);

            case 'image':
                return await this.createImageObject(objData);

            case 'path':
                return this.createPathObject(objData);

            case 'group':
                return await this.createGroupObject(objData);

            default:
                console.warn('Unknown object type:', objData.type);
                return null;
        }
    }

    /**
     * Create text object
     */
    createTextObject(objData) {
        return new fabric.Text(objData.text || 'Sample Text', {
            left: objData.left || 0,
            top: objData.top || 0,
            fontFamily: objData.fontFamily || 'Arial',
            fontSize: objData.fontSize || 16,
            fill: objData.fill || '#000000',
            fontWeight: objData.fontWeight || 'normal',
            fontStyle: objData.fontStyle || 'normal',
            textAlign: objData.textAlign || 'left',
            angle: objData.angle || 0,
            scaleX: objData.scaleX || 1,
            scaleY: objData.scaleY || 1,
            opacity: objData.opacity || 1,
            selectable: true,
            moveable: true
        });
    }

    /**
     * Create rectangle object
     */
    createRectObject(objData) {
        return new fabric.Rect({
            left: objData.left || 0,
            top: objData.top || 0,
            width: objData.width || 100,
            height: objData.height || 100,
            fill: objData.fill || '#000000',
            stroke: objData.stroke || null,
            strokeWidth: objData.strokeWidth || 0,
            angle: objData.angle || 0,
            scaleX: objData.scaleX || 1,
            scaleY: objData.scaleY || 1,
            opacity: objData.opacity || 1,
            rx: objData.rx || 0,
            ry: objData.ry || 0,
            selectable: true,
            moveable: true
        });
    }

    /**
     * Create circle object
     */
    createCircleObject(objData) {
        return new fabric.Circle({
            left: objData.left || 0,
            top: objData.top || 0,
            radius: objData.radius || 50,
            fill: objData.fill || '#000000',
            stroke: objData.stroke || null,
            strokeWidth: objData.strokeWidth || 0,
            angle: objData.angle || 0,
            scaleX: objData.scaleX || 1,
            scaleY: objData.scaleY || 1,
            opacity: objData.opacity || 1,
            selectable: true,
            moveable: true
        });
    }

    /**
     * Create image object
     */
    async createImageObject(objData) {
        return new Promise((resolve, reject) => {
            if (!objData.src) {
                reject(new Error('Image source not provided'));
                return;
            }

            fabric.Image.fromURL(objData.src, (img) => {
                if (!img) {
                    reject(new Error('Failed to load image'));
                    return;
                }

                img.set({
                    left: objData.left || 0,
                    top: objData.top || 0,
                    angle: objData.angle || 0,
                    scaleX: objData.scaleX || 1,
                    scaleY: objData.scaleY || 1,
                    opacity: objData.opacity || 1,
                    selectable: true,
                    moveable: true
                });

                // Apply size if specified
                if (objData.width && objData.height) {
                    img.scaleToWidth(objData.width);
                    img.scaleToHeight(objData.height);
                }

                resolve(img);
            }, {
                crossOrigin: 'anonymous'
            });
        });
    }

    /**
     * Create path object
     */
    createPathObject(objData) {
        if (!objData.path) {
            return null;
        }

        return new fabric.Path(objData.path, {
            left: objData.left || 0,
            top: objData.top || 0,
            fill: objData.fill || '#000000',
            stroke: objData.stroke || null,
            strokeWidth: objData.strokeWidth || 0,
            angle: objData.angle || 0,
            scaleX: objData.scaleX || 1,
            scaleY: objData.scaleY || 1,
            opacity: objData.opacity || 1,
            selectable: true,
            moveable: true
        });
    }

    /**
     * Create group object
     */
    async createGroupObject(objData) {
        if (!objData.objects || !Array.isArray(objData.objects)) {
            return null;
        }

        const objects = [];

        for (const childData of objData.objects) {
            const childObj = await this.createFabricObject(childData);
            if (childObj) {
                objects.push(childObj);
            }
        }

        if (objects.length === 0) {
            return null;
        }

        return new fabric.Group(objects, {
            left: objData.left || 0,
            top: objData.top || 0,
            angle: objData.angle || 0,
            scaleX: objData.scaleX || 1,
            scaleY: objData.scaleY || 1,
            opacity: objData.opacity || 1,
            selectable: true,
            moveable: true
        });
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const loadingElement = document.getElementById('template-loading');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }

        // Show loading overlay on canvas if available
        this.showCanvasLoading();
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loadingElement = document.getElementById('template-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }

        this.hideCanvasLoading();
    }

    /**
     * Show canvas loading overlay
     */
    showCanvasLoading() {
        let overlay = document.getElementById('canvas-loading-overlay');

        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'canvas-loading-overlay';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                font-size: 16px;
                color: #333;
            `;
            overlay.innerHTML = `
                <div style="text-align: center;">
                    <div style="margin-bottom: 10px;">
                        <i class="fas fa-spinner fa-spin fa-2x"></i>
                    </div>
                    <div>Loading template...</div>
                </div>
            `;

            const canvasWrapper = document.querySelector('.canvas-wrapper');
            if (canvasWrapper) {
                canvasWrapper.appendChild(overlay);
            }
        }

        overlay.style.display = 'flex';
    }

    /**
     * Hide canvas loading overlay
     */
    hideCanvasLoading() {
        const overlay = document.getElementById('canvas-loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    /**
     * Show error state
     */
    showErrorState(error) {
        console.error('Template loading error:', error);

        // Show user-friendly error message
        const errorMessage = this.getUserFriendlyErrorMessage(error);
        this.showNotification(errorMessage, 'error');
    }

    /**
     * Get user-friendly error message
     */
    getUserFriendlyErrorMessage(error) {
        if (error.message.includes('network') || error.message.includes('fetch')) {
            return 'Failed to load template due to network error. Please check your connection and try again.';
        }

        if (error.message.includes('not found') || error.message.includes('404')) {
            return 'Template not found. It may have been removed or moved.';
        }

        if (error.message.includes('Canvas not available')) {
            return 'Design canvas is not ready. Please wait a moment and try again.';
        }

        return 'Failed to load template. Please try again or contact support if the problem persists.';
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Try to use existing notification system
        if (typeof showNotification === 'function') {
            showNotification(message, type);
            return;
        }

        // Fallback to simple alert or console
        if (type === 'error') {
            alert(`Error: ${message}`);
        } else {
            console.log(`Notification: ${message}`);
        }
    }

    /**
     * Get current template
     */
    getCurrentTemplate() {
        return this.currentTemplate;
    }

    /**
     * Check if template is loading
     */
    isLoadingTemplate() {
        return this.loadingTemplate;
    }

    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(`templateCanvas:${eventName}`, { detail });
        document.dispatchEvent(event);
    }

    /**
     * Destroy and cleanup
     */
    destroy() {
        this.currentTemplate = null;
        this.loadingTemplate = false;
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TemplateCanvasManager;
} else if (typeof window !== 'undefined') {
    window.TemplateCanvasManager = TemplateCanvasManager;
}