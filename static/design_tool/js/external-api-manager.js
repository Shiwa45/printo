/**
 * Enhanced External API Manager
 * Handles image search from multiple stock photo APIs with proper error handling
 */

class ExternalAPIManager {
    constructor(config = {}) {
        this.config = {
            imageSearchEndpoint: '/api/design/search/images/',
            defaultSource: 'all',
            retryAttempts: 3,
            retryDelay: 1000,
            cacheTimeout: 10 * 60 * 1000, // 10 minutes
            ...config
        };

        this.cache = new Map();
        this.loadingPromises = new Map();
        this.abortControllers = new Map();
        this.rateLimits = new Map();

        // Initialize rate limits
        this.initializeRateLimits();
    }

    /**
     * Initialize rate limit tracking
     */
    initializeRateLimits() {
        const sources = ['pixabay', 'unsplash', 'pexels'];
        sources.forEach(source => {
            this.rateLimits.set(source, {
                requests: 0,
                resetTime: Date.now() + (60 * 60 * 1000), // 1 hour
                maxRequests: this.getMaxRequestsForSource(source)
            });
        });
    }

    /**
     * Get maximum requests per hour for each source
     */
    getMaxRequestsForSource(source) {
        const limits = {
            'pixabay': 5000,  // Very generous limit
            'unsplash': 50,   // Conservative limit
            'pexels': 200     // Medium limit
        };
        return limits[source] || 100;
    }

    /**
     * Search for images from external APIs
     */
    async searchImages(query, options = {}) {
        const searchOptions = {
            source: 'all',
            page: 1,
            perPage: 20,
            ...options
        };

        const cacheKey = this.getCacheKey('search', query, searchOptions);

        // Check cache first
        const cached = this.getCachedData(cacheKey);
        if (cached) {
            console.log('Returning cached search results');
            return cached;
        }

        // Check if already loading
        if (this.loadingPromises.has(cacheKey)) {
            return this.loadingPromises.get(cacheKey);
        }

        // Start loading
        const loadingPromise = this._performImageSearch(query, searchOptions, cacheKey);
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
     * Perform the actual image search
     */
    async _performImageSearch(query, options, cacheKey) {
        let lastError;

        for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
            try {
                // Create abort controller for this request
                const abortController = new AbortController();
                this.abortControllers.set(cacheKey, abortController);

                const result = await this._makeImageSearchRequest(query, options, abortController.signal);

                // Process and validate results
                const processedResult = this.processImageSearchResults(result);

                // Cache the result
                this.cacheData(cacheKey, processedResult);

                // Dispatch success event
                this.dispatchEvent('imageSearchSuccess', {
                    query,
                    options,
                    result: processedResult
                });

                return processedResult;

            } catch (error) {
                lastError = error;
                console.warn(`Image search attempt ${attempt} failed:`, error);

                // Don't retry if request was aborted
                if (error.name === 'AbortError') {
                    throw error;
                }

                // Don't retry rate limit errors
                if (error.message.includes('rate limit')) {
                    throw error;
                }

                if (attempt < this.config.retryAttempts) {
                    await this.delay(this.config.retryDelay * attempt);
                }
            } finally {
                this.abortControllers.delete(cacheKey);
            }
        }

        // All attempts failed
        console.error('Image search failed after all attempts:', lastError);
        this.dispatchEvent('imageSearchError', { query, options, error: lastError });

        // Return fallback data
        return this.getFallbackImageResults(query);
    }

    /**
     * Make the actual API request
     */
    async _makeImageSearchRequest(query, options, signal) {
        const url = new URL(this.config.imageSearchEndpoint, window.location.origin);
        url.searchParams.append('query', query);
        url.searchParams.append('source', options.source);
        url.searchParams.append('page', options.page);
        url.searchParams.append('per_page', options.perPage);

        // Check rate limits before making request
        if (!this.checkRateLimit(options.source)) {
            throw new Error(`Rate limit exceeded for ${options.source}`);
        }

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            signal
        });

        if (!response.ok) {
            if (response.status === 429) {
                throw new Error(`Rate limit exceeded (HTTP ${response.status})`);
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Update rate limit
        this.updateRateLimit(options.source);

        return data;
    }

    /**
     * Process and validate image search results
     */
    processImageSearchResults(data) {
        const processed = {
            images: [],
            total: 0,
            page: 1,
            perPage: 20,
            query: '',
            sources: [],
            ...data
        };

        // Validate and enhance each image
        if (data.images && Array.isArray(data.images)) {
            processed.images = data.images.map(img => this.validateImageData(img)).filter(Boolean);
        } else if (data.results && Array.isArray(data.results)) {
            // Handle different API response formats
            processed.images = data.results.map(img => this.validateImageData(img)).filter(Boolean);
        }

        return processed;
    }

    /**
     * Validate and enhance image data
     */
    validateImageData(imageData) {
        if (!imageData || typeof imageData !== 'object') {
            return null;
        }

        // Ensure required fields exist
        const requiredFields = ['id', 'thumbnail_url', 'medium_url'];
        const hasRequiredFields = requiredFields.every(field =>
            imageData[field] || imageData[field.replace('_', '')] || imageData[field.replace('_url', '')]
        );

        if (!hasRequiredFields) {
            console.warn('Image data missing required fields:', imageData);
            return null;
        }

        // Normalize field names and add missing data
        return {
            id: imageData.id || Math.random().toString(36).substr(2, 9),
            source: imageData.source || 'unknown',
            title: imageData.title || imageData.alt || imageData.tags || 'Untitled',
            description: imageData.description || '',
            thumbnail_url: this.normalizeImageURL(imageData.thumbnail_url || imageData.previewURL || imageData.preview_url),
            medium_url: this.normalizeImageURL(imageData.medium_url || imageData.webformatURL || imageData.url),
            large_url: this.normalizeImageURL(imageData.large_url || imageData.largeImageURL || imageData.fullHDURL || imageData.medium_url),
            width: parseInt(imageData.width || imageData.imageWidth || 400),
            height: parseInt(imageData.height || imageData.imageHeight || 300),
            photographer: imageData.photographer || imageData.user || 'Unknown',
            photographer_url: imageData.photographer_url || imageData.pageURL || '',
            tags: this.normalizeTags(imageData.tags),
            attribution_required: imageData.attribution_required !== false,
            license: imageData.license || 'Stock Photo License',
            download_url: imageData.download_url || imageData.medium_url,
            isValid: true
        };
    }

    /**
     * Normalize image URL to handle relative paths
     */
    normalizeImageURL(url) {
        if (!url) return '';

        // Handle absolute URLs
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }

        // Handle protocol-relative URLs
        if (url.startsWith('//')) {
            return 'https:' + url;
        }

        // Handle relative URLs (shouldn't happen with external APIs, but just in case)
        if (url.startsWith('/')) {
            return window.location.origin + url;
        }

        return url;
    }

    /**
     * Normalize tags data
     */
    normalizeTags(tags) {
        if (!tags) return [];

        if (typeof tags === 'string') {
            // Handle comma-separated tags
            return tags.split(',').map(tag => tag.trim()).filter(Boolean);
        }

        if (Array.isArray(tags)) {
            return tags.map(tag => typeof tag === 'object' ? tag.title || tag.name || '' : String(tag)).filter(Boolean);
        }

        return [];
    }

    /**
     * Get trending/popular images
     */
    async getTrendingImages(options = {}) {
        const trendingOptions = {
            source: 'all',
            perPage: 20,
            ...options
        };

        // Use popular search terms for trending content
        const trendingQueries = ['design', 'business', 'technology', 'abstract', 'nature'];
        const randomQuery = trendingQueries[Math.floor(Math.random() * trendingQueries.length)];

        return this.searchImages(randomQuery, {
            ...trendingOptions,
            page: 1
        });
    }

    /**
     * Get images by category
     */
    async getImagesByCategory(category, options = {}) {
        const categoryQueries = {
            'business': 'business office professional',
            'technology': 'technology computer digital',
            'nature': 'nature landscape outdoor',
            'people': 'people person portrait',
            'abstract': 'abstract pattern design',
            'food': 'food restaurant cooking',
            'travel': 'travel vacation destination'
        };

        const query = categoryQueries[category] || category;
        return this.searchImages(query, options);
    }

    /**
     * Download image data for use in canvas
     */
    async downloadImageData(imageUrl) {
        try {
            // Create a proxy request to avoid CORS issues
            const proxyUrl = `/api/design/proxy-image/?url=${encodeURIComponent(imageUrl)}`;

            const response = await fetch(proxyUrl);
            if (!response.ok) {
                throw new Error(`Failed to download image: ${response.statusText}`);
            }

            const blob = await response.blob();
            return blob;

        } catch (error) {
            console.error('Failed to download image:', error);

            // Fallback: try direct access (might fail due to CORS)
            try {
                const response = await fetch(imageUrl);
                if (response.ok) {
                    return await response.blob();
                }
            } catch (fallbackError) {
                console.warn('Direct image access also failed:', fallbackError);
            }

            throw error;
        }
    }

    /**
     * Add image to canvas
     */
    async addImageToCanvas(imageData, canvas) {
        if (!canvas || typeof canvas.add !== 'function') {
            throw new Error('Invalid canvas object');
        }

        try {
            // Show loading state
            this.dispatchEvent('imageLoadingStarted', { imageData });

            // Use medium quality URL for canvas
            const imageUrl = imageData.medium_url || imageData.thumbnail_url;

            // Create fabric image
            const fabricImage = await this.createFabricImage(imageUrl);

            // Position image in center of canvas
            const canvasCenter = {
                x: canvas.getWidth() / 2,
                y: canvas.getHeight() / 2
            };

            fabricImage.set({
                left: canvasCenter.x - fabricImage.width / 2,
                top: canvasCenter.y - fabricImage.height / 2,
                selectable: true,
                moveable: true
            });

            // Add custom properties for tracking
            fabricImage.set({
                customType: 'stockImage',
                stockImageData: imageData
            });

            // Add to canvas
            canvas.add(fabricImage);
            canvas.setActiveObject(fabricImage);
            canvas.renderAll();

            this.dispatchEvent('imageAddedToCanvas', {
                imageData,
                fabricImage,
                canvas
            });

            return fabricImage;

        } catch (error) {
            console.error('Failed to add image to canvas:', error);
            this.dispatchEvent('imageLoadingError', { imageData, error });
            throw error;
        }
    }

    /**
     * Create Fabric.js image object
     */
    createFabricImage(imageUrl) {
        return new Promise((resolve, reject) => {
            fabric.Image.fromURL(imageUrl, (img) => {
                if (!img) {
                    reject(new Error('Failed to create fabric image'));
                    return;
                }

                // Scale image to reasonable size
                const maxWidth = 400;
                const maxHeight = 400;

                if (img.width > maxWidth || img.height > maxHeight) {
                    const scale = Math.min(maxWidth / img.width, maxHeight / img.height);
                    img.scale(scale);
                }

                resolve(img);
            }, {
                crossOrigin: 'anonymous'
            });
        });
    }

    /**
     * Check rate limit for a source
     */
    checkRateLimit(source) {
        if (source === 'all') return true;

        const limit = this.rateLimits.get(source);
        if (!limit) return true;

        // Reset if time has passed
        if (Date.now() > limit.resetTime) {
            limit.requests = 0;
            limit.resetTime = Date.now() + (60 * 60 * 1000);
        }

        return limit.requests < limit.maxRequests;
    }

    /**
     * Update rate limit counter
     */
    updateRateLimit(source) {
        if (source === 'all') return;

        const limit = this.rateLimits.get(source);
        if (limit) {
            limit.requests++;
        }
    }

    /**
     * Get cache key
     */
    getCacheKey(type, ...args) {
        return `${type}_${args.map(arg => JSON.stringify(arg)).join('_')}`;
    }

    /**
     * Get cached data if not expired
     */
    getCachedData(cacheKey) {
        const cached = this.cache.get(cacheKey);

        if (cached && (Date.now() - cached.timestamp) < this.config.cacheTimeout) {
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
    }

    /**
     * Get fallback image results when API fails
     */
    getFallbackImageResults(query) {
        return {
            images: [],
            total: 0,
            page: 1,
            perPage: 20,
            query: query,
            sources: [],
            error: 'External image search temporarily unavailable'
        };
    }

    /**
     * Cancel all pending requests
     */
    cancelAllRequests() {
        this.abortControllers.forEach(controller => {
            controller.abort();
        });
        this.abortControllers.clear();
        this.loadingPromises.clear();
    }

    /**
     * Utility delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Dispatch custom events
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(`externalAPI:${eventName}`, { detail });
        document.dispatchEvent(event);
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('External API cache cleared');
    }

    /**
     * Destroy and cleanup
     */
    destroy() {
        this.cancelAllRequests();
        this.clearCache();
        this.rateLimits.clear();
    }
}

// Global instance
let globalExternalAPIManager = null;

/**
 * Get or create global external API manager
 */
function getExternalAPIManager(config = {}) {
    if (!globalExternalAPIManager) {
        globalExternalAPIManager = new ExternalAPIManager(config);
    }
    return globalExternalAPIManager;
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ExternalAPIManager,
        getExternalAPIManager
    };
} else if (typeof window !== 'undefined') {
    window.ExternalAPIManager = ExternalAPIManager;
    window.getExternalAPIManager = getExternalAPIManager;
}