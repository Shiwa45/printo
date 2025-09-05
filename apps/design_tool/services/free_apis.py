# apps/design_tool/services/free_apis.py - Free Image API Integration Service
import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import hashlib
import time

logger = logging.getLogger(__name__)

class ImageSearchService:
    """Service for searching free stock images from multiple APIs"""
    
    def __init__(self):
        # API Keys - Store in settings.py or environment variables
        self.unsplash_access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
        self.pixabay_api_key = getattr(settings, 'PIXABAY_API_KEY', '')
        self.pexels_api_key = getattr(settings, 'PEXELS_API_KEY', '')
        
        # Rate limiting counters
        self.rate_limits = {
            'unsplash': {'requests': 0, 'reset_time': 0, 'per_hour': 50},
            'pixabay': {'requests': 0, 'reset_time': 0, 'per_hour': 5000}, # Very generous
            'pexels': {'requests': 0, 'reset_time': 0, 'per_hour': 200},
        }
    
    def search_all_sources(self, query: str, page: int = 1, per_page: int = 20) -> List[Dict]:
        """Search all available image sources and combine results"""
        results = []
        
        # Try each source and combine results
        sources = ['unsplash', 'pixabay', 'pexels']
        per_source = max(1, per_page // len(sources))
        
        for source in sources:
            try:
                source_results = self.search_single_source(source, query, 1, per_source)
                results.extend(source_results)
                
                # If we have enough results, break
                if len(results) >= per_page:
                    break
                    
            except Exception as e:
                logger.warning(f"Error searching {source}: {e}")
                continue
        
        # Shuffle and limit results
        import random
        random.shuffle(results)
        return results[:per_page]
    
    def search_single_source(self, source: str, query: str, page: int = 1, per_page: int = 20) -> List[Dict]:
        """Search a specific image source"""
        if not self._check_rate_limit(source):
            logger.warning(f"Rate limit exceeded for {source}")
            return []
        
        # Check cache first
        cache_key = f"image_search_{source}_{hashlib.md5(query.encode()).hexdigest()}_{page}_{per_page}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results
        
        results = []
        
        try:
            if source == 'unsplash' and self.unsplash_access_key:
                results = self._search_unsplash(query, page, per_page)
            elif source == 'pixabay' and self.pixabay_api_key:
                results = self._search_pixabay(query, page, per_page)
            elif source == 'pexels' and self.pexels_api_key:
                results = self._search_pexels(query, page, per_page)
            
            # Cache results for 1 hour
            cache.set(cache_key, results, 3600)
            self._increment_rate_limit(source)
            
        except Exception as e:
            logger.error(f"Error searching {source} for '{query}': {e}")
        
        return results
    
    def _search_unsplash(self, query: str, page: int, per_page: int) -> List[Dict]:
        """Search Unsplash API"""
        url = "https://api.unsplash.com/search/photos"
        headers = {
            'Authorization': f'Client-ID {self.unsplash_access_key}',
            'Accept-Version': 'v1'
        }
        params = {
            'query': query,
            'page': page,
            'per_page': min(per_page, 30),  # Unsplash max is 30
            'orientation': 'all'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for photo in data.get('results', []):
            results.append({
                'id': f"unsplash_{photo['id']}",
                'source': 'unsplash',
                'title': photo.get('alt_description', photo.get('description', 'Untitled')),
                'description': photo.get('description', ''),
                'thumbnail_url': photo['urls']['thumb'],
                'medium_url': photo['urls']['regular'],
                'large_url': photo['urls']['full'],
                'width': photo['width'],
                'height': photo['height'],
                'photographer': photo['user']['name'],
                'photographer_url': photo['user']['links']['html'],
                'download_url': photo['links']['download'],
                'tags': [tag['title'] for tag in photo.get('tags', [])],
                'attribution_required': True,
                'license': 'Unsplash License'
            })
        
        return results
    
    def _search_pixabay(self, query: str, page: int, per_page: int) -> List[Dict]:
        """Search Pixabay API"""
        url = "https://pixabay.com/api/"
        params = {
            'key': self.pixabay_api_key,
            'q': query,
            'image_type': 'photo',
            'orientation': 'all',
            'category': 'all',
            'safesearch': 'true',
            'page': page,
            'per_page': min(per_page, 200)  # Pixabay max is 200
        }
        
        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for image in data.get('hits', []):
            results.append({
                'id': f"pixabay_{image['id']}",
                'source': 'pixabay',
                'title': image.get('tags', 'Untitled'),
                'description': '',
                'thumbnail_url': image['previewURL'],
                'medium_url': image['webformatURL'],
                'large_url': image.get('fullHDURL', image['largeImageURL']),
                'width': image['imageWidth'],
                'height': image['imageHeight'],
                'photographer': image['user'],
                'photographer_url': f"https://pixabay.com/users/{image['user']}-{image['user_id']}/",
                'download_url': image['webformatURL'],
                'tags': image['tags'].split(', '),
                'attribution_required': False,
                'license': 'Pixabay License'
            })
        
        return results
    
    def _search_pexels(self, query: str, page: int, per_page: int) -> List[Dict]:
        """Search Pexels API"""
        url = "https://api.pexels.com/v1/search"
        headers = {
            'Authorization': self.pexels_api_key
        }
        params = {
            'query': query,
            'page': page,
            'per_page': min(per_page, 80)  # Pexels max is 80
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for photo in data.get('photos', []):
            results.append({
                'id': f"pexels_{photo['id']}",
                'source': 'pexels',
                'title': photo.get('alt', 'Untitled'),
                'description': '',
                'thumbnail_url': photo['src']['tiny'],
                'medium_url': photo['src']['medium'],
                'large_url': photo['src']['original'],
                'width': photo['width'],
                'height': photo['height'],
                'photographer': photo['photographer'],
                'photographer_url': photo['photographer_url'],
                'download_url': photo['src']['original'],
                'tags': [],
                'attribution_required': True,
                'license': 'Pexels License'
            })
        
        return results
    
    def _check_rate_limit(self, source: str) -> bool:
        """Check if we can make a request to the source"""
        current_time = time.time()
        limit_info = self.rate_limits[source]
        
        # Reset counter if an hour has passed
        if current_time - limit_info['reset_time'] >= 3600:
            limit_info['requests'] = 0
            limit_info['reset_time'] = current_time
        
        return limit_info['requests'] < limit_info['per_hour']
    
    def _increment_rate_limit(self, source: str):
        """Increment rate limit counter"""
        self.rate_limits[source]['requests'] += 1
    
    def get_trending_images(self, source: str = 'all', per_page: int = 20) -> List[Dict]:
        """Get trending/popular images"""
        cache_key = f"trending_images_{source}_{per_page}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results
        
        results = []
        
        try:
            if source == 'all':
                # Get trending from each source
                trending_queries = ['design', 'business', 'technology', 'abstract']
                for query in trending_queries:
                    query_results = self.search_all_sources(query, 1, 5)
                    results.extend(query_results)
            else:
                # Get from specific source
                if source == 'unsplash':
                    results = self._get_unsplash_trending(per_page)
                elif source == 'pixabay':
                    results = self._get_pixabay_trending(per_page)
                elif source == 'pexels':
                    results = self._get_pexels_trending(per_page)
            
            # Cache for 30 minutes
            cache.set(cache_key, results, 1800)
            
        except Exception as e:
            logger.error(f"Error getting trending images from {source}: {e}")
        
        return results[:per_page]
    
    def _get_unsplash_trending(self, per_page: int) -> List[Dict]:
        """Get trending images from Unsplash"""
        if not self.unsplash_access_key:
            return []
        
        url = "https://api.unsplash.com/photos"
        headers = {
            'Authorization': f'Client-ID {self.unsplash_access_key}',
            'Accept-Version': 'v1'
        }
        params = {
            'order_by': 'popular',
            'per_page': min(per_page, 30)
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for photo in data:
            results.append({
                'id': f"unsplash_{photo['id']}",
                'source': 'unsplash',
                'title': photo.get('alt_description', 'Untitled'),
                'thumbnail_url': photo['urls']['thumb'],
                'medium_url': photo['urls']['regular'],
                'large_url': photo['urls']['full'],
                'width': photo['width'],
                'height': photo['height'],
                'photographer': photo['user']['name'],
                'photographer_url': photo['user']['links']['html'],
                'attribution_required': True
            })
        
        return results
    
    def _get_pixabay_trending(self, per_page: int) -> List[Dict]:
        """Get trending images from Pixabay"""
        return self._search_pixabay('popular', 1, per_page)
    
    def _get_pexels_trending(self, per_page: int) -> List[Dict]:
        """Get curated images from Pexels"""
        if not self.pexels_api_key:
            return []
        
        url = "https://api.pexels.com/v1/curated"
        headers = {
            'Authorization': self.pexels_api_key
        }
        params = {
            'page': 1,
            'per_page': min(per_page, 80)
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for photo in data.get('photos', []):
            results.append({
                'id': f"pexels_{photo['id']}",
                'source': 'pexels',
                'title': photo.get('alt', 'Untitled'),
                'thumbnail_url': photo['src']['tiny'],
                'medium_url': photo['src']['medium'],
                'large_url': photo['src']['original'],
                'width': photo['width'],
                'height': photo['height'],
                'photographer': photo['photographer'],
                'photographer_url': photo['photographer_url'],
                'attribution_required': True
            })
        
        return results

# Global service instance
image_search_service = ImageSearchService()