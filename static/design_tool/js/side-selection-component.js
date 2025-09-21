/**
 * Side Selection Component for Front/Back Design Tool
 * Handles user selection of design sides (front only, back only, both sides)
 */

class SideSelectionComponent {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.options = {
            productId: null,
            onSelectionChange: null,
            defaultSelection: 'single',
            ...options
        };
        
        this.availableOptions = [];
        this.selectedOption = this.options.defaultSelection;
        this.productData = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Fetch product design options
            await this.loadProductOptions();
            
            // Render the component
            this.render();
            
            // Bind events
            this.bindEvents();
            
        } catch (error) {
            console.error('Failed to initialize SideSelectionComponent:', error);
            this.renderError('Failed to load design options');
        }
    }
    
    async loadProductOptions() {
        if (!this.options.productId) {
            throw new Error('Product ID is required');
        }
        
        const response = await fetch(`/design-tool/api/product/${this.options.productId}/design-options/`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Failed to load design options');
        }
        
        this.availableOptions = data.design_options;
        this.selectedOption = data.default_option;
        this.productData = {
            frontBackEnabled: data.front_back_enabled,
            hasFrontTemplates: data.has_front_templates,
            hasBackTemplates: data.has_back_templates
        };
    }
    
    render() {
        if (!this.container) {
            console.error('Container not found for SideSelectionComponent');
            return;
        }
        
        // Don't show component if only single option is available
        if (this.availableOptions.length <= 1 && this.availableOptions[0] === 'single') {
            this.container.style.display = 'none';
            return;
        }
        
        const html = `
            <div class="side-selection-component">
                <div class="side-selection-header">
                    <h3 class="side-selection-title">
                        <i class="fas fa-layer-group"></i>
                        Choose Design Sides
                    </h3>
                    <p class="side-selection-description">
                        Select which sides you want to design for this product
                    </p>
                </div>
                
                <div class="side-selection-options">
                    ${this.renderOptions()}
                </div>
                
                <div class="side-selection-info">
                    ${this.renderSelectionInfo()}
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
        this.container.style.display = 'block';
    }
    
    renderOptions() {
        const optionLabels = {
            'single': {
                label: 'Single Side',
                description: 'Design one side only',
                icon: 'fas fa-square'
            },
            'front_only': {
                label: 'Front Only',
                description: 'Design the front side',
                icon: 'fas fa-square-full'
            },
            'back_only': {
                label: 'Back Only', 
                description: 'Design the back side',
                icon: 'fas fa-square'
            },
            'both_sides': {
                label: 'Both Sides',
                description: 'Design front and back',
                icon: 'fas fa-clone'
            }
        };
        
        return this.availableOptions.map(option => {
            const config = optionLabels[option];
            const isSelected = option === this.selectedOption;
            const isDisabled = !this.isOptionAvailable(option);
            
            return `
                <div class="side-option ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}" 
                     data-option="${option}">
                    <div class="side-option-icon">
                        <i class="${config.icon}"></i>
                    </div>
                    <div class="side-option-content">
                        <div class="side-option-label">${config.label}</div>
                        <div class="side-option-description">${config.description}</div>
                        ${isDisabled ? '<div class="side-option-warning">No templates available</div>' : ''}
                    </div>
                    <div class="side-option-radio">
                        <input type="radio" 
                               name="design-side" 
                               value="${option}" 
                               ${isSelected ? 'checked' : ''}
                               ${isDisabled ? 'disabled' : ''}>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    renderSelectionInfo() {
        const infoMessages = {
            'single': 'You can design one side of your product.',
            'front_only': 'You will design only the front side of your product.',
            'back_only': 'You will design only the back side of your product.',
            'both_sides': 'You can design both the front and back sides. Use the navigation tabs to switch between sides.'
        };
        
        const message = infoMessages[this.selectedOption] || '';
        
        return `
            <div class="selection-info-message">
                <i class="fas fa-info-circle"></i>
                <span>${message}</span>
            </div>
        `;
    }
    
    renderError(message) {
        this.container.innerHTML = `
            <div class="side-selection-error">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;
    }
    
    isOptionAvailable(option) {
        switch (option) {
            case 'single':
                return true; // Always available as fallback
            case 'front_only':
                return this.productData?.hasFrontTemplates || false;
            case 'back_only':
                return this.productData?.hasBackTemplates || false;
            case 'both_sides':
                return (this.productData?.hasFrontTemplates && this.productData?.hasBackTemplates) || false;
            default:
                return false;
        }
    }
    
    bindEvents() {
        // Handle option selection
        this.container.addEventListener('click', (e) => {
            const optionElement = e.target.closest('.side-option');
            if (optionElement && !optionElement.classList.contains('disabled')) {
                const option = optionElement.dataset.option;
                this.selectOption(option);
            }
        });
        
        // Handle radio button changes
        this.container.addEventListener('change', (e) => {
            if (e.target.name === 'design-side') {
                this.selectOption(e.target.value);
            }
        });
    }
    
    selectOption(option) {
        if (!this.availableOptions.includes(option) || !this.isOptionAvailable(option)) {
            return;
        }
        
        const previousOption = this.selectedOption;
        this.selectedOption = option;
        
        // Update UI
        this.updateSelection();
        
        // Update info message
        this.updateSelectionInfo();
        
        // Trigger callback
        if (this.options.onSelectionChange && typeof this.options.onSelectionChange === 'function') {
            this.options.onSelectionChange(option, previousOption);
        }
        
        // Dispatch custom event
        this.container.dispatchEvent(new CustomEvent('sideSelectionChange', {
            detail: {
                selectedOption: option,
                previousOption: previousOption,
                availableOptions: this.availableOptions
            }
        }));
    }
    
    updateSelection() {
        // Update radio buttons
        const radios = this.container.querySelectorAll('input[name="design-side"]');
        radios.forEach(radio => {
            radio.checked = radio.value === this.selectedOption;
        });
        
        // Update visual selection
        const options = this.container.querySelectorAll('.side-option');
        options.forEach(option => {
            const isSelected = option.dataset.option === this.selectedOption;
            option.classList.toggle('selected', isSelected);
        });
    }
    
    updateSelectionInfo() {
        const infoContainer = this.container.querySelector('.selection-info-message span');
        if (infoContainer) {
            const infoMessages = {
                'single': 'You can design one side of your product.',
                'front_only': 'You will design only the front side of your product.',
                'back_only': 'You will design only the back side of your product.',
                'both_sides': 'You can design both the front and back sides. Use the navigation tabs to switch between sides.'
            };
            
            infoContainer.textContent = infoMessages[this.selectedOption] || '';
        }
    }
    
    // Public methods
    getSelectedOption() {
        return this.selectedOption;
    }
    
    setSelectedOption(option) {
        this.selectOption(option);
    }
    
    getAvailableOptions() {
        return [...this.availableOptions];
    }
    
    isEnabled() {
        return this.productData?.frontBackEnabled || false;
    }
    
    refresh() {
        this.init();
    }
    
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
            this.container.style.display = 'none';
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SideSelectionComponent;
} else if (typeof window !== 'undefined') {
    window.SideSelectionComponent = SideSelectionComponent;
}