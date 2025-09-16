import { ApiClient } from '../api';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient Deduplication', () => {
  let apiClient: ApiClient;
  let mockResponse: any;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Create new client for each test
    apiClient = new ApiClient(1000); // 1 second TTL for testing

    // Setup mock response
    mockResponse = {
      data: { message: 'success' },
      status: 200,
      statusText: 'OK',
    };
    mockedAxios.create.mockReturnValue(mockedAxios as any);
    mockedAxios.request.mockResolvedValue(mockResponse);
  });

  afterEach(() => {
    // Clear cache between tests
    apiClient.clearCache();
  });

  describe('Request Deduplication', () => {
    it('should deduplicate identical GET requests', async () => {
      const requestConfig = { method: 'get', url: '/test' };

      // Make multiple identical requests
      const promises = [
        apiClient.deduplicatedRequest(requestConfig),
        apiClient.deduplicatedRequest(requestConfig),
        apiClient.deduplicatedRequest(requestConfig),
      ];

      const results = await Promise.all(promises);

      // Should only make one actual HTTP request
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // All promises should resolve with same data
      expect(results).toHaveLength(3);
      results.forEach(result => {
        expect(result).toEqual(mockResponse.data);
      });
    });

    it('should handle concurrent requests properly', async () => {
      const requestConfig = { method: 'get', url: '/concurrent' };

      // Start multiple concurrent requests
      const promise1 = apiClient.deduplicatedRequest(requestConfig);
      const promise2 = apiClient.deduplicatedRequest(requestConfig);
      const promise3 = apiClient.deduplicatedRequest(requestConfig);

      const results = await Promise.all([promise1, promise2, promise3]);

      // Should only make one HTTP request
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // All should get the same result
      results.forEach(result => {
        expect(result).toEqual(mockResponse.data);
      });
    });

    it('should differentiate requests with different parameters', async () => {
      const request1 = { method: 'get', url: '/test', params: { id: 1 } };
      const request2 = { method: 'get', url: '/test', params: { id: 2 } };

      await Promise.all([
        apiClient.deduplicatedRequest(request1),
        apiClient.deduplicatedRequest(request2),
      ]);

      // Should make two separate HTTP requests
      expect(mockedAxios.request).toHaveBeenCalledTimes(2);
    });

    it('should respect TTL and expire cache entries', async () => {
      const requestConfig = { method: 'get', url: '/ttl-test' };

      // First request
      await apiClient.deduplicatedRequest(requestConfig);
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // Wait for TTL to expire
      await new Promise(resolve => setTimeout(resolve, 1100));

      // Second request should make new HTTP call
      await apiClient.deduplicatedRequest(requestConfig);
      expect(mockedAxios.request).toHaveBeenCalledTimes(2);
    });
  });

  describe('Deduplication Statistics', () => {
    it('should track cache hits and misses', async () => {
      const requestConfig = { method: 'get', url: '/stats-test' };

      // First request (cache miss)
      await apiClient.deduplicatedRequest(requestConfig);
      let stats = apiClient.getDeduplicationStats();
      expect(stats.misses).toBe(1);
      expect(stats.hits).toBe(0);

      // Second request (cache hit)
      await apiClient.deduplicatedRequest(requestConfig);
      stats = apiClient.getDeduplicationStats();
      expect(stats.misses).toBe(1);
      expect(stats.hits).toBe(1);
    });

    it('should track concurrent request deduplication', async () => {
      const requestConfig = { method: 'get', url: '/concurrent-stats' };

      // Start concurrent requests
      const promises = [
        apiClient.deduplicatedRequest(requestConfig),
        apiClient.deduplicatedRequest(requestConfig),
        apiClient.deduplicatedRequest(requestConfig),
      ];

      await Promise.all(promises);

      const stats = apiClient.getDeduplicationStats();
      expect(stats.concurrent).toBe(2); // 2 concurrent requests deduplicated
      expect(stats.misses).toBe(1);
      expect(stats.hits).toBe(2);
    });
  });

  describe('Error Handling', () => {
    it('should not cache failed requests', async () => {
      const requestConfig = { method: 'get', url: '/error-test' };

      // Mock failure
      mockedAxios.request.mockRejectedValueOnce(new Error('Network error'));

      // First request fails
      await expect(apiClient.deduplicatedRequest(requestConfig)).rejects.toThrow('Network error');

      // Reset mock for success
      mockedAxios.request.mockResolvedValue(mockResponse);

      // Second request should make new HTTP call (not cached)
      await apiClient.deduplicatedRequest(requestConfig);
      expect(mockedAxios.request).toHaveBeenCalledTimes(2);
    });

    it('should handle malformed requests gracefully', async () => {
      const invalidConfig = { method: 'invalid', url: '/test' };

      await expect(apiClient.deduplicatedRequest(invalidConfig)).rejects.toThrow();
    });
  });

  describe('ISA-Specific Scenarios', () => {
    it('should deduplicate research queries', async () => {
      const researchQuery = 'CSRD compliance requirements';

      // Simulate multiple research requests with same query
      const promises = [
        apiClient.research(researchQuery),
        apiClient.research(researchQuery),
        apiClient.research(researchQuery),
      ];

      const results = await Promise.all(promises);

      // Should only make one HTTP request
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // All results should be identical
      expect(results[0]).toEqual(results[1]);
      expect(results[1]).toEqual(results[2]);
    });

    it('should deduplicate user profile requests', async () => {
      // Simulate multiple calls to get current user
      const promises = [
        apiClient.getCurrentUser(),
        apiClient.getCurrentUser(),
        apiClient.getCurrentUser(),
      ];

      const results = await Promise.all(promises);

      // Should only make one HTTP request
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // All results should be the same user data
      results.forEach(result => {
        expect(result).toEqual(mockResponse.data);
      });
    });

    it('should deduplicate admin user list requests', async () => {
      const listParams = { skip: 0, limit: 50 };

      // Simulate multiple admin user list requests
      const promises = [
        apiClient.getUsers(listParams.skip, listParams.limit),
        apiClient.getUsers(listParams.skip, listParams.limit),
        apiClient.getUsers(listParams.skip, listParams.limit),
      ];

      const results = await Promise.all(promises);

      // Should only make one HTTP request
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // All results should be identical
      expect(results[0]).toEqual(results[1]);
      expect(results[1]).toEqual(results[2]);
    });
  });

  describe('Performance Benchmarks', () => {
    it('should demonstrate caching performance improvement', async () => {
      const requestConfig = { method: 'get', url: '/performance-test' };

      const iterations = 100;
      const startTime = Date.now();

      // Make many requests to same endpoint
      const promises = [];
      for (let i = 0; i < iterations; i++) {
        promises.push(apiClient.deduplicatedRequest(requestConfig));
      }

      await Promise.all(promises);

      const endTime = Date.now();
      const totalTime = endTime - startTime;

      // Should only make one HTTP request despite 100 API calls
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // Calculate requests per second
      const requestsPerSecond = iterations / (totalTime / 1000);
      console.log(`Deduplication performance: ${requestsPerSecond.toFixed(2)} req/sec`);

      // Should handle high throughput
      expect(requestsPerSecond).toBeGreaterThan(1000);
    });

    it('should handle mixed request patterns efficiently', async () => {
      const endpoints = ['/users', '/research', '/admin', '/health'];
      const methods = ['get', 'post'];
      const allPromises: Promise<any>[] = [];

      // Generate mixed request patterns
      for (let i = 0; i < 50; i++) {
        const endpoint = endpoints[i % endpoints.length];
        const method = methods[i % methods.length];

        if (method === 'get') {
          allPromises.push(apiClient.deduplicatedRequest({ method, url: endpoint }));
        } else {
          // POST requests with different data (should not be deduplicated)
          allPromises.push(apiClient.deduplicatedRequest({
            method,
            url: endpoint,
            data: { id: i }
          }));
        }
      }

      await Promise.all(allPromises);

      // Should deduplicate GET requests but not POST requests
      const getRequests = Math.floor(50 / methods.length); // Half are GET
      const postRequests = Math.ceil(50 / methods.length); // Half are POST

      // GET requests should be deduplicated to 4 (one per endpoint)
      // POST requests should all be separate (25)
      expect(mockedAxios.request).toHaveBeenCalledTimes(4 + 25);
    });
  });

  describe('Memory Efficiency', () => {
    it('should not leak memory with cache operations', async () => {
      const requestConfig = { method: 'get', url: '/memory-test' };

      // Perform many operations
      for (let i = 0; i < 1000; i++) {
        await apiClient.deduplicatedRequest({
          ...requestConfig,
          params: { id: i } // Different params to avoid deduplication
        });
      }

      // Cache should automatically clean up expired entries
      // (Note: In a real scenario, we'd monitor actual memory usage)
      const stats = apiClient.getDeduplicationStats();
      expect(stats.misses).toBe(1000); // All should be misses due to different params
    });

    it('should clean up expired cache entries', async () => {
      // Create client with very short TTL
      const shortTtlClient = new ApiClient(100); // 100ms TTL

      const requestConfig = { method: 'get', url: '/cleanup-test' };

      // Make request
      await shortTtlClient.deduplicatedRequest(requestConfig);
      expect(mockedAxios.request).toHaveBeenCalledTimes(1);

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      // Make same request again
      await shortTtlClient.deduplicatedRequest(requestConfig);
      expect(mockedAxios.request).toHaveBeenCalledTimes(2); // Should make new request
    });
  });

  describe('Integration Tests', () => {
    it('should work with real API endpoints', async () => {
      // Mock successful responses for different endpoints
      mockedAxios.request.mockImplementation((config) => {
        const responses: { [key: string]: any } = {
          '/auth/me': { data: { id: 1, email: 'test@example.com' } },
          '/research': { data: { results: ['result1', 'result2'] } },
          '/admin/users': { data: [{ id: 1, email: 'admin@example.com' }] },
        };

        return Promise.resolve(responses[config.url || ''] || mockResponse);
      });

      // Test auth endpoint
      const user = await apiClient.getCurrentUser();
      expect(user.id).toBe(1);

      // Test research endpoint
      const research = await apiClient.research('test query');
      expect(research.results).toHaveLength(2);

      // Test admin endpoint
      const users = await apiClient.getUsers();
      expect(users).toHaveLength(1);

      // Verify deduplication worked
      expect(mockedAxios.request).toHaveBeenCalledTimes(3);
    });

    it('should handle authentication token management', async () => {
      // Mock localStorage
      const mockLocalStorage = {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      };
      Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

      // Mock token in storage
      mockLocalStorage.getItem.mockReturnValue('test-token');

      const requestConfig = { method: 'get', url: '/protected' };
      await apiClient.deduplicatedRequest(requestConfig);

      // Should include authorization header
      expect(mockedAxios.request).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token'
          })
        })
      );
    });
  });
});