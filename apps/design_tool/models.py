# apps/design_tool/models.py - Enhanced Models
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from apps.products.models import Product, ProductCategory

User = settings.AUTH_USER_MODEL

class DesignTemplate(models.Model):
    """Enhanced design templates with SVG support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='design_templates')
    product_types = models.JSONField(default=list, help_text="Which products can use this template")
    
    # Side specification for front/back design
    SIDE_CHOICES = [
        ('front', 'Front'),
        ('back', 'Back'),
        ('single', 'Single Side'),  # For backward compatibility
    ]
    side = models.CharField(max_length=10, choices=SIDE_CHOICES, default='single', help_text="Which side this template is for")
    
    
    # Template files - Support SVG
# In apps/design_tool/models.py, change this line:
    template_file = models.FileField(
        upload_to='templates/files/',
        validators=[FileExtensionValidator(allowed_extensions=['svg', 'json'])],
        help_text="SVG template file or JSON canvas data",
        null=True, blank=True  # Add these temporarily
    )
    template_data = models.JSONField(help_text="Parsed canvas data from SVG", null=True, blank=True)
    
    # Images
    preview_image = models.ImageField(upload_to='templates/previews/', blank=True)
    thumbnail_image = models.ImageField(upload_to='templates/thumbnails/', blank=True)
    
    # Specifications
    width = models.FloatField(help_text="Width in mm")
    height = models.FloatField(help_text="Height in mm")
    dpi = models.IntegerField(default=300)
    
    # Print specifications
    bleed_mm = models.FloatField(default=3.0, help_text="Bleed area in mm")
    safe_area_mm = models.FloatField(default=5.0, help_text="Safe area margin in mm")
    min_font_size = models.FloatField(default=6.0, help_text="Minimum font size in pt")
    description = models.TextField(blank=True)
    
    COLOR_MODES = [
        ('RGB', 'RGB'),
        ('CMYK', 'CMYK'),
    ]
    color_mode = models.CharField(max_length=4, choices=COLOR_MODES, default='CMYK')
    
    # Categorization
    tags = models.JSONField(default=list)
    is_premium = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    # Admin fields
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending_review', 'Pending Review'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-usage_count', 'name']
        unique_together = ['category', 'side', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.category.name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate template_data from SVG if needed
        if self.template_file and not self.template_data:
            self.parse_svg_to_canvas_data()
        super().save(*args, **kwargs)
    
    def parse_svg_to_canvas_data(self):
        """Convert SVG to Fabric.js compatible JSON data"""
        # This would parse SVG and convert to Fabric.js format
        # For now, we'll create a placeholder structure
        self.template_data = {
            "version": "5.3.0",
            "objects": [],
            "background": "#ffffff",
            "width": int(self.width * 3.78),  # Convert mm to px (approximate)
            "height": int(self.height * 3.78)
        }

class UserDesign(models.Model):
    """User saved designs with order integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    template = models.ForeignKey(DesignTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    name = models.CharField(max_length=255)
    
    # Design type and data for front/back support
    DESIGN_TYPE_CHOICES = [
        ('single', 'Single Side'),
        ('front_only', 'Front Only'),
        ('back_only', 'Back Only'),
        ('both_sides', 'Both Sides'),
    ]
    design_type = models.CharField(max_length=15, choices=DESIGN_TYPE_CHOICES, default='single')
    
    # Legacy field for backward compatibility
    design_data = models.JSONField(help_text="Legacy canvas data for single-sided designs", null=True, blank=True)
    
    # New fields for front/back design data
    front_design_data = models.JSONField(help_text="Front side canvas data", null=True, blank=True)
    back_design_data = models.JSONField(help_text="Back side canvas data", null=True, blank=True)
    
    preview_image = models.ImageField(upload_to='user_designs/previews/', blank=True)
    front_preview_image = models.ImageField(upload_to='user_designs/previews/front/', blank=True)
    back_preview_image = models.ImageField(upload_to='user_designs/previews/back/', blank=True)
    
    # Design specifications
    final_width_mm = models.FloatField(null=True, blank=True)
    final_height_mm = models.FloatField(null=True, blank=True)
    
    # Order integration
    is_ordered = models.BooleanField(default=False)
    order_count = models.IntegerField(default=0)
    
    # Status
    is_favorite = models.BooleanField(default=False)
    is_ready_for_print = models.BooleanField(default=False)
    
    last_modified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_modified']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def get_design_data(self):
        """Get design data in appropriate format based on design type"""
        # Handle legacy designs that don't have design_type set
        if not self.design_type or self.design_type == 'single':
            return self.design_data
        return {
            'type': self.design_type,
            'front': self.front_design_data,
            'back': self.back_design_data
        }
    
    def set_design_data(self, data):
        """Set design data from various formats"""
        if isinstance(data, dict) and 'type' in data:
            # New format with front/back data
            self.design_type = data.get('type', 'single')
            self.front_design_data = data.get('front')
            self.back_design_data = data.get('back')
        else:
            # Legacy single-sided format
            self.design_type = 'single'
            self.design_data = data
    
    def clean(self):
        """Validate design data based on type"""
        from django.core.exceptions import ValidationError
        super().clean()
        
        # Handle legacy designs
        if not self.design_type:
            if self.design_data:
                self.design_type = 'single'
            else:
                raise ValidationError('Design must have either design_type or legacy design_data.')
        
        # Validate based on design type
        if self.design_type == 'single' and not self.design_data:
            raise ValidationError({'design_data': 'Single-sided designs must have design data.'})
        elif self.design_type == 'front_only' and not self.front_design_data:
            raise ValidationError({'front_design_data': 'Front-only designs must have front design data.'})
        elif self.design_type == 'back_only' and not self.back_design_data:
            raise ValidationError({'back_design_data': 'Back-only designs must have back design data.'})
        elif self.design_type == 'both_sides' and (not self.front_design_data or not self.back_design_data):
            raise ValidationError('Both-sides designs must have both front and back design data.')


class DesignAsset(models.Model):
    """User uploaded assets like images, fonts, graphics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_assets')
    name = models.CharField(max_length=255)
    asset_file = models.FileField(upload_to='design_assets/', db_column='file')
    
    ASSET_TYPES = [
        ('image', 'Image'),
        ('font', 'Font'),
        ('graphic', 'Graphic'),
        ('icon', 'Icon'),
    ]
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)
    file_size = models.IntegerField(help_text="File size in bytes")
    
    upload_date = models.DateTimeField(auto_now_add=True, db_column='created_at')
    is_public = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.name} - {self.asset_type}"


class DesignHistory(models.Model):
    """Track design changes and versions"""
    design = models.ForeignKey(UserDesign, on_delete=models.CASCADE, related_name='history')
    version_number = models.IntegerField(default=1)
    design_data = models.JSONField(default=dict, help_text="Snapshot of design data")
    change_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['design', 'version_number']
    
    def __str__(self):
        return f"{self.design.name} - v{self.version_number}"


class StockImage(models.Model):
    """Stock images from external APIs"""
    external_id = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=50, default='pixabay', help_text="API source like 'pixabay', 'unsplash'")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Image URLs from external service
    small_url = models.URLField()
    medium_url = models.URLField()
    large_url = models.URLField()
    
    # Metadata
    tags = models.JSONField(default=list)
    width = models.IntegerField(default=800)
    height = models.IntegerField(default=600)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.source})"


class DesignShare(models.Model):
    """Share designs with others"""
    design = models.ForeignKey(UserDesign, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_designs')
    share_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Share settings
    is_public = models.BooleanField(default=False)
    allow_edit = models.BooleanField(default=False)
    allow_download = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    view_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['design', 'shared_by']
    
    def __str__(self):
        return f"Share: {self.design.name} by {self.shared_by.username}"

