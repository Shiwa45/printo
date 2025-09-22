/**
 * Enhanced Utilities for Design Tool
 * Provides robust utility functions with error handling
 */

class EnhancedUtilities {
    constructor() {
        this.cache = new Map();
        this.loadingStates = new Map();
    }

    /**
     * Safe DOM manipulation utilities
     */
    dom = {
        /**
         * Safely get element by ID
         */
        getElementById: (id) => {
            try {
                return document.getElementById(id);
            } catch (error) {
                console.warn(`Failed to get element by ID: ${id}`, error);
                return null;
            }
        },

        /**
         * Safely get elements by selector
         */
        querySelector: (selector) => {
            try {
                return document.querySelector(selector);
            } catch (error) {
                console.warn(`Failed to query selector: ${selector}`, error);
                return null;
            }
        },

        /**
         * Safely get all elements by selector
         */
        querySelectorAll: (selector) => {
            try {
                return document.querySelectorAll(selector);
            } catch (error) {
                console.warn(`Failed to query selector all: ${selector}`, error);
                return [];
            }
        },

        /**
         * Safely add event listener
         */
        addEventListener: (element, event, handler, options = {}) => {
            try {
                if (element && typeof element.addEventListener === 'function') {
                    element.addEventListener(event, handler, options);
                    return true;
                }
                return false;
            } catch (error) {
                console.warn(`Failed to add event listener: ${event}`, error);
                return false;
            }
        },

        /**
         * Safely remove event listener
         */
        removeEventListener: (element, event, handler, options = {}) => {
            try {
                if (element && typeof element.removeEventListener === 'function') {
                    element.removeEventListener(event, handler, options);
                    return true;
                }
                return false;
            } catch (error) {
                console.warn(`Failed to remove event listener: ${event}`, error);
                return false;
            }
        },

        /**
         * Wait for element to exist in DOM
         */
        waitForElement: (selector, timeout = 5000) => {
            return new Promise((resolve, reject) => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                    return;
                }

                const observer = new MutationObserver(() => {
                    const element = document.querySelector(selector);
                    if (element) {
                        observer.disconnect();
                        clearTimeout(timer);
                        resolve(element);
                    }
                });

                const timer = setTimeout(() => {
                    observer.disconnect();
                    reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                }, timeout);

                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            });
        },

        /**
         * Create element safely
         */
        createElement: (tagName, attributes = {}, children = []) => {
            try {
                const element = document.createElement(tagName);

                // Set attributes
                Object.entries(attributes).forEach(([key, value]) => {
                    if (key === 'className') {
                        element.className = value;
                    } else if (key === 'innerHTML') {
                        element.innerHTML = value;
                    } else if (key === 'textContent') {
                        element.textContent = value;
                    } else {
                        element.setAttribute(key, value);
                    }
                });

                // Add children
                children.forEach(child => {
                    if (typeof child === 'string') {
                        element.appendChild(document.createTextNode(child));
                    } else if (child instanceof Node) {
                        element.appendChild(child);
                    }
                });

                return element;
            } catch (error) {
                console.error('Failed to create element:', error);
                return null;
            }
        }
    };

    /**
     * Safe API utilities
     */
    api = {
        /**
         * Safe fetch with timeout and retries
         */
        fetch: async (url, options = {}) => {
            const config = {
                timeout: 10000,
                retries: 3,
                retryDelay: 1000,
                ...options
            };

            let lastError;

            for (let attempt = 1; attempt <= config.retries; attempt++) {
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), config.timeout);

                    const response = await fetch(url, {
                        ...config,
                        signal: controller.signal
                    });

                    clearTimeout(timeoutId);

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    return response;

                } catch (error) {
                    lastError = error;
                    console.warn(`Fetch attempt ${attempt} failed:`, error);

                    if (attempt < config.retries && error.name !== 'AbortError') {
                        await this.delay(config.retryDelay * attempt);
                    }
                }
            }

            throw lastError;
        },

        /**
         * Safe JSON fetch
         */
        fetchJSON: async (url, options = {}) => {
            const response = await this.api.fetch(url, options);
            return response.json();
        },

        /**
         * Safe form data submission
         */
        submitForm: async (url, formData, options = {}) => {
            return this.api.fetch(url, {
                method: 'POST',
                body: formData,
                ...options
            });
        }
    };

    /**
     * Canvas utilities
     */
    canvas = {
        /**
         * Safely get canvas instance
         */
        getCanvas: () => {
            try {
                if (window.canvas && typeof window.canvas.getObjects === 'function') {
                    return window.canvas;
                }

                if (window.canvasManager && window.canvasManager.getCanvas) {
                    return window.canvasManager.getCanvas();
                }

                return null;
            } catch (error) {
                console.warn('Failed to get canvas:', error);
                return null;
            }
        },

        /**
         * Safely add object to canvas
         */
        addObject: (object) => {
            try {
                const canvas = this.canvas.getCanvas();
                if (canvas && object) {
                    canvas.add(object);
                    canvas.renderAll();
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Failed to add object to canvas:', error);
                return false;
            }
        },

        /**
         * Safely remove object from canvas
         */
        removeObject: (object) => {
            try {
                const canvas = this.canvas.getCanvas();
                if (canvas && object) {
                    canvas.remove(object);
                    canvas.renderAll();
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Failed to remove object from canvas:', error);
                return false;
            }
        },

        /**
         * Get active object safely
         */
        getActiveObject: () => {
            try {
                const canvas = this.canvas.getCanvas();
                return canvas ? canvas.getActiveObject() : null;
            } catch (error) {
                console.warn('Failed to get active object:', error);
                return null;
            }
        },

        /**
         * Clear selection safely
         */
        clearSelection: () => {
            try {
                const canvas = this.canvas.getCanvas();
                if (canvas) {
                    canvas.discardActiveObject();
                    canvas.renderAll();
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Failed to clear selection:', error);
                return false;
            }
        }
    };

    /**
     * Loading state management
     */
    loading = {
        /**
         * Show loading state
         */
        show: (key, message = 'Loading...') => {
            try {
                this.loadingStates.set(key, true);

                let loader = document.getElementById(`loader-${key}`);
                if (!loader) {
                    loader = this.dom.createElement('div', {
                        id: `loader-${key}`,
                        className: 'enhanced-loader',
                        innerHTML: `
                            <div class="loader-content">
                                <div class="spinner"></div>
                                <div class="loader-message">${message}</div>
                            </div>
                        `
                    });

                    // Add styles if not present
                    if (!document.getElementById('enhanced-loader-styles')) {
                        const styles = this.dom.createElement('style', {
                            id: 'enhanced-loader-styles',
                            textContent: `
                                .enhanced-loader {
                                    position: fixed;
                                    top: 0;
                                    left: 0;
                                    right: 0;
                                    bottom: 0;
                                    background: rgba(255, 255, 255, 0.9);
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    z-index: 9999;
                                    font-family: Arial, sans-serif;
                                }
                                .loader-content {
                                    text-align: center;
                                }
                                .spinner {
                                    width: 40px;
                                    height: 40px;
                                    border: 4px solid #f3f3f3;
                                    border-top: 4px solid #3498db;
                                    border-radius: 50%;
                                    animation: spin 1s linear infinite;
                                    margin: 0 auto 10px;
                                }
                                @keyframes spin {
                                    0% { transform: rotate(0deg); }
                                    100% { transform: rotate(360deg); }
                                }
                                .loader-message {
                                    color: #333;
                                    font-size: 14px;
                                }
                            `
                        });
                        document.head.appendChild(styles);
                    }

                    document.body.appendChild(loader);
                }

                return true;
            } catch (error) {
                console.error('Failed to show loading state:', error);
                return false;
            }
        },

        /**
         * Hide loading state
         */
        hide: (key) => {
            try {
                this.loadingStates.delete(key);
                const loader = document.getElementById(`loader-${key}`);
                if (loader) {
                    loader.remove();
                }
                return true;
            } catch (error) {
                console.error('Failed to hide loading state:', error);
                return false;
            }
        },

        /**
         * Check if loading
         */
        isLoading: (key) => {
            return this.loadingStates.has(key);
        }
    };

    /**
     * Notification utilities
     */
    notify = {
        /**
         * Show notification
         */
        show: (message, type = 'info', duration = 5000) => {
            try {
                // Try existing notification system first
                if (typeof window.showNotification === 'function') {
                    return window.showNotification(message, type);
                }

                // Fallback notification
                const notification = this.dom.createElement('div', {
                    className: `notification notification-${type}`,
                    innerHTML: `
                        <div class="notification-content">
                            <span class="notification-message">${message}</span>
                            <button class="notification-close">&times;</button>
                        </div>
                    `
                });

                // Add styles if not present
                if (!document.getElementById('notification-styles')) {
                    const styles = this.dom.createElement('style', {
                        id: 'notification-styles',
                        textContent: `
                            .notification {
                                position: fixed;
                                top: 20px;
                                right: 20px;
                                max-width: 400px;
                                padding: 15px;
                                border-radius: 5px;
                                z-index: 10000;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                                font-family: Arial, sans-serif;
                                font-size: 14px;
                                opacity: 0;
                                transform: translateX(100%);
                                transition: all 0.3s ease;
                            }
                            .notification.show {
                                opacity: 1;
                                transform: translateX(0);
                            }
                            .notification-info { background: #cce7ff; color: #004085; border-left: 4px solid #007bff; }
                            .notification-success { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
                            .notification-warning { background: #fff3cd; color: #856404; border-left: 4px solid #ffc107; }
                            .notification-error { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
                            .notification-content {
                                display: flex;
                                align-items: center;
                                justify-content: space-between;
                            }
                            .notification-close {
                                background: none;
                                border: none;
                                font-size: 18px;
                                cursor: pointer;
                                margin-left: 10px;
                            }
                        `
                    });
                    document.head.appendChild(styles);
                }

                document.body.appendChild(notification);

                // Show animation
                setTimeout(() => notification.classList.add('show'), 10);

                // Close button
                const closeBtn = notification.querySelector('.notification-close');
                closeBtn.addEventListener('click', () => {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                });

                // Auto-hide
                if (duration > 0) {
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.classList.remove('show');
                            setTimeout(() => notification.remove(), 300);
                        }
                    }, duration);
                }

                return true;
            } catch (error) {
                console.error('Failed to show notification:', error);
                return false;
            }
        },

        success: (message, duration) => this.notify.show(message, 'success', duration),
        error: (message, duration) => this.notify.show(message, 'error', duration),
        warning: (message, duration) => this.notify.show(message, 'warning', duration),
        info: (message, duration) => this.notify.show(message, 'info', duration)
    };

    /**
     * Validation utilities
     */
    validate = {
        /**
         * Check if value is not null or undefined
         */
        exists: (value) => value !== null && value !== undefined,

        /**
         * Check if string is not empty
         */
        notEmpty: (str) => typeof str === 'string' && str.trim().length > 0,

        /**
         * Check if value is a valid number
         */
        isNumber: (value) => typeof value === 'number' && !isNaN(value),

        /**
         * Check if value is a valid URL
         */
        isURL: (str) => {
            try {
                new URL(str);
                return true;
            } catch {
                return false;
            }
        },

        /**
         * Check if value is a valid email
         */
        isEmail: (str) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(str);
        }
    };

    /**
     * Utility delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Debounce function
     */
    debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    /**
     * Throttle function
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Generate unique ID
     */
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Deep clone object
     */
    deepClone(obj) {
        try {
            return JSON.parse(JSON.stringify(obj));
        } catch (error) {
            console.warn('Failed to deep clone object:', error);
            return obj;
        }
    }

    /**
     * Clear all caches
     */
    clearCache() {
        this.cache.clear();
        console.log('Utilities cache cleared');
    }

    /**
     * Destroy utilities and cleanup
     */
    destroy() {
        this.clearCache();
        this.loadingStates.clear();
    }
}

// Global utilities instance
let globalUtilities = null;

/**
 * Get or create global utilities instance
 */
function getUtilities() {
    if (!globalUtilities) {
        globalUtilities = new EnhancedUtilities();
    }
    return globalUtilities;
}

// Export utilities for easy access
const utils = getUtilities();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EnhancedUtilities,
        getUtilities,
        utils
    };
} else if (typeof window !== 'undefined') {
    window.EnhancedUtilities = EnhancedUtilities;
    window.getUtilities = getUtilities;
    window.utils = utils;
}