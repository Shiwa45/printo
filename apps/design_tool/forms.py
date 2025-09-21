# apps/design_tool/forms.py - Custom forms for admin interface
from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import DesignTemplate
from apps.products.models import Product
import json


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget for multiple file upload"""
    allow_multiple_selected = True
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': True})
        super().__init__(attrs)


class MultipleFileField(forms.FileField):
    """Custom field for multiple file upload"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class TagsWidget(forms.TextInput):
    """Custom widget for tags - comma-separated input"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'vTextField',
            'placeholder': 'Enter tags separated by commas (e.g., business, professional, modern)',
            'style': 'width: 100%;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def format_value(self, value):
        if isinstance(value, list):
            return ', '.join(value)
        return value or ''
    
    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if value:
            # Split by comma and clean up whitespace
            return [tag.strip() for tag in value.split(',') if tag.strip()]
        return []


class ProductTypesWidget(forms.CheckboxSelectMultiple):
    """Custom widget for product_types - checkbox selection"""
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = []
    
    def format_value(self, value):
        if isinstance(value, list):
            return value
        return value or []


class TemplateDataWidget(forms.Textarea):
    """Custom widget for template_data - read-only JSON display"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'readonly': True,
            'style': 'width: 100%; height: 200px; font-family: monospace; background-color: #f8f9fa;',
            'class': 'vLargeTextField'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def format_value(self, value):
        if value:
            try:
                return json.dumps(value, indent=2)
            except (TypeError, ValueError):
                return str(value)
        return ''


class DesignTemplateAdminForm(forms.ModelForm):
    """Custom form for DesignTemplate admin"""
    
    tags = forms.CharField(
        required=False,
        widget=TagsWidget(),
        help_text="Enter tags separated by commas"
    )
    
    product_types = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select which products can use this template"
    )
    
    template_data = forms.CharField(
        required=False,
        widget=TemplateDataWidget(),
        help_text="Auto-generated canvas data from SVG file"
    )
    
    class Meta:
        model = DesignTemplate
        fields = '__all__'
        widgets = {
            'side': forms.Select(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'dpi': forms.NumberInput(attrs={'min': '72', 'max': '600'}),
            'bleed_mm': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '10'}),
            'safe_area_mm': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '20'}),
            'min_font_size': forms.NumberInput(attrs={'step': '0.1', 'min': '4', 'max': '72'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set choices for product_types from available products
        try:
            product_choices = []
            products = Product.objects.filter(design_tool_enabled=True).values('id', 'name', 'category__name')
            for product in products:
                product_choices.append((
                    product['id'], 
                    f"{product['category__name']} - {product['name']}"
                ))
            
            self.fields['product_types'].choices = product_choices
        except Exception:
            # Handle case where database isn't ready yet
            self.fields['product_types'].choices = []
        
        # Set initial values for custom fields
        if self.instance.pk:
            # Format tags
            if self.instance.tags:
                self.fields['tags'].initial = ', '.join(self.instance.tags)
            
            # Set product_types initial values
            if self.instance.product_types:
                self.fields['product_types'].initial = self.instance.product_types
    
    def clean_tags(self):
        """Convert comma-separated tags to list"""
        tags = self.cleaned_data.get('tags', '')
        if tags:
            return [tag.strip() for tag in tags.split(',') if tag.strip()]
        return []
    
    def clean_product_types(self):
        """Ensure product_types is a list of integers"""
        product_types = self.cleaned_data.get('product_types', [])
        if product_types:
            return [int(pt) for pt in product_types if pt.isdigit()]
        return []
    
    def clean_template_data(self):
        """Validate and parse template_data JSON"""
        template_data = self.cleaned_data.get('template_data', '')
        if template_data:
            try:
                return json.loads(template_data)
            except json.JSONDecodeError:
                # If it's invalid JSON, just return the original data
                if self.instance.pk:
                    return self.instance.template_data
                return {}
        return self.instance.template_data if self.instance.pk else {}


class UserFriendlyDesignTemplateForm(forms.ModelForm):
    """Simplified form for template upload"""
    
    tags_input = forms.CharField(
        label='Tags',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'business, professional, modern, clean',
            'class': 'form-control',
            'data-toggle': 'tooltip',
            'title': 'Add tags to help users find this template'
        }),
        help_text="Separate tags with commas"
    )
    
    product_types_list = forms.ModelMultipleChoiceField(
        queryset=Product.objects.none(),  # Will be set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'product-types-checkboxes'}),
        help_text="Select which products can use this template"
    )
    
    class Meta:
        model = DesignTemplate
        fields = [
            'name', 'category', 'side', 'description', 'template_file', 'width', 'height', 
            'bleed_mm', 'safe_area_mm', 'is_premium', 'is_featured', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Template name (e.g., "Modern Business Card")'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Width in mm'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1', 
                'min': '0',
                'placeholder': 'Height in mm'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the template'
            }),
            'bleed_mm': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '10',
                'placeholder': '3.0'
            }),
            'safe_area_mm': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0', 
                'max': '20',
                'placeholder': '5.0'
            }),
            'template_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.svg,.json'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'side': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set queryset for product_types_list
        try:
            self.fields['product_types_list'].queryset = Product.objects.filter(design_tool_enabled=True)
        except Exception:
            # Handle case where database isn't ready yet
            self.fields['product_types_list'].queryset = Product.objects.none()
    
    def clean_tags_input(self):
        """Convert comma-separated tags to list"""
        tags = self.cleaned_data.get('tags_input', '')
        if tags:
            return [tag.strip() for tag in tags.split(',') if tag.strip()]
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set tags from the custom input
        instance.tags = self.cleaned_data.get('tags_input', [])
        
        # Set product_types from the multi-select
        product_types = self.cleaned_data.get('product_types_list')
        if product_types:
            instance.product_types = [product.id for product in product_types]
        else:
            instance.product_types = []
        
        if commit:
            instance.save()
        
        return instance


class BulkTemplateUploadForm(forms.Form):
    """Form for bulk template upload"""
    
    category = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        empty_label="Choose a category...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    template_files = MultipleFileField(
        help_text="Select multiple SVG files"
    )
    
    default_width = forms.FloatField(
        initial=89.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0'
        }),
        help_text="Default width in mm (can be overridden per template)"
    )
    
    default_height = forms.FloatField(
        initial=54.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0'
        }),
        help_text="Default height in mm (can be overridden per template)"
    )
    
    is_premium = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Mark all templates as premium"
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Mark all templates as featured"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only show categories that have design-enabled products
        try:
            from apps.products.models import ProductCategory
            self.fields['category'].queryset = ProductCategory.objects.filter(
                products__design_tool_enabled=True
            ).distinct()
        except Exception:
            # Handle case where database isn't ready yet
            pass