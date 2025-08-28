// Pricing Calculator JavaScript

class PricingCalculator {
    constructor() {
        this.init();
    }
    
    init() {
        // Initialize pricing calculator functionality
        this.bindEvents();
    }
    
    bindEvents() {
        // Add event listeners for pricing calculator inputs
        const quantityInputs = document.querySelectorAll('.quantity-input');
        quantityInputs.forEach(input => {
            input.addEventListener('change', this.updatePrice.bind(this));
        });
        
        const optionInputs = document.querySelectorAll('.option-input');
        optionInputs.forEach(input => {
            input.addEventListener('change', this.updatePrice.bind(this));
        });
    }
    
    updatePrice(event) {
        // Calculate and update price based on selected options
        const form = event.target.closest('form');
        if (!form) return;
        
        let basePrice = parseFloat(form.dataset.basePrice) || 0;
        let quantity = parseInt(form.querySelector('.quantity-input')?.value) || 1;
        let options = form.querySelectorAll('.option-input:checked');
        
        let totalPrice = basePrice;
        
        // Add option costs
        options.forEach(option => {
            totalPrice += parseFloat(option.dataset.cost) || 0;
        });
        
        // Multiply by quantity
        totalPrice *= quantity;
        
        // Update price display
        const priceDisplay = form.querySelector('.price-display');
        if (priceDisplay) {
            priceDisplay.textContent = `₹${totalPrice.toFixed(2)}`;
        }
    }
}

// Initialize pricing calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new PricingCalculator();
});
