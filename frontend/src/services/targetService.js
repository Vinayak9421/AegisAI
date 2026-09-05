/**
 * Target management service interfacing with /api/v1/targets and /api/v1/provenance.
 */

import apiClient from './apiClient';

export const targetService = {
  /**
   * List all registered targets for the current tenant.
   */
  async listTargets() {
    const res = await apiClient.get('/targets');
    return res.items || [];
  },

  /**
   * Get single target by ID.
   */
  async getTarget(targetId) {
    return apiClient.get(`/targets/${targetId}`);
  },

  /**
   * Register a new target system to evaluate.
   */
  async createTarget(payload) {
    return apiClient.post('/targets', payload);
  },

  /**
   * Run connection and health verification probe on target.
   */
  async verifyTarget(targetId) {
    return apiClient.post(`/targets/${targetId}/verify`);
  },

  /**
   * Submit or update target blueprint (Phase 3 Provenance & Identity Engine).
   */
  async submitBlueprint(targetId, blueprintData) {
    return apiClient.post(`/targets/${targetId}/blueprint`, blueprintData);
  },

  /**
   * Get active blueprint and identity score.
   */
  async getBlueprint(targetId) {
    return apiClient.get(`/targets/${targetId}/blueprint`);
  },
};

export default targetService;
