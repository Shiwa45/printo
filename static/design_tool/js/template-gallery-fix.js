/**
 * Template Gallery Fix
 * Ensures templates are properly loaded and displayed in the gallery
 */

(function() {
    'use strict';

    let isInitialized = false;

    /**
     * Initialize template gallery with proper loading
     */
    function initializeTemplateGallery() {
        if (isInitialized) return;

        console.log('Initializing template gallery...');

        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeTemplateGallery);
            return;
        }

        try {
            // Find template gallery container
            const galleryContainer = findTemplateGalleryContainer();
            if (!galleryContainer) {
                console.warn('Template gallery container not found');
                return;
            }

            // Load templates
            loadAndDisplayTemplates(galleryContainer);

            isInitialized = true;

        } catch (error) {
            console.error('Failed to initialize template gallery:', error);
        }
    }

    /**
     * Find template gallery container
     */
    function findTemplateGalleryContainer() {
        // Try multiple possible selectors
        const selectors = [
            '#templateGallery',
            '.template-gallery',
            '#templates-list',
            '.templates-grid',
            '#template-gallery',
            '.templates-container',
            '[data-templates]'
        ];

        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                console.log(`Found template gallery container: ${selector}`);
                return element;
            }
        }

        // If not found, create one
        return createTemplateGalleryContainer();
    }

    /**
     * Create template gallery container if it doesn't exist
     */
    function createTemplateGalleryContainer() {
        try {
            const container = document.createElement('div');
            container.id = 'templateGallery';
            container.className = 'template-gallery';
            container.innerHTML = `
                <div class="template-gallery-header">
                    <h3>Templates</h3>
                    <div class="template-search-container">
                        <input type="text" class="template-search" placeholder="Search templates...">
                        <button class="search-btn"><i class="fas fa-search"></i></button>
                    </div>
                </div>
                <div class="template-categories">
                    <button class="category-btn active" data-category="all">All</button>
                    <button class="category-btn" data-category="business">Business</button>
                    <button class="category-btn" data-category="marketing">Marketing</button>
                    <button class="category-btn" data-category="stationery">Stationery</button>
                </div>
                <div class="templates-grid" id="templates-list">
                    <div class="loading-message">Loading templates...</div>
                </div>
            `;

            // Add styles
            addTemplateGalleryStyles();

            // Find suitable parent
            const parent = document.querySelector('.sidebar-right') ||
                          document.querySelector('.templates-panel') ||
                          document.querySelector('.right-panel') ||
                          document.body;

            parent.appendChild(container);

            console.log('Created template gallery container');
            return container;

        } catch (error) {
            console.error('Failed to create template gallery container:', error);
            return null;
        }
    }

    /**
     * Add template gallery styles
     */
    function addTemplateGalleryStyles() {
        if (document.getElementById('template-gallery-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'template-gallery-styles';
        styles.textContent = `
            .template-gallery {
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                margin: 10px;
            }

            .template-gallery-header {
                padding: 15px;
                border-bottom: 1px solid #eee;
                background: #f8f9fa;
            }

            .template-gallery-header h3 {
                margin: 0 0 10px 0;
                font-size: 16px;
                font-weight: 600;
                color: #333;
            }

            .template-search-container {
                display: flex;
                gap: 5px;
            }

            .template-search {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }

            .search-btn {
                padding: 8px 12px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }

            .template-categories {
                display: flex;
                gap: 5px;
                padding: 10px 15px;
                border-bottom: 1px solid #eee;
                flex-wrap: wrap;
            }

            .category-btn {
                padding: 6px 12px;
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 20px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }

            .category-btn.active {
                background: #007bff;
                color: white;
                border-color: #007bff;
            }

            .templates-grid {
                padding: 15px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                max-height: 400px;
                overflow-y: auto;
            }

            .template-item {
                background: #fff;
                border: 2px solid #eee;
                border-radius: 8px;
                overflow: hidden;
                cursor: pointer;
                transition: all 0.3s;
                position: relative;
            }

            .template-item:hover {
                border-color: #007bff;
                box-shadow: 0 4px 12px rgba(0,123,255,0.2);
                transform: translateY(-2px);
            }

            .template-item.active {
                border-color: #28a745;
                box-shadow: 0 4px 12px rgba(40,167,69,0.3);
            }

            .template-preview {
                width: 100%;
                height: 80px;
                background: #f8f9fa;
                display: flex;
                align-items: center;
                justify-content: center;
                border-bottom: 1px solid #eee;
                position: relative;
            }

            .template-preview img {
                max-width: 100%;
                max-height: 100%;
                object-fit: cover;
            }

            .template-preview .placeholder {
                color: #6c757d;
                font-size: 24px;
            }

            .template-info {
                padding: 8px;
            }

            .template-name {
                font-size: 12px;
                font-weight: 500;
                color: #333;
                margin-bottom: 4px;
                line-height: 1.2;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }

            .template-dimensions {
                font-size: 10px;
                color: #6c757d;
            }

            .loading-message, .error-message, .no-templates {
                text-align: center;
                padding: 40px 20px;
                color: #6c757d;
                font-size: 14px;
            }

            .error-message {
                color: #dc3545;
            }

            .premium-badge, .featured-badge {
                position: absolute;
                top: 4px;
                right: 4px;
                padding: 2px 6px;
                font-size: 10px;
                border-radius: 10px;
                color: white;
                font-weight: 500;
            }

            .premium-badge {
                background: #ffc107;
                color: #000;
            }

            .featured-badge {
                background: #28a745;
            }
        `;

        document.head.appendChild(styles);
    }

    /**
     * Load and display templates
     */
    async function loadAndDisplayTemplates(container) {
        try {
            const templatesList = container.querySelector('#templates-list') ||
                                 container.querySelector('.templates-grid');

            if (!templatesList) {
                console.error('Templates list container not found');
                return;
            }

            // Show loading state
            templatesList.innerHTML = '<div class="loading-message">Loading templates...</div>';

            // Load templates using enhanced template loader
            let templates;
            if (window.templateLoader) {
                const result = await window.templateLoader.loadTemplates();
                templates = result.results || result;
            } else {
                // Fallback to direct API call
                const response = await fetch('/api/design/templates/');
                const data = await response.json();
                templates = data.results || data;
            }

            console.log('Loaded templates:', templates.length);

            // Display templates
            displayTemplates(templatesList, templates);

            // Setup template interaction handlers
            setupTemplateHandlers(container);

        } catch (error) {
            console.error('Failed to load templates:', error);

            const templatesList = container.querySelector('#templates-list') ||
                                 container.querySelector('.templates-grid');
            if (templatesList) {
                templatesList.innerHTML = `
                    <div class="error-message">
                        Failed to load templates.<br>
                        <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Retry
                        </button>
                    </div>
                `;
            }
        }
    }

    /**
     * Display templates in the gallery
     */
    function displayTemplates(container, templates) {
        if (!templates || templates.length === 0) {
            container.innerHTML = '<div class="no-templates">No templates available</div>';
            return;
        }

        const templatesHTML = templates.map(template => createTemplateHTML(template)).join('');
        container.innerHTML = templatesHTML;

        console.log(`Displayed ${templates.length} templates`);
    }

    /**
     * Create HTML for a single template
     */
    function createTemplateHTML(template) {
        const previewImage = template.preview_image || template.thumbnail_image;
        const dimensions = `${Math.round(template.width)} × ${Math.round(template.height)} mm`;

        return `
            <div class="template-item" data-template-id="${template.id}" data-template='${JSON.stringify(template)}'>
                <div class="template-preview">
                    ${previewImage ?
                        `<img src="${previewImage}" alt="${template.name}" loading="lazy" onerror="this.style.display='none'">` :
                        `<div class="placeholder"><i class="fas fa-image"></i></div>`
                    }
                    ${template.is_premium ? '<span class="premium-badge">Premium</span>' : ''}
                    ${template.is_featured ? '<span class="featured-badge">Featured</span>' : ''}
                </div>
                <div class="template-info">
                    <div class="template-name">${template.name}</div>
                    <div class="template-dimensions">${dimensions}</div>
                </div>
            </div>
        `;
    }

    /**
     * Setup template interaction handlers
     */
    function setupTemplateHandlers(container) {
        // Template selection
        container.addEventListener('click', (e) => {
            const templateItem = e.target.closest('.template-item');
            if (templateItem) {
                handleTemplateSelection(templateItem);
            }
        });

        // Category filtering
        const categoryButtons = container.querySelectorAll('.category-btn');
        categoryButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active category
                categoryButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Filter templates
                filterTemplatesByCategory(btn.dataset.category);
            });
        });

        // Search functionality
        const searchInput = container.querySelector('.template-search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    searchTemplates(e.target.value);
                }, 300);
            });
        }
    }

    /**
     * Handle template selection and loading to canvas
     */
    async function handleTemplateSelection(templateItem) {
        try {
            const templateId = templateItem.dataset.templateId;
            const templateData = JSON.parse(templateItem.dataset.template);

            console.log('Selected template:', templateData.name);

            // Update visual selection
            document.querySelectorAll('.template-item.active').forEach(item => {
                item.classList.remove('active');
            });
            templateItem.classList.add('active');

            // Show loading state
            templateItem.style.opacity = '0.7';
            const loadingSpinner = document.createElement('div');
            loadingSpinner.className = 'template-loading';
            loadingSpinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            loadingSpinner.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255,255,255,0.9);
                padding: 10px;
                border-radius: 50%;
                z-index: 10;
            `;
            templateItem.style.position = 'relative';
            templateItem.appendChild(loadingSpinner);

            // Load template to canvas
            if (window.templateCanvasManager) {
                await window.templateCanvasManager.loadTemplateToCanvas(templateId);
            } else if (window.applyTemplate) {
                await window.applyTemplate(templateId);
            } else {
                throw new Error('No template loading method available');
            }

            // Show success feedback
            if (window.utils && window.utils.notify) {
                window.utils.notify.success(`Template "${templateData.name}" loaded successfully`);
            } else {
                console.log('Template loaded successfully');
            }

        } catch (error) {
            console.error('Failed to load template:', error);

            // Show error feedback
            if (window.utils && window.utils.notify) {
                window.utils.notify.error('Failed to load template. Please try again.');
            } else {
                alert('Failed to load template. Please try again.');
            }
        } finally {
            // Remove loading state
            templateItem.style.opacity = '';
            const loadingSpinner = templateItem.querySelector('.template-loading');
            if (loadingSpinner) {
                loadingSpinner.remove();
            }
        }
    }

    /**
     * Filter templates by category
     */
    function filterTemplatesByCategory(category) {
        const templateItems = document.querySelectorAll('.template-item');

        templateItems.forEach(item => {
            const templateData = JSON.parse(item.dataset.template);
            const shouldShow = category === 'all' ||
                              templateData.product_types.includes(category) ||
                              templateData.category?.toString().includes(category);

            item.style.display = shouldShow ? 'block' : 'none';
        });
    }

    /**
     * Search templates
     */
    function searchTemplates(query) {
        const templateItems = document.querySelectorAll('.template-item');

        templateItems.forEach(item => {
            const templateData = JSON.parse(item.dataset.template);
            const searchText = (templateData.name + ' ' + templateData.tags.join(' ')).toLowerCase();
            const shouldShow = !query || searchText.includes(query.toLowerCase());

            item.style.display = shouldShow ? 'block' : 'none';
        });
    }

    // Initialize when ready
    initializeTemplateGallery();

    // Also initialize when canvas is ready
    document.addEventListener('canvas:canvasInitialized', () => {
        setTimeout(initializeTemplateGallery, 500);
    });

    // Export for manual initialization
    window.initializeTemplateGallery = initializeTemplateGallery;

})();