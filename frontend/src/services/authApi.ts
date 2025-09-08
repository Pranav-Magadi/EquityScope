import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Types for authentication
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  company?: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name?: string;
  company?: string;
  status: string;
  email_verified: boolean;
  tier: string;
  subscription_status: {
    is_active: boolean;
    expires_at?: string;
    days_remaining?: number;
  };
  total_analyses: number;
  monthly_analyses: number;
  rate_limits: {
    analyses_per_hour: number;
    analyses_per_day: number;
    analyses_per_month: number;
  };
  created_at: string;
  last_login?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface ApiKeyResponse {
  api_key_id: string;
  name: string;
  key: string;
  expires_at?: string;
  created_at: string;
  warning: string;
}

export interface UsageStats {
  total_analyses: number;
  monthly_analyses: number;
  current_streak: number;
  favorite_sectors: string[];
  most_analyzed_companies: string[];
  cost_savings: {
    total_saved: number;
    cache_hit_rate: number;
  };
}

// Create axios instance for auth API
const authApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
class TokenManager {
  private static TOKEN_KEY = 'equityscope_token';
  private static USER_KEY = 'equityscope_user';

  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  static removeToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  static getUser(): UserResponse | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  static setUser(user: UserResponse): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  static isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      // Check if token is expired (basic check)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp > now;
    } catch {
      return false;
    }
  }
}

// Request interceptor to add auth token
authApi.interceptors.request.use(
  (config) => {
    const token = TokenManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for auth errors
authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      TokenManager.removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export class AuthService {
  // Authentication
  static async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response: AxiosResponse<TokenResponse> = await authApi.post('/api/v2/auth/login', credentials);
    const { access_token, user } = response.data;
    
    TokenManager.setToken(access_token);
    TokenManager.setUser(user);
    
    return response.data;
  }

  static async register(userData: RegisterRequest): Promise<UserResponse> {
    const response: AxiosResponse<UserResponse> = await authApi.post('/api/v2/auth/register', userData);
    return response.data;
  }

  static async logout(): Promise<void> {
    try {
      await authApi.post('/api/v2/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      TokenManager.removeToken();
    }
  }

  // User profile
  static async getCurrentUser(): Promise<UserResponse> {
    const response: AxiosResponse<UserResponse> = await authApi.get('/api/v2/auth/me');
    TokenManager.setUser(response.data);
    return response.data;
  }

  static async updateProfile(updates: { full_name?: string; company?: string }): Promise<UserResponse> {
    const response: AxiosResponse<UserResponse> = await authApi.put('/api/v2/auth/me', updates);
    TokenManager.setUser(response.data);
    return response.data;
  }

  // Password management
  static async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await authApi.post('/api/v2/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  static async forgotPassword(email: string): Promise<void> {
    await authApi.post('/api/v2/auth/forgot-password', { email });
  }

  static async resetPassword(token: string, newPassword: string): Promise<void> {
    await authApi.post('/api/v2/auth/reset-password', {
      token,
      new_password: newPassword
    });
  }

  // Email verification
  static async verifyEmail(token: string): Promise<void> {
    await authApi.post('/api/v2/auth/verify-email', { token });
  }

  // Usage and statistics
  static async getUsageStats(): Promise<UsageStats> {
    const response: AxiosResponse<UsageStats> = await authApi.get('/api/v2/auth/usage-stats');
    return response.data;
  }

  static async getRateLimitStatus(): Promise<any> {
    const response = await authApi.get('/api/v2/auth/rate-limit-status');
    return response.data;
  }

  // API Keys
  static async createApiKey(name: string, expiresInDays?: number): Promise<ApiKeyResponse> {
    const response: AxiosResponse<ApiKeyResponse> = await authApi.post('/api/v2/auth/api-keys', {
      name,
      expires_days: expiresInDays
    });
    return response.data;
  }

  static async getActiveSessions(): Promise<any[]> {
    const response = await authApi.get('/api/v2/auth/sessions');
    return response.data.active_sessions;
  }

  static async invalidateSession(sessionId: string): Promise<void> {
    await authApi.delete(`/api/v2/auth/sessions/${sessionId}`);
  }

  // Token management utilities
  static getStoredToken(): string | null {
    return TokenManager.getToken();
  }

  static getStoredUser(): UserResponse | null {
    return TokenManager.getUser();
  }

  static isAuthenticated(): boolean {
    return TokenManager.isAuthenticated();
  }

  static clearAuth(): void {
    TokenManager.removeToken();
  }
}

// Enhanced API service with authentication
export class AuthenticatedApiService {
  private static getAuthHeaders() {
    const token = TokenManager.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // Protected analysis endpoints
  static async analyzeCompany(ticker: string, userAssumptions?: any): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v2/analyze`,
      {
        ticker,
        user_assumptions: userAssumptions
      },
      {
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders()
        }
      }
    );
    return response.data;
  }

  static async multiStageDCF(
    ticker: string,
    mode?: string,
    userLevel?: string,
    userAssumptions?: any
  ): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v2/multi-stage-dcf`,
      {
        ticker,
        mode,
        user_level: userLevel,
        user_assumptions: userAssumptions
      },
      {
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders()
        }
      }
    );
    return response.data;
  }

  static async getModeRecommendation(ticker: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v2/mode-recommendation`,
      { ticker },
      {
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders()
        }
      }
    );
    return response.data;
  }

  static async getUserDashboard(): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v2/user-dashboard`,
      {
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  static async getSubscriptionPlans(): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v2/subscription-plans`
    );
    return response.data;
  }

  static async getDemoAnalyses(): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v2/demo-analyses`
    );
    return response.data;
  }

  static async getDemoAnalysis(ticker: string): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v2/demo-analyses/${ticker}`
    );
    return response.data;
  }
}

export { TokenManager };
export default AuthService;