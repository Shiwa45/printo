/**
 * Enhanced UI Components Manager
 * Handles all UI interactions with proper error handling and state management
 */

class EnhancedUIManager {
    constructor(config = {}) {
        this.config = {
            enableAnimations: true,
            debounceDelay: 300,
            tooltipDelay: 1000,
            ...config
        };

        this.components = new Map();
        this.eventListeners = new Map();
        this.activeModals = new Set();
        this.isInitialized = false;

        this.initialize();
    }

    /**
     * Initialize UI manager
     */
    initialize() {
        if (this.isInitialized) return;

        try {
            this.initializeComponents();
            this.setupGlobalEventHandlers();
            this.setupKeyboardShortcuts();
            this.setupTooltips();
            this.setupModals();
            this.setupContextMenus();

            this.isInitialized = true;
            console.log('Enhanced UI Manager initialized');

        } catch (error) {
            console.error('Failed to initialize UI Manager:', error);
        }
    }

    /**
     * Initialize UI components
     */
    initializeComponents() {
        // Toolbar components
        this.initializeToolbar();

        // Panel components
        this.initializePanels();

        // Property panels
        this.initializePropertyPanels();

        // Layer management
        this.initializeLayerPanel();

        // Template gallery
        this.initializeTemplateGallery();

        // Image search
        this.initializeImageSearch();

        // Context toolbar
        this.initializeContextToolbar();
    }

    /**
     * Initialize toolbar
     */
    initializeToolbar() {
        const toolbar = utils.dom.querySelector('.tools-sidebar');
        if (!toolbar) return;

        const toolItems = utils.dom.querySelectorAll('.tool-item');

        toolItems.forEach(item => {
            utils.dom.addEventListener(item, 'click', (e) => {
                this.handleToolSelection(item, e);
            });

            utils.dom.addEventListener(item, 'mouseenter', (e) => {
                this.showTooltip(item, item.dataset.tooltip || item.title);
            });

            utils.dom.addEventListener(item, 'mouseleave', (e) => {
                this.hideTooltip();
            });
        });

        this.components.set('toolbar', {
            element: toolbar,
            items: toolItems,
            activeItem: null
        });
    }

    /**
     * Handle tool selection
     */
    handleToolSelection(toolItem, event) {
        try {
            // Remove active state from all tools
            const allTools = utils.dom.querySelectorAll('.tool-item');
            allTools.forEach(tool => tool.classList.remove('active'));

            // Add active state to selected tool
            toolItem.classList.add('active');

            // Get tool type
            const toolType = toolItem.dataset.tool || toolItem.id;

            // Handle different tool types
            this.activateTool(toolType);

            // Update toolbar state
            const toolbar = this.components.get('toolbar');
            if (toolbar) {
                toolbar.activeItem = toolItem;
            }

            // Dispatch tool change event
            this.dispatchEvent('toolChanged', {
                toolType,
                toolElement: toolItem
            });

        } catch (error) {
            console.error('Tool selection failed:', error);
            utils.notify.error('Failed to select tool');
        }
    }

    /**
     * Activate specific tool
     */
    activateTool(toolType) {
        const canvas = utils.canvas.getCanvas();
        if (!canvas) return;

        try {
            // Clear any existing selection
            utils.canvas.clearSelection();

            // Set cursor and interaction mode based on tool
            switch (toolType) {
                case 'select':
                    canvas.isDrawingMode = false;
                    canvas.selection = true;
                    canvas.defaultCursor = 'default';
                    break;

                case 'text':
                    canvas.isDrawingMode = false;
                    canvas.selection = false;
                    canvas.defaultCursor = 'text';
                    this.enableTextTool();
                    break;

                case 'shape':
                    canvas.isDrawingMode = false;
                    canvas.selection = false;
                    canvas.defaultCursor = 'crosshair';
                    this.enableShapeTool();
                    break;

                case 'draw':
                    canvas.isDrawingMode = true;
                    canvas.selection = false;
                    canvas.freeDrawingBrush.width = 2;
                    canvas.freeDrawingBrush.color = '#000000';
                    break;

                case 'image':
                    canvas.isDrawingMode = false;
                    canvas.selection = false;
                    this.openImagePanel();
                    break;

                default:
                    console.warn('Unknown tool type:', toolType);
            }

        } catch (error) {
            console.error('Failed to activate tool:', error);
        }
    }

    /**
     * Initialize panels
     */
    initializePanels() {
        const panels = utils.dom.querySelectorAll('.panel, .sidebar-panel');

        panels.forEach(panel => {
            // Make panels collapsible
            this.makePanelCollapsible(panel);

            // Handle panel resize
            this.makePanelResizable(panel);
        });
    }

    /**
     * Make panel collapsible
     */
    makePanelCollapsible(panel) {
        const header = utils.dom.querySelector('.panel-header', panel) ||
                      utils.dom.querySelector('.sidebar-header', panel);

        if (!header) return;

        // Add collapse button if not exists
        let collapseBtn = header.querySelector('.collapse-btn');
        if (!collapseBtn) {
            collapseBtn = utils.dom.createElement('button', {
                className: 'collapse-btn',
                innerHTML: '<i class="fas fa-chevron-up"></i>',
                title: 'Collapse panel'
            });
            header.appendChild(collapseBtn);
        }

        utils.dom.addEventListener(collapseBtn, 'click', (e) => {
            e.stopPropagation();
            this.togglePanel(panel);
        });
    }

    /**
     * Toggle panel collapse state
     */
    togglePanel(panel) {
        try {
            const isCollapsed = panel.classList.contains('collapsed');
            const content = panel.querySelector('.panel-content') ||
                           panel.querySelector('.sidebar-content');

            if (isCollapsed) {
                panel.classList.remove('collapsed');
                if (content) content.style.display = 'block';
            } else {
                panel.classList.add('collapsed');
                if (content) content.style.display = 'none';
            }

            // Update collapse button
            const collapseBtn = panel.querySelector('.collapse-btn i');
            if (collapseBtn) {
                collapseBtn.className = isCollapsed ?
                    'fas fa-chevron-up' : 'fas fa-chevron-down';
            }

        } catch (error) {
            console.error('Failed to toggle panel:', error);
        }
    }

    /**
     * Initialize property panels
     */
    initializePropertyPanels() {
        const propertyPanel = utils.dom.querySelector('#propertyPanel');
        if (!propertyPanel) return;

        // Setup property change handlers
        const inputs = propertyPanel.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const debouncedHandler = utils.debounce(() => {
                this.handlePropertyChange(input);
            }, this.config.debounceDelay);

            utils.dom.addEventListener(input, 'input', debouncedHandler);
            utils.dom.addEventListener(input, 'change', debouncedHandler);
        });

        this.components.set('propertyPanel', {
            element: propertyPanel,
            inputs: inputs
        });
    }

    /**
     * Handle property changes
     */
    handlePropertyChange(input) {
        try {
            const activeObject = utils.canvas.getActiveObject();
            if (!activeObject) return;

            const property = input.dataset.property || input.name;
            let value = input.value;

            // Convert value based on input type
            if (input.type === 'number') {
                value = parseFloat(value) || 0;
            } else if (input.type === 'checkbox') {
                value = input.checked;
            }

            // Apply property to active object
            if (property && activeObject.set) {
                activeObject.set(property, value);
                utils.canvas.getCanvas()?.renderAll();
            }

            // Dispatch property change event
            this.dispatchEvent('propertyChanged', {
                property,
                value,
                object: activeObject
            });

        } catch (error) {
            console.error('Property change failed:', error);
        }
    }

    /**
     * Initialize layer panel
     */
    initializeLayerPanel() {
        const layerPanel = utils.dom.querySelector('#layersPanel');
        if (!layerPanel) return;

        // Setup layer list update
        document.addEventListener('canvas:objectAdded', () => {
            this.updateLayersList();
        });

        document.addEventListener('canvas:objectRemoved', () => {
            this.updateLayersList();
        });

        document.addEventListener('canvas:selectionCreated', () => {
            this.updateLayerSelection();
        });

        this.components.set('layerPanel', {
            element: layerPanel
        });

        // Initial update
        this.updateLayersList();
    }

    /**
     * Update layers list
     */
    updateLayersList() {
        try {
            const layersList = utils.dom.querySelector('#layersList');
            if (!layersList) return;

            const canvas = utils.canvas.getCanvas();
            if (!canvas) return;

            const objects = canvas.getObjects();

            // Clear existing list
            layersList.innerHTML = '';

            // Add each object as a layer
            objects.forEach((obj, index) => {
                const layerItem = this.createLayerItem(obj, index);
                layersList.appendChild(layerItem);
            });

        } catch (error) {
            console.error('Failed to update layers list:', error);
        }
    }

    /**
     * Create layer item element
     */
    createLayerItem(object, index) {
        const layerName = object.customType || object.type || `Layer ${index + 1}`;
        const isVisible = object.visible !== false;

        return utils.dom.createElement('div', {
            className: 'layer-item',
            'data-object-index': index
        }, [
            utils.dom.createElement('span', {
                className: 'layer-name',
                textContent: layerName
            }),
            utils.dom.createElement('div', {
                className: 'layer-controls'
            }, [
                utils.dom.createElement('button', {
                    className: `visibility-btn ${isVisible ? 'visible' : 'hidden'}`,
                    innerHTML: `<i class="fas fa-${isVisible ? 'eye' : 'eye-slash'}"></i>`,
                    onclick: () => this.toggleLayerVisibility(object)
                }),
                utils.dom.createElement('button', {
                    className: 'delete-btn',
                    innerHTML: '<i class="fas fa-trash"></i>',
                    onclick: () => this.deleteLayer(object)
                })
            ])
        ]);
    }

    /**
     * Initialize template gallery
     */
    initializeTemplateGallery() {
        const templateGallery = utils.dom.querySelector('#templateGallery');
        if (!templateGallery) return;

        // Setup template search
        const searchInput = templateGallery.querySelector('.template-search');
        if (searchInput) {
            const debouncedSearch = utils.debounce((query) => {
                this.searchTemplates(query);
            }, this.config.debounceDelay);

            utils.dom.addEventListener(searchInput, 'input', (e) => {
                debouncedSearch(e.target.value);
            });
        }

        // Setup category filters
        const categoryButtons = templateGallery.querySelectorAll('.category-btn');
        categoryButtons.forEach(btn => {
            utils.dom.addEventListener(btn, 'click', (e) => {
                this.filterTemplatesByCategory(btn.dataset.category);
            });
        });

        this.components.set('templateGallery', {
            element: templateGallery,
            searchInput,
            categoryButtons
        });
    }

    /**
     * Initialize image search
     */
    initializeImageSearch() {
        const imageSearch = utils.dom.querySelector('#imageSearch');
        if (!imageSearch) return;

        // Setup search functionality
        const searchInput = imageSearch.querySelector('.image-search-input');
        const searchBtn = imageSearch.querySelector('.search-btn');

        if (searchInput && searchBtn) {
            const performSearch = () => {
                const query = searchInput.value.trim();
                if (query) {
                    this.searchImages(query);
                }
            };

            utils.dom.addEventListener(searchBtn, 'click', performSearch);
            utils.dom.addEventListener(searchInput, 'keypress', (e) => {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });
        }

        this.components.set('imageSearch', {
            element: imageSearch,
            searchInput,
            searchBtn
        });
    }

    /**
     * Search images using external API
     */
    async searchImages(query) {
        try {
            utils.loading.show('imageSearch', 'Searching images...');

            const apiManager = getExternalAPIManager();
            const results = await apiManager.searchImages(query);

            this.displayImageResults(results.images);

        } catch (error) {
            console.error('Image search failed:', error);
            utils.notify.error('Image search failed. Please try again.');
        } finally {
            utils.loading.hide('imageSearch');
        }
    }

    /**
     * Display image search results
     */
    displayImageResults(images) {
        const resultsContainer = utils.dom.querySelector('#imageResults');
        if (!resultsContainer) return;

        resultsContainer.innerHTML = '';

        if (!images || images.length === 0) {
            resultsContainer.innerHTML = '<p class="no-results">No images found.</p>';
            return;
        }

        images.forEach(image => {
            const imageElement = this.createImageResultElement(image);
            resultsContainer.appendChild(imageElement);
        });
    }

    /**
     * Create image result element
     */
    createImageResultElement(imageData) {
        const imageElement = utils.dom.createElement('div', {
            className: 'image-result',
            'data-image-id': imageData.id
        });

        imageElement.innerHTML = `
            <img src="${imageData.thumbnail_url}" alt="${imageData.title}"
                 loading="lazy" onerror="this.style.display='none'">
            <div class="image-overlay">
                <button class="add-image-btn" data-image='${JSON.stringify(imageData)}'>
                    <i class="fas fa-plus"></i> Add
                </button>
            </div>
        `;

        // Add click handler for adding image to canvas
        const addBtn = imageElement.querySelector('.add-image-btn');
        utils.dom.addEventListener(addBtn, 'click', (e) => {
            e.stopPropagation();
            this.addImageToCanvas(imageData);
        });

        return imageElement;
    }

    /**
     * Add image to canvas
     */
    async addImageToCanvas(imageData) {
        try {
            utils.loading.show('addImage', 'Adding image...');

            const apiManager = getExternalAPIManager();
            await apiManager.addImageToCanvas(imageData, utils.canvas.getCanvas());

            utils.notify.success('Image added to canvas');

        } catch (error) {
            console.error('Failed to add image to canvas:', error);
            utils.notify.error('Failed to add image to canvas');
        } finally {
            utils.loading.hide('addImage');
        }
    }

    /**
     * Initialize context toolbar
     */
    initializeContextToolbar() {
        const contextToolbar = utils.dom.querySelector('#contextToolbar');
        if (!contextToolbar) return;

        // Hide initially
        contextToolbar.style.display = 'none';

        // Setup context toolbar buttons
        const buttons = contextToolbar.querySelectorAll('button');
        buttons.forEach(btn => {
            utils.dom.addEventListener(btn, 'click', (e) => {
                this.handleContextAction(btn.dataset.action || btn.className);
            });
        });

        this.components.set('contextToolbar', {
            element: contextToolbar,
            buttons
        });

        // Listen for selection changes
        document.addEventListener('canvas:selectionCreated', () => {
            this.showContextToolbar();
        });

        document.addEventListener('canvas:selectionCleared', () => {
            this.hideContextToolbar();
        });
    }

    /**
     * Show context toolbar
     */
    showContextToolbar() {
        const contextToolbar = this.components.get('contextToolbar')?.element;
        if (contextToolbar) {
            contextToolbar.style.display = 'block';
        }
    }

    /**
     * Hide context toolbar
     */
    hideContextToolbar() {
        const contextToolbar = this.components.get('contextToolbar')?.element;
        if (contextToolbar) {
            contextToolbar.style.display = 'none';
        }
    }

    /**
     * Setup global event handlers
     */
    setupGlobalEventHandlers() {
        // Handle window resize
        utils.dom.addEventListener(window, 'resize', utils.debounce(() => {
            this.handleWindowResize();
        }, 250));

        // Handle clicks outside elements
        utils.dom.addEventListener(document, 'click', (e) => {
            this.handleGlobalClick(e);
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        const shortcuts = {
            'ctrl+z': () => this.undo(),
            'ctrl+y': () => this.redo(),
            'ctrl+c': () => this.copy(),
            'ctrl+v': () => this.paste(),
            'ctrl+a': () => this.selectAll(),
            'delete': () => this.deleteSelected(),
            'escape': () => this.clearSelection()
        };

        utils.dom.addEventListener(document, 'keydown', (e) => {
            const key = this.getShortcutKey(e);
            const action = shortcuts[key];

            if (action) {
                e.preventDefault();
                action();
            }
        });
    }

    /**
     * Get keyboard shortcut key
     */
    getShortcutKey(event) {
        const parts = [];

        if (event.ctrlKey) parts.push('ctrl');
        if (event.shiftKey) parts.push('shift');
        if (event.altKey) parts.push('alt');

        parts.push(event.key.toLowerCase());

        return parts.join('+');
    }

    /**
     * Setup tooltips
     */
    setupTooltips() {
        const elementsWithTooltips = utils.dom.querySelectorAll('[data-tooltip], [title]');

        elementsWithTooltips.forEach(element => {
            const tooltip = element.dataset.tooltip || element.title;
            if (tooltip) {
                element.removeAttribute('title'); // Prevent default tooltip

                utils.dom.addEventListener(element, 'mouseenter', () => {
                    this.showTooltip(element, tooltip);
                });

                utils.dom.addEventListener(element, 'mouseleave', () => {
                    this.hideTooltip();
                });
            }
        });
    }

    /**
     * Show tooltip
     */
    showTooltip(element, text) {
        this.hideTooltip(); // Hide any existing tooltip

        setTimeout(() => {
            const tooltip = utils.dom.createElement('div', {
                id: 'ui-tooltip',
                className: 'ui-tooltip',
                textContent: text
            });

            document.body.appendChild(tooltip);

            // Position tooltip
            const rect = element.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.bottom + 10 + 'px';

            // Show with animation
            setTimeout(() => tooltip.classList.add('show'), 10);

        }, this.config.tooltipDelay);
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        const tooltip = utils.dom.getElementById('ui-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    /**
     * Setup modals
     */
    setupModals() {
        const modals = utils.dom.querySelectorAll('.modal');

        modals.forEach(modal => {
            const closeBtn = modal.querySelector('.modal-close, .close');
            if (closeBtn) {
                utils.dom.addEventListener(closeBtn, 'click', () => {
                    this.closeModal(modal);
                });
            }

            // Close on background click
            utils.dom.addEventListener(modal, 'click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }

    /**
     * Open modal
     */
    openModal(modalId) {
        const modal = utils.dom.getElementById(modalId);
        if (!modal) return false;

        modal.style.display = 'block';
        this.activeModals.add(modal);

        // Disable body scroll
        document.body.style.overflow = 'hidden';

        return true;
    }

    /**
     * Close modal
     */
    closeModal(modal) {
        if (typeof modal === 'string') {
            modal = utils.dom.getElementById(modal);
        }

        if (!modal) return false;

        modal.style.display = 'none';
        this.activeModals.delete(modal);

        // Re-enable body scroll if no modals are open
        if (this.activeModals.size === 0) {
            document.body.style.overflow = '';
        }

        return true;
    }

    /**
     * Setup context menus
     */
    setupContextMenus() {
        // Prevent default context menu on canvas
        const canvas = utils.dom.querySelector('#fabricCanvas');
        if (canvas) {
            utils.dom.addEventListener(canvas, 'contextmenu', (e) => {
                e.preventDefault();
            });
        }
    }

    /**
     * Dispatch UI event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(`ui:${eventName}`, { detail });
        document.dispatchEvent(event);
    }

    /**
     * Handle window resize
     */
    handleWindowResize() {
        // Update canvas size if needed
        const canvas = utils.canvas.getCanvas();
        if (canvas) {
            canvas.calcOffset();
        }

        // Update guide overlays
        if (window.canvasManager?.guideOverlayManager) {
            window.canvasManager.guideOverlayManager.syncWithMainCanvas();
        }
    }

    /**
     * Handle global clicks
     */
    handleGlobalClick(event) {
        // Close dropdowns, tooltips, etc.
        this.hideTooltip();

        // Close any open context menus
        const contextMenus = utils.dom.querySelectorAll('.context-menu.show');
        contextMenus.forEach(menu => {
            menu.classList.remove('show');
        });
    }

    /**
     * Cleanup and destroy
     */
    destroy() {
        this.components.clear();
        this.eventListeners.clear();
        this.activeModals.clear();
        this.isInitialized = false;
    }

    // Placeholder methods for shortcuts (to be implemented)
    undo() { console.log('Undo not implemented'); }
    redo() { console.log('Redo not implemented'); }
    copy() { console.log('Copy not implemented'); }
    paste() { console.log('Paste not implemented'); }
    selectAll() { console.log('Select all not implemented'); }
    deleteSelected() {
        const activeObject = utils.canvas.getActiveObject();
        if (activeObject) {
            utils.canvas.removeObject(activeObject);
        }
    }
    clearSelection() {
        utils.canvas.clearSelection();
    }
}

// Global UI manager instance
let globalUIManager = null;

/**
 * Get or create global UI manager
 */
function getUIManager(config = {}) {
    if (!globalUIManager) {
        globalUIManager = new EnhancedUIManager(config);
    }
    return globalUIManager;
}

// Initialize UI manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => getUIManager());
} else {
    getUIManager();
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EnhancedUIManager,
        getUIManager
    };
} else if (typeof window !== 'undefined') {
    window.EnhancedUIManager = EnhancedUIManager;
    window.getUIManager = getUIManager;
}