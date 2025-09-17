import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import {
  User,
  UserCreate,
  UserUpdate,
  LoginRequest,
  Token,
  PasswordResetRequest,
  PasswordResetConfirm,
  ResearchResponse,
  UserListItem
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CacheEntry {
  response: any;
  timestamp: number;
  promise?: Promise<any>;
}

interface DeduplicationStats {
  hits: number;
  misses: number;
  concurrent: number;
}

class ApiClient {
  private client: AxiosInstance;
  private cache: Map<string, CacheEntry>;
  private ttl: number;
  private stats: DeduplicationStats;

  constructor(ttl: number = 300000) { // 5 minutes default
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    this.cache = new Map();
    this.ttl = ttl;
    this.stats = { hits: 0, misses: 0, concurrent: 0 };

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          window.location.href = '/auth/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private generateKey(config: AxiosRequestConfig): string {
    const { method, url, params, data } = config;
    return `${method?.toUpperCase() || 'GET'}:${url}:${JSON.stringify(params || {})}:${JSON.stringify(data || {})}`;
  }

  private isExpired(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp > this.ttl;
  }

  private getCachedResponse(key: string): CacheEntry | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    if (this.isExpired(entry)) {
      this.cache.delete(key);
      return null;
    }
    return entry;
  }

  private setCachedResponse(key: string, response: any, promise?: Promise<any>) {
    this.cache.set(key, {
      response,
      timestamp: Date.now(),
      promise,
    });
  }

  private clearExpired() {
    for (const [key, entry] of this.cache.entries()) {
      if (this.isExpired(entry)) {
        this.cache.delete(key);
      }
    }
  }

  private async deduplicatedRequest<T>(config: AxiosRequestConfig): Promise<T> {
    const key = this.generateKey(config);
    let entry = this.getCachedResponse(key);

    if (entry) {
      if (entry.promise) {
        // Concurrent request in progress
        this.stats.concurrent++;
        return entry.promise as Promise<T>;
      } else {
        // Cache hit
        this.stats.hits++;
        return entry.response;
      }
    }

    // Cache miss
    this.stats.misses++;
    const promise = this.client.request<T>(config).then((response) => {
      this.setCachedResponse(key, response.data);
      return response.data;
    }).catch((error) => {
      // On error, don't cache, but remove any pending promise
      this.cache.delete(key);
      throw error;
    });

    // Set pending promise for concurrent requests
    this.setCachedResponse(key, null, promise);

    return promise;
  }

  // Get deduplication statistics
  getDeduplicationStats(): DeduplicationStats {
    return { ...this.stats };
  }

  // Clear cache
  clearCache() {
    this.cache.clear();
  }

  // Auth endpoints
  async register(data: UserCreate): Promise<Token> {
    return this.deduplicatedRequest<Token>({ method: 'post', url: '/auth/register', data });
  }

  async login(data: LoginRequest): Promise<Token> {
    return this.deduplicatedRequest<Token>({ method: 'post', url: '/auth/login', data });
  }

  async getCurrentUser(): Promise<User> {
    return this.deduplicatedRequest<User>({ method: 'get', url: '/auth/me' });
  }

  async updateProfile(data: UserUpdate): Promise<{ message: string }> {
    return this.deduplicatedRequest<{ message: string }>({ method: 'put', url: '/auth/me', data });
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    return this.deduplicatedRequest<{ message: string }>({ method: 'post', url: '/auth/change-password', data: {
      old_password: oldPassword,
      new_password: newPassword,
    } });
  }

  async forgotPassword(data: PasswordResetRequest): Promise<{ message: string }> {
    return this.deduplicatedRequest<{ message: string }>({ method: 'post', url: '/auth/forgot-password', data });
  }

  async resetPassword(data: PasswordResetConfirm): Promise<{ message: string }> {
    return this.deduplicatedRequest<{ message: string }>({ method: 'post', url: '/auth/reset-password', data });
  }

  // Research endpoints
  async research(query: string): Promise<ResearchResponse> {
    return this.deduplicatedRequest<ResearchResponse>({ method: 'get', url: '/research', params: { query } });
  }

  // Admin endpoints
  async getUsers(skip = 0, limit = 100): Promise<UserListItem[]> {
    return this.deduplicatedRequest<UserListItem[]>({ method: 'get', url: '/admin/users', params: { skip, limit } });
  }

  async updateUserRole(userId: number, role: string): Promise<{ message: string }> {
    return this.deduplicatedRequest<{ message: string }>({ method: 'put', url: `/admin/users/${userId}/role`, data: { new_role: role } });
  }

  // Health check
  async healthCheck(): Promise<string> {
    return this.deduplicatedRequest<string>({ method: 'get', url: '/' });
  }
}

export const apiClient = new ApiClient();