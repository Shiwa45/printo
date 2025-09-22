/**
 * Enhanced Canvas Manager with Fixed GuideOverlayManager
 * Addresses initialization issues and provides robust error handling
 */

class EnhancedCanvasManager {
    constructor(config = {}) {
        this.config = {
            widthMM: 89,
            heightMM: 54,
            dpi: 300,
            bleedMM: 3.0,
            safeAreaMM: 5.0,
            canvasId: 'fabricCanvas',
            wrapperSelector: '.canvas-wrapper',
            ...config
        };

        this.canvas = null;
        this.guideOverlayManager = null;
        this.isInitialized = false;
        this.initPromise = null;

        // Bind methods to preserve context
        this.initialize = this.initialize.bind(this);
        this.createCanvasWrapper = this.createCanvasWrapper.bind(this);
    }

    /**
     * Initialize the canvas system with proper error handling
     */
    async initialize() {
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = this._doInitialize();
        return this.initPromise;
    }

    async _doInitialize() {
        try {
            // Ensure DOM is ready
            await this.waitForDOM();

            // Ensure Fabric.js is loaded
            await this.waitForFabric();

            // Ensure canvas element exists
            this.ensureCanvasElement();

            // Create canvas wrapper if it doesn't exist
            this.ensureCanvasWrapper();

            // Initialize Fabric.js canvas
            this.createFabricCanvas();

            // Initialize guide overlay manager
            this.initializeGuideOverlay();

            // Setup event handlers
            this.setupEventHandlers();

            this.isInitialized = true;
            console.log('Canvas system initialized successfully');

            // Dispatch initialization event
            this.dispatchEvent('canvasInitialized', {
                canvas: this.canvas,
                guideOverlayManager: this.guideOverlayManager
            });

            return this.canvas;

        } catch (error) {
            console.error('Canvas initialization failed:', error);
            this.dispatchEvent('canvasInitializationFailed', { error });
            throw error;
        }
    }

    /**
     * Wait for DOM to be ready
     */
    waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }

    /**
     * Wait for Fabric.js to be available
     */
    waitForFabric() {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50; // 5 seconds max wait

            const checkFabric = () => {
                if (typeof fabric !== 'undefined' && fabric.Canvas) {
                    resolve();
                    return;
                }

                attempts++;
                if (attempts >= maxAttempts) {
                    reject(new Error('Fabric.js not available after 5 seconds'));
                    return;
                }

                setTimeout(checkFabric, 100);
            };

            checkFabric();
        });
    }

    /**
     * Ensure canvas element exists
     */
    ensureCanvasElement() {
        let canvasElement = document.getElementById(this.config.canvasId);

        if (!canvasElement) {
            // Create canvas element
            canvasElement = document.createElement('canvas');
            canvasElement.id = this.config.canvasId;

            // Find a suitable parent or create one
            const wrapper = document.querySelector(this.config.wrapperSelector) ||
                          document.querySelector('#canvas-container') ||
                          document.body;

            wrapper.appendChild(canvasElement);
            console.log('Created missing canvas element');
        }

        return canvasElement;
    }

    /**
     * Ensure canvas wrapper exists
     */
    ensureCanvasWrapper() {
        let wrapper = document.querySelector(this.config.wrapperSelector);

        if (!wrapper) {
            wrapper = this.createCanvasWrapper();
            console.log('Created missing canvas wrapper');
        }

        return wrapper;
    }

    /**
     * Create canvas wrapper element
     */
    createCanvasWrapper() {
        const wrapper = document.createElement('div');
        wrapper.className = 'canvas-wrapper';
        wrapper.style.cssText = `
            position: relative;
            display: inline-block;
            border: 1px solid #ccc;
            background: #ffffff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        `;

        // Find canvas element and wrap it
        const canvasElement = document.getElementById(this.config.canvasId);
        if (canvasElement && canvasElement.parentNode) {
            canvasElement.parentNode.insertBefore(wrapper, canvasElement);
            wrapper.appendChild(canvasElement);
        } else {
            // Create container for wrapper
            const container = document.querySelector('#canvas-container') ||
                            document.querySelector('.designer-canvas') ||
                            document.body;
            container.appendChild(wrapper);
        }

        return wrapper;
    }

    /**
     * Create Fabric.js canvas
     */
    createFabricCanvas() {
        const widthPx = this.mmToPx(this.config.widthMM);
        const heightPx = this.mmToPx(this.config.heightMM);

        this.canvas = new fabric.Canvas(this.config.canvasId, {
            width: widthPx,
            height: heightPx,
            backgroundColor: '#ffffff',
            preserveObjectStacking: true,
            selection: true,
            allowTouchScrolling: false
        });

        console.log(`Canvas created: ${widthPx}x${heightPx}px (${this.config.widthMM}x${this.config.heightMM}mm)`);
    }

    /**
     * Initialize guide overlay manager with enhanced error handling
     */
    initializeGuideOverlay() {
        try {
            // Check if guide overlay already exists and remove it
            this.removeExistingGuideOverlays();

            this.guideOverlayManager = new EnhancedGuideOverlayManager(this.canvas, this.config);
            console.log('Guide overlay manager initialized');
        } catch (error) {
            console.error('Failed to initialize guide overlay manager:', error);
            // Continue without overlay - non-critical feature
        }
    }

    /**
     * Remove any existing guide overlays to prevent duplicates
     */
    removeExistingGuideOverlays() {
        try {
            // Remove any existing guide overlay canvases
            const existingOverlays = document.querySelectorAll('.guide-overlay, #guide-overlay');
            existingOverlays.forEach(overlay => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            });

            // Also check for and remove old GuideOverlayManager instances
            if (window.guideOverlayManager && window.guideOverlayManager.destroy) {
                window.guideOverlayManager.destroy();
            }

            console.log('Existing guide overlays removed');
        } catch (error) {
            console.warn('Error removing existing guide overlays:', error);
        }
    }

    /**
     * Setup canvas event handlers
     */
    setupEventHandlers() {
        if (!this.canvas) return;

        // Selection events
        this.canvas.on('selection:created', () => {
            this.dispatchEvent('selectionCreated');
        });

        this.canvas.on('selection:updated', () => {
            this.dispatchEvent('selectionUpdated');
        });

        this.canvas.on('selection:cleared', () => {
            this.dispatchEvent('selectionCleared');
        });

        // Object modification events
        this.canvas.on('object:modified', () => {
            this.dispatchEvent('objectModified');
            this.syncGuideOverlay();
        });

        this.canvas.on('object:added', () => {
            this.dispatchEvent('objectAdded');
        });

        this.canvas.on('object:removed', () => {
            this.dispatchEvent('objectRemoved');
        });

        // Canvas transformation events
        this.canvas.on('after:render', () => {
            this.syncGuideOverlay();
        });

        this.canvas.on('mouse:wheel', () => {
            this.syncGuideOverlay();
        });

        // Right-click context menu
        this.canvas.on('mouse:down', (options) => {
            if (options.e.button === 2) { // Right click
                this.handleRightClick(options);
            }
        });

        // Prevent default context menu
        if (this.canvas.upperCanvasEl) {
            this.canvas.upperCanvasEl.addEventListener('contextmenu', (e) => {
                e.preventDefault();
            });
        }
    }

    /**
     * Handle right-click events
     */
    handleRightClick(options) {
        const target = this.canvas.findTarget(options.e);
        if (target && !this.isGuideObject(target)) {
            this.canvas.setActiveObject(target);
            this.canvas.renderAll();
            this.dispatchEvent('contextMenu', { event: options.e, target });
        }
    }

    /**
     * Check if object is a guide object
     */
    isGuideObject(obj) {
        return obj.customType === 'grid' ||
               obj.customType === 'bleed' ||
               obj.customType === 'safezone';
    }

    /**
     * Sync guide overlay with main canvas
     */
    syncGuideOverlay() {
        if (this.guideOverlayManager) {
            requestAnimationFrame(() => {
                this.guideOverlayManager.syncWithMainCanvas();
            });
        }
    }

    /**
     * Convert millimeters to pixels
     */
    mmToPx(mm) {
        return (mm * this.config.dpi) / 25.4;
    }

    /**
     * Convert pixels to millimeters
     */
    pxToMm(px) {
        return (px * 25.4) / this.config.dpi;
    }

    /**
     * Dispatch custom events
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(`canvas:${eventName}`, {
            detail: {
                canvas: this.canvas,
                manager: this,
                ...detail
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get canvas instance
     */
    getCanvas() {
        return this.canvas;
    }

    /**
     * Check if canvas is initialized
     */
    isReady() {
        return this.isInitialized && this.canvas !== null;
    }

    /**
     * Destroy canvas and cleanup
     */
    destroy() {
        if (this.guideOverlayManager) {
            this.guideOverlayManager.destroy();
        }

        if (this.canvas) {
            this.canvas.dispose();
        }

        this.canvas = null;
        this.guideOverlayManager = null;
        this.isInitialized = false;
        this.initPromise = null;
    }
}

/**
 * Enhanced Guide Overlay Manager with better error handling
 */
class EnhancedGuideOverlayManager {
    constructor(mainCanvas, config = {}) {
        this.mainCanvas = mainCanvas;
        this.config = config;
        this.overlayCanvas = null;
        this.overlayContext = null;
        this.isVisible = true;
        this.bleedColor = '#ff0000';
        this.safeZoneColor = '#00ff00';

        this.createOverlay();
    }

    createOverlay() {
        try {
            // Create overlay canvas
            this.overlayCanvas = document.createElement('canvas');
            this.overlayCanvas.className = 'guide-overlay';
            this.overlayCanvas.id = 'guide-overlay';
            this.overlayCanvas.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                pointer-events: none;
                z-index: 10;
            `;

            // Find canvas wrapper
            const canvasWrapper = document.querySelector('.canvas-wrapper');
            if (!canvasWrapper) {
                throw new Error('Canvas wrapper not found');
            }

            // Add overlay to wrapper
            canvasWrapper.appendChild(this.overlayCanvas);
            this.overlayContext = this.overlayCanvas.getContext('2d');

            // Initial sync
            this.syncWithMainCanvas();

            console.log('Guide overlay created successfully');

        } catch (error) {
            console.error('Failed to create guide overlay:', error);
            throw error;
        }
    }

    syncWithMainCanvas() {
        if (!this.overlayCanvas || !this.overlayContext || !this.mainCanvas) {
            return;
        }

        try {
            // Match canvas dimensions
            const canvasEl = this.mainCanvas.getElement();
            this.overlayCanvas.width = canvasEl.width;
            this.overlayCanvas.height = canvasEl.height;
            this.overlayCanvas.style.width = canvasEl.style.width;
            this.overlayCanvas.style.height = canvasEl.style.height;

            // Clear and redraw
            this.clearOverlay();
            if (this.isVisible) {
                this.drawGuides();
            }

        } catch (error) {
            console.error('Error syncing overlay:', error);
        }
    }

    clearOverlay() {
        if (this.overlayContext && this.overlayCanvas) {
            this.overlayContext.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
        }
    }

    drawGuides() {
        this.drawBleedLines();
        this.drawSafeZoneLines();
    }

    drawBleedLines() {
        if (!this.overlayContext || !this.config.bleedMM) return;

        const bleedPx = this.mmToPx(this.config.bleedMM);
        const ctx = this.overlayContext;

        ctx.strokeStyle = this.bleedColor;
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);

        // Draw bleed rectangle
        ctx.strokeRect(
            -bleedPx,
            -bleedPx,
            this.overlayCanvas.width + (bleedPx * 2),
            this.overlayCanvas.height + (bleedPx * 2)
        );

        ctx.setLineDash([]);
    }

    drawSafeZoneLines() {
        if (!this.overlayContext || !this.config.safeAreaMM) return;

        const safeAreaPx = this.mmToPx(this.config.safeAreaMM);
        const ctx = this.overlayContext;

        ctx.strokeStyle = this.safeZoneColor;
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 3]);

        // Draw safe zone rectangle
        ctx.strokeRect(
            safeAreaPx,
            safeAreaPx,
            this.overlayCanvas.width - (safeAreaPx * 2),
            this.overlayCanvas.height - (safeAreaPx * 2)
        );

        ctx.setLineDash([]);
    }

    mmToPx(mm) {
        return (mm * this.config.dpi) / 25.4;
    }

    toggleVisibility() {
        this.isVisible = !this.isVisible;
        if (this.isVisible) {
            this.syncWithMainCanvas();
        } else {
            this.clearOverlay();
        }
    }

    setVisibility(visible) {
        this.isVisible = visible;
        if (this.isVisible) {
            this.syncWithMainCanvas();
        } else {
            this.clearOverlay();
        }
    }

    destroy() {
        if (this.overlayCanvas && this.overlayCanvas.parentNode) {
            this.overlayCanvas.parentNode.removeChild(this.overlayCanvas);
        }

        this.overlayCanvas = null;
        this.overlayContext = null;
        this.mainCanvas = null;
    }
}

// Global factory function for easy initialization
window.createEnhancedCanvas = function(config = {}) {
    const manager = new EnhancedCanvasManager(config);
    return manager.initialize();
};

// Export classes for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EnhancedCanvasManager,
        EnhancedGuideOverlayManager
    };
} else if (typeof window !== 'undefined') {
    window.EnhancedCanvasManager = EnhancedCanvasManager;
    window.EnhancedGuideOverlayManager = EnhancedGuideOverlayManager;
}