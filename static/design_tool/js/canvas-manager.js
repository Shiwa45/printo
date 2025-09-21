/**
 * Canvas Manager for Front/Back Design Tool
 * Handles multiple canvas instances and switching between front and back designs
 */

class CanvasManager {
    constructor(config) {
        this.config = {
            width_px: 1050,
            height_px: 638,
            width_mm: 89,
            height_mm: 54,
            dpi: 300,
            bleed_mm: 3.0,
            safe_area_mm: 5.0,
            ...config
        };
        
        this.canvases = {};
        this.layers = {};
        this.currentSide = 'single';
        this.designType = 'single';
        this.activeStage = null;
        this.activeLayer = null;
        this.visualGuides = null;
        
        this.container = document.getElementById('konva-container');
        if (!this.container) {
            throw new Error('Canvas container not found');
        }
    }
    
    setDesignType(designType) {
        this.designType = designType;
    }
    
    initializeCanvas(side) {
        // Create canvas container for this side
        const canvasId = `canvas-${side}`;
        let canvasContainer = document.getElementById(canvasId);
        
        if (!canvasContainer) {
            canvasContainer = document.createElement('div');
            canvasContainer.id = canvasId;
            canvasContainer.style.display = side === this.currentSide ? 'block' : 'none';
            this.container.appendChild(canvasContainer);
        }
        
        // Create Konva stage
        const stage = new Konva.Stage({
            container: canvasId,
            width: this.config.width_px,
            height: this.config.height_px
        });
        
        // Create main layer
        const layer = new Konva.Layer();
        stage.add(layer);
        
        // Store references
        this.canvases[side] = stage;
        this.layers[side] = layer;
        
        // Set as active if this is the current side
        if (side === this.currentSide) {
            this.activeStage = stage;
            this.activeLayer = layer;
        }
        
        // Initialize visual guides
        this.initializeVisualGuides(stage, side);
        
        // Setup canvas events
        this.setupCanvasEvents(stage, side);
        
        return stage;
    }
    
    initializeVisualGuides(stage, side) {
        if (!this.visualGuides) {
            this.visualGuides = new VisualGuidesOverlay(this.config);
        }
        
        this.visualGuides.addToCanvas(stage, side);
    }
    
    setupCanvasEvents(stage, side) {
        // Add common canvas event handlers
        stage.on('click tap', (e) => {
            // Handle canvas click events
            if (e.target === stage) {
                // Clicked on empty canvas
                this.deselectAll();
            }
        });
        
        stage.on('dragstart', () => {
            // Handle drag start
        });
        
        stage.on('dragend', () => {
            // Handle drag end
            this.saveState();
        });
    }
    
    switchSide(side) {
        if (!this.canvases[side] || side === this.currentSide) {
            return;
        }
        
        // Hide current canvas
        this.hideCanvas(this.currentSide);
        
        // Show target canvas
        this.showCanvas(side);
        
        // Update current side
        this.currentSide = side;
        this.activeStage = this.canvases[side];
        this.activeLayer = this.layers[side];
        
        // Update UI
        this.updateSideNavigation();
        
        // Trigger event
        this.dispatchEvent('sideChanged', {
            currentSide: side,
            stage: this.activeStage,
            layer: this.activeLayer
        });
    }
    
    hideCanvas(side) {
        const canvasContainer = document.getElementById(`canvas-${side}`);
        if (canvasContainer) {
            canvasContainer.style.display = 'none';
        }
    }
    
    showCanvas(side) {
        const canvasContainer = document.getElementById(`canvas-${side}`);
        if (canvasContainer) {
            canvasContainer.style.display = 'block';
        }
        
        // Ensure canvas is properly sized
        if (this.canvases[side]) {
            this.canvases[side].batchDraw();
        }
    }
    
    updateSideNavigation() {
        const sideNavButtons = document.querySelectorAll('.side-nav-btn');
        sideNavButtons.forEach(btn => {
            const btnSide = btn.dataset.side;
            btn.classList.toggle('active', btnSide === this.currentSide);
        });
        
        // Show/hide side navigation based on design type
        const sideNavigation = document.getElementById('sideNavigation');
        if (sideNavigation) {
            sideNavigation.style.display = this.designType === 'both_sides' ? 'block' : 'none';
        }
    }
    
    loadTemplate(side, templateData) {
        if (!this.canvases[side] || !templateData) {
            return;
        }
        
        const stage = this.canvases[side];
        const layer = this.layers[side];
        
        try {
            // Clear existing content (except visual guides)
            const children = layer.children.slice();
            children.forEach(child => {
                if (!child.name || !child.name().includes('visual-guide')) {
                    child.destroy();
                }
            });
            
            // Load template data
            if (templateData.objects && Array.isArray(templateData.objects)) {
                templateData.objects.forEach(obj => {
                    this.createObjectFromData(obj, layer);
                });
            }
            
            layer.batchDraw();
            
        } catch (error) {
            console.error('Error loading template:', error);
        }
    }
    
    createObjectFromData(objData, layer) {
        // Create Konva objects from template data
        // This is a simplified implementation - you may need to expand based on your template format
        
        switch (objData.type) {
            case 'rect':
                const rect = new Konva.Rect({
                    x: objData.left || 0,
                    y: objData.top || 0,
                    width: objData.width || 100,
                    height: objData.height || 100,
                    fill: objData.fill || '#000000',
                    stroke: objData.stroke,
                    strokeWidth: objData.strokeWidth || 0,
                    draggable: true
                });
                layer.add(rect);
                break;
                
            case 'circle':
                const circle = new Konva.Circle({
                    x: objData.left || 0,
                    y: objData.top || 0,
                    radius: objData.radius || 50,
                    fill: objData.fill || '#000000',
                    stroke: objData.stroke,
                    strokeWidth: objData.strokeWidth || 0,
                    draggable: true
                });
                layer.add(circle);
                break;
                
            case 'text':
                const text = new Konva.Text({
                    x: objData.left || 0,
                    y: objData.top || 0,
                    text: objData.text || 'Sample Text',
                    fontSize: objData.fontSize || 16,
                    fontFamily: objData.fontFamily || 'Arial',
                    fill: objData.fill || '#000000',
                    draggable: true
                });
                layer.add(text);
                break;
                
            default:
                console.warn('Unknown object type:', objData.type);
        }
    }
    
    getDesignData(side = null) {
        const targetSide = side || this.currentSide;
        const stage = this.canvases[targetSide];
        
        if (!stage) {
            return null;
        }
        
        // Export stage data (excluding visual guides)
        const stageData = stage.toJSON();
        const parsedData = JSON.parse(stageData);
        
        // Filter out visual guides
        if (parsedData.children && parsedData.children[0] && parsedData.children[0].children) {
            parsedData.children[0].children = parsedData.children[0].children.filter(child => 
                !child.attrs || !child.attrs.name || !child.attrs.name.includes('visual-guide')
            );
        }
        
        return parsedData;
    }
    
    getAllDesignData() {
        const data = {};
        
        Object.keys(this.canvases).forEach(side => {
            data[side] = this.getDesignData(side);
        });
        
        return {
            type: this.designType,
            data: data
        };
    }
    
    deselectAll() {
        if (this.activeStage) {
            this.activeStage.find('Transformer').forEach(tr => tr.destroy());
            this.activeLayer.batchDraw();
        }
    }
    
    saveState() {
        // Save current state for undo/redo functionality
        // Implementation depends on your undo/redo system
    }
    
    dispatchEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    }
    
    destroy() {
        // Clean up all canvases
        Object.values(this.canvases).forEach(stage => {
            stage.destroy();
        });
        
        // Clear containers
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        // Reset state
        this.canvases = {};
        this.layers = {};
        this.activeStage = null;
        this.activeLayer = null;
    }
}

/**
 * Visual Guides Overlay for showing bleed lines and safe zones
 */
class VisualGuidesOverlay {
    constructor(config) {
        this.config = config;
        this.bleedColor = '#ff0000';  // Red for bleed lines
        this.safeZoneColor = '#000000';  // Black for safe zones
        this.guidesVisible = true;
    }
    
    addToCanvas(stage, side) {
        // Create guides layer
        let guidesLayer = stage.findOne('.visual-guides-layer');
        if (!guidesLayer) {
            guidesLayer = new Konva.Layer({ name: 'visual-guides-layer' });
            stage.add(guidesLayer);
        }
        
        // Clear existing guides
        guidesLayer.destroyChildren();
        
        // Add bleed lines
        this.addBleedLines(guidesLayer);
        
        // Add safe zone
        this.addSafeZone(guidesLayer);
        
        // Move guides layer to top
        guidesLayer.moveToTop();
        guidesLayer.batchDraw();
    }
    
    addBleedLines(layer) {
        const bleedPx = this.mmToPx(this.config.bleed_mm);
        
        // Outer bleed rectangle
        const bleedRect = new Konva.Rect({
            x: -bleedPx,
            y: -bleedPx,
            width: this.config.width_px + (bleedPx * 2),
            height: this.config.height_px + (bleedPx * 2),
            stroke: this.bleedColor,
            strokeWidth: 2,
            dash: [8, 4],
            listening: false,
            name: 'visual-guide-bleed'
        });
        
        layer.add(bleedRect);
        
        // Add bleed line labels
        const bleedLabel = new Konva.Text({
            x: -bleedPx - 40,
            y: this.config.height_px / 2 - 10,
            text: `Bleed line`,
            fontSize: 12,
            fontFamily: 'Arial',
            fill: this.bleedColor,
            listening: false,
            name: 'visual-guide-bleed-label'
        });
        layer.add(bleedLabel);
        
        // Add measurement indicators
        this.addMeasurementRulers(layer, bleedPx);
        
        // Corner crop marks
        const cropMarkLength = 15;
        const cropMarks = [
            // Top-left
            { x1: -bleedPx - cropMarkLength, y1: -bleedPx, x2: -bleedPx + cropMarkLength, y2: -bleedPx },
            { x1: -bleedPx, y1: -bleedPx - cropMarkLength, x2: -bleedPx, y2: -bleedPx + cropMarkLength },
            // Top-right
            { x1: this.config.width_px + bleedPx - cropMarkLength, y1: -bleedPx, x2: this.config.width_px + bleedPx + cropMarkLength, y2: -bleedPx },
            { x1: this.config.width_px + bleedPx, y1: -bleedPx - cropMarkLength, x2: this.config.width_px + bleedPx, y2: -bleedPx + cropMarkLength },
            // Bottom-left
            { x1: -bleedPx - cropMarkLength, y1: this.config.height_px + bleedPx, x2: -bleedPx + cropMarkLength, y2: this.config.height_px + bleedPx },
            { x1: -bleedPx, y1: this.config.height_px + bleedPx - cropMarkLength, x2: -bleedPx, y2: this.config.height_px + bleedPx + cropMarkLength },
            // Bottom-right
            { x1: this.config.width_px + bleedPx - cropMarkLength, y1: this.config.height_px + bleedPx, x2: this.config.width_px + bleedPx + cropMarkLength, y2: this.config.height_px + bleedPx },
            { x1: this.config.width_px + bleedPx, y1: this.config.height_px + bleedPx - cropMarkLength, x2: this.config.width_px + bleedPx, y2: this.config.height_px + bleedPx + cropMarkLength }
        ];
        
        cropMarks.forEach(mark => {
            const line = new Konva.Line({
                points: [mark.x1, mark.y1, mark.x2, mark.y2],
                stroke: this.bleedColor,
                strokeWidth: 1,
                listening: false,
                name: 'visual-guide-crop-mark'
            });
            layer.add(line);
        });
    }
    
    addSafeZone(layer) {
        const safeMarginPx = this.mmToPx(this.config.safe_area_mm);
        
        const safeRect = new Konva.Rect({
            x: safeMarginPx,
            y: safeMarginPx,
            width: this.config.width_px - (safeMarginPx * 2),
            height: this.config.height_px - (safeMarginPx * 2),
            stroke: this.safeZoneColor,
            strokeWidth: 1,
            dash: [6, 3],
            listening: false,
            name: 'visual-guide-safe-zone'
        });
        
        layer.add(safeRect);
        
        // Add safe zone label
        const safeLabel = new Konva.Text({
            x: safeMarginPx + 10,
            y: safeMarginPx + 10,
            text: `Safe zone`,
            fontSize: 12,
            fontFamily: 'Arial',
            fill: this.safeZoneColor,
            listening: false,
            name: 'visual-guide-safe-label'
        });
        layer.add(safeLabel);
    }
    
    addMeasurementRulers(layer, bleedPx) {
        const rulerColor = '#666666';
        const rulerTextColor = '#333333';
        
        // Top ruler
        const topRuler = new Konva.Rect({
            x: -bleedPx - 30,
            y: -bleedPx - 25,
            width: this.config.width_px + (bleedPx * 2) + 60,
            height: 20,
            fill: '#f0f0f0',
            stroke: '#cccccc',
            strokeWidth: 1,
            listening: false,
            name: 'visual-guide-ruler'
        });
        layer.add(topRuler);
        
        // Left ruler
        const leftRuler = new Konva.Rect({
            x: -bleedPx - 30,
            y: -bleedPx,
            width: 25,
            height: this.config.height_px + (bleedPx * 2),
            fill: '#f0f0f0',
            stroke: '#cccccc',
            strokeWidth: 1,
            listening: false,
            name: 'visual-guide-ruler'
        });
        layer.add(leftRuler);
        
        // Add measurement marks and labels
        const totalWidthMm = this.config.width_mm + (this.config.bleed_mm * 2);
        const totalHeightMm = this.config.height_mm + (this.config.bleed_mm * 2);
        
        // Top measurement
        const topMeasurement = new Konva.Text({
            x: -bleedPx + (this.config.width_px + bleedPx * 2) / 2 - 20,
            y: -bleedPx - 20,
            text: `${totalWidthMm.toFixed(1)} mm`,
            fontSize: 11,
            fontFamily: 'Arial',
            fill: rulerTextColor,
            listening: false,
            name: 'visual-guide-measurement'
        });
        layer.add(topMeasurement);
        
        // Left measurement
        const leftMeasurement = new Konva.Text({
            x: -bleedPx - 25,
            y: -bleedPx + (this.config.height_px + bleedPx * 2) / 2 - 6,
            text: `${totalHeightMm.toFixed(1)} mm`,
            fontSize: 11,
            fontFamily: 'Arial',
            fill: rulerTextColor,
            rotation: -90,
            listening: false,
            name: 'visual-guide-measurement'
        });
        layer.add(leftMeasurement);
        
        // Add tick marks on rulers
        const tickSpacing = 50; // pixels between ticks
        
        // Top ruler ticks
        for (let i = 0; i <= this.config.width_px + (bleedPx * 2); i += tickSpacing) {
            const tick = new Konva.Line({
                points: [-bleedPx + i, -bleedPx - 5, -bleedPx + i, -bleedPx],
                stroke: rulerColor,
                strokeWidth: 1,
                listening: false,
                name: 'visual-guide-tick'
            });
            layer.add(tick);
        }
        
        // Left ruler ticks
        for (let i = 0; i <= this.config.height_px + (bleedPx * 2); i += tickSpacing) {
            const tick = new Konva.Line({
                points: [-bleedPx - 5, -bleedPx + i, -bleedPx, -bleedPx + i],
                stroke: rulerColor,
                strokeWidth: 1,
                listening: false,
                name: 'visual-guide-tick'
            });
            layer.add(tick);
        }
    }
    
    mmToPx(mm) {
        return (mm * this.config.dpi) / 25.4;
    }
    
    toggleVisibility(stage) {
        this.guidesVisible = !this.guidesVisible;
        
        const guidesLayer = stage.findOne('.visual-guides-layer');
        if (guidesLayer) {
            guidesLayer.visible(this.guidesVisible);
            guidesLayer.batchDraw();
        }
    }
    
    setVisibility(stage, visible) {
        this.guidesVisible = visible;
        
        const guidesLayer = stage.findOne('.visual-guides-layer');
        if (guidesLayer) {
            guidesLayer.visible(visible);
            guidesLayer.batchDraw();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CanvasManager, VisualGuidesOverlay };
} else if (typeof window !== 'undefined') {
    window.CanvasManager = CanvasManager;
    window.VisualGuidesOverlay = VisualGuidesOverlay;
}