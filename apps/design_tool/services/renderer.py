# apps/design_tool/services/renderer.py - Server-side Design Rendering Service
from PIL import Image, ImageDraw, ImageFont, ImageColor
from PIL.ImageColor import getrgb
from io import BytesIO
import json
import logging
import requests
from typing import Dict, List, Tuple, Optional, Union
from django.core.files.base import ContentFile
from django.conf import settings
import os
import math
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

logger = logging.getLogger(__name__)

class DesignRenderer:
    """Service for rendering Konva.js designs to images and PDFs"""
    
    def __init__(self):
        self.default_font_path = self._get_default_font_path()
        self.font_cache = {}
    
    def _get_default_font_path(self) -> str:
        """Get default font path for different OS"""
        default_fonts = {
            'nt': 'C:\\Windows\\Fonts\\arial.ttf',  # Windows
            'posix': '/System/Library/Fonts/Arial.ttf'  # macOS/Linux
        }
        
        font_path = default_fonts.get(os.name, '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
        
        # Check if font exists, fallback if not
        if not os.path.exists(font_path):
            # Try common alternatives
            alternatives = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/TTF/arial.ttf',
                '/System/Library/Fonts/Helvetica.ttc',
                'arial.ttf'  # Hope it's in PATH
            ]
            
            for alt in alternatives:
                if os.path.exists(alt):
                    font_path = alt
                    break
        
        return font_path
    
    def generate_preview(self, design_data: dict, width: int = 400, height: int = 300) -> ContentFile:
        """Generate a preview image from Konva.js design data"""
        try:
            # Create PIL image
            preview_img = self._render_design_to_image(design_data, width, height, 72)
            
            # Convert to bytes
            img_buffer = BytesIO()
            preview_img.save(img_buffer, format='JPEG', quality=85, optimize=True)
            img_buffer.seek(0)
            
            return ContentFile(img_buffer.getvalue())
            
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            raise
    
    def export_to_png(self, design_data: dict, width: int, height: int, dpi: int = 300) -> ContentFile:
        """Export design to high-resolution PNG"""
        try:
            # Render at high DPI
            img = self._render_design_to_image(design_data, width, height, dpi)
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', optimize=True, dpi=(dpi, dpi))
            img_buffer.seek(0)
            
            return ContentFile(img_buffer.getvalue())
            
        except Exception as e:
            logger.error(f"Error exporting to PNG: {e}")
            raise
    
    def export_to_pdf(self, design_data: dict, width_mm: float, height_mm: float, dpi: int = 300) -> ContentFile:
        """Export design to print-ready PDF"""
        try:
            # Convert mm to pixels
            width_px = int(width_mm * dpi / 25.4)
            height_px = int(height_mm * dpi / 25.4)
            
            # Render to high-res image first
            img = self._render_design_to_image(design_data, width_px, height_px, dpi)
            
            # Create PDF
            pdf_buffer = BytesIO()
            
            # Convert mm to points (1 mm = 2.834645669 points)
            width_points = width_mm * 2.834645669
            height_points = height_mm * 2.834645669
            
            c = canvas.Canvas(pdf_buffer, pagesize=(width_points, height_points))
            
            # Save image to temp file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                img.save(temp_file.name, format='PNG', dpi=(dpi, dpi))
                temp_path = temp_file.name
            
            try:
                # Add image to PDF
                c.drawImage(temp_path, 0, 0, width_points, height_points)
                c.save()
                
                # Clean up temp file
                os.unlink(temp_path)
                
            except Exception as cleanup_error:
                # Ensure temp file is cleaned up even if there's an error
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise cleanup_error
            
            pdf_buffer.seek(0)
            return ContentFile(pdf_buffer.getvalue())
            
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise
    
    def _render_design_to_image(self, design_data: dict, width: int, height: int, dpi: int = 300) -> Image.Image:
        """Render Konva.js design data to PIL Image"""
        # Create base image with white background
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Parse stage data
            stage_data = design_data
            
            if isinstance(design_data, str):
                stage_data = json.loads(design_data)
            
            # Get layers (children of stage)
            layers = stage_data.get('children', [])
            
            for layer in layers:
                self._render_layer(draw, layer, img, width, height, dpi)
            
        except Exception as e:
            logger.error(f"Error rendering design: {e}")
            # Return white image if rendering fails
            pass
        
        return img
    
    def _render_layer(self, draw: ImageDraw.ImageDraw, layer_data: dict, img: Image.Image, canvas_width: int, canvas_height: int, dpi: int):
        """Render a single layer (group) and its children"""
        children = layer_data.get('children', [])
        
        for child in children:
            try:
                self._render_object(draw, child, img, canvas_width, canvas_height, dpi)
            except Exception as e:
                logger.warning(f"Error rendering object {child.get('className', 'unknown')}: {e}")
                continue
    
    def _render_object(self, draw: ImageDraw.ImageDraw, obj_data: dict, img: Image.Image, canvas_width: int, canvas_height: int, dpi: int):
        """Render a single Konva object"""
        class_name = obj_data.get('className', '')
        attrs = obj_data.get('attrs', {})
        
        if class_name == 'Text':
            self._render_text(draw, attrs, dpi)
        elif class_name == 'Rect':
            self._render_rect(draw, attrs)
        elif class_name == 'Circle':
            self._render_circle(draw, attrs)
        elif class_name == 'Ellipse':
            self._render_ellipse(draw, attrs)
        elif class_name == 'Line':
            self._render_line(draw, attrs)
        elif class_name == 'Image':
            self._render_image(draw, attrs, img, canvas_width, canvas_height)
        elif class_name == 'Group':
            # Render group children
            children = obj_data.get('children', [])
            for child in children:
                self._render_object(draw, child, img, canvas_width, canvas_height, dpi)
    
    def _render_text(self, draw: ImageDraw.ImageDraw, attrs: dict, dpi: int):
        """Render text object"""
        text = attrs.get('text', '')
        if not text:
            return
        
        x = attrs.get('x', 0)
        y = attrs.get('y', 0)
        font_size = attrs.get('fontSize', 16)
        font_family = attrs.get('fontFamily', 'Arial')
        fill = attrs.get('fill', '#000000')
        
        # Scale font size for DPI
        scaled_font_size = int(font_size * dpi / 72)
        
        try:
            font = self._get_font(font_family, scaled_font_size)
            
            # Convert color
            color = self._parse_color(fill)
            
            # Handle text alignment
            align = attrs.get('align', 'left')
            
            # Get text dimensions for alignment
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Adjust position based on alignment
            if align == 'center':
                x -= text_width // 2
            elif align == 'right':
                x -= text_width
            
            draw.text((x, y), text, fill=color, font=font)
            
        except Exception as e:
            logger.warning(f"Error rendering text: {e}")
            # Fallback to default font
            draw.text((x, y), text, fill=fill)
    
    def _render_rect(self, draw: ImageDraw.ImageDraw, attrs: dict):
        """Render rectangle object"""
        x = attrs.get('x', 0)
        y = attrs.get('y', 0)
        width = attrs.get('width', 100)
        height = attrs.get('height', 100)
        
        # Colors
        fill = attrs.get('fill')
        stroke = attrs.get('stroke')
        stroke_width = attrs.get('strokeWidth', 1)
        
        # Draw filled rectangle
        if fill:
            fill_color = self._parse_color(fill)
            draw.rectangle([x, y, x + width, y + height], fill=fill_color)
        
        # Draw outline
        if stroke and stroke_width > 0:
            stroke_color = self._parse_color(stroke)
            draw.rectangle([x, y, x + width, y + height], outline=stroke_color, width=int(stroke_width))
    
    def _render_circle(self, draw: ImageDraw.ImageDraw, attrs: dict):
        """Render circle object"""
        x = attrs.get('x', 0)
        y = attrs.get('y', 0)
        radius = attrs.get('radius', 50)
        
        # Colors
        fill = attrs.get('fill')
        stroke = attrs.get('stroke')
        stroke_width = attrs.get('strokeWidth', 1)
        
        # Calculate bounding box
        left = x - radius
        top = y - radius
        right = x + radius
        bottom = y + radius
        
        # Draw filled circle
        if fill:
            fill_color = self._parse_color(fill)
            draw.ellipse([left, top, right, bottom], fill=fill_color)
        
        # Draw outline
        if stroke and stroke_width > 0:
            stroke_color = self._parse_color(stroke)
            draw.ellipse([left, top, right, bottom], outline=stroke_color, width=int(stroke_width))
    
    def _render_ellipse(self, draw: ImageDraw.ImageDraw, attrs: dict):
        """Render ellipse object"""
        x = attrs.get('x', 0)
        y = attrs.get('y', 0)
        radius_x = attrs.get('radiusX', 50)
        radius_y = attrs.get('radiusY', 30)
        
        # Colors
        fill = attrs.get('fill')
        stroke = attrs.get('stroke')
        stroke_width = attrs.get('strokeWidth', 1)
        
        # Calculate bounding box
        left = x - radius_x
        top = y - radius_y
        right = x + radius_x
        bottom = y + radius_y
        
        # Draw filled ellipse
        if fill:
            fill_color = self._parse_color(fill)
            draw.ellipse([left, top, right, bottom], fill=fill_color)
        
        # Draw outline
        if stroke and stroke_width > 0:
            stroke_color = self._parse_color(stroke)
            draw.ellipse([left, top, right, bottom], outline=stroke_color, width=int(stroke_width))
    
    def _render_line(self, draw: ImageDraw.ImageDraw, attrs: dict):
        """Render line object"""
        points = attrs.get('points', [])
        stroke = attrs.get('stroke', '#000000')
        stroke_width = attrs.get('strokeWidth', 1)
        
        if len(points) < 4:  # Need at least 2 points (x1, y1, x2, y2)
            return
        
        stroke_color = self._parse_color(stroke)
        
        # Draw line segments
        for i in range(0, len(points) - 2, 2):
            x1, y1 = points[i], points[i + 1]
            x2, y2 = points[i + 2], points[i + 3]
            draw.line([(x1, y1), (x2, y2)], fill=stroke_color, width=int(stroke_width))
    
    def _render_image(self, draw: ImageDraw.ImageDraw, attrs: dict, base_img: Image.Image, canvas_width: int, canvas_height: int):
        """Render image object"""
        try:
            x = attrs.get('x', 0)
            y = attrs.get('y', 0)
            width = attrs.get('width', 100)
            height = attrs.get('height', 100)
            
            # Get image source
            image_src = attrs.get('src', '')
            
            if not image_src:
                return
            
            # Load image based on source type
            if image_src.startswith('data:'):
                # Base64 encoded image
                img_data = self._load_base64_image(image_src)
            elif image_src.startswith('http'):
                # Remote image
                img_data = self._load_remote_image(image_src)
            else:
                # Local file (handle with caution)
                img_data = self._load_local_image(image_src)
            
            if img_data:
                # Resize image to match dimensions
                img_data = img_data.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                
                # Paste image onto base canvas
                base_img.paste(img_data, (int(x), int(y)))
                
        except Exception as e:
            logger.warning(f"Error rendering image: {e}")
            # Draw placeholder rectangle
            draw.rectangle([x, y, x + width, y + height], outline='#cccccc', width=1)
            draw.text((x + 5, y + 5), "Image", fill='#999999')
    
    def _load_base64_image(self, data_url: str) -> Optional[Image.Image]:
        """Load image from base64 data URL"""
        try:
            # Extract base64 data
            header, data = data_url.split(',', 1)
            img_data = base64.b64decode(data)
            return Image.open(BytesIO(img_data))
        except Exception as e:
            logger.error(f"Error loading base64 image: {e}")
            return None
    
    def _load_remote_image(self, url: str) -> Optional[Image.Image]:
        """Load image from remote URL"""
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.error(f"Error loading remote image {url}: {e}")
            return None
    
    def _load_local_image(self, path: str) -> Optional[Image.Image]:
        """Load image from local file system (use with caution)"""
        try:
            # Validate path for security
            if os.path.isabs(path) or '..' in path:
                logger.warning(f"Suspicious image path: {path}")
                return None
            
            # Construct safe path relative to media root
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            
            if os.path.exists(full_path):
                return Image.open(full_path)
            else:
                logger.warning(f"Image file not found: {full_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading local image {path}: {e}")
            return None
    
    def _get_font(self, font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
        """Get font object with caching"""
        cache_key = f"{font_family}_{font_size}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            # Map common web fonts to system fonts
            font_mapping = {
                'Arial': 'arial.ttf',
                'Helvetica': 'arial.ttf',
                'Times': 'times.ttf',
                'Times New Roman': 'times.ttf',
                'Courier': 'cour.ttf',
                'Courier New': 'cour.ttf',
                'Verdana': 'verdana.ttf',
                'Georgia': 'georgia.ttf',
                'Comic Sans MS': 'comic.ttf',
                'Impact': 'impact.ttf',
            }
            
            font_file = font_mapping.get(font_family, self.default_font_path)
            
            # Try to load the specific font
            try:
                font = ImageFont.truetype(font_file, font_size)
            except (OSError, IOError):
                # Fallback to default font
                font = ImageFont.truetype(self.default_font_path, font_size)
            
            self.font_cache[cache_key] = font
            return font
            
        except Exception as e:
            logger.warning(f"Error loading font {font_family}: {e}")
            # Ultimate fallback to default font
            try:
                font = ImageFont.load_default()
                self.font_cache[cache_key] = font
                return font
            except:
                # If even default fails, use built-in
                font = ImageFont.load_default()
                self.font_cache[cache_key] = font
                return font
    
    def _parse_color(self, color: str) -> Union[str, Tuple[int, int, int, int]]:
        """Parse color string to RGB tuple"""
        if not color:
            return '#000000'
        
        try:
            # Handle common formats
            if color.startswith('#'):
                return color
            elif color.startswith('rgb'):
                # Parse rgb(r, g, b) or rgba(r, g, b, a)
                return color
            elif color in ['red', 'blue', 'green', 'black', 'white', 'yellow', 'orange', 'purple', 'pink', 'gray', 'brown']:
                return color
            else:
                # Try to convert using PIL
                return ImageColor.getcolor(color, 'RGB')
        except Exception:
            # Default to black if parsing fails
            return '#000000'

# Global renderer instance
design_renderer = DesignRenderer()