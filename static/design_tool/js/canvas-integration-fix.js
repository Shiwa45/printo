/**
 * Canvas Integration Fix
 * Replaces problematic canvas initialization with enhanced version
 */

// Safe canvas initialization function
function initializeCanvasSafely(config = {}) {
    // Default configuration
    const defaultConfig = {
        widthMM: 89,
        heightMM: 54,
        dpi: 300,
        bleedMM: 3.0,
        safeAreaMM: 5.0,
        canvasId: 'fabricCanvas',
        wrapperSelector: '.canvas-wrapper'
    };

    const finalConfig = { ...defaultConfig, ...config };

    // Create enhanced canvas manager
    const canvasManager = new EnhancedCanvasManager(finalConfig);

    // Initialize and handle results
    return canvasManager.initialize()
        .then(canvas => {
            console.log('Canvas initialized successfully');

            // Set global variables for backward compatibility
            if (typeof window !== 'undefined') {
                window.canvas = canvas;
                window.canvasManager = canvasManager;
                window.guideOverlayManager = canvasManager.guideOverlayManager;
            }

            // Add grid if the function exists
            if (typeof addGrid === 'function') {
                try {
                    addGrid();
                } catch (error) {
                    console.warn('Failed to add grid:', error);
                }
            }

            // Save initial history if function exists
            if (typeof saveHistory === 'function') {
                try {
                    saveHistory();
                } catch (error) {
                    console.warn('Failed to save initial history:', error);
                }
            }

            // Update color palette if function exists
            if (typeof updateDesignColorPalette === 'function') {
                try {
                    updateDesignColorPalette();
                } catch (error) {
                    console.warn('Failed to update color palette:', error);
                }
            }

            // Load popular cliparts with delay if function exists
            if (typeof loadPopularCliparts === 'function') {
                setTimeout(() => {
                    try {
                        loadPopularCliparts();
                    } catch (error) {
                        console.warn('Failed to load popular cliparts:', error);
                    }
                }, 1000);
            }

            return canvas;
        })
        .catch(error => {
            console.error('Canvas initialization failed:', error);

            // Show user-friendly error message
            showCanvasError(error);

            throw error;
        });
}

// Enhanced event handlers with better error handling
function setupEnhancedEventHandlers() {
    // Listen for canvas events
    document.addEventListener('canvas:selectionCreated', () => {
        safeCall('updateContextToolbar');
        safeCall('updateLayersList');
    });

    document.addEventListener('canvas:selectionUpdated', () => {
        safeCall('updateContextToolbar');
        safeCall('updateLayersList');
    });

    document.addEventListener('canvas:selectionCleared', () => {
        safeCall('hideContextToolbar');
        safeCall('updateLayersList');
    });

    document.addEventListener('canvas:objectModified', () => {
        safeCall('saveHistory');
        safeCall('updateLayersList');
        safeCall('updateDesignColorPalette');
    });

    document.addEventListener('canvas:objectAdded', () => {
        safeCall('saveHistory');
        safeCall('updateLayersList');
        safeCall('updateDesignColorPalette');
    });

    document.addEventListener('canvas:objectRemoved', () => {
        safeCall('saveHistory');
        safeCall('updateLayersList');
        safeCall('updateDesignColorPalette');
    });

    document.addEventListener('canvas:contextMenu', (event) => {
        const { event: mouseEvent, target } = event.detail;
        safeCall('showContextMenu', mouseEvent, target);
    });
}

// Utility function to safely call functions
function safeCall(functionName, ...args) {
    try {
        if (typeof window[functionName] === 'function') {
            return window[functionName](...args);
        } else {
            console.warn(`Function ${functionName} not found`);
        }
    } catch (error) {
        console.warn(`Error calling ${functionName}:`, error);
    }
}

// Show canvas error to user
function showCanvasError(error) {
    const errorContainer = document.getElementById('canvas-error') || createErrorContainer();

    errorContainer.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <h4><i class="fas fa-exclamation-triangle"></i> Canvas Initialization Failed</h4>
            <p>There was a problem initializing the design canvas. This could be due to:</p>
            <ul>
                <li>Browser compatibility issues</li>
                <li>Slow internet connection</li>
                <li>JavaScript conflicts</li>
            </ul>
            <p><strong>What you can do:</strong></p>
            <ul>
                <li>Refresh the page (F5)</li>
                <li>Try a different browser (Chrome, Firefox, Safari)</li>
                <li>Clear your browser cache</li>
                <li>Disable browser extensions temporarily</li>
            </ul>
            <button class="btn btn-primary" onclick="location.reload()">
                <i class="fas fa-refresh"></i> Refresh Page
            </button>
            <details style="margin-top: 10px;">
                <summary>Technical Details</summary>
                <pre style="font-size: 12px; margin-top: 5px;">${error.message}</pre>
            </details>
        </div>
    `;

    errorContainer.style.display = 'block';
}

// Create error container if it doesn't exist
function createErrorContainer() {
    const container = document.createElement('div');
    container.id = 'canvas-error';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        max-width: 600px;
        display: none;
    `;

    document.body.appendChild(container);
    return container;
}

// Enhanced DOMContentLoaded handler
function initializeDesignTool() {
    console.log('Initializing design tool with enhanced canvas manager...');

    // Setup enhanced event handlers first
    setupEnhancedEventHandlers();

    // Initialize canvas with error handling
    initializeCanvasSafely()
        .then(canvas => {
            console.log('Design tool initialized successfully');

            // Call other initialization functions safely
            safeCall('setupEventHandlers');
            safeCall('drawRulers');
            safeCall('updateContextToolbar');
            safeCall('loadProducts');
            safeCall('loadCategories');
            safeCall('loadTemplates');
            safeCall('checkURLParams');

            // Hide any existing error messages
            const errorContainer = document.getElementById('canvas-error');
            if (errorContainer) {
                errorContainer.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Design tool initialization failed:', error);
        });
}

// Replace the original DOMContentLoaded handler
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDesignTool);
} else {
    // DOM is already loaded
    initializeDesignTool();
}

// Export for external use
if (typeof window !== 'undefined') {
    window.initializeCanvasSafely = initializeCanvasSafely;
    window.initializeDesignTool = initializeDesignTool;
}