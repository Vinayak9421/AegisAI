/**
 * Authentication service handling login, registration, and user session retrieval.
 */

import apiClient from './apiClient';

export const authService = {
  /**
   * Authenticate user or admin with email and password.
   * @param {string} email
   * @param {string} password
   */
  async login(email, password) {
    const data = await apiClient.post('/auth/login', { email, password });
    if (data.access_token) {
      localStorage.setItem('aegis_token', data.access_token);
      localStorage.setItem('aegis_user', JSON.stringify(data.user));
    }
    return data;
  },

  /**
   * Register a new user and tenant workspace.
   * @param {Object} payload { email, password, organization_name }
   */
  async register(payload) {
    const data = await apiClient.post('/auth/register', payload);
    if (data.access_token) {
      localStorage.setItem('aegis_token', data.access_token);
      localStorage.setItem('aegis_user', JSON.stringify(data.user));
    }
    return data;
  },

  /**
   * Fetch profile of currently authenticated user.
   */
  async getMe() {
    return apiClient.get('/auth/me');
  },

  /**
   * Log out user and clear stored tokens.
   */
  logout() {
    localStorage.removeItem('aegis_token');
    localStorage.removeItem('aegis_user');
  },

  /**
   * Get currently stored user object.
   */
  getCurrentUser() {
    try {
      const stored = localStorage.getItem('aegis_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  },

  /**
   * Check if current user is admin.
   */
  isAdmin() {
    const user = this.getCurrentUser();
    return user?.role === 'ADMIN';
  },
};

export default authService;
