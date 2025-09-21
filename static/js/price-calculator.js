/**
 * Real-time Price Calculator Component
 * Handles dynamic price calculations for products with specifications
 */
class PriceCalculator {
    constructor(productId, options = {}) {
        this.productId = productId;
        this.subcategoryId = null;
        this.specifications = {};
        this.options = {
            container: options.container || '#price-calculator',
            displayContainer: options.displayContainer || '#price-display',
            loadingClass: options.loadingClass || 'calculating',
            errorClass: options.errorClass || 'error',
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadInitialPricing();
    }
    
    bindEvents() {
        const container = document.querySelector(this.options.container);
        if (!container) return;
        
        // Bind specification selectors
        container.querySelectorAll('.spec-selector').forEach(selector => {
            selector.addEventListener('change', (e) => {
                this.updateSpecification(e.target.name, e.target.value);
                this.calculatePrice();
            });
        });
        
        // Bind subcategory selector
        const subcategorySelector = container.querySelector('#subcategory-selector');
        if (subcategorySelector) {
            subcategorySelector.addEventListener('change', (e) => {
                this.subcategoryId = e.target.value || null;
                this.calculatePrice();
            });
        }
        
        // Bind quantity input
        const quantityInput = container.querySelector('#quantity-input');
        if (quantityInput) {
            quantityInput.addEventListener('input', (e) => {
                const quantity = parseInt(e.target.value) || 1;
                this.updateSpecification('quantity', quantity);
                this.debounceCalculatePrice();
            });
        }
        
        // Bind customization checkboxes
        container.querySelectorAll('.customization-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateCustomization(e.target.name, e.target.checked);
                this.calculatePrice();
            });
        });
    }
    
    updateSpecification(key, value) {
        this.specifications[key] = value;
        this.updateUI();
    }
    
    updateCustomization(key, value) {
        if (!this.specifications.customizations) {
            this.specifications.customizations = {};
        }
        this.specifications.customizations[key] = value;
    }
    
    debounceCalculatePrice() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.calculatePrice();
        }, 500);
    }
    
    async calculatePrice() {
        const displayContainer = document.querySelector(this.options.displayContainer);
        if (!displayContainer) return;
        
        // Show loading state
        displayContainer.classList.add(this.options.loadingClass);
        displayContainer.classList.remove(this.options.errorClass);
        
        try {
            const requestData = {
                product_id: this.productId,
                subcategory_id: this.subcategoryId,
                product_type: this.getProductType(),
                ...this.specifications
            };
            
            const response = await fetch('/api/calculate-price/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.errors && data.errors.length > 0) {
                this.displayError(data.errors.join(', '));
            } else {
                this.displayPricing(data);
            }
        } catch (error) {
            console.error('Price calculation failed:', error);
            this.displayError('Unable to calculate price. Please try again.');
        } finally {
            displayContainer.classList.remove(this.options.loadingClass);
        }
    }
    
    displayPricing(pricing) {
        const displayContainer = document.querySelector(this.options.displayContainer);
        if (!displayContainer) return;
        
        displayContainer.innerHTML = `
            <div class="pricing-breakdown">
                <div class="breakdown-items">
                    ${pricing.breakdown.map(item => `
                        <div class="price-line ${item.cost < 0 ? 'discount' : ''}">
                            <span class="item-description">${item.item}</span>
                            <span class="item-cost">₹${Math.abs(parseFloat(item.cost)).toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                
                ${pricing.discount > 0 ? `
                    <div class="price-line subtotal">
                        <span>Subtotal:</span>
                        <span>₹${parseFloat(pricing.subtotal).toFixed(2)}</span>
                    </div>
                    <div class="price-line discount">
                        <span>Discount:</span>
                        <span>-₹${parseFloat(pricing.discount).toFixed(2)}</span>
                    </div>
                ` : ''}
                
                <div class="price-line total">
                    <span>Total:</span>
                    <span>₹${parseFloat(pricing.total).toFixed(2)}</span>
                </div>
                
                <div class="price-line per-unit">
                    <span>Per Unit:</span>
                    <span>₹${parseFloat(pricing.per_unit).toFixed(2)}</span>
                </div>
            </div>
            
            <div class="pricing-actions">
                <button class="btn btn-primary add-to-cart-btn" onclick="addToCart()">
                    Add to Cart
                </button>
                <button class="btn btn-secondary get-quote-btn" onclick="getQuote()">
                    Get Quote
                </button>
            </div>
        `;
        
        // Update any price displays elsewhere on the page
        this.updatePriceDisplays(pricing.total);
    }
    
    displayError(message) {
        const displayContainer = document.querySelector(this.options.displayContainer);
        if (!displayContainer) return;
        
        displayContainer.classList.add(this.options.errorClass);
        displayContainer.innerHTML = `
            <div class="pricing-error">
                <div class="error-icon">⚠️</div>
                <div class="error-message">${message}</div>
                <div class="error-actions">
                    <button class="btn btn-outline" onclick="location.href='/contact/'">
                        Contact for Quote
                    </button>
                </div>
            </div>
        `;
    }
    
    updatePriceDisplays(totalPrice) {
        // Update any other price displays on the page
        document.querySelectorAll('.dynamic-price').forEach(element => {
            element.textContent = `₹${parseFloat(totalPrice).toFixed(2)}`;
        });
    }
    
    updateUI() {
        // Update any UI elements based on current specifications
        const summaryContainer = document.querySelector('#specification-summary');
        if (summaryContainer && Object.keys(this.specifications).length > 0) {
            const summaryHTML = Object.entries(this.specifications)
                .filter(([key, value]) => key !== 'customizations' && value)
                .map(([key, value]) => `
                    <span class="spec-tag">
                        ${this.formatSpecificationLabel(key)}: ${value}
                    </span>
                `).join('');
            
            summaryContainer.innerHTML = summaryHTML;
        }
    }
    
    formatSpecificationLabel(key) {
        const labels = {
            'size': 'Size',
            'paper_type': 'Paper',
            'print_type': 'Print Type',
            'binding_type': 'Binding',
            'pages': 'Pages',
            'quantity': 'Quantity',
            'finish': 'Finish'
        };
        return labels[key] || key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    getProductType() {
        // Determine product type based on specifications or product data
        if (this.specifications.pages || this.specifications.binding_type) {
            return 'book';
        }
        return 'standard';
    }
    
    loadInitialPricing() {
        // Set default specifications and calculate initial price
        const container = document.querySelector(this.options.container);
        if (!container) return;
        
        // Get default values from form elements
        container.querySelectorAll('.spec-selector').forEach(selector => {
            if (selector.value) {
                this.updateSpecification(selector.name, selector.value);
            }
        });
        
        // Set default quantity
        const quantityInput = container.querySelector('#quantity-input');
        if (quantityInput && quantityInput.value) {
            this.updateSpecification('quantity', parseInt(quantityInput.value));
        }
        
        // Calculate initial price
        if (Object.keys(this.specifications).length > 0) {
            this.calculatePrice();
        }
    }
    
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    // Public methods for external use
    setSpecification(key, value) {
        this.updateSpecification(key, value);
        this.calculatePrice();
    }
    
    setSubcategory(subcategoryId) {
        this.subcategoryId = subcategoryId;
        this.calculatePrice();
    }
    
    getCurrentPricing() {
        return this.lastPricing;
    }
    
    reset() {
        this.specifications = {};
        this.subcategoryId = null;
        this.updateUI();
        this.loadInitialPricing();
    }
}

// Global functions for button actions
function addToCart() {
    if (window.priceCalculator) {
        const pricing = window.priceCalculator.getCurrentPricing();
        if (pricing) {
            // Implementation for adding to cart
            console.log('Adding to cart:', pricing);
        }
    }
}

function getQuote() {
    if (window.priceCalculator) {
        const specifications = window.priceCalculator.specifications;
        // Redirect to quote page with specifications
        const params = new URLSearchParams(specifications);
        window.location.href = `/quote/?${params.toString()}`;
    }
}

// Auto-initialize if product ID is available
document.addEventListener('DOMContentLoaded', function() {
    const productId = document.querySelector('[data-product-id]')?.dataset.productId;
    if (productId) {
        window.priceCalculator = new PriceCalculator(productId);
    }
});