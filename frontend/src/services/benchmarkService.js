/**
 * Benchmark catalog service querying ingested datasets and test cases.
 */

import apiClient from './apiClient';

export const benchmarkService = {
  /**
   * List all ingested benchmark sources (FinRed, HarmBench, AdvBench).
   */
  async listSources() {
    const res = await apiClient.get('/benchmarks/sources');
    return res.items || [];
  },

  /**
   * List individual attack test cases directly from PostgreSQL DB.
   */
  async listTestCases(params = {}) {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.severity) query.append('severity', params.severity);
    if (params.search) query.append('search', params.search);
    if (params.limit) query.append('limit', params.limit || 50);
    if (params.offset !== undefined) query.append('offset', params.offset);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await apiClient.get(`/benchmarks/test-cases${queryString}`);
    return {
      items: res.items || [],
      total: res.total_estimate || 0,
    };
  },

  /**
   * Get category summary stats for the threat matrix.
   */
  async getCategoryStats() {
    return apiClient.get('/benchmarks/stats');
  },
};

export default benchmarkService;
