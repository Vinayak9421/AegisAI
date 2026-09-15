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
    if (Array.isArray(res)) return res;
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

  /**
   * Upload custom benchmark test suite (CSV or JSON).
   */
  async uploadTestSuite(formData) {
    return apiClient.upload('/benchmarks/upload', formData);
  },

  /**
   * Delete a benchmark test suite source and its test cases.
   */
  async deleteSource(sourceId) {
    return apiClient.delete(`/benchmarks/sources/${sourceId}`);
  },

  /**
   * Download sample test suite template (CSV or JSON).
   */
  async downloadTemplate(format = 'csv') {
    const token = apiClient.getAuthToken();
    const tenantId = apiClient.getTenantId();
    const url = `${apiClient.baseUrl}/benchmarks/templates/${format}`;
    const res = await fetch(url, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(tenantId ? { 'X-Tenant-ID': tenantId } : {}),
      },
    });
    if (!res.ok) {
      throw new Error(`Failed to download template: ${res.statusText}`);
    }
    const blob = await res.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', `aegis_test_suite_template.${format}`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
};

export default benchmarkService;
