/**
 * Authentication API
 * Functions for user authentication
 */

import { getApiBaseUrl, getAuthToken, setAuthToken, removeAuthToken } from './client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  is_admin: boolean;
  subscription_status: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  is_admin: boolean;
}

/**
 * Login user
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const apiUrl = getApiBaseUrl();
  const loginUrl = `${apiUrl}/api/v1/auth/login`;
  
  // Debug logging
  console.log('[Login] API URL:', apiUrl);
  console.log('[Login] Login URL:', loginUrl);
  
  try {
    const response = await fetch(loginUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      
      // Handle FastAPI validation errors (array format)
      if (Array.isArray(error.detail)) {
        const messages = error.detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
        throw new Error(messages || 'Login failed');
      }
      
      // Handle simple error message
      throw new Error(error.detail || error.message || 'Login failed');
    }

    const authData: AuthResponse = await response.json();
    setAuthToken(authData.access_token);
    return authData;
  } catch (error) {
    // Handle network errors (Failed to fetch)
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw new Error(
        `Cannot connect to backend server at ${apiUrl}. ` +
        `Please ensure the backend is running on port 8000. ` +
        `Error: ${error.message}`
      );
    }
    // Re-throw other errors
    throw error;
  }
}

/**
 * Register new user
 */
export async function register(data: RegisterRequest): Promise<void> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
    
    // Handle FastAPI validation errors (array format)
    if (Array.isArray(error.detail)) {
      const messages = error.detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
      throw new Error(messages || 'Registration failed');
    }
    
    // Handle simple error message
    throw new Error(error.detail || error.message || 'Registration failed');
  }
}

/**
 * Get current user
 */
export async function getCurrentUser(): Promise<UserResponse> {
  const token = getAuthToken();
  if (!token) {
    // Return a special error that won't be logged as a console error
    const error = new Error('No authentication token');
    (error as any).isUnauthenticated = true;
    throw error;
  }

  // Create an AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

  try {
    const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      // If 401 or 403, user is not authenticated - remove token and throw silent error
      if (response.status === 401 || response.status === 403) {
        removeAuthToken();
        const error = new Error('Authentication failed');
        (error as any).isUnauthenticated = true;
        throw error;
      }
      // For other errors, throw normal error
      removeAuthToken();
      throw new Error(`Failed to get current user: ${response.status} ${response.statusText}`);
    }

    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    // Handle AbortError (timeout) gracefully
    if (error instanceof Error && error.name === 'AbortError') {
      const timeoutError = new Error('Request timeout');
      timeoutError.name = 'TimeoutError';
      (timeoutError as any).isUnauthenticated = true;
      throw timeoutError;
    }
    // Re-throw the error (it may have isUnauthenticated flag)
    throw error;
  }
}

/**
 * Logout user
 */
export function logout(): void {
  removeAuthToken();
}

