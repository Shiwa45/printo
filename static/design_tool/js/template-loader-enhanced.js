/**
 * Enhanced Template Loader with Error Handling and Caching
 * Fixes template loading issues and provides better UX
 */

class EnhancedTemplateLoader {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: '/api/design/templates/',
            cacheTimeout: 5 * 60 * 1000, // 5 minutes
            retryAttempts: 3,
            retryDelay: 1000,
            ...config
        };

        this.cache = new Map();
        this.loadingPromises = new Map();
        this.eventListeners = new Map();
    }

    /**
     * Load templates with caching and error handling
     */
    async loadTemplates(filters = {}) {
        const cacheKey = this.getCacheKey(filters);

        // Check cache first
        const cached = this.getCachedData(cacheKey);
        if (cached) {
            return cached;
        }

        // Check if already loading
        if (this.loadingPromises.has(cacheKey)) {
            return this.loadingPromises.get(cacheKey);
        }

        // Start loading
        const loadingPromise = this._loadTemplatesFromAPI(filters, cacheKey);
        this.loadingPromises.set(cacheKey, loadingPromise);

        try {
            const result = await loadingPromise;
            this.loadingPromises.delete(cacheKey);
            return result;
        } catch (error) {
            this.loadingPromises.delete(cacheKey);
            throw error;
        }
    }

    /**
     * Load templates from API with retry logic
     */
    async _loadTemplatesFromAPI(filters, cacheKey) {
        let lastError;

        for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
            try {
                const url = this.buildURL(filters);
                console.log(`Loading templates (attempt ${attempt}):`, url);

                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                const processedData = this.processTemplateData(data);

                // Cache the result
                this.cacheData(cacheKey, processedData);

                this.dispatchEvent('templatesLoaded', {
                    templates: processedData.results,
                    count: processedData.count,
                    filters: filters
                });

                return processedData;

            } catch (error) {
                lastError = error;
                console.warn(`Template loading attempt ${attempt} failed:`, error);

                if (attempt < this.config.retryAttempts) {
                    await this.delay(this.config.retryDelay * attempt);
                }
            }
        }

        // All attempts failed
        console.error('Template loading failed after all attempts:', lastError);
        this.dispatchEvent('templateLoadError', { error: lastError, filters });

        // Try to return fallback data
        return this.getFallbackTemplates();
    }

    /**
     * Process and validate template data
     */
    processTemplateData(data) {
        if (!data || !data.results) {
            throw new Error('Invalid template data structure');
        }

        const processedResults = data.results.map(template => {
            // Validate and fix template data
            const processedTemplate = {
                ...template,
                template_data: this.validateTemplateData(template.template_data),
                preview_image: this.processImageURL(template.preview_image),
                thumbnail_image: this.processImageURL(template.thumbnail_image)
            };

            // Add computed properties
            processedTemplate.dimensions = `${template.width} × ${template.height} mm`;
            processedTemplate.isValid = this.isTemplateValid(processedTemplate);

            return processedTemplate;
        });

        return {
            ...data,
            results: processedResults
        };
    }

    /**
     * Validate and fix template data
     */
    validateTemplateData(templateData) {
        try {
            // Handle null or undefined
            if (!templateData) {
                return this.getEmptyTemplateData();
            }

            // Handle string data
            if (typeof templateData === 'string') {
                // Try to parse JSON string
                if (templateData === 'null' || templateData === '"null"') {
                    return this.getEmptyTemplateData();
                }

                try {
                    const parsed = JSON.parse(templateData);
                    return this.validateParsedTemplate(parsed);
                } catch (parseError) {
                    console.warn('Failed to parse template data:', parseError);
                    return this.getEmptyTemplateData();
                }
            }

            // Handle object data
            if (typeof templateData === 'object') {
                return this.validateParsedTemplate(templateData);
            }

            // Fallback
            return this.getEmptyTemplateData();

        } catch (error) {
            console.warn('Template data validation failed:', error);
            return this.getEmptyTemplateData();
        }
    }

    /**
     * Validate parsed template object
     */
    validateParsedTemplate(data) {
        const validTemplate = {
            version: data.version || '5.3.0',
            objects: Array.isArray(data.objects) ? data.objects : [],
            background: data.background || '#ffffff',
            width: typeof data.width === 'number' ? data.width : 400,
            height: typeof data.height === 'number' ? data.height : 300
        };

        // Validate objects array
        validTemplate.objects = validTemplate.objects.filter(obj => {
            return obj && typeof obj === 'object' && obj.type;
        });

        return validTemplate;
    }

    /**
     * Get empty template data structure
     */
    getEmptyTemplateData() {
        return {
            version: '5.3.0',
            objects: [],
            background: '#ffffff',
            width: 400,
            height: 300
        };
    }

    /**
     * Process image URLs to handle relative paths
     */
    processImageURL(url) {
        if (!url) return null;

        // Handle absolute URLs
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }

        // Handle relative URLs
        if (url.startsWith('/')) {
            return window.location.origin + url;
        }

        return url;
    }

    /**
     * Check if template is valid for use
     */
    isTemplateValid(template) {
        return !!(
            template.id &&
            template.name &&
            template.template_data &&
            template.width > 0 &&
            template.height > 0
        );
    }

    /**
     * Build API URL with filters
     */
    buildURL(filters) {
        const url = new URL(this.config.apiEndpoint, window.location.origin);

        Object.entries(filters).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                url.searchParams.append(key, value);
            }
        });

        return url.toString();
    }

    /**
     * Generate cache key from filters
     */
    getCacheKey(filters) {
        return JSON.stringify(filters);
    }

    /**
     * Get cached data if not expired
     */
    getCachedData(cacheKey) {
        const cached = this.cache.get(cacheKey);

        if (cached && (Date.now() - cached.timestamp) < this.config.cacheTimeout) {
            console.log('Returning cached templates');
            return cached.data;
        }

        if (cached) {
            this.cache.delete(cacheKey);
        }

        return null;
    }

    /**
     * Cache data with timestamp
     */
    cacheData(cacheKey, data) {
        this.cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });

        // Cleanup old cache entries
        this.cleanupCache();
    }

    /**
     * Cleanup expired cache entries
     */
    cleanupCache() {
        const now = Date.now();
        const keysToDelete = [];

        for (const [key, value] of this.cache.entries()) {
            if ((now - value.timestamp) > this.config.cacheTimeout) {
                keysToDelete.push(key);
            }
        }

        keysToDelete.forEach(key => this.cache.delete(key));
    }

    /**
     * Get fallback templates when API fails
     */
    getFallbackTemplates() {
        return {
            count: 1,
            results: [{
                id: 'fallback-empty',
                name: 'Blank Template',
                category: null,
                product_types: [],
                template_data: this.getEmptyTemplateData(),
                preview_image: null,
                thumbnail_image: null,
                width: 89,
                height: 54,
                dpi: 300,
                color_mode: 'CMYK',
                tags: [],
                is_premium: false,
                is_featured: false,
                dimensions: '89 × 54 mm',
                isValid: true
            }]
        };
    }

    /**
     * Load specific template by ID
     */
    async loadTemplate(templateId) {
        try {
            const url = `${this.config.apiEndpoint}${templateId}/`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const template = await response.json();
            const processedTemplate = {
                ...template,
                template_data: this.validateTemplateData(template.template_data),
                preview_image: this.processImageURL(template.preview_image),
                thumbnail_image: this.processImageURL(template.thumbnail_image)
            };

            this.dispatchEvent('templateLoaded', { template: processedTemplate });
            return processedTemplate;

        } catch (error) {
            console.error('Failed to load template:', templateId, error);
            this.dispatchEvent('templateLoadError', { error, templateId });
            throw error;
        }
    }

    /**
     * Search templates by text
     */
    async searchTemplates(query, filters = {}) {
        const searchFilters = {
            ...filters,
            search: query
        };

        return this.loadTemplates(searchFilters);
    }

    /**
     * Load templates by category
     */
    async loadTemplatesByCategory(categoryId) {
        return this.loadTemplates({ category: categoryId });
    }

    /**
     * Load featured templates
     */
    async loadFeaturedTemplates() {
        return this.loadTemplates({ is_featured: true });
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('Template cache cleared');
    }

    /**
     * Utility delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Event handling
     */
    addEventListener(eventName, callback) {
        if (!this.eventListeners.has(eventName)) {
            this.eventListeners.set(eventName, []);
        }
        this.eventListeners.get(eventName).push(callback);
    }

    removeEventListener(eventName, callback) {
        const listeners = this.eventListeners.get(eventName);
        if (listeners) {
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    dispatchEvent(eventName, detail = {}) {
        const listeners = this.eventListeners.get(eventName) || [];
        listeners.forEach(callback => {
            try {
                callback(detail);
            } catch (error) {
                console.error(`Error in event listener for ${eventName}:`, error);
            }
        });

        // Also dispatch DOM event
        const domEvent = new CustomEvent(`templateLoader:${eventName}`, { detail });
        document.dispatchEvent(domEvent);
    }

    /**
     * Destroy loader and cleanup
     */
    destroy() {
        this.cache.clear();
        this.loadingPromises.clear();
        this.eventListeners.clear();
    }
}

// Global template loader instance
let globalTemplateLoader = null;

/**
 * Get or create global template loader instance
 */
function getTemplateLoader(config = {}) {
    if (!globalTemplateLoader) {
        globalTemplateLoader = new EnhancedTemplateLoader(config);
    }
    return globalTemplateLoader;
}

/**
 * Load templates with the global loader (backward compatibility)
 */
async function loadTemplates(filters = {}) {
    const loader = getTemplateLoader();
    return loader.loadTemplates(filters);
}

/**
 * Load specific template
 */
async function loadTemplate(templateId) {
    const loader = getTemplateLoader();
    return loader.loadTemplate(templateId);
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EnhancedTemplateLoader,
        getTemplateLoader,
        loadTemplates,
        loadTemplate
    };
} else if (typeof window !== 'undefined') {
    window.EnhancedTemplateLoader = EnhancedTemplateLoader;
    window.getTemplateLoader = getTemplateLoader;
    window.loadTemplates = loadTemplates;
    window.loadTemplate = loadTemplate;
}