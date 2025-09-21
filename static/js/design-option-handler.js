/**
 * Design Option Handler
 * Manages the "Upload Design" vs "Design Now" selection and front/back options
 */
class DesignOptionHandler {
    constructor(productId, options = {}) {
        this.productId = productId;
        this.options = {
            container: options.container || '#design-options',
            modalContainer: options.modalContainer || 'body',
            ...options
        };
        
        this.productData = null;
        this.selectedOption = null;
        this.selectedSides = [];
        
        this.init();
    }
    
    async init() {
        await this.loadProductData();
        this.createDesignOptions();
        this.bindEvents();
    }
    
    async loadProductData() {
        try {
            const response = await fetch(`/api/products/${this.productId}/design-options/`);
            this.productData = await response.json();
        } catch (error) {
            console.error('Failed to load product data:', error);
            this.productData = {
                design_tool_enabled: false,
                front_back_design_enabled: false,
                supports_upload: true,
                accepted_formats: ['pdf', 'png', 'jpg'],
                max_file_size_mb: 50
            };
        }
    }
    
    createDesignOptions() {
        const container = document.querySelector(this.options.container);
        if (!container || !this.productData.design_tool_enabled) return;
        
        container.innerHTML = `
            <div class="design-choice-section">
                <h3 class="section-title">
                    <i class="fas fa-palette"></i>
                    Choose Your Design Option
                </h3>
                <p class="section-description">
                    Select how you'd like to create your design
                </p>
                
                <div class="design-choice-buttons">
                    ${this.productData.supports_upload ? `
                        <button class="design-btn upload-btn" data-action="upload">
                            <div class="btn-icon">
                                <i class="fas fa-upload"></i>
                            </div>
                            <div class="btn-content">
                                <h4>Upload Design</h4>
                                <p>Have your own design ready?</p>
                                <small>Accepted: ${this.productData.accepted_formats?.join(', ').toUpperCase() || 'PDF, PNG, JPG'}</small>
                            </div>
                            <div class="btn-arrow">
                                <i class="fas fa-arrow-right"></i>
                            </div>
                        </button>
                    ` : ''}
                    
                    <button class="design-btn create-btn" data-action="create">
                        <div class="btn-icon">
                            <i class="fas fa-magic"></i>
                        </div>
                        <div class="btn-content">
                            <h4>Design Now</h4>
                            <p>Use our design tool</p>
                            <small>Templates, images & more</small>
                        </div>
                        <div class="btn-arrow">
                            <i class="fas fa-arrow-right"></i>
                        </div>
                    </button>
                </div>
                
                <div class="design-features">
                    <div class="feature-item">
                        <i class="fas fa-check-circle"></i>
                        <span>Professional Quality</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-check-circle"></i>
                        <span>Print-Ready Output</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-check-circle"></i>
                        <span>Free Design Support</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        const container = document.querySelector(this.options.container);
        if (!container) return;
        
        container.querySelectorAll('.design-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.selectedOption = action;
                
                if (action === 'upload') {
                    this.showUploadModal();
                } else if (action === 'create') {
                    this.handleDesignNow();
                }
            });
        });
    }
    
    handleDesignNow() {
        if (this.productData.front_back_design_enabled) {
            this.showSideSelectionModal();
        } else {
            this.redirectToDesignTool(['front']);
        }
    }
    
    showSideSelectionModal() {
        const modal = this.createModal('side-selection', {
            title: 'Choose Design Option',
            content: `
                <div class="side-selection-content">
                    <p class="modal-description">
                        This product supports front and back design. Choose which sides you'd like to design:
                    </p>
                    
                    <div class="side-options">
                        <button class="side-btn" data-sides="front">
                            <div class="side-icon">
                                <i class="fas fa-file-alt"></i>
                            </div>
                            <div class="side-content">
                                <h4>Front Only</h4>
                                <p>Design the front side</p>
                            </div>
                        </button>
                        
                        <button class="side-btn" data-sides="back">
                            <div class="side-icon">
                                <i class="fas fa-file"></i>
                            </div>
                            <div class="side-content">
                                <h4>Back Only</h4>
                                <p>Design the back side</p>
                            </div>
                        </button>
                        
                        <button class="side-btn featured" data-sides="front,back">
                            <div class="side-icon">
                                <i class="fas fa-copy"></i>
                            </div>
                            <div class="side-content">
                                <h4>Both Sides</h4>
                                <p>Design front and back</p>
                                <small class="featured-badge">Most Popular</small>
                            </div>
                        </button>
                    </div>
                </div>
            `,
            actions: `
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                    Cancel
                </button>
            `
        });
        
        // Bind side selection events
        modal.querySelectorAll('.side-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sides = e.currentTarget.dataset.sides.split(',');
                this.selectedSides = sides;
                modal.remove();
                this.redirectToDesignTool(sides);
            });
        });
    }
    
    showUploadModal() {
        const modal = this.createModal('upload-design', {
            title: 'Upload Your Design',
            content: `
                <div class="upload-content">
                    <div class="upload-zone" id="upload-zone">
                        <div class="upload-icon">
                            <i class="fas fa-cloud-upload-alt"></i>
                        </div>
                        <div class="upload-text">
                            <h4>Drag & drop your files here</h4>
                            <p>or <button type="button" class="link-btn" id="browse-files">browse files</button></p>
                        </div>
                        <input type="file" id="file-input" multiple accept="${this.getAcceptedFormats()}" style="display: none;">
                    </div>
                    
                    <div class="upload-info">
                        <div class="info-item">
                            <i class="fas fa-info-circle"></i>
                            <span>Accepted formats: ${this.productData.accepted_formats?.join(', ').toUpperCase() || 'PDF, PNG, JPG'}</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-weight-hanging"></i>
                            <span>Maximum file size: ${this.productData.max_file_size_mb || 50}MB</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-image"></i>
                            <span>Minimum resolution: ${this.productData.min_resolution_dpi || 300}DPI</span>
                        </div>
                    </div>
                    
                    <div class="uploaded-files" id="uploaded-files" style="display: none;">
                        <h5>Uploaded Files:</h5>
                        <div class="file-list" id="file-list"></div>
                    </div>
                </div>
            `,
            actions: `
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                    Cancel
                </button>
                <button class="btn btn-primary" id="proceed-upload" disabled>
                    Proceed to Order
                </button>
            `
        });
        
        this.bindUploadEvents(modal);
    }
    
    bindUploadEvents(modal) {
        const uploadZone = modal.querySelector('#upload-zone');
        const fileInput = modal.querySelector('#file-input');
        const browseBtn = modal.querySelector('#browse-files');
        const proceedBtn = modal.querySelector('#proceed-upload');
        const fileList = modal.querySelector('#file-list');
        const uploadedFiles = modal.querySelector('#uploaded-files');
        
        let selectedFiles = [];
        
        // Browse files button
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files, selectedFiles, fileList, uploadedFiles, proceedBtn);
        });
        
        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            this.handleFileSelection(e.dataTransfer.files, selectedFiles, fileList, uploadedFiles, proceedBtn);
        });
        
        // Proceed button
        proceedBtn.addEventListener('click', () => {
            this.proceedWithUpload(selectedFiles);
            modal.remove();
        });
    }
    
    handleFileSelection(files, selectedFiles, fileList, uploadedFiles, proceedBtn) {
        Array.from(files).forEach(file => {
            if (this.validateFile(file)) {
                selectedFiles.push(file);
                this.addFileToList(file, fileList);
            }
        });
        
        if (selectedFiles.length > 0) {
            uploadedFiles.style.display = 'block';
            proceedBtn.disabled = false;
        }
    }
    
    validateFile(file) {
        const acceptedFormats = this.productData.accepted_formats || ['pdf', 'png', 'jpg'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        const maxSize = (this.productData.max_file_size_mb || 50) * 1024 * 1024;
        
        if (!acceptedFormats.includes(fileExtension)) {
            alert(`File format ${fileExtension.toUpperCase()} is not supported. Accepted formats: ${acceptedFormats.join(', ').toUpperCase()}`);
            return false;
        }
        
        if (file.size > maxSize) {
            alert(`File size exceeds ${this.productData.max_file_size_mb || 50}MB limit.`);
            return false;
        }
        
        return true;
    }
    
    addFileToList(file, fileList) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-${this.getFileIcon(file.name)}"></i>
                <div class="file-details">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
            </div>
            <button class="remove-file" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        fileList.appendChild(fileItem);
    }
    
    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const icons = {
            'pdf': 'pdf',
            'png': 'image',
            'jpg': 'image',
            'jpeg': 'image',
            'ai': 'vector-square',
            'psd': 'image'
        };
        return icons[extension] || 'file';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    getAcceptedFormats() {
        const formats = this.productData.accepted_formats || ['pdf', 'png', 'jpg'];
        return formats.map(format => `.${format}`).join(',');
    }
    
    createModal(type, options) {
        const modal = document.createElement('div');
        modal.className = `modal design-modal ${type}-modal`;
        modal.innerHTML = `
            <div class="modal-backdrop" onclick="this.closest('.modal').remove()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${options.title}</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${options.content}
                </div>
                <div class="modal-footer">
                    ${options.actions}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        return modal;
    }
    
    redirectToDesignTool(sides) {
        const params = new URLSearchParams({
            product_id: this.productId,
            sides: sides.join(',')
        });
        
        window.location.href = `/design-tool/?${params.toString()}`;
    }
    
    proceedWithUpload(files) {
        // Store files in session storage or send to server
        const fileData = Array.from(files).map(file => ({
            name: file.name,
            size: file.size,
            type: file.type
        }));
        
        sessionStorage.setItem('uploadedDesignFiles', JSON.stringify(fileData));
        
        // Redirect to order page with upload flag
        const params = new URLSearchParams({
            product_id: this.productId,
            design_type: 'upload',
            files: files.length
        });
        
        window.location.href = `/order/?${params.toString()}`;
    }
}

// Auto-initialize if product has design options
document.addEventListener('DOMContentLoaded', function() {
    const productId = document.querySelector('[data-product-id]')?.dataset.productId;
    const hasDesignTool = document.querySelector('[data-design-tool="true"]');
    
    if (productId && hasDesignTool) {
        window.designOptionHandler = new DesignOptionHandler(productId);
    }
});