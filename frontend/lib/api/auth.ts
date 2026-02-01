/**
 * Authentication API
 * Functions for user authentication
 */

import { getApiBaseUrl, getAuthToken, setAuthToken, removeAuthToken } from '@/lib/api/client';

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
  discord_handle?: string;
  created_at?: string;
  email_verified: boolean;
  auth_provider: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
  confirm_new_password: string;
}

export interface GoogleAuthRequest {
  credential: string;
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
      const msg = Array.isArray(error.detail)
        ? error.detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ')
        : (error.detail || error.message || 'Login failed');

      // 404 = login route not found → usually wrong API URL (e.g. pointing at Vercel instead of Render)
      if (response.status === 404) {
        throw new Error(
          `Login endpoint not found (404). In Vercel → Settings → Environment Variables, set NEXT_PUBLIC_API_URL to your backend URL (e.g. https://boosterboxpro.onrender.com). Current attempt was: ${loginUrl}`
        );
      }
      throw new Error(msg || 'Login failed');
    }

    const authData: AuthResponse = await response.json();
    setAuthToken(authData.access_token);
    return authData;
  } catch (error) {
    // Handle network errors (Failed to fetch) – often CORS or backend unreachable
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      const isProduction = apiUrl.startsWith('https://');
      const origin =
        typeof window !== 'undefined'
          ? window.location.origin
          : 'this site';
      const hint = isProduction
        ? `Add this exact URL to Render CORS_ORIGINS: ${origin} (no trailing slash). Then save, wait for redeploy, and try again. If backend was sleeping, wait ~30s and retry.`
        : 'Ensure the backend is running (e.g. port 8000 for local).';
      throw new Error(
        `Cannot connect to backend at ${apiUrl}. ${hint} [${error.message}]`
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

/**
 * Forgot password — request reset email
 */
export async function forgotPassword(data: ForgotPasswordRequest): Promise<{ message: string }> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

/**
 * Reset password with token from email
 */
export async function resetPassword(data: ResetPasswordRequest): Promise<{ message: string }> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Reset failed' }));
    throw new Error(error.detail || 'Reset failed');
  }
  return response.json();
}

/**
 * Verify email with token from email
 */
export async function verifyEmail(token: string): Promise<{ message: string; email_verified: boolean }> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/verify-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Verification failed' }));
    throw new Error(error.detail || 'Verification failed');
  }
  return response.json();
}

/**
 * Resend verification email (requires auth)
 */
export async function resendVerification(): Promise<{ message: string }> {
  const token = getAuthToken();
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/resend-verification`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to resend' }));
    throw new Error(error.detail || 'Failed to resend');
  }
  return response.json();
}

/**
 * Authenticate with Google ID token
 */
export async function googleAuth(data: GoogleAuthRequest): Promise<AuthResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Google sign-in failed' }));
    throw new Error(error.detail || 'Google sign-in failed');
  }
  const authData: AuthResponse = await response.json();
  setAuthToken(authData.access_token);
  return authData;
}

