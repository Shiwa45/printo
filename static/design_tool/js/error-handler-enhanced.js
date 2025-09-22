/**
 * Enhanced Error Handler for Design Tool
 * Provides comprehensive error handling and recovery mechanisms
 */

class EnhancedErrorHandler {
    constructor(config = {}) {
        this.config = {
            enableConsoleLogging: true,
            enableUserNotifications: true,
            enableErrorReporting: false,
            maxRetryAttempts: 3,
            retryDelay: 1000,
            ...config
        };

        this.errorLog = [];
        this.errorCounts = new Map();
        this.isInitialized = false;

        this.initializeErrorHandling();
    }

    /**
     * Initialize global error handling
     */
    initializeErrorHandling() {
        if (this.isInitialized) return;

        // Handle uncaught JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleGlobalError({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error,
                stack: event.error?.stack
            });
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleGlobalError({
                type: 'promise',
                message: event.reason?.message || 'Unhandled promise rejection',
                error: event.reason,
                stack: event.reason?.stack
            });
        });

        // Handle canvas-specific errors
        document.addEventListener('canvas:error', (event) => {
            this.handleCanvasError(event.detail);
        });

        // Handle template errors
        document.addEventListener('templateLoader:templateLoadError', (event) => {
            this.handleTemplateError(event.detail);
        });

        // Handle external API errors
        document.addEventListener('externalAPI:imageSearchError', (event) => {
            this.handleAPIError(event.detail);
        });

        this.isInitialized = true;
        console.log('Enhanced error handler initialized');
    }

    /**
     * Handle global JavaScript errors
     */
    handleGlobalError(errorInfo) {
        const errorId = this.generateErrorId(errorInfo);

        // Log the error
        this.logError(errorId, errorInfo);

        // Check if this is a recurring error
        const count = this.errorCounts.get(errorId) || 0;
        this.errorCounts.set(errorId, count + 1);

        // Don't spam notifications for repeated errors
        if (count < 3) {
            this.notifyUser(errorInfo);
        }

        // Try to recover from common errors
        this.attemptErrorRecovery(errorInfo);

        // Report to external service if enabled
        if (this.config.enableErrorReporting) {
            this.reportError(errorInfo);
        }
    }

    /**
     * Handle canvas-specific errors
     */
    handleCanvasError(errorInfo) {
        console.error('Canvas error:', errorInfo);

        const enhancedError = {
            type: 'canvas',
            component: 'canvas',
            ...errorInfo
        };

        this.logError(this.generateErrorId(enhancedError), enhancedError);

        // Try canvas recovery
        this.attemptCanvasRecovery(errorInfo);

        this.notifyUser({
            message: 'Canvas error detected. Attempting to recover...',
            type: 'warning'
        });
    }

    /**
     * Handle template-related errors
     */
    handleTemplateError(errorInfo) {
        console.error('Template error:', errorInfo);

        const enhancedError = {
            type: 'template',
            component: 'template',
            ...errorInfo
        };

        this.logError(this.generateErrorId(enhancedError), enhancedError);

        this.notifyUser({
            message: 'Template loading failed. Please try another template.',
            type: 'error'
        });
    }

    /**
     * Handle external API errors
     */
    handleAPIError(errorInfo) {
        console.error('API error:', errorInfo);

        const enhancedError = {
            type: 'api',
            component: 'external_api',
            ...errorInfo
        };

        this.logError(this.generateErrorId(enhancedError), enhancedError);

        this.notifyUser({
            message: 'Image search temporarily unavailable. Please try again later.',
            type: 'warning'
        });
    }

    /**
     * Attempt error recovery
     */
    attemptErrorRecovery(errorInfo) {
        const message = errorInfo.message?.toLowerCase() || '';

        // Common error recovery patterns
        if (message.includes('canvas') || message.includes('fabric')) {
            this.attemptCanvasRecovery(errorInfo);
        } else if (message.includes('fetch') || message.includes('network')) {
            this.attemptNetworkRecovery(errorInfo);
        } else if (message.includes('undefined') || message.includes('null')) {
            this.attemptNullReferenceRecovery(errorInfo);
        }
    }

    /**
     * Attempt canvas recovery
     */
    attemptCanvasRecovery(errorInfo) {
        try {
            // Try to reinitialize canvas if it's broken
            if (window.canvasManager && !window.canvasManager.isReady()) {
                console.log('Attempting canvas recovery...');

                setTimeout(() => {
                    if (typeof window.initializeCanvasSafely === 'function') {
                        window.initializeCanvasSafely()
                            .then(() => {
                                this.notifyUser({
                                    message: 'Canvas recovered successfully',
                                    type: 'success'
                                });
                            })
                            .catch(err => {
                                console.error('Canvas recovery failed:', err);
                            });
                    }
                }, 1000);
            }

            // Clear any stuck transformers
            if (window.canvas) {
                const transformers = window.canvas.find('Transformer');
                transformers.forEach(tr => tr.destroy());
                window.canvas.renderAll();
            }

        } catch (error) {
            console.error('Canvas recovery attempt failed:', error);
        }
    }

    /**
     * Attempt network recovery
     */
    attemptNetworkRecovery(errorInfo) {
        // Clear caches and retry
        if (window.templateLoader) {
            window.templateLoader.clearCache();
        }

        if (window.globalExternalAPIManager) {
            window.globalExternalAPIManager.clearCache();
        }

        console.log('Network recovery: Cleared caches');
    }

    /**
     * Attempt null reference recovery
     */
    attemptNullReferenceRecovery(errorInfo) {
        // Common null reference fixes
        try {
            // Ensure global variables are defined
            if (typeof window.canvas === 'undefined' && window.canvasManager) {
                window.canvas = window.canvasManager.getCanvas();
            }

            // Ensure DOM elements exist
            this.ensureRequiredDOMElements();

        } catch (error) {
            console.error('Null reference recovery failed:', error);
        }
    }

    /**
     * Ensure required DOM elements exist
     */
    ensureRequiredDOMElements() {
        const requiredElements = [
            { id: 'fabricCanvas', type: 'canvas' },
            { class: 'canvas-wrapper', type: 'div' },
            { id: 'konva-container', type: 'div' }
        ];

        requiredElements.forEach(element => {
            let el;

            if (element.id) {
                el = document.getElementById(element.id);
            } else if (element.class) {
                el = document.querySelector(`.${element.class}`);
            }

            if (!el) {
                console.warn(`Missing required element: ${element.id || element.class}`);
                // Create the missing element
                this.createMissingElement(element);
            }
        });
    }

    /**
     * Create missing DOM element
     */
    createMissingElement(elementConfig) {
        try {
            const element = document.createElement(elementConfig.type);

            if (elementConfig.id) {
                element.id = elementConfig.id;
            }

            if (elementConfig.class) {
                element.className = elementConfig.class;
            }

            // Find suitable parent
            const parent = document.querySelector('#canvas-container') ||
                          document.querySelector('.designer-canvas') ||
                          document.body;

            parent.appendChild(element);

            console.log(`Created missing element: ${elementConfig.id || elementConfig.class}`);

        } catch (error) {
            console.error('Failed to create missing element:', error);
        }
    }

    /**
     * Generate unique error ID
     */
    generateErrorId(errorInfo) {
        const key = `${errorInfo.type}_${errorInfo.message}_${errorInfo.filename || ''}`;
        return btoa(key).substring(0, 16);
    }

    /**
     * Log error to internal log
     */
    logError(errorId, errorInfo) {
        const logEntry = {
            id: errorId,
            timestamp: new Date().toISOString(),
            ...errorInfo
        };

        this.errorLog.push(logEntry);

        // Keep only last 100 errors
        if (this.errorLog.length > 100) {
            this.errorLog.shift();
        }

        if (this.config.enableConsoleLogging) {
            console.group(`🚨 Error ${errorId}`);
            console.error('Message:', errorInfo.message);
            console.error('Type:', errorInfo.type);
            if (errorInfo.stack) {
                console.error('Stack:', errorInfo.stack);
            }
            console.error('Full Info:', errorInfo);
            console.groupEnd();
        }
    }

    /**
     * Notify user of error
     */
    notifyUser(errorInfo) {
        if (!this.config.enableUserNotifications) return;

        const message = this.getUserFriendlyMessage(errorInfo);
        const type = errorInfo.type || 'error';

        // Try to use existing notification system
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            // Fallback notification
            this.showFallbackNotification(message, type);
        }
    }

    /**
     * Get user-friendly error message
     */
    getUserFriendlyMessage(errorInfo) {
        const message = errorInfo.message?.toLowerCase() || '';

        if (message.includes('network') || message.includes('fetch')) {
            return 'Network connection issue. Please check your internet connection.';
        }

        if (message.includes('canvas') || message.includes('fabric')) {
            return 'Design canvas encountered an issue. Attempting to recover...';
        }

        if (message.includes('template')) {
            return 'Template loading failed. Please try a different template.';
        }

        if (message.includes('image') || message.includes('pixabay')) {
            return 'Image search temporarily unavailable. Please try again.';
        }

        if (errorInfo.type === 'javascript') {
            return 'A technical issue occurred. The application is attempting to recover.';
        }

        return errorInfo.message || 'An unexpected error occurred.';
    }

    /**
     * Show fallback notification
     */
    showFallbackNotification(message, type) {
        // Create or update notification element
        let notification = document.getElementById('error-notification');

        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'error-notification';
            notification.style.cssText = `
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
                display: none;
            `;
            document.body.appendChild(notification);
        }

        // Set style based on type
        const styles = {
            error: 'background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;',
            warning: 'background: #fff3cd; color: #856404; border: 1px solid #ffeaa7;',
            success: 'background: #d4edda; color: #155724; border: 1px solid #c3e6cb;',
            info: 'background: #cce7ff; color: #004085; border: 1px solid #b3d7ff;'
        };

        notification.style.cssText += styles[type] || styles.info;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.style.display='none'"
                        style="background: none; border: none; font-size: 18px; cursor: pointer;">×</button>
            </div>
        `;

        notification.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (notification) {
                notification.style.display = 'none';
            }
        }, 5000);
    }

    /**
     * Report error to external service
     */
    reportError(errorInfo) {
        // Implementation would depend on your error reporting service
        // e.g., Sentry, LogRocket, etc.
        console.log('Error reporting not implemented');
    }

    /**
     * Get error statistics
     */
    getErrorStats() {
        const stats = {
            totalErrors: this.errorLog.length,
            recentErrors: this.errorLog.filter(e =>
                Date.now() - new Date(e.timestamp).getTime() < 60000
            ).length,
            errorTypes: {},
            topErrors: []
        };

        // Count error types
        this.errorLog.forEach(error => {
            stats.errorTypes[error.type] = (stats.errorTypes[error.type] || 0) + 1;
        });

        // Get top recurring errors
        const errorFrequency = Array.from(this.errorCounts.entries())
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5);

        stats.topErrors = errorFrequency;

        return stats;
    }

    /**
     * Clear error log
     */
    clearErrorLog() {
        this.errorLog = [];
        this.errorCounts.clear();
        console.log('Error log cleared');
    }

    /**
     * Safely execute function with error handling
     */
    safeExecute(fn, context = null, ...args) {
        try {
            if (typeof fn === 'function') {
                return fn.apply(context, args);
            } else {
                throw new Error('Provided argument is not a function');
            }
        } catch (error) {
            this.handleGlobalError({
                type: 'safe_execute',
                message: `Safe execution failed: ${error.message}`,
                error: error,
                function: fn.name || 'anonymous',
                stack: error.stack
            });
            return null;
        }
    }

    /**
     * Create safe wrapper for async functions
     */
    safeAsync(asyncFn, context = null) {
        return async (...args) => {
            try {
                return await asyncFn.apply(context, args);
            } catch (error) {
                this.handleGlobalError({
                    type: 'async_error',
                    message: `Async function failed: ${error.message}`,
                    error: error,
                    function: asyncFn.name || 'anonymous',
                    stack: error.stack
                });
                throw error;
            }
        };
    }

    /**
     * Destroy error handler
     */
    destroy() {
        this.clearErrorLog();
        this.isInitialized = false;
    }
}

// Global error handler instance
let globalErrorHandler = null;

/**
 * Get or create global error handler
 */
function getErrorHandler(config = {}) {
    if (!globalErrorHandler) {
        globalErrorHandler = new EnhancedErrorHandler(config);
    }
    return globalErrorHandler;
}

/**
 * Safe function execution utility
 */
function safeCall(fn, context = null, ...args) {
    const errorHandler = getErrorHandler();
    return errorHandler.safeExecute(fn, context, ...args);
}

/**
 * Safe async function execution utility
 */
function safeAsync(asyncFn, context = null) {
    const errorHandler = getErrorHandler();
    return errorHandler.safeAsync(asyncFn, context);
}

// Initialize error handler when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => getErrorHandler());
} else {
    getErrorHandler();
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EnhancedErrorHandler,
        getErrorHandler,
        safeCall,
        safeAsync
    };
} else if (typeof window !== 'undefined') {
    window.EnhancedErrorHandler = EnhancedErrorHandler;
    window.getErrorHandler = getErrorHandler;
    window.safeCall = safeCall;
    window.safeAsync = safeAsync;
}