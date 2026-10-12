import apiClient from './apiClient';

class SystemService {
  /**
   * Fetch runtime system configuration including active judge model, provider, and environment.
   */
  async getConfig() {
    return apiClient.get('/system/config');
  }
}

const systemService = new SystemService();
export default systemService;
