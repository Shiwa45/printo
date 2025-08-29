// Advanced Pricing Calculator for Drishthi Printing Services
class PricingCalculator {
    constructor() {
        this.rates = {
            // Book printing rates based on your Excel data
            book: {
                'A4': {
                    'bw_standard': {'75gsm': 1.1, '100gsm': 1.35, '100gsm_art': 1.8, '130gsm_art': 2.1},
                    'bw_premium': {'75gsm': 1.3, '100gsm': 1.55, '100gsm_art': 2.0, '130gsm_art': 2.3},
                    'color_standard': {'75gsm': 2.5, '100gsm': 2.7, '100gsm_art': 2.9, '130gsm_art': 3.15},
                    'color_premium': {'75gsm': 2.7, '100gsm': 2.9, '100gsm_art': 3.1, '130gsm_art': 3.3}
                },
                'Letter': {
                    'bw_standard': {'75gsm': 1.1, '100gsm': 1.35, '100gsm_art': 1.8, '130gsm_art': 2.1},
                    'bw_premium': {'75gsm': 1.3, '100gsm': 1.55, '100gsm_art': 2.0, '130gsm_art': 2.3},
                    'color_standard': {'75gsm': 2.5, '100gsm': 2.7, '100gsm_art': 2.9, '130gsm_art': 3.15},
                    'color_premium': {'75gsm': 2.7, '100gsm': 2.9, '100gsm_art': 3.1, '130gsm_art': 3.3}
                },
                'Executive': {
                    'bw_standard': {'75gsm': 1.1, '100gsm': 1.35, '100gsm_art': 1.8, '130gsm_art': 2.1},
                    'bw_premium': {'75gsm': 1.3, '100gsm': 1.55, '100gsm_art': 2.0, '130gsm_art': 2.3},
                    'color_standard': {'75gsm': 2.5, '100gsm': 2.7, '100gsm_art': 2.9, '130gsm_art': 3.15},
                    'color_premium': {'75gsm': 2.7, '100gsm': 2.9, '100gsm_art': 3.1, '130gsm_art': 3.3}
                },
                'A5': {
                    'bw_standard': {'75gsm': 0.6, '100gsm': 0.75, '100gsm_art': 0.9, '130gsm_art': 1.1},
                    'bw_premium': {'75gsm': 0.75, '100gsm': 0.9, '100gsm_art': 1.1, '130gsm_art': 1.25},
                    'color_standard': {'75gsm': 1.25, '100gsm': 1.35, '100gsm_art': 1.45, '130gsm_art': 1.58},
                    'color_premium': {'75gsm': 1.35, '100gsm': 1.45, '100gsm_art': 1.6, '130gsm_art': 1.75}
                }
            },
            // Binding costs
            binding: {
                'paperback_perfect': 40,
                'spiral_binding': 40, 
                'hardcover': 150,
                'saddle_stitch': 25,
                'wire_o_bound': 60
            },
            // Shipping rates
            shipping: {
                'A4': {'bw': 0.1, 'color': 0.13},
                'Letter': {'bw': 0.1, 'color': 0.13},
                'Executive': {'bw': 0.1, 'color': 0.13},
                'A5': {'bw': 0.05, 'color': 0.07}
            },
            // Standard product rates
            standard: {
                business_cards: {
                    base_per_100: 299,
                    paper_costs: {'300gsm': 0, '350gsm': 50, '400gsm': 100},
                    finish_costs: {'matte': 0, 'gloss': 0, 'spot_uv': 150, 'foiling': 300}
                },
                letterhead: {
                    base_per_100: 199,
                    paper_costs: {'80gsm': 0, '100gsm': 25, '120gsm': 50}
                },
                brochures: {
                    base_per_100: 599,
                    folding_costs: {'bi': 0, 'tri': 25, 'z': 25, 'gate': 50, 'accordion': 75}
                },
                flyers: {
                    base_per_100: 199
                }
            }
        };
        
        // Quantity discount tiers based on your Excel
        this.quantityDiscounts = [
            {min: 25, discount: 0.02, label: '2%'},
            {min: 50, discount: 0.04, label: '4%'},
            {min: 75, discount: 0.06, label: '6%'},
            {min: 100, discount: 0.08, label: '8%'},
            {min: 150, discount: 0.10, label: '10%'},
            {min: 200, discount: 0.12, label: '12%'},
            {min: 250, discount: 0.14, label: '14%'},
            {min: 300, discount: 0.16, label: '16%'}
        ];
        
        this.designRates = {
            cover_design: 1500,
            isbn_allocation: 1500,
            design_support: {'A4': 50, 'Letter': 50, 'Executive': 50, 'A5': 40}
        };
    }
    
    calculateBookPrice(options) {
        const {
            size = 'A4',
            paperType = '75gsm', 
            printType = 'bw_standard',
            pages = 100,
            quantity = 50,
            bindingType = 'paperback_perfect',
            includeCoverDesign = false,
            includeIsbn = false,
            includeDesignSupport = false
        } = options;
        
        const result = {
            breakdown: [],
            subtotal: 0,
            discount: 0,
            total: 0,
            perBook: 0,
            errors: []
        };
        
        // Validate inputs
        if (!this.rates.book[size]) {
            result.errors.push(`Invalid size: ${size}`);
            return result;
        }
        
        if (!this.rates.book[size][printType]) {
            result.errors.push(`Invalid print type: ${printType}`);
            return result;
        }
        
        if (!this.rates.book[size][printType][paperType]) {
            result.errors.push(`Invalid paper type: ${paperType}`);
            return result;
        }
        
        // Calculate printing cost
        const pageRate = this.rates.book[size][printType][paperType];
        const printingCost = pages * pageRate * quantity;
        result.breakdown.push({
            item: `Printing (${pages} pages × ${quantity} books × ₹${pageRate})`,
            cost: printingCost
        });
        
        // Calculate binding cost
        const bindingCost = this.rates.binding[bindingType] * quantity;
        result.breakdown.push({
            item: `${this.getBindingName(bindingType)} (${quantity} books × ₹${this.rates.binding[bindingType]})`,
            cost: bindingCost
        });
        
        // Calculate shipping
        const shippingType = printType.includes('color') ? 'color' : 'bw';
        const shippingRate = this.rates.shipping[size][shippingType];
        const shippingCost = pages * shippingRate * quantity;
        result.breakdown.push({
            item: `Shipping (${pages} pages × ${quantity} books × ₹${shippingRate})`,
            cost: shippingCost
        });
        
        result.subtotal = printingCost + bindingCost + shippingCost;
        
        // Add one-time costs
        if (includeCoverDesign) {
            result.breakdown.push({
                item: 'Cover Design (One-time)',
                cost: this.designRates.cover_design
            });
            result.subtotal += this.designRates.cover_design;
        }
        
        if (includeIsbn) {
            result.breakdown.push({
                item: 'ISBN Allocation (One-time)',
                cost: this.designRates.isbn_allocation
            });
            result.subtotal += this.designRates.isbn_allocation;
        }
        
        if (includeDesignSupport) {
            const supportCost = this.designRates.design_support[size];
            result.breakdown.push({
                item: `Design Support (${size})`,
                cost: supportCost
            });
            result.subtotal += supportCost;
        }
        
        // Calculate quantity discount
        const discountInfo = this.getQuantityDiscount(quantity);
        if (discountInfo.percentage > 0) {
            result.discount = result.subtotal * discountInfo.percentage;
            result.breakdown.push({
                item: `Quantity Discount (${quantity} books - ${discountInfo.label})`,
                cost: -result.discount
            });
        }
        
        result.total = result.subtotal - result.discount;
        result.perBook = result.total / quantity;
        
        return result;
    }
    
    calculateStandardPrice(productType, options) {
        const {
            quantity = 100,
            size = 'standard',
            paper = 'standard',
            finish = 'standard',
            folding = 'bi',
            additionalServices = []
        } = options;
        
        const result = {
            breakdown: [],
            subtotal: 0,
            discount: 0,
            total: 0,
            perPiece: 0,
            errors: []
        };
        
        if (!this.rates.standard[productType]) {
            result.errors.push(`Invalid product type: ${productType}`);
            return result;
        }
        
        const productRates = this.rates.standard[productType];
        let unitCost = productRates.base_per_100 / 100;
        
        // Calculate base cost
        let baseCost = (productRates.base_per_100 / 100) * quantity;
        result.breakdown.push({
            item: `${this.getProductName(productType)} (${quantity} pieces × ₹${unitCost.toFixed(2)})`,
            cost: baseCost
        });
        
        result.subtotal = baseCost;
        
        // Add paper costs
        if (productRates.paper_costs && productRates.paper_costs[paper]) {
            const paperCost = productRates.paper_costs[paper];
            if (paperCost > 0) {
                result.breakdown.push({
                    item: `Premium Paper (${this.getPaperName(paper)})`,
                    cost: paperCost
                });
                result.subtotal += paperCost;
            }
        }
        
        // Add finish costs
        if (productRates.finish_costs && productRates.finish_costs[finish]) {
            const finishCost = productRates.finish_costs[finish];
            if (finishCost > 0) {
                result.breakdown.push({
                    item: `${this.getFinishName(finish)} Finish`,
                    cost: finishCost
                });
                result.subtotal += finishCost;
            }
        }
        
        // Add folding costs (for brochures)
        if (productRates.folding_costs && productRates.folding_costs[folding]) {
            const foldingCost = productRates.folding_costs[folding];
            if (foldingCost > 0) {
                result.breakdown.push({
                    item: `${this.getFoldingName(folding)} Folding`,
                    cost: foldingCost
                });
                result.subtotal += foldingCost;
            }
        }
        
        // Add additional services
        additionalServices.forEach(service => {
            if (service.selected) {
                let serviceCost = service.cost;
                if (service.type === 'percentage') {
                    serviceCost = result.subtotal * (service.cost / 100);
                }
                result.breakdown.push({
                    item: service.name,
                    cost: serviceCost
                });
                result.subtotal += serviceCost;
            }
        });
        
        result.total = result.subtotal - result.discount;
        result.perPiece = result.total / quantity;
        
        return result;
    }
    
    getQuantityDiscount(quantity) {
        for (let i = this.quantityDiscounts.length - 1; i >= 0; i--) {
            if (quantity >= this.quantityDiscounts[i].min) {
                return {
                    percentage: this.quantityDiscounts[i].discount,
                    label: this.quantityDiscounts[i].label,
                    minQuantity: this.quantityDiscounts[i].min
                };
            }
        }
        return { percentage: 0, label: 'No Discount', minQuantity: 0 };
    }
    
    getBindingName(bindingType) {
        const names = {
            'paperback_perfect': 'Paperback (Perfect Binding)',
            'spiral_binding': 'Spiral Binding',
            'hardcover': 'Hardcover',
            'saddle_stitch': 'Saddle Stitch',
            'wire_o_bound': 'Wire-O Bound'
        };
        return names[bindingType] || bindingType;
    }
    
    getProductName(productType) {
        const names = {
            'business_cards': 'Business Cards',
            'letterhead': 'Letterheads',
            'brochures': 'Brochures',
            'flyers': 'Flyers'
        };
        return names[productType] || productType;
    }
    
    getPaperName(paperType) {
        const names = {
            '75gsm': '75 GSM',
            '100gsm': '100 GSM',
            '100gsm_art': '100 GSM Art Paper',
            '130gsm_art': '130 GSM Art Paper',
            '300gsm': '300 GSM Art Card',
            '350gsm': '350 GSM Art Card',
            '400gsm': '400 GSM Textured',
            '80gsm': '80 GSM Bond Paper',
            '120gsm': '120 GSM Art Paper'
        };
        return names[paperType] || paperType;
    }
    
    getFinishName(finishType) {
        const names = {
            'matte': 'Matte Lamination',
            'gloss': 'Gloss Lamination',
            'spot_uv': 'Spot UV',
            'foiling': 'Foil Stamping'
        };
        return names[finishType] || finishType;
    }
    
    getFoldingName(foldingType) {
        const names = {
            'bi': 'Bi-fold',
            'tri': 'Tri-fold',
            'z': 'Z-fold',
            'gate': 'Gate Fold',
            'accordion': 'Accordion Fold'
        };
        return names[foldingType] || foldingType;
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(amount);
    }
    
    formatNumber(number) {
        return new Intl.NumberFormat('en-IN').format(number);
    }
}

// Global calculator instance
const calculator = new PricingCalculator();

// Main calculation function called by the template
function calculatePrice() {
    const serviceType = getServiceType();
    let result;
    
    if (serviceType === 'book') {
        result = calculateBookPrice();
    } else {
        result = calculateStandardPrice();
    }
    
    if (result.errors.length > 0) {
        showErrors(result.errors);
        return;
    }
    
    updatePriceDisplay(result);
    showPriceBreakdown(result);
}

function getServiceType() {
    const title = document.querySelector('h1')?.textContent.toLowerCase() || '';
    if (title.includes('book') || title.includes('comic') || title.includes('children')) {
        return 'book';
    }
    return 'standard';
}

function calculateBookPrice() {
    const options = {
        size: getElementValue('bookSize', 'A4'),
        paperType: getElementValue('paperType', '75gsm'),
        printType: getElementValue('printType', 'bw_standard'),
        pages: parseInt(getElementValue('pages', '100')),
        quantity: parseInt(getElementValue('quantity', '50')),
        bindingType: getElementValue('bindingType', 'paperback_perfect'),
        includeCoverDesign: isElementChecked('designService'),
        includeIsbn: isElementChecked('isbnService'),
        includeDesignSupport: isElementChecked('designSupport')
    };
    
    return calculator.calculateBookPrice(options);
}

function calculateStandardPrice() {
    const productType = getProductTypeFromUrl();
    const quantity = parseInt(getElementValue('standardQuantity', '100'));
    
    const additionalServices = [
        {
            name: 'Rush Delivery (24 hours)',
            selected: isElementChecked('rushDelivery'),
            type: 'percentage',
            cost: 20
        },
        {
            name: 'Professional Design Service',
            selected: isElementChecked('designService'),
            type: 'fixed',
            cost: 1500
        },
        {
            name: 'Physical Proof Sample',
            selected: isElementChecked('proofing'),
            type: 'fixed',
            cost: 200
        }
    ];
    
    const options = {
        quantity: quantity,
        size: getElementValue('productSize', 'standard'),
        paper: getElementValue('standardPaper', 'standard'),
        finish: getElementValue('finish', 'standard'),
        folding: getElementValue('folding', 'bi'),
        additionalServices: additionalServices
    };
    
    return calculator.calculateStandardPrice(productType, options);
}

function getProductTypeFromUrl() {
    const path = window.location.pathname;
    if (path.includes('business-card')) return 'business_cards';
    if (path.includes('letterhead') || path.includes('letter-head')) return 'letterhead';
    if (path.includes('brochure')) return 'brochures';
    if (path.includes('flyer')) return 'flyers';
    return 'business_cards'; // default
}

function getElementValue(id, defaultValue) {
    const element = document.getElementById(id);
    return element ? element.value : defaultValue;
}

function isElementChecked(id) {
    const element = document.getElementById(id);
    return element ? element.checked : false;
}

function updatePriceDisplay(result) {
    const totalPriceElement = document.getElementById('totalPrice');
    const finalTotalElement = document.getElementById('finalTotal');
    
    if (totalPriceElement) {
        totalPriceElement.textContent = calculator.formatCurrency(result.total);
    }
    
    if (finalTotalElement) {
        finalTotalElement.textContent = calculator.formatCurrency(result.total);
    }
    
    // Update per unit price if available
    const perUnitElement = document.getElementById('perUnitPrice');
    if (perUnitElement) {
        if (result.perBook) {
            perUnitElement.textContent = calculator.formatCurrency(result.perBook);
        } else if (result.perPiece) {
            perUnitElement.textContent = calculator.formatCurrency(result.perPiece);
        }
    }
}

function showPriceBreakdown(result) {
    const breakdownDiv = document.getElementById('breakdownDetails');
    const priceBreakdownSection = document.getElementById('priceBreakdown');
    
    if (!breakdownDiv || !priceBreakdownSection) return;
    
    breakdownDiv.innerHTML = '';
    
    result.breakdown.forEach(item => {
        const div = document.createElement('div');
        div.className = 'flex justify-between items-center py-1';
        
        const isDiscount = item.cost < 0;
        const costClass = isDiscount ? 'text-green-600 font-semibold' : 'text-gray-900';
        const costText = isDiscount ? 
            `- ${calculator.formatCurrency(Math.abs(item.cost))}` : 
            calculator.formatCurrency(item.cost);
        
        div.innerHTML = `
            <span class="text-sm text-gray-600">${item.item}</span>
            <span class="text-sm ${costClass}">${costText}</span>
        `;
        
        breakdownDiv.appendChild(div);
    });
    
    // Add GST calculation (18% in India)
    const gstAmount = result.total * 0.18;
    const gstDiv = document.createElement('div');
    gstDiv.className = 'flex justify-between items-center py-1 border-t border-gray-200 mt-2 pt-2';
    gstDiv.innerHTML = `
        <span class="text-sm text-gray-600">GST (18%)</span>
        <span class="text-sm text-gray-900">${calculator.formatCurrency(gstAmount)}</span>
    `;
    breakdownDiv.appendChild(gstDiv);
    
    // Update final total with GST
    const finalTotal = result.total + gstAmount;
    const finalTotalElement = document.getElementById('finalTotal');
    if (finalTotalElement) {
        finalTotalElement.textContent = calculator.formatCurrency(finalTotal);
    }
    
    // Show the breakdown section
    priceBreakdownSection.classList.remove('hidden');
    
    // Scroll to breakdown
    priceBreakdownSection.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'nearest' 
    });
}

function showErrors(errors) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
    errorDiv.innerHTML = `
        <strong>Error:</strong> ${errors.join(', ')}
    `;
    
    const calculatorForm = document.getElementById('priceCalculator');
    if (calculatorForm) {
        calculatorForm.insertBefore(errorDiv, calculatorForm.firstChild);
        
        // Remove error after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Real-time calculation on input change
function initializeRealTimeCalculation() {
    const inputs = document.querySelectorAll('#priceCalculator input, #priceCalculator select');
    
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            const priceBreakdownSection = document.getElementById('priceBreakdown');
            if (!priceBreakdownSection?.classList.contains('hidden')) {
                // Auto-recalculate if breakdown is already shown
                setTimeout(calculatePrice, 100);
            }
        });
        
        // For number inputs, also listen to 'input' event for real-time updates
        if (input.type === 'number') {
            input.addEventListener('input', function() {
                const priceBreakdownSection = document.getElementById('priceBreakdown');
                if (!priceBreakdownSection?.classList.contains('hidden')) {
                    // Debounce the calculation
                    clearTimeout(this.calcTimeout);
                    this.calcTimeout = setTimeout(calculatePrice, 500);
                }
            });
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeRealTimeCalculation();
    
    // Add smooth scroll for quote calculator link
    const quoteLinks = document.querySelectorAll('a[href="#quote-calculator"]');
    quoteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.getElementById('quote-calculator');
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Initialize calculator with default values
    const totalPriceElement = document.getElementById('totalPrice');
    if (totalPriceElement && !totalPriceElement.textContent.includes('₹')) {
        // Set starting price from template context
        const startingPrice = parseInt(totalPriceElement.textContent) || 299;
        totalPriceElement.textContent = calculator.formatCurrency(startingPrice);
    }
});

// Export for use in other scripts
window.PricingCalculator = PricingCalculator;
window.calculatePrice = calculatePrice;