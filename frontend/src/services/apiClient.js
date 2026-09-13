/**
 * Aegis AI - Centralized HTTP Client
 * Attaches JWT Bearer authentication, handles standard ApiResponse envelope,
 * and formats API errors.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  getAuthToken() {
    return localStorage.getItem('aegis_token');
  }

  getTenantId() {
    const userJson = localStorage.getItem('aegis_user');
    if (!userJson) return null;
    try {
      const user = JSON.parse(userJson);
      return user.tenant_id;
    } catch {
      return null;
    }
  }

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    const token = this.getAuthToken();
    const tenantId = this.getTenantId();

    const headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(tenantId ? { 'X-Tenant-ID': tenantId } : {}),
      ...options.headers,
    };

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('aegis_token');
        localStorage.removeItem('aegis_user');
        if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register')) {
          window.dispatchEvent(new CustomEvent('aegis_auth_expired'));
        }
      }

      const isJson = response.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await response.json() : await response.text();

      if (!response.ok) {
        const errorMsg = data?.error?.message || data?.detail || `Request failed with status ${response.status}`;
        throw new Error(errorMsg);
      }

      // Backend wraps data in { data: ..., meta: ... }
      return data?.data !== undefined ? data.data : data;
    } catch (err) {
      console.error(`API [${config.method || 'GET'}] ${url} failed:`, err);
      throw err;
    }
  }

  get(endpoint, headers = {}) {
    return this.request(endpoint, { method: 'GET', headers });
  }

  post(endpoint, body, headers = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
      headers,
    });
  }

  put(endpoint, body, headers = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
      headers,
    });
  }

  patch(endpoint, body, headers = {}) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
      headers,
    });
  }

  delete(endpoint, headers = {}) {
    return this.request(endpoint, { method: 'DELETE', headers });
  }
}

export const apiClient = new ApiClient();
export default apiClient;
