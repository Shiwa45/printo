# Complete Open Source Design Tool Setup Guide

This guide will help you set up the complete open source design tool system that replaces Fabric.js with Konva.js and integrates with free image APIs.

## Features Implemented

### 🎨 **Frontend (Complete Konva.js Editor)**
- **Professional Design Interface**: Modern, Canva-like interface with larger canvas area
- **Advanced Tools**: Text editing, shapes (rect, circle, triangle, star), image upload, drawing
- **Image Search**: Integration with Unsplash, Pixabay, and Pexels APIs
- **Panels**: Layers management, properties editing, history (undo/redo)
- **Export**: High-quality PNG and PDF export with print-ready specifications
- **Responsive Design**: Works on desktop and tablet devices

### 🔧 **Backend (Django Integration)**
- **Enhanced Models**: Template management, user designs, design sharing, asset management
- **Free API Services**: Unified image search across multiple free APIs
- **Server-side Rendering**: PIL/Pillow-based rendering for high-quality exports
- **Admin Interface**: Super admin template management with bulk upload
- **RESTful APIs**: Complete API endpoints for all design operations

### 📊 **Database Schema**
- `DesignTemplate`: SVG templates with Konva.js compatibility
- `UserDesign`: User saved designs with version control
- `DesignAsset`: User uploaded images and assets
- `StockImage`: Cached stock images from APIs
- `DesignHistory`: Undo/redo functionality
- `DesignShare`: Design collaboration features

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements.txt already includes all necessary packages:
- Django==4.2.7
- Pillow==10.1.0 (for image processing)
- reportlab==4.0.7 (for PDF generation)
- requests==2.31.0 (for API calls)
- cairosvg==2.7.1 (for SVG processing)
- defusedxml==0.7.1 (for secure XML parsing)

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
```

**Required API Keys (All FREE):**

1. **Unsplash API** (5,000 requests/month free)
   - Sign up: https://unsplash.com/developers
   - Add to .env: `UNSPLASH_ACCESS_KEY=your-key-here`

2. **Pixabay API** (Unlimited free)
   - Sign up: https://pixabay.com/api/docs/
   - Add to .env: `PIXABAY_API_KEY=your-key-here`

3. **Pexels API** (200 requests/hour free)
   - Sign up: https://www.pexels.com/api/
   - Add to .env: `PEXELS_API_KEY=your-key-here`

### 3. Database Migration

```bash
python manage.py makemigrations design_tool
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Collect Static Files (Production)

```bash
python manage.py collectstatic
```

### 6. Import Sample Templates (Optional)

```bash
# Place SVG files in a directory, then run:
python manage.py import_svg_templates --directory /path/to/svg/files --category business-cards
```

## Usage Guide

### Admin Panel (/admin/)

1. **Template Management**:
   - Upload SVG templates
   - Set categories and dimensions
   - Mark as featured/premium
   - Bulk template upload interface

2. **User Design Management**:
   - View all user designs
   - Export designs in bulk
   - Manage design permissions

### Design Editor (/design-tool/editor/product-slug/)

1. **Tools Panel**:
   - Select tool for object manipulation
   - Text tool for adding/editing text
   - Shapes tool for basic shapes

2. **Stock Images**:
   - Search across multiple free APIs
   - One-click image insertion
   - Automatic attribution handling

3. **User Assets**:
   - Upload personal images
   - Manage uploaded assets
   - Reuse across designs

4. **Canvas Operations**:
   - Zoom in/out
   - Undo/redo functionality
   - Grid snapping
   - Object transformation

5. **Export Options**:
   - PNG export (web/print quality)
   - PDF export (print-ready)
   - Custom dimensions and DPI

### Template Gallery (/design-tool/templates/)

1. **Browse Templates**:
   - Filter by category
   - Search by keywords
   - View template dimensions

2. **Use Templates**:
   - One-click template loading
   - Instant editor launch
   - Template customization

### My Designs (/design-tool/my-designs/)

1. **Design Management**:
   - View all saved designs
   - Edit existing designs
   - Duplicate designs
   - Delete unwanted designs

2. **Order Integration**:
   - Finalize designs for printing
   - Add to cart with quantity
   - Generate print-ready PDFs

## API Endpoints

### Design Operations
- `POST /design-tool/api/save/` - Save design
- `POST /design-tool/api/export/` - Export design
- `GET /design-tool/api/design/{id}/data/` - Load design data

### Template Management
- `GET /design-tool/api/template/{id}/data/` - Load template data

### Asset Management
- `POST /design-tool/api/upload/asset/` - Upload user asset
- `GET /design-tool/api/assets/` - Get user assets

### Image Search
- `GET /design-tool/api/search/images/` - Search stock images

### Order Integration
- `POST /design-tool/api/finalize-and-order/` - Finalize and add to cart

## Architecture Overview

### Frontend Stack
- **Konva.js**: Canvas manipulation and rendering
- **Tailwind CSS**: Modern, responsive styling
- **Vanilla JavaScript**: No framework dependencies
- **Font Awesome**: Professional icons

### Backend Stack
- **Django 4.2**: Web framework
- **PIL/Pillow**: Image processing
- **ReportLab**: PDF generation
- **Requests**: HTTP client for APIs

### Database
- **SQLite** (development) / **PostgreSQL** (production)
- **JSON fields** for design data storage
- **UUID primary keys** for security
- **Indexed queries** for performance

## Print Industry Standards

### Specifications
- **Default DPI**: 300 (print quality)
- **Color Mode**: CMYK support
- **Bleed Area**: 3mm default
- **Safe Area**: 5mm margin
- **File Formats**: PNG, PDF export

### Product Dimensions
- Business Cards: 89×54mm
- Brochures: 210×297mm (A4)
- Flyers: 210×297mm (A4)
- Letterheads: 210×297mm (A4)
- Stickers: 100×100mm (square)
- Bill Books: 148×210mm (A5)

## Security Features

### Data Protection
- **CSRF Protection**: All forms protected
- **File Upload Validation**: Type and size limits
- **Image Processing**: Server-side validation
- **API Rate Limiting**: Built-in protection

### User Permissions
- **Authentication Required**: For saving designs
- **Design Ownership**: Users can only edit their designs
- **Admin Separation**: Template management restricted
- **Secure File Handling**: No direct file system access

## Performance Optimizations

### Caching
- **Image Search**: 1-hour cache for API responses
- **Template Data**: Database-level caching
- **Asset Thumbnails**: Auto-generated thumbnails

### File Management
- **Efficient Uploads**: Chunked file processing
- **Image Optimization**: Automatic compression
- **CDN Ready**: Static file optimization

## Troubleshooting

### Common Issues

1. **Images not loading**:
   - Check API keys in .env file
   - Verify internet connection
   - Check API rate limits

2. **Export failing**:
   - Ensure Pillow is properly installed
   - Check file permissions
   - Verify font files exist

3. **Templates not showing**:
   - Run database migrations
   - Check template status (should be 'active')
   - Verify category assignments

4. **Canvas not rendering**:
   - Clear browser cache
   - Check JavaScript console for errors
   - Ensure Konva.js is loaded

### Performance Tips

1. **Large Images**:
   - Compress images before upload
   - Use appropriate dimensions
   - Enable thumbnail generation

2. **Database**:
   - Regular cleanup of old designs
   - Index optimization
   - Cache frequently accessed data

3. **API Calls**:
   - Implement request debouncing
   - Cache search results
   - Rotate API keys if needed

## Production Deployment

### Environment Setup
```bash
# Set production environment variables
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/db

# Configure file storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

### Web Server
```nginx
# Nginx configuration example
location /media/ {
    alias /path/to/media/;
    expires 30d;
}

location /static/ {
    alias /path/to/static/;
    expires 1y;
}

location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Support and Maintenance

### Regular Tasks
- Monitor API usage limits
- Clean up unused design files
- Update dependencies
- Backup user designs

### Monitoring
- Check API response times
- Monitor storage usage
- Track user engagement
- Review error logs

## Cost Analysis

### Free Tier Limits
- **Unsplash**: 5,000 requests/month
- **Pixabay**: Unlimited requests
- **Pexels**: 200 requests/hour (4,800/day)
- **Total**: ~10,000 free searches/month

### Scaling Options
- Multiple API keys for higher limits
- Image caching for reduced API calls
- Premium API upgrades if needed
- Self-hosted image libraries

This completes the setup guide for your comprehensive open source design tool system!