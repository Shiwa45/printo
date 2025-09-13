// src/services/products.ts
import api from './api';

// Helper to extract data from axios response
const getData = <T>(response: any): T => response.data as T;

// Product Types (expand the existing ones)
export interface ProductCategory {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon?: string;
  subcategories?: ProductCategory[];
}

export interface ProductImage {
  image: string;
  alt_text: string;
  is_primary: boolean;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  category: ProductCategory;
  product_type: string;
  description: string;
  short_description: string;
  base_price: string;
  pricing_structure?: any;
  size_options?: any;
  paper_options?: any;
  print_options?: any;
  binding_options?: any;
  finish_options?: any;
  design_tool_enabled: boolean;
  design_templates?: any;
  min_quantity: number;
  max_quantity: number;
  stock_status: string;
  lead_time_days: number;
  rush_available: boolean;
  featured: boolean;
  bestseller: boolean;
  images: ProductImage[];
  primary_image?: string;
  tags: string[];
}

export interface PaginatedProducts {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

export const productsService = {
  // Get all categories
  getCategories: async (): Promise<ProductCategory[]> => {
    const response = await api.get<ProductCategory[]>('/categories/');
    return getData(response);
  },

  // Get category by slug
  getCategory: async (slug: string): Promise<ProductCategory> => {
    const response = await api.get<ProductCategory>(`/categories/${slug}/`);
    return getData(response);
  },

  // Get all products with pagination and filters
  getProducts: async (params?: {
    page?: number;
    category?: string;
    search?: string;
    featured?: boolean;
    bestseller?: boolean;
    design_tool_enabled?: boolean;
  }): Promise<PaginatedProducts> => {
    const response = await api.get<PaginatedProducts>('/products/', { params });
    return getData(response);
  },

  // Get product by slug
  getProduct: async (slug: string): Promise<Product> => {
    const response = await api.get<Product>(`/products/${slug}/`);
    return getData(response);
  },

  // Get bestselling products
  getBestsellers: async (): Promise<Product[]> => {
    const response = await api.get<Product[]>('/products/bestsellers/');
    return getData(response);
  },

  // Get design-enabled products
  getDesignProducts: async (): Promise<Product[]> => {
    const response = await api.get<Product[]>('/products/design_products/');
    return getData(response);
  },

  // Search products
  searchProducts: async (query: string): Promise<Product[]> => {
    const response = await api.get<PaginatedProducts>('/products/', {
      params: { search: query }
    });
    return getData<PaginatedProducts>(response).results;
  },

  // Calculate pricing
  calculatePricing: async (productSlug: string, specifications: any): Promise<any> => {
    const response = await api.post('/pricing/calculate/', {
      product_slug: productSlug,
      quantity: specifications.quantity || 1,
      specifications: specifications,
    });
    return getData(response);
  },
};

export default productsService;