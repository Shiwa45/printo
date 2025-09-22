/**
 * Enhanced Template Integration
 * Integrates enhanced template loading with existing design tool functionality
 */

(function() {
    'use strict';

    let templateLoader = null;
    let templateCanvasManager = null;
    let isInitialized = false;

    /**
     * Initialize enhanced template system
     */
    function initializeEnhancedTemplateSystem() {
        if (isInitialized) {
            return;
        }

        try {
            // Create template loader
            templateLoader = getTemplateLoader({
                apiEndpoint: '/api/design/templates/',
                cacheTimeout: 5 * 60 * 1000, // 5 minutes
                retryAttempts: 3
            });

            // Wait for canvas to be ready
            if (window.canvasManager && window.canvasManager.isReady()) {
                initializeTemplateCanvasManager();
            } else {
                // Listen for canvas initialization
                document.addEventListener('canvas:canvasInitialized', () => {
                    initializeTemplateCanvasManager();
                });
            }

            setupTemplateEventHandlers();
            enhanceExistingTemplateFunctions();

            isInitialized = true;
            console.log('Enhanced template system initialized');

        } catch (error) {
            console.error('Failed to initialize enhanced template system:', error);
        }
    }

    /**
     * Initialize template canvas manager
     */
    function initializeTemplateCanvasManager() {
        if (!window.canvasManager) {
            console.warn('Canvas manager not available for template integration');
            return;
        }

        templateCanvasManager = new TemplateCanvasManager(window.canvasManager, templateLoader);
        window.templateCanvasManager = templateCanvasManager;

        console.log('Template canvas manager initialized');
    }

    /**
     * Setup template event handlers
     */
    function setupTemplateEventHandlers() {
        // Enhanced template loading events
        document.addEventListener('templateLoader:templatesLoaded', (event) => {
            const { templates, count } = event.detail;
            updateTemplatesList(templates);
            updateTemplatesCount(count);
        });

        document.addEventListener('templateLoader:templateLoadError', (event) => {
            const { error } = event.detail;
            showTemplateLoadError(error);
        });

        // Template canvas events
        document.addEventListener('templateCanvas:templateLoaded', (event) => {
            const { template } = event.detail;
            onTemplateLoadedToCanvas(template);
        });

        document.addEventListener('templateCanvas:templateLoadFailed', (event) => {
            const { error } = event.detail;
            showTemplateCanvasError(error);
        });
    }

    /**
     * Enhance existing template functions
     */
    function enhanceExistingTemplateFunctions() {
        // Replace loadTemplates function
        if (typeof window.loadTemplates === 'function') {
            window.loadTemplatesOriginal = window.loadTemplates;
        }

        window.loadTemplates = async function(filters = {}) {
            try {
                const result = await templateLoader.loadTemplates(filters);
                return result;
            } catch (error) {
                console.error('Enhanced template loading failed, falling back to original:', error);
                if (window.loadTemplatesOriginal) {
                    return window.loadTemplatesOriginal(filters);
                }
                throw error;
            }
        };

        // Replace applyTemplate function
        if (typeof window.applyTemplate === 'function') {
            window.applyTemplateOriginal = window.applyTemplate;
        }

        window.applyTemplate = async function(templateId, side = 'single') {
            if (templateCanvasManager) {
                return templateCanvasManager.loadTemplateToCanvas(templateId, side);
            } else {
                console.warn('Template canvas manager not available, using original method');
                if (window.applyTemplateOriginal) {
                    return window.applyTemplateOriginal(templateId, side);
                }
            }
        };

        // Enhance template selection handlers
        enhanceTemplateClickHandlers();
    }

    /**
     * Enhance template click handlers
     */
    function enhanceTemplateClickHandlers() {
        // Use event delegation for dynamically loaded templates
        document.addEventListener('click', function(event) {
            const templateItem = event.target.closest('.template-item, .template-card, [data-template-id]');

            if (templateItem) {
                const templateId = templateItem.dataset.templateId ||
                                templateItem.getAttribute('data-template-id');

                if (templateId) {
                    event.preventDefault();
                    handleTemplateSelection(templateId);
                }
            }
        });
    }

    /**
     * Handle template selection
     */
    async function handleTemplateSelection(templateId) {
        try {
            // Show loading state
            showTemplateSelectionLoading(templateId);

            // Load template to canvas
            if (templateCanvasManager) {
                await templateCanvasManager.loadTemplateToCanvas(templateId);
                showTemplateSelectionSuccess();
            } else {
                throw new Error('Template canvas manager not available');
            }

        } catch (error) {
            console.error('Template selection failed:', error);
            showTemplateSelectionError(error);
        }
    }

    /**
     * Update templates list in the UI
     */
    function updateTemplatesList(templates) {
        const templateContainers = [
            document.getElementById('templates-list'),
            document.querySelector('.templates-grid'),
            document.querySelector('#template-gallery')
        ];

        templateContainers.forEach(container => {
            if (container) {
                renderTemplatesInContainer(container, templates);
            }
        });
    }

    /**
     * Render templates in container
     */
    function renderTemplatesInContainer(container, templates) {
        if (!templates || templates.length === 0) {
            container.innerHTML = `
                <div class="no-templates-message">
                    <i class="fas fa-image"></i>
                    <p>No templates available</p>
                </div>
            `;
            return;
        }

        const templateHTML = templates.map(template => generateTemplateHTML(template)).join('');
        container.innerHTML = templateHTML;
    }

    /**
     * Generate HTML for a template
     */
    function generateTemplateHTML(template) {
        const imageUrl = template.thumbnail_image || template.preview_image || '/static/images/template-placeholder.png';
        const validClass = template.isValid ? '' : 'template-invalid';

        return `
            <div class="template-item ${validClass}" data-template-id="${template.id}">
                <div class="template-image">
                    <img src="${imageUrl}" alt="${template.name}"
                         onerror="this.src='/static/images/template-placeholder.png'">
                    ${template.is_premium ? '<span class="premium-badge">Premium</span>' : ''}
                    ${template.is_featured ? '<span class="featured-badge">Featured</span>' : ''}
                </div>
                <div class="template-info">
                    <div class="template-name">${template.name}</div>
                    <div class="template-dimensions">${template.dimensions}</div>
                    ${!template.isValid ? '<div class="template-warning">Invalid template data</div>' : ''}
                </div>
            </div>
        `;
    }

    /**
     * Update templates count
     */
    function updateTemplatesCount(count) {
        const countElements = document.querySelectorAll('.templates-count');
        countElements.forEach(element => {
            element.textContent = count;
        });
    }

    /**
     * Show template load error
     */
    function showTemplateLoadError(error) {
        console.error('Template load error:', error);

        const errorMessage = `
            <div class="template-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Failed to load templates</p>
                <button onclick="location.reload()" class="retry-button">Retry</button>
            </div>
        `;

        const templateContainers = [
            document.getElementById('templates-list'),
            document.querySelector('.templates-grid')
        ];

        templateContainers.forEach(container => {
            if (container) {
                container.innerHTML = errorMessage;
            }
        });
    }

    /**
     * Show template canvas error
     */
    function showTemplateCanvasError(error) {
        showNotification('Failed to apply template to canvas: ' + error.message, 'error');
    }

    /**
     * Handle template loaded to canvas
     */
    function onTemplateLoadedToCanvas(template) {
        console.log('Template loaded to canvas:', template.name);

        // Update UI to show active template
        updateActiveTemplate(template);

        // Save to history if function exists
        if (typeof saveHistory === 'function') {
            saveHistory();
        }

        // Update layers list if function exists
        if (typeof updateLayersList === 'function') {
            updateLayersList();
        }

        showNotification(`Template "${template.name}" loaded successfully`, 'success');
    }

    /**
     * Update active template in UI
     */
    function updateActiveTemplate(template) {
        // Remove existing active states
        document.querySelectorAll('.template-item.active').forEach(item => {
            item.classList.remove('active');
        });

        // Add active state to current template
        const activeTemplate = document.querySelector(`[data-template-id="${template.id}"]`);
        if (activeTemplate) {
            activeTemplate.classList.add('active');
        }

        // Update template info panel if it exists
        const templateInfo = document.getElementById('current-template-info');
        if (templateInfo) {
            templateInfo.innerHTML = `
                <div class="current-template">
                    <span class="template-name">${template.name}</span>
                    <span class="template-dimensions">${template.dimensions}</span>
                </div>
            `;
        }
    }

    /**
     * Show template selection loading state
     */
    function showTemplateSelectionLoading(templateId) {
        const templateItem = document.querySelector(`[data-template-id="${templateId}"]`);
        if (templateItem) {
            templateItem.classList.add('loading');
        }
    }

    /**
     * Show template selection success
     */
    function showTemplateSelectionSuccess() {
        document.querySelectorAll('.template-item.loading').forEach(item => {
            item.classList.remove('loading');
        });
    }

    /**
     * Show template selection error
     */
    function showTemplateSelectionError(error) {
        document.querySelectorAll('.template-item.loading').forEach(item => {
            item.classList.remove('loading');
        });

        showNotification('Failed to load template: ' + error.message, 'error');
    }

    /**
     * Show notification (fallback implementation)
     */
    function showNotification(message, type = 'info') {
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    /**
     * Load templates for current product/category
     */
    async function loadTemplatesForProduct(productId) {
        if (!templateLoader) {
            console.warn('Template loader not initialized');
            return;
        }

        try {
            const result = await templateLoader.loadTemplates({
                product_types: productId
            });

            return result;
        } catch (error) {
            console.error('Failed to load templates for product:', error);
            throw error;
        }
    }

    /**
     * Load featured templates
     */
    async function loadFeaturedTemplates() {
        if (!templateLoader) {
            console.warn('Template loader not initialized');
            return;
        }

        try {
            const result = await templateLoader.loadFeaturedTemplates();
            return result;
        } catch (error) {
            console.error('Failed to load featured templates:', error);
            throw error;
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeEnhancedTemplateSystem);
    } else {
        initializeEnhancedTemplateSystem();
    }

    // Export functions for external use
    if (typeof window !== 'undefined') {
        window.templateLoader = templateLoader;
        window.loadTemplatesForProduct = loadTemplatesForProduct;
        window.loadFeaturedTemplates = loadFeaturedTemplates;
    }

})();