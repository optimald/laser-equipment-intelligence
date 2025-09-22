// API service for connecting to the Railway backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://laser-backend-production.up.railway.app';

// Debug: Log the API URL being used
console.log('🔗 API_BASE_URL:', API_BASE_URL);

export interface SearchParams {
  query?: string;
  brand?: string;
  model?: string;
  condition?: string;
  max_price?: number;
  min_price?: number;
  location?: string;
  sources?: string[];
  min_score?: number;
  limit?: number;
}

export interface EquipmentListing {
  id: number;
  title: string;
  brand?: string;
  model?: string;
  condition?: string;
  price?: number;
  source: string;
  location?: string;
  description?: string;
  images?: string[];
  discovered_at: string;
  margin_estimate?: number;
  score_overall?: number;
  url?: string;
}

export interface SourceConfiguration {
  id: string;
  name: string;
  priority: string;
  enabled: boolean;
  last_run?: string;
  status: string;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Search API methods
  async searchEquipment(params: SearchParams): Promise<EquipmentListing[]> {
    return this.request<EquipmentListing[]>('/api/v1/search/equipment', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getAvailableSources(): Promise<string[]> {
    const response = await this.request<{ sources: string[] }>('/api/v1/search/sources');
    return response.sources;
  }

  async getAvailableBrands(): Promise<string[]> {
    const response = await this.request<{ brands: string[] }>('/api/v1/search/brands');
    return response.brands;
  }

  async getSearchStats(): Promise<{
    total_listings: number;
    recent_listings: number;
    source_stats: Array<{ source: string; count: number }>;
  }> {
    return this.request('/api/v1/search/stats');
  }

  // Configuration API methods
  async getSourceConfigurations(): Promise<SourceConfiguration[]> {
    return this.request<SourceConfiguration[]>('/api/v1/config/sources');
  }

  async updateSourceConfiguration(sourceId: string, enabled: boolean): Promise<SourceConfiguration> {
    return this.request<SourceConfiguration>(`/api/v1/config/sources/${sourceId}`, {
      method: 'PUT',
      body: JSON.stringify({ enabled }),
    });
  }

  // Spider API methods
  async getSpiderStatus(): Promise<Array<{
    name: string;
    status: string;
    last_run?: string;
    items_last_run: number;
    avg_items_per_run: number;
    success_rate: number;
  }>> {
    return this.request('/api/v1/spiders');
  }

  async runSpider(spiderName: string): Promise<{ message: string }> {
    return this.request(`/api/v1/spiders/run/${spiderName}`, {
      method: 'POST',
    });
  }

  async runAllSpiders(): Promise<{ message: string }> {
    return this.request('/api/v1/spiders/run-all', {
      method: 'POST',
    });
  }

  async getSpiderStats(): Promise<{
    total_runs: number;
    successful_runs: number;
    failed_runs: number;
    success_rate: number;
    total_items_scraped: number;
    runs_by_spider: Array<{
      spider_name: string;
      run_count: number;
      avg_items: number;
      successful_runs: number;
    }>;
  }> {
    return this.request('/api/v1/spiders/stats');
  }

  // LaserMatch Endpoints
  async scrapeLaserMatch(): Promise<{
    message: string;
    items_scraped: number;
    items_added: number;
    execution_time: number;
  }> {
    return this.request('/api/v1/lasermatch/scrape', {
      method: 'POST',
    });
  }

  async getLaserMatchItems(skip = 0, limit = 100): Promise<{
    items: any[];
    total: number;
  }> {
    const url = `/api/v1/lasermatch/items?skip=${skip}&limit=${limit}`;
    console.log('🌐 Fetching LaserMatch items from:', API_BASE_URL + url);
    return this.request(url);
  }

  async getLaserMatchStats(): Promise<{
    total_items: number;
    hot_list_items: number;
    in_demand_items: number;
    latest_update: string | null;
  }> {
    return this.request('/api/v1/lasermatch/stats');
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }
}

export const apiService = new ApiService();
export default apiService;