/**
 * Job execution service for scheduling, running, and retrieving evaluation test runs.
 */

import apiClient from './apiClient';

export const jobService = {
  /**
   * List evaluation jobs with optional filtering.
   */
  async listJobs(params = {}) {
    const query = new URLSearchParams();
    if (params.target_id) query.append('target_id', params.target_id);
    if (params.state) query.append('state', params.state);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await apiClient.get(`/jobs${queryString}`);
    return res.items || [];
  },

  /**
   * Get single job by ID.
   */
  async getJob(jobId) {
    return apiClient.get(`/jobs/${jobId}`);
  },

  /**
   * Create a new evaluation job for a target.
   * @param {Object} payload { target_id, mode: 'QUICK'|'FULL', authorization_confirmed: true }
   */
  async createJob(payload) {
    return apiClient.post('/jobs', {
      authorization_confirmed: true,
      mode: 'QUICK',
      ...payload,
    });
  },

  /**
   * Run the evaluation execution runner for a job.
   */
  async runJob(jobId) {
    return apiClient.post(`/jobs/${jobId}/run`);
  },

  /**
   * Cancel an in-flight evaluation job.
   */
  async cancelJob(jobId) {
    return apiClient.post(`/jobs/${jobId}/cancel`);
  },

  /**
   * Retrieve test case results and judge verdicts for a job.
   */
  async getJobResults(jobId, params = {}) {
    const query = new URLSearchParams();
    if (params.verdict) query.append('verdict', params.verdict);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await apiClient.get(`/jobs/${jobId}/results${queryString}`);
    return res.items || [];
  },

  /**
   * Retrieve multi-dimensional Trust & Safety certificate for a job.
   */
  async getCertificate(jobId) {
    return apiClient.get(`/jobs/${jobId}/certificate`);
  },

  /**
   * Generate/finalize Trust & Safety certificate for a job.
   */
  async generateCertificate(jobId) {
    return apiClient.post(`/jobs/${jobId}/certificate`);
  },
};

export default jobService;
